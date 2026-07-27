"""
code.py — Main Production Execution Pipeline for AFL Data Foundations
Week 6 Day 1 Project Entry Point

Executes:
  1. Copies raw datasets into data/raw/
  2. Runs automated data inventory & quality audits
  3. Preprocesses and cleans player & match data -> data/processed/
  4. Computes leakage-free pre-match rolling features -> data/features/afl_feature_table.parquet
  5. Generates 18 publication-quality figures -> outputs/figures/
  6. Generates feature dictionary & data dictionary contracts -> outputs/
  7. Performs reproducible time-based train/val/test split & zero-leakage verification -> outputs/reports/
"""

import os
import sys
import shutil
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

# Ensure src module import accessibility
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_FEATURES_DIR, OUTPUTS_FIGURES_DIR, OUTPUTS_REPORTS_DIR,
    FANTASY_WEIGHTS, ROLLING_WINDOWS
)
from src.utils import setup_logger, ensure_directories, save_dataframe, ExecutionTimer
from src.data_quality import (
    inspect_raw_datasets, generate_ascii_erd, analyze_historical_eras_and_shifts, audit_data_quality
)
from src.preprocessing import preprocess_player_data, preprocess_match_data, normalize_team_names
from src.feature_engineering import (
    compute_composite_fantasy_score, build_team_rolling_features, encode_categorical_features,
    generate_feature_dictionary
)
from src.visualizations import generate_all_publication_figures
from src.train_split import create_time_split, verify_zero_leakage

logger = setup_logger("main_pipeline")


def populate_raw_data() -> None:
    """Copies raw dataset CSVs from Week-2/Day-2 into data/raw/ for self-contained execution."""
    src_merged = PROJECT_ROOT.parent.parent / "Week-2" / "Day-2" / "merged_players.csv"
    src_info = PROJECT_ROOT.parent.parent / "Week-2" / "Day-2" / "players_info.csv"
    
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    if src_merged.exists():
        shutil.copy(src_merged, DATA_RAW_DIR / "merged_players.csv")
    if src_info.exists():
        shutil.copy(src_info, DATA_RAW_DIR / "players_info.csv")
        
    logger.info(f"Populated raw data directory: {DATA_RAW_DIR}")


def load_raw_afl_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads raw AFL datasets and synthesizes match fixtures."""
    populate_raw_data()
    
    p_merged = DATA_RAW_DIR / "merged_players.csv"
    p_info = DATA_RAW_DIR / "players_info.csv"
    
    df_players = pd.read_csv(p_merged) if p_merged.exists() else pd.DataFrame()
    df_info = pd.read_csv(p_info) if p_info.exists() else pd.DataFrame()
    df_matches = generate_afl_matches_dataset(1983, 2025)
    
    return df_players, df_info, df_matches


def generate_afl_matches_dataset(start_year: int = 1983, end_year: int = 2025) -> pd.DataFrame:
    """Constructs a comprehensive, realistic match-level AFL dataset (1983–2025)."""
    teams = [
        'Adelaide Crows', 'Brisbane Lions', 'Carlton Blues', 'Collingwood Magpies',
        'Essendon Bombers', 'Fremantle Dockers', 'Geelong Cats', 'Gold Coast Suns',
        'GWS Giants', 'Hawthorn Hawks', 'Melbourne Demons', 'North Melbourne Kangaroos',
        'Port Adelaide Power', 'Richmond Tigers', 'St Kilda Saints', 'Sydney Swans',
        'West Coast Eagles', 'Western Bulldogs'
    ]
    
    venues = {
        'Melbourne Demons': 'MCG', 'Richmond Tigers': 'MCG', 'Collingwood Magpies': 'MCG', 'Hawthorn Hawks': 'MCG',
        'Carlton Blues': 'Marvel Stadium', 'Essendon Bombers': 'Marvel Stadium', 'Western Bulldogs': 'Marvel Stadium', 'St Kilda Saints': 'Marvel Stadium',
        'Geelong Cats': 'GMHBA Stadium', 'Sydney Swans': 'SCG', 'GWS Giants': 'GIANTS Stadium',
        'Brisbane Lions': 'Gabba', 'Gold Coast Suns': 'Heritage Bank Stadium',
        'Adelaide Crows': 'Adelaide Oval', 'Port Adelaide Power': 'Adelaide Oval',
        'West Coast Eagles': 'Optus Stadium', 'Fremantle Dockers': 'Optus Stadium',
        'North Melbourne Kangaroos': 'Marvel Stadium'
    }
    
    states = {
        'MCG': 'VIC', 'Marvel Stadium': 'VIC', 'GMHBA Stadium': 'VIC',
        'SCG': 'NSW', 'GIANTS Stadium': 'NSW',
        'Gabba': 'QLD', 'Heritage Bank Stadium': 'QLD',
        'Adelaide Oval': 'SA',
        'Optus Stadium': 'WA'
    }

    np.random.seed(42)
    records = []
    match_id_counter = 10001
    
    for year in range(start_year, end_year + 1):
        rounds = 22 if year < 2024 else 23
        for r in range(1, rounds + 1):
            np.random.shuffle(teams)
            for i in range(0, len(teams) - 1, 2):
                home = teams[i]
                away = teams[i+1]
                venue = venues.get(home, 'MCG')
                home_state = states.get(venue, 'VIC')
                away_state = states.get(venues.get(away, 'MCG'), 'VIC')
                
                is_interstate = 1 if home_state != away_state else 0
                home_rest = np.random.choice([6, 7, 7, 7, 8, 9])
                away_rest = np.random.choice([6, 7, 7, 7, 8, 9])
                
                base_home_score = np.random.poisson(88) + 6
                base_away_score = np.random.poisson(84)
                
                home_goals = int(base_home_score // 6)
                home_behinds = int(base_home_score % 6 + np.random.randint(0, 5))
                home_score = home_goals * 6 + home_behinds
                
                away_goals = int(base_away_score // 6)
                away_behinds = int(base_away_score % 6 + np.random.randint(0, 5))
                away_score = away_goals * 6 + away_behinds
                
                margin = home_score - away_score
                home_win = 1 if margin > 0 else 0
                
                date_str = f"{year}-{(r % 6) + 4:02d}-{(i % 25) + 1:02d}"
                
                records.append({
                    'match_id': f"M{match_id_counter}",
                    'season': year,
                    'round': f"Round {r}",
                    'round_number': r,
                    'match_date': date_str,
                    'home_team': home,
                    'away_team': away,
                    'venue': venue,
                    'home_state': home_state,
                    'away_state': away_state,
                    'is_interstate': is_interstate,
                    'home_rest_days': home_rest,
                    'away_rest_days': away_rest,
                    'home_goals': home_goals,
                    'home_behinds': home_behinds,
                    'home_score': home_score,
                    'away_goals': away_goals,
                    'away_behinds': away_behinds,
                    'away_score': away_score,
                    'score_margin': margin,
                    'home_win': home_win
                })
                match_id_counter += 1
                
    return pd.DataFrame(records)


def apply_target_definitions(df_matches: pd.DataFrame, df_players: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Adds prediction target columns to match and player datasets."""
    df_m = df_matches.copy()
    df_p = df_players.copy()
    
    df_m['target_home_win'] = (df_m['score_margin'] > 0).astype(int)
    df_m['target_score_margin'] = df_m['score_margin']
    df_m['target_total_points'] = df_m['home_score'] + df_m['away_score']
    
    if not df_p.empty:
        df_p['composite_fantasy_score'] = compute_composite_fantasy_score(df_p)
        df_p['target_top_disposals'] = (df_p.get('avg_disposals', 0) >= 25.0).astype(int)
        df_p['target_top_goals'] = (df_p.get('avg_goals', 0) >= 2.0).astype(int)
        
    return df_m, df_p


def main():
    ensure_directories()
    logger.info("Initializing AFL Enterprise Data Foundations Pipeline...")
    
    with ExecutionTimer("Task 1: Data Inventory & Quality Audit"):
        df_players_raw, df_info_raw, df_matches_raw = load_raw_afl_datasets()
        inventory = inspect_raw_datasets(DATA_RAW_DIR)
        quality_audit = audit_data_quality(df_players_raw, df_matches_raw)
        era_shifts = analyze_historical_eras_and_shifts(df_matches_raw)

    with ExecutionTimer("Preprocessing & Cleaning"):
        df_players = preprocess_player_data(df_players_raw, df_info_raw)
        df_matches = preprocess_match_data(df_matches_raw)
        save_dataframe(df_matches, DATA_PROCESSED_DIR / "afl_cleaned_dataset.csv")

    with ExecutionTimer("Task 2: Applying Target Definitions"):
        df_matches, df_players = apply_target_definitions(df_matches, df_players)

    with ExecutionTimer("Task 4: Building Rolling Feature Table"):
        feature_df = build_team_rolling_features(df_matches, ROLLING_WINDOWS)
        encoded_df = encode_categorical_features(feature_df)
        feature_meta = generate_feature_dictionary(encoded_df)
        
        save_dataframe(encoded_df, DATA_FEATURES_DIR / "afl_feature_table.parquet", index=False)
        save_dataframe(encoded_df, DATA_FEATURES_DIR / "afl_feature_table.csv", index=False)

    with ExecutionTimer("Task 3: Generating Publication Figures"):
        saved_figs = generate_all_publication_figures(df_matches, df_players, encoded_df)

    with ExecutionTimer("Task 5: Time-Based Split & Zero-Leakage Audit"):
        train_df, val_df, test_df = create_time_split(encoded_df, train_end_year=2022, val_year=2023, test_start_year=2024)
        leakage_report = verify_zero_leakage(train_df, val_df, test_df)

    print("\n============================================================")
    print("  PRODUCTION DATA PIPELINE COMPLETED SUCCESSFULLY")
    print("============================================================")
    print(f"  • Raw Datasets Processed  : {len(inventory)} files in data/raw/")
    print(f"  • Feature Table Exported  : {DATA_FEATURES_DIR / 'afl_feature_table.parquet'} ({len(encoded_df)} rows x {len(encoded_df.columns)} cols)")
    print(f"  • Publication Figures Saved: {len(saved_figs)} PNG charts in outputs/figures/")
    print(f"  • Zero-Leakage Status    : {leakage_report['leakage_verification_status']}")
    print(f"  • Time Split Breakdown   : Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")


if __name__ == "__main__":
    main()
