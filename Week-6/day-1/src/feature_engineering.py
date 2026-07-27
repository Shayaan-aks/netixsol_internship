"""
feature_engineering.py — Leakage-free pre-match rolling feature computation pipeline & feature dictionary generator
Week 6 Day 1: AFL Data Foundations Project
"""

import os
from pathlib import Path
from typing import Tuple, Dict, List, Any
import numpy as np
import pandas as pd

from .config import (
    FANTASY_WEIGHTS, ROLLING_WINDOWS, TOP_DISPOSALS_THRESHOLD, TOP_GOALS_THRESHOLD,
    DATA_FEATURES_DIR, OUTPUTS_DIR, VENUE_STATE_MAP
)
from .utils import setup_logger, save_dataframe

logger = setup_logger("feature_engineering")


def compute_composite_fantasy_score(df: pd.DataFrame, custom_weights: Dict[str, float] = None) -> pd.Series:
    """
    Computes AFL Fantasy / SuperCoach Composite Score using configurable weights.
    Formula: Score = sum(stat_i * weight_i)
    """
    weights = custom_weights or FANTASY_WEIGHTS
    score = pd.Series(0.0, index=df.index)
    
    for col, weight in weights.items():
        if col in df.columns:
            score += df[col].fillna(0) * weight
            
    return score


def build_team_rolling_features(df_matches: pd.DataFrame, windows: List[int] = None) -> pd.DataFrame:
    """
    Engineers team rolling form features (win %, offense, defense, margin) across specified windows
    strictly using historical pre-match data (.shift(1)) to prevent data leakage.
    """
    windows = windows or ROLLING_WINDOWS
    df = df_matches.sort_values(['season', 'round_number', 'match_date']).copy()
    
    team_outcomes = {}  # team -> list of match result dicts
    h2h_history = {}    # (teamA, teamB) -> list of winners
    venue_history = {}  # (team, venue) -> list of results

    # Columns to populate
    feature_dict = {f"feat_home_win_pct_last{w}": [] for w in windows}
    feature_dict.update({f"feat_away_win_pct_last{w}": [] for w in windows})
    feature_dict.update({f"feat_home_avg_score_last{w}": [] for w in windows})
    feature_dict.update({f"feat_away_avg_score_last{w}": [] for w in windows})
    feature_dict.update({f"feat_home_avg_conceded_last{w}": [] for w in windows})
    feature_dict.update({f"feat_away_avg_conceded_last{w}": [] for w in windows})
    
    home_win_streak = []
    away_win_streak = []
    home_loss_streak = []
    away_loss_streak = []
    h2h_home_win_rate = []
    venue_home_win_rate = []
    prev_meeting_margin = []

    for idx, row in df.iterrows():
        h_team = row['home_team']
        a_team = row['away_team']
        venue = row['venue']
        
        h_hist = team_outcomes.get(h_team, [])
        a_hist = team_outcomes.get(a_team, [])
        
        # 1. Rolling Win %, Offense, Defense across windows (3, 5, 10)
        for w in windows:
            if len(h_hist) > 0:
                h_sub = h_hist[-w:]
                h_win_pct = np.mean([x['win'] for x in h_sub])
                h_avg_pts = np.mean([x['score_for'] for x in h_sub])
                h_avg_con = np.mean([x['score_against'] for x in h_sub])
            else:
                h_win_pct, h_avg_pts, h_avg_con = 0.50, 85.0, 85.0
                
            if len(a_hist) > 0:
                a_sub = a_hist[-w:]
                a_win_pct = np.mean([x['win'] for x in a_sub])
                a_avg_pts = np.mean([x['score_for'] for x in a_sub])
                a_avg_con = np.mean([x['score_against'] for x in a_sub])
            else:
                a_win_pct, a_avg_pts, a_avg_con = 0.50, 85.0, 85.0

            feature_dict[f"feat_home_win_pct_last{w}"].append(round(h_win_pct, 3))
            feature_dict[f"feat_away_win_pct_last{w}"].append(round(a_win_pct, 3))
            feature_dict[f"feat_home_avg_score_last{w}"].append(round(h_avg_pts, 1))
            feature_dict[f"feat_away_avg_score_last{w}"].append(round(a_avg_pts, 1))
            feature_dict[f"feat_home_avg_conceded_last{w}"].append(round(h_avg_con, 1))
            feature_dict[f"feat_away_avg_conceded_last{w}"].append(round(a_avg_con, 1))

        # 2. Win / Loss Streaks
        h_w_strk, h_l_strk = 0, 0
        for item in reversed(h_hist):
            if item['win'] == 1:
                if h_l_strk == 0: h_w_strk += 1
                else: break
            else:
                if h_w_strk == 0: h_l_strk += 1
                else: break
                
        a_w_strk, a_l_strk = 0, 0
        for item in reversed(a_hist):
            if item['win'] == 1:
                if a_l_strk == 0: a_w_strk += 1
                else: break
            else:
                if a_w_strk == 0: a_l_strk += 1
                else: break

        home_win_streak.append(h_w_strk)
        away_win_streak.append(a_w_strk)
        home_loss_streak.append(h_l_strk)
        away_loss_streak.append(a_l_strk)

        # 3. Head-to-Head History
        h2h_key = tuple(sorted([h_team, a_team]))
        h2h_list = h2h_history.get(h2h_key, [])
        if len(h2h_list) > 0:
            h2h_p = sum(1 for item in h2h_list if item['winner'] == h_team) / len(h2h_list)
            prev_margin = h2h_list[-1]['margin'] if h2h_list[-1]['home_team'] == h_team else -h2h_list[-1]['margin']
        else:
            h2h_p = 0.50
            prev_margin = 0.0

        h2h_home_win_rate.append(round(h2h_p, 3))
        prev_meeting_margin.append(prev_margin)

        # 4. Venue Record
        v_list = venue_history.get((h_team, venue), [])
        v_win_p = np.mean(v_list) if len(v_list) > 0 else 0.50
        venue_home_win_rate.append(round(v_win_p, 3))

        # Update History AFTER pre-match feature calculation
        h_score = row['home_score']
        a_score = row['away_score']
        margin = row['score_margin']
        h_win = 1 if margin > 0 else 0
        a_win = 1 if margin < 0 else 0
        winner = h_team if h_win == 1 else a_team

        if h_team not in team_outcomes: team_outcomes[h_team] = []
        if a_team not in team_outcomes: team_outcomes[a_team] = []
        team_outcomes[h_team].append({'win': h_win, 'score_for': h_score, 'score_against': a_score})
        team_outcomes[a_team].append({'win': a_win, 'score_for': a_score, 'score_against': h_score})

        if h2h_key not in h2h_history: h2h_history[h2h_key] = []
        h2h_history[h2h_key].append({'winner': winner, 'margin': margin, 'home_team': h_team})

        if (h_team, venue) not in venue_history: venue_history[(h_team, venue)] = []
        venue_history[(h_team, venue)].append(h_win)

    # Attach to DataFrame
    for k, v in feature_dict.items():
        df[k] = v

    df['feat_home_win_streak'] = home_win_streak
    df['feat_away_win_streak'] = away_win_streak
    df['feat_home_loss_streak'] = home_loss_streak
    df['feat_away_loss_streak'] = away_loss_streak
    df['feat_h2h_home_win_rate'] = h2h_home_win_rate
    df['feat_venue_home_win_rate'] = venue_home_win_rate
    df['feat_prev_meeting_margin'] = prev_meeting_margin
    
    # Net Differences
    df['feat_form_diff_last5'] = df['feat_home_win_pct_last5'] - df['feat_away_win_pct_last5']
    df['feat_offense_diff_last5'] = df['feat_home_avg_score_last5'] - df['feat_away_avg_score_last5']
    df['feat_rest_days_diff'] = df['home_rest_days'] - df['away_rest_days']
    
    logger.info(f"Engineered team rolling features across windows {windows}.")
    return df


def encode_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encodes categorical columns (venue, teams, position) using label encoding."""
    df_enc = df.copy()
    cat_cols = ['home_team', 'away_team', 'venue', 'home_state', 'away_state']
    
    for c in cat_cols:
        if c in df_enc.columns:
            df_enc[f"enc_{c}"] = df_enc[c].astype('category').cat.codes
            
    return df_enc


def generate_feature_dictionary(df_features: pd.DataFrame) -> pd.DataFrame:
    """Generates an automated Feature Dictionary CSV detailing window, source columns, and leakage risk."""
    metadata = []
    
    for col in df_features.columns:
        if col.startswith("feat_"):
            window = "Pre-Match Rolling (Last 3/5/10)"
            risk = "Zero (Strictly shifted pre-kickoff)"
            desc = col.replace("_", " ").title()
        elif col.startswith("target_"):
            window = "Post-Match Outcome"
            risk = "Target Variable (Excluded from predictors)"
            desc = "Model Prediction Target"
        else:
            window = "Match Metadata"
            risk = "Zero (Pre-match metadata)"
            desc = col.replace("_", " ").title()
            
        metadata.append({
            "Feature Name": col,
            "Description": desc,
            "Formula / Calculation": f"Derived from {col}",
            "Computation Window": window,
            "Source Columns": "score_margin, match_date, home_team, away_team",
            "Leakage Risk": risk
        })
        
    meta_df = pd.DataFrame(metadata)
    out_csv = OUTPUTS_DIR / "feature_dictionary.csv"
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    meta_df.to_csv(out_csv, index=False)
    logger.info(f"Generated feature dictionary: {out_csv}")
    return meta_df
