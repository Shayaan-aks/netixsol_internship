"""
gen_nb.py — Script to generate code.ipynb and notebook.ipynb for Week 6 Day 1: AFL Data Foundations
"""
import json
import os

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
    "# Week 6 Day 1 — AFL Data Foundations: EDA, Feature Engineering & Prediction Targets\n",
    "\n",
    "> **Goal:** Perform deep data inventory, define prediction target contracts, conduct exploratory data analysis,\n",
    "> engineer leakage-free rolling features, and establish a reproducible time-based train/hold-out split.\n",
    "\n",
    "**Stack:** `pandas` · `numpy` · `pyarrow` · `matplotlib` · `seaborn` · `python-dotenv`  \n",
    "**Dataset Scope:** AFL Seasons 1983–2025 (42 Seasons, 8,532 Matches, 25,481 Player-Season Records)  \n"
]))

# ── SETUP & ENV ───────────────────────────────────────────────────────────────
cells.append(md_cell(["## Setup & Environment Configuration\n"]))
cells.append(code_cell([
    "import os, sys, json, time, textwrap, warnings\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "warnings.filterwarnings('ignore')\n",
    "load_dotenv('.env.example')\n",
    "\n",
    "print(f'Python version : {sys.version.split()[0]}')\n",
    "print(f'Pandas version : {pd.__version__}')\n",
    "print(f'NumPy version  : {np.__version__}')\n"
]))

# ── TASK 1: DATA INVENTORY ────────────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 1: Data Inventory, Entity Grains & Structural Era Analysis\n",
    "\n",
    "### Entity Grains & Join Keys\n",
    "- **`afl_matches.csv` (Match Level):** Primary Key `match_id`. Foreign Keys: `home_team`, `away_team`, `season`.\n",
    "- **`merged_players.csv` (Player-Season Level):** Primary Key `(player_id, year, team)`. Foreign Keys: `player_id`, `year`.\n",
    "- **`players_info.csv` (Player Demographic Level):** Primary Key `id` / `player_id`.\n"
]))

cells.append(code_cell([
    "from code import load_raw_afl_datasets, perform_data_quality_checks\n",
    "\n",
    "# Load datasets & run quality checks\n",
    "df_players, df_info, df_matches = load_raw_afl_datasets()\n",
    "report = perform_data_quality_checks(df_players, df_info, df_matches)\n",
    "\n",
    "print('Data Inventory Report:')\n",
    "print(json.dumps(report, indent=2))\n"
]))

# ── TASK 2: TARGET DEFINITIONS ────────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 2: Define Prediction Targets & Data Contract\n",
    "\n",
    "### Target Contract\n",
    "1. **`target_home_win` (Binary Classification):** 1 if Home Score > Away Score, 0 otherwise.\n",
    "2. **`target_score_margin` (Regression):** Home Score - Away Score.\n",
    "3. **`composite_fantasy_score` (SuperCoach Formula):** $3K + 2HB + 3M + 6G + 1B + 4T + 1HO$.\n"
]))

cells.append(code_cell([
    "from code import apply_target_definitions\n",
    "\n",
    "df_matches, df_players = apply_target_definitions(df_matches, df_players)\n",
    "print('Target definitions applied to match and player datasets.')\n",
    "print('Match targets sample:')\n",
    "print(df_matches[['match_id', 'home_team', 'away_team', 'home_score', 'away_score', 'target_score_margin', 'target_home_win']].head())\n"
]))

# ── TASK 3: EDA & VISUAL RELATIONSHIPS ───────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 3: Exploratory Data Analysis & Visual Relationships\n"
]))

cells.append(code_cell([
    "from code import perform_eda_analysis\n",
    "\n",
    "eda_res = perform_eda_analysis(df_matches, df_players)\n",
    "print('EDA Summary Highlights:')\n",
    "print(f'• Historical Home Win Rate : {eda_res[\"historical_home_win_rate_percent\"]}%')\n",
    "print(f'• Average Score Margin      : +{eda_res[\"average_home_margin_points\"]} pts')\n",
    "print(f'• Top Historical Disposals  : {eda_res[\"top_historical_disposal_leaders\"][:3]}')\n",
    "print(f'• Top Historical Goals      : {eda_res[\"top_historical_goal_leaders\"][:3]}')\n"
]))

# ── TASK 4: FEATURE ENGINEERING ───────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 4: Feature Engineering for Prediction (No Data Leakage)\n"
]))

cells.append(code_cell([
    "from code import build_leakage_free_feature_table\n",
    "\n",
    "# Build and export versioned feature table\n",
    "feature_df = build_leakage_free_feature_table(df_matches)\n",
    "print('Engineered Features Sample:')\n",
    "print(feature_df[['match_id', 'home_team', 'away_team', 'feat_home_form_last5', 'feat_away_form_last5', 'feat_form_diff_last5', 'feat_rest_days_diff']].head())\n"
]))

# ── TASK 5: TRAIN / HOLD-OUT SPLIT ────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 5: Reproducible Train / Hold-Out Time Split\n"
]))

cells.append(code_cell([
    "from code import get_time_split\n",
    "\n",
    "train_df, holdout_df = get_time_split(feature_df, cut_year=2024)\n",
    "print(f'Train Set (1983-2023)    : {len(train_df)} matches')\n",
    "print(f'Hold-Out Set (2024-2025) : {len(holdout_df)} matches')\n"
]))

# Build Notebook Dictionary
notebook_dict = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python"},
        "orig_nbformat": 4
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Write code.ipynb and notebook.ipynb
with open("code.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

with open("notebook.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print("Generated code.ipynb and notebook.ipynb successfully.")
