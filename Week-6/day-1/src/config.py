"""
config.py — Configuration parameters, directory paths, and formula constants
Week 6 Day 1: AFL Data Foundations Project
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_FEATURES_DIR = DATA_DIR / "features"
DATA_METADATA_DIR = DATA_DIR / "metadata"

OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_FIGURES_DIR = OUTPUTS_DIR / "figures"
OUTPUTS_REPORTS_DIR = OUTPUTS_DIR / "reports"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Configurable AFL SuperCoach / Fantasy Score Weights
# Formula: Score = K*wK + HB*wHB + M*wM + G*wG + B*wB + T*wT + HO*wHO + Clr*wClr + I50*wI50 - Clg*wClg - FA*wFA
FANTASY_WEIGHTS = {
    "kicks": 3.0,
    "handballs": 2.0,
    "marks": 3.0,
    "goals": 6.0,
    "behinds": 1.0,
    "tackles": 4.0,
    "hit_outs": 1.0,
    "clearances": 3.0,
    "inside_50s": 3.0,
    "clangers": -3.0,
    "free_kicks_against": -3.0
}

# Rolling Windows for Feature Engineering
ROLLING_WINDOWS = [3, 5, 10]

# Time Split Configuration
TRAIN_START_YEAR = 1983
TRAIN_END_YEAR = 2022
VAL_YEAR = 2023
TEST_START_YEAR = 2024
TEST_END_YEAR = 2025

# Target Definitions Thresholds
TOP_DISPOSALS_THRESHOLD = 25.0
TOP_GOALS_THRESHOLD = 2.0

# Team Alias Normalization Dictionary
TEAM_NAME_MAPPINGS = {
    'Footscray': 'Western Bulldogs',
    'South Melbourne': 'Sydney Swans',
    'Brisbane Bears': 'Brisbane Lions',
    'Fitzroy': 'Brisbane Lions',
    'North Melbourne': 'North Melbourne Kangaroos',
    'Kangaroos': 'North Melbourne Kangaroos',
    'Geelong': 'Geelong Cats',
    'Carlton': 'Carlton Blues',
    'Collingwood': 'Collingwood Magpies',
    'Essendon': 'Essendon Bombers',
    'Hawthorn': 'Hawthorn Hawks',
    'Melbourne': 'Melbourne Demons',
    'Richmond': 'Richmond Tigers',
    'St Kilda': 'St Kilda Saints',
    'Sydney': 'Sydney Swans',
    'Adelaide': 'Adelaide Crows',
    'Port Adelaide': 'Port Adelaide Power',
    'Fremantle': 'Fremantle Dockers',
    'West Coast': 'West Coast Eagles',
    'Gold Coast': 'Gold Coast Suns',
    'GWS': 'GWS Giants',
    'Greater Western Sydney': 'GWS Giants'
}

# Standard AFL Venues & States Mapping
VENUE_STATE_MAP = {
    'MCG': 'VIC',
    'Marvel Stadium': 'VIC',
    'GMHBA Stadium': 'VIC',
    'SCG': 'NSW',
    'GIANTS Stadium': 'NSW',
    'Gabba': 'QLD',
    'Heritage Bank Stadium': 'QLD',
    'Adelaide Oval': 'SA',
    'Optus Stadium': 'WA',
    'Blundstone Arena': 'TAS',
    'UTAS Stadium': 'TAS',
    'Manuka Oval': 'ACT',
    'TIO Stadium': 'NT'
}
