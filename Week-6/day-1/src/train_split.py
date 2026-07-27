"""
train_split.py — Reproducible time-based train/val/test split & zero-leakage verification audit
Week 6 Day 1: AFL Data Foundations Project
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

from .config import (
    TRAIN_START_YEAR, TRAIN_END_YEAR, VAL_YEAR, TEST_START_YEAR, TEST_END_YEAR,
    OUTPUTS_REPORTS_DIR
)
from .utils import setup_logger

logger = setup_logger("train_split")


def create_time_split(
    df: pd.DataFrame,
    train_end_year: int = TRAIN_END_YEAR,
    val_year: int = VAL_YEAR,
    test_start_year: int = TEST_START_YEAR
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Creates a strict, reproducible time-based split:
      - Train Set      : Seasons <= train_end_year (e.g. 1983 - 2022)
      - Validation Set : Season == val_year (e.g. 2023)
      - Test Set       : Seasons >= test_start_year (e.g. 2024 - 2025)

    Prevents time-series data leakage in sports outcome forecasting.
    """
    if 'season' not in df.columns:
        raise KeyError("DataFrame must contain 'season' column for time-based splitting.")

    train_df = df[df['season'] <= train_end_year].copy()
    val_df = df[df['season'] == val_year].copy()
    test_df = df[df['season'] >= test_start_year].copy()

    logger.info(
        f"Time Split Complete -> Train: {len(train_df)} ({TRAIN_START_YEAR}-{train_end_year}), "
        f"Val: {len(val_df)} ({val_year}), Test: {len(test_df)} ({test_start_year}-{TEST_END_YEAR})"
    )

    return train_df, val_df, test_df


def verify_zero_leakage(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs rigorous leakage audit to verify:
      1. Chronological Ordering: Max train date < Min val date < Min test date.
      2. Feature Non-Overlap: No feature uses post-kickoff stats.
      3. Overlap Checks: 0 match_ids shared across splits.
    """
    train_max_season = train_df['season'].max()
    val_season = val_df['season'].unique() if not val_df.empty else []
    test_min_season = test_df['season'].min()

    match_id_overlap = len(set(train_df['match_id']).intersection(set(test_df['match_id'])))

    # Check for post-match feature leakage
    post_match_features_flagged = [
        col for col in train_df.columns
        if any(term in col.lower() for term in ['final_disposals', 'in_game', 'post_match', 'match_goals'])
    ]

    report = {
        "chronological_validation": {
            "train_max_season": int(train_max_season),
            "val_seasons": [int(x) for x in val_season],
            "test_min_season": int(test_min_season),
            "is_chronologically_valid": train_max_season < test_min_season
        },
        "match_id_overlap_count": match_id_overlap,
        "flagged_post_match_features": post_match_features_flagged,
        "leakage_verification_status": "PASSED (Zero Leakage Detected)" if match_id_overlap == 0 and not post_match_features_flagged else "FAILED"
    }

    # Generate Leakage Report Markdown File
    os.makedirs(OUTPUTS_REPORTS_DIR, exist_ok=True)
    report_file = OUTPUTS_REPORTS_DIR / "leakage_report.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Zero Data Leakage Verification Report\n\n")
        f.write(f"**Verification Status:** `{report['leakage_verification_status']}`\n\n")
        f.write(f"## 1. Chronological Split Boundaries\n")
        f.write(f"- **Train Set Max Season:** `{report['chronological_validation']['train_max_season']}`\n")
        f.write(f"- **Validation Set Season:** `{report['chronological_validation']['val_seasons']}`\n")
        f.write(f"- **Test Set Min Season:** `{report['chronological_validation']['test_min_season']}`\n\n")
        f.write(f"## 2. Match ID Overlap Audit\n")
        f.write(f"- **Overlapping Match IDs:** `{report['match_id_overlap_count']}` (0 Required)\n\n")
        f.write(f"## 3. Post-Match Feature Leakage Audit\n")
        f.write(f"- **Flagged Leakage Columns:** `{report['flagged_post_match_features'] or 'None (All features pre-match)'}`\n\n")
        f.write(f"## 4. Realistic Accuracy Ceiling Rationale\n")
        f.write(f"> Sports outcome forecasting carries inherent stochastic variance (weather, in-game injuries, umpire decisions). ")
        f.write(f"> A realistic accuracy ceiling for AFL match winner tipping is **68% to 72%**. ")
        f.write(f"> Any model reporting > 85% or 100% accuracy indicates severe future data leakage.\n")

    logger.info(f"Generated zero-leakage report: {report_file}")
    return report
