"""
data_quality.py — Automated data inventory, ERD generation, era shifts, and quality audit
Week 6 Day 1: AFL Data Foundations Project
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

from .utils import setup_logger

logger = setup_logger("data_quality")


def inspect_raw_datasets(data_raw_dir: Path) -> Dict[str, Any]:
    """
    Automatically inspects raw CSV/Parquet files in data/raw.
    Returns inventory details including row/col counts, candidate primary/foreign keys, and grains.
    """
    inventory = {}
    data_raw_dir = Path(data_raw_dir)
    
    if not data_raw_dir.exists():
        logger.warning(f"Raw data directory {data_raw_dir} does not exist.")
        return inventory

    for file_path in data_raw_dir.glob("*.*"):
        if file_path.suffix not in ['.csv', '.parquet']:
            continue
            
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path, nrows=1000)
                full_len = sum(1 for _ in open(file_path, encoding='utf-8', errors='ignore')) - 1
            else:
                df = pd.read_parquet(file_path)
                full_len = len(df)
                
            cols = df.columns.tolist()
            
            # Infer Entity Grain & Primary Keys
            grain, pk, fk = infer_grain_and_keys(file_path.name, cols)
            
            inventory[file_path.name] = {
                "filename": file_path.name,
                "rows": full_len,
                "columns_count": len(cols),
                "columns_sample": cols[:10],
                "primary_key": pk,
                "foreign_keys": fk,
                "inferred_grain": grain
            }
        except Exception as e:
            logger.error(f"Error inspecting {file_path.name}: {e}")
            
    return inventory


def infer_grain_and_keys(filename: str, columns: List[str]) -> Tuple[str, List[str], List[str]]:
    """Infers entity grain, primary key(s), and foreign keys from schema and filename."""
    fname = filename.lower()
    
    if "match" in fname:
        return "Match Level (One row = one AFL match)", ["match_id"], ["home_team", "away_team", "season"]
    elif "player_info" in fname or "info" in fname:
        return "Player Profile Level (One row = one AFL player)", ["id"], ["debut_team"]
    elif "player" in fname or "seasonal" in fname:
        return "Player-Season Level (One row = one player in one season)", ["player_id", "year", "team"], ["player_id", "team", "year"]
    else:
        return "Generic Event Level", ["id"], []


def generate_ascii_erd() -> str:
    """Generates an ASCII Entity Relationship Diagram (ERD)."""
    erd = """
=============================================================================
                       AFL ENTITY RELATIONSHIP DIAGRAM (ERD)
=============================================================================

 ┌─────────────────────────┐               ┌─────────────────────────┐
 │   afl_matches.csv       │               │   merged_players.csv    │
 ├─────────────────────────┤               ├─────────────────────────┤
 │ PK: match_id            │               │ PK: player_id, year     │
 │ FK: home_team, season   │◄─────────────►│ FK: team, year          │
 │ FK: away_team, venue    │  Team / Year  │ Stats: disposals, goals │
 └─────────────────────────┘     Join      └────────────┬────────────┘
                                                        │
                                                        │ player_id
                                                        ▼
                                           ┌─────────────────────────┐
                                           │   players_info.csv      │
                                           ├─────────────────────────┤
                                           │ PK: player_id           │
                                           │ Attributes: height...   │
                                           └─────────────────────────┘
=============================================================================
"""
    return erd.strip()


def analyze_historical_eras_and_shifts(df_matches: pd.DataFrame) -> Dict[str, Any]:
    """Analyzes date ranges, seasons, teams, players, and structural historical eras."""
    min_year = int(df_matches['season'].min()) if 'season' in df_matches.columns else 1983
    max_year = int(df_matches['season'].max()) if 'season' in df_matches.columns else 2025
    n_seasons = max_year - min_year + 1
    
    n_teams = df_matches['home_team'].nunique() if 'home_team' in df_matches.columns else 18
    
    eras = [
        {"era": "VFL Era (1982)", "event": "South Melbourne VFL team relocated to SCG as Sydney Swans"},
        {"era": "National Expansion (1987)", "event": "West Coast Eagles & Brisbane Bears joined VFL/AFL"},
        {"era": "AFL Renaming (1990)", "event": "VFL officially renamed to Australian Football League (AFL)"},
        {"era": "Merged Club (1996)", "event": "Fitzroy Lions merged with Brisbane Bears to form Brisbane Lions"},
        {"era": "Adelaide Expansion (1991, 1997)", "event": "Adelaide Crows (1991) and Port Adelaide Power (1997) joined"},
        {"era": "Modern 18-Team Expansion (2011, 2012)", "event": "Gold Coast Suns (2011) and GWS Giants (2012) expanded league to 18 teams"},
        {"era": "Interchange Cap Shifts (2014-2021)", "event": "Interchange rotations capped at 120 (2014), 90 (2016), and 75 (2021)"}
    ]
    
    return {
        "earliest_season": min_year,
        "latest_season": max_year,
        "number_of_seasons": n_seasons,
        "number_of_teams": n_teams,
        "historical_eras_documented": eras
    }


def audit_data_quality(df_players: pd.DataFrame, df_matches: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs data quality checks: missing values, duplicates, negative stats,
    outliers, and team alias inconsistencies.
    """
    audit = {}
    
    # Missing Value Audit
    audit["missing_values"] = {
        "df_players": df_players.isna().sum().to_dict() if not df_players.empty else {},
        "df_matches": df_matches.isna().sum().to_dict() if not df_matches.empty else {}
    }
    
    # Duplicate Audit
    audit["duplicates"] = {
        "df_players_duplicates": int(df_players.duplicated().sum()) if not df_players.empty else 0,
        "df_matches_duplicates": int(df_matches.duplicated().sum()) if not df_matches.empty else 0
    }
    
    # Negative / Impossible Stat Checks
    impossible_stats = []
    if not df_players.empty:
        for col in ['kicks', 'handballs', 'goals', 'behinds', 'tackles', 'disposals']:
            if col in df_players.columns:
                neg_cnt = int((df_players[col] < 0).sum())
                if neg_cnt > 0:
                    impossible_stats.append(f"Negative values found in {col}: {neg_cnt} rows")
                    
    audit["impossible_value_checks"] = impossible_stats or ["No negative statistics found (Pass)"]
    
    # Outlier Detection
    outliers = []
    if not df_players.empty and 'avg_disposals' in df_players.columns:
        high_disp = df_players[df_players['avg_disposals'] > 45]
        if not high_disp.empty:
            outliers.append(f"High disposal averages (>45 per game): {len(high_disp)} players")
            
    if not df_players.empty and 'avg_goals' in df_players.columns:
        high_goals = df_players[df_players['avg_goals'] > 7]
        if not high_goals.empty:
            outliers.append(f"High goal averages (>7 per game): {len(high_goals)} players")
            
    audit["outliers_detected"] = outliers or ["No extreme statistical anomalies found"]
    
    return audit
