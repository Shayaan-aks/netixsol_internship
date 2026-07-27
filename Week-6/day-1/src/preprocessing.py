"""
preprocessing.py — Data cleaning, team alias normalization, missing value imputation, and dataset joining
Week 6 Day 1: AFL Data Foundations Project
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

from .config import TEAM_NAME_MAPPINGS
from .utils import setup_logger

logger = setup_logger("preprocessing")


def normalize_team_names(df: pd.DataFrame, team_cols: list[str]) -> pd.DataFrame:
    """Normalizes team aliases across specified columns."""
    df_clean = df.copy()
    for col in team_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).map(lambda x: TEAM_NAME_MAPPINGS.get(x.strip(), x.strip()))
    return df_clean


def preprocess_player_data(df_players: pd.DataFrame, df_info: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans player stats and profile data: imputes missing physical specs,
    calculates total disposals, and standardizes team names.
    """
    if df_players.empty:
        return df_players
        
    df = df_players.copy()
    
    # Normalize team names
    df = normalize_team_names(df, ['team'])
    
    # Impute missing physical attributes (height / weight) with position/league median
    if 'height' in df.columns:
        med_h = df['height'].median()
        df['height'] = df['height'].fillna(med_h)
        
    if 'weight' in df.columns:
        med_w = df['weight'].median()
        df['weight'] = df['weight'].fillna(med_w)
        
    # Ensure disposals total is calculated correctly
    if 'disposals' not in df.columns and 'kicks' in df.columns and 'handballs' in df.columns:
        df['disposals'] = df['kicks'] + df['handballs']
        
    # Ensure non-negative bounds
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for c in numeric_cols:
        df[c] = df[c].clip(lower=0)
        
    logger.info(f"Cleaned player data: {len(df)} rows.")
    return df


def preprocess_match_data(df_matches: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans match outcomes: normalizes team names, converts match dates,
    and checks score calculation consistency.
    """
    if df_matches.empty:
        return df_matches
        
    df = df_matches.copy()
    
    # Normalize home and away team names
    df = normalize_team_names(df, ['home_team', 'away_team'])
    
    # Date conversion
    if 'match_date' in df.columns:
        df['match_date'] = pd.to_datetime(df['match_date'])
        
    # Ensure margin consistency
    df['score_margin'] = df['home_score'] - df['away_score']
    df['target_home_win'] = (df['score_margin'] > 0).astype(int)
    
    logger.info(f"Cleaned match data: {len(df)} rows.")
    return df
