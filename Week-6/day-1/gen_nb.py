"""
gen_nb.py — Generates notebooks/afl_data_foundation.ipynb, code.ipynb, and notebook.ipynb
Week 6 Day 1: AFL Data Foundations Project
"""

import json
import os
from pathlib import Path

def code_cell(src_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src_lines
    }

def md_cell(src_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": src_lines
    }

cells = []

# ── HEADER ────────────────────────────────────────────────────────────────────
cells.append(md_cell([
    "# AFL Data Foundations — EDA, Feature Engineering & Prediction Targets\n",
    "\n",
    "> **Role:** Senior Machine Learning & Sports Analytics Engineer  \n",
    "> **Objective:** Build a production-grade, modular AFL data analytics foundation supporting Match Winner Prediction, Top Player Performance Forecasting, and an autonomous LangGraph AI Assistant / RAG Pipeline.\n",
    "\n",
    "**Stack:** Python 3.13 · Pandas · NumPy · PyArrow · Scikit-Learn · Seaborn · Matplotlib  \n",
    "**Architecture:** Modular `src/` Package (`config`, `utils`, `data_quality`, `preprocessing`, `feature_engineering`, `train_split`, `visualizations`)  \n"
]))

# ── SETUP & ENV ───────────────────────────────────────────────────────────────
cells.append(md_cell(["## Setup & Environment Configuration\n"]))
cells.append(code_cell([
    "import os, sys, json, warnings\n",
    "from pathlib import Path\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "\n",
    "# Ensure project root and src/ module path is accessible\n",
    "PROJECT_ROOT = Path('.').resolve().parent if Path('.').resolve().name == 'notebooks' else Path('.').resolve()\n",
    "if str(PROJECT_ROOT) not in sys.path:\n",
    "    sys.path.insert(0, str(PROJECT_ROOT))\n",
    "\n",
    "from src.config import DATA_RAW_DIR, DATA_FEATURES_DIR, OUTPUTS_DIR, FANTASY_WEIGHTS\n",
    "from src.utils import setup_logger, ensure_directories, ExecutionTimer\n",
    "\n",
    "ensure_directories()\n",
    "logger = setup_logger()\n",
    "print('Project directories & environment initialized successfully.')\n"
]))

# ── TASK 1: DATA INVENTORY ────────────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 1: Data Inventory, Entity Grains, Relocations & Quality Audit\n",
    "\n",
    "### Automatically Inspect Raw Datasets & Infer Entity Grains\n"
]))

cells.append(code_cell([
    "from src.data_quality import inspect_raw_datasets, generate_ascii_erd, analyze_historical_eras_and_shifts, audit_data_quality\n",
    "from src.preprocessing import preprocess_player_data, preprocess_match_data\n",
    "from code import load_raw_afl_datasets\n",
    "\n",
    "df_players_raw, df_info_raw, df_matches_raw = load_raw_afl_datasets()\n",
    "\n",
    "# Inspect Raw Inventory & ERD\n",
    "inventory = inspect_raw_datasets(DATA_RAW_DIR)\n",
    "print(generate_ascii_erd())\n",
    "\n",
    "print('Quality Audit & Data Inventory Summary:')\n",
    "audit_res = audit_data_quality(df_players_raw, df_matches_raw)\n",
    "print(f'• Duplicate rows in players: {audit_res[\"duplicates\"][\"df_players_duplicates\"]}')\n",
    "print(f'• Duplicate rows in matches: {audit_res[\"duplicates\"][\"df_matches_duplicates\"]}')\n",
    "print(f'• Impossible Stat Checks   : {audit_res[\"impossible_value_checks\"]}')\n"
]))

# ── TASK 2: DEFINE PREDICTION TARGETS ─────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 2: Define Prediction Targets & Data Contract\n",
    "\n",
    "### Target Contract Summary\n",
    "1. **`target_home_win` (Binary Classification):** 1 if Home Score > Away Score, 0 otherwise.\n",
    "2. **`target_score_margin` (Regression):** Home Score - Away Score.\n",
    "3. **`composite_fantasy_score` (SuperCoach Formula):** Configurable weighted sum of statistical performance.\n"
]))

cells.append(code_cell([
    "from src.feature_engineering import compute_composite_fantasy_score\n",
    "from code import apply_target_definitions\n",
    "\n",
    "df_matches, df_players = apply_target_definitions(df_matches_raw, df_players_raw)\n",
    "print('Match Targets Contract Sample:')\n",
    "print(df_matches[['match_id', 'home_team', 'away_team', 'home_score', 'away_score', 'target_score_margin', 'target_home_win']].head())\n"
]))

# ── TASK 3: EDA & VISUALIZATIONS ──────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 3: Exploratory Data Analysis & Publication Visualizations\n"
]))

cells.append(code_cell([
    "from src.visualizations import generate_all_publication_figures\n",
    "from src.feature_engineering import build_team_rolling_features\n",
    "\n",
    "feature_df = build_team_rolling_features(df_matches)\n",
    "saved_figures = generate_all_publication_figures(df_matches, df_players, feature_df)\n",
    "print(f'Successfully generated and saved {len(saved_figures)} publication figures to outputs/figures/.')\n"
]))

# ── TASK 4: FEATURE ENGINEERING ───────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 4: Zero-Leakage Feature Engineering & Feature Dictionary\n"
]))

cells.append(code_cell([
    "from src.feature_engineering import encode_categorical_features, generate_feature_dictionary\n",
    "from src.utils import save_dataframe\n",
    "from src.config import DATA_FEATURES_DIR\n",
    "\n",
    "encoded_df = encode_categorical_features(feature_df)\n",
    "feature_meta = generate_feature_dictionary(encoded_df)\n",
    "\n",
    "parquet_file = DATA_FEATURES_DIR / 'afl_feature_table.parquet'\n",
    "save_dataframe(encoded_df, parquet_file, index=False)\n",
    "print(f'Feature table exported to {parquet_file} ({len(encoded_df)} rows x {len(encoded_df.columns)} columns).')\n"
]))

# ── TASK 5: TRAIN / HOLD-OUT SPLIT ────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 5: Time-Based Train / Val / Test Split & Leakage Verification\n"
]))

cells.append(code_cell([
    "from src.train_split import create_time_split, verify_zero_leakage\n",
    "\n",
    "train_df, val_df, test_df = create_time_split(encoded_df, train_end_year=2022, val_year=2023, test_start_year=2024)\n",
    "leakage_report = verify_zero_leakage(train_df, val_df, test_df)\n",
    "\n",
    "print('Time Split Summary:')\n",
    "print(f'• Train Set (1983-2022) : {len(train_df)} matches ({len(train_df)/len(encoded_df)*100:.1f}%)')\n",
    "print(f'• Val Set   (2023)      : {len(val_df)} matches ({len(val_df)/len(encoded_df)*100:.1f}%)')\n",
    "print(f'• Test Set  (2024-2025) : {len(test_df)} matches ({len(test_df)/len(encoded_df)*100:.1f}%)')\n",
    "print(f'• Leakage Status        : {leakage_report[\"leakage_verification_status\"]}')\n"
]))

# Build Notebook Structure
notebook_dict = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python"},
        "orig_nbformat": 4
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Write notebooks/afl_data_foundation.ipynb, code.ipynb, and notebook.ipynb
nb_dir = Path("notebooks")
os.makedirs(nb_dir, exist_ok=True)

with open(nb_dir / "afl_data_foundation.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

with open("code.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

with open("notebook.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print("Generated notebooks/afl_data_foundation.ipynb, code.ipynb, and notebook.ipynb successfully.")
