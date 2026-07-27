# AFL Production Analytics Foundation & Feature Engineering Engine

**Week 6 Day 1 Project** | **Stack:** Python 3.13 · Pandas · NumPy · PyArrow · Scikit-Learn · Seaborn · Matplotlib

---

## 📌 Project Overview

This repository establishes a production-grade **AFL (Australian Football League) Data Analytics Foundation** designed to power downstream machine learning models (Match Winner, Top Disposal Getter, Top Goal Kicker) and an autonomous **LangGraph AI Sports Assistant / RAG pipeline**.

The codebase enforces strict **software engineering standards**: modular functions decoupled into a reusable Python package (`src/`), zero-leakage pre-match rolling feature computation (`.shift(1)`), automated data quality auditing, 18 publication-quality figures, and reproducible time-based train/validation/test splits.

---

## 📂 Project Architecture & Directory Structure

```
netixsol_internship/Week-6/day-1/
├── notebooks/
│   └── afl_data_foundation.ipynb     # Main reproducible project notebook importing src modules
├── data/
│   ├── raw/                           # Raw input datasets (merged_players.csv, players_info.csv)
│   ├── processed/                     # Preprocessed & normalized dataset (afl_cleaned_dataset.csv)
│   ├── features/                      # Versioned feature tables (afl_feature_table.parquet / .csv)
│   └── metadata/                      # Schema & metadata caches
├── src/
│   ├── __init__.py
│   ├── config.py                      # Constants, paths, fantasy score weights, window sizes
│   ├── utils.py                       # Logger initialization, directory managers, I/O wrappers
│   ├── data_quality.py                # Automated data inventory, ERD generator, era shifts & audit
│   ├── preprocessing.py               # Imputation, team alias normalization, data cleaning
│   ├── feature_engineering.py         # Zero-leakage pre-match rolling feature pipeline
│   ├── train_split.py                 # Time-based split generator & leakage verification
│   └── visualizations.py              # Publication-quality plotting library (18 saved figures)
├── outputs/
│   ├── figures/                       # 18 saved publication-quality PNG charts
│   ├── reports/
│   │   ├── leakage_report.md          # Zero-leakage verification report
│   │   └── final_report.md            # Comprehensive Executive Engineering Report
│   ├── feature_dictionary.csv         # Automated feature dictionary contract
│   └── data_dictionary.md             # 1-page Data Contract for Target Definitions
├── requirements.txt                   # Production dependencies specification
└── README.md                          # Project documentation & execution guide
```

---

## 🛠️ Module Documentation (`src/`)

- **`src/config.py`**: Defines central directory paths, configurable AFL SuperCoach / Fantasy weights dictionary, rolling window sizes (`[3, 5, 10]`), target thresholds (`disposals >= 25`, `goals >= 2`), team name alias mappings, and venue-state mappings.
- **`src/utils.py`**: Provides standardized logging (`setup_logger`), directory verification (`ensure_directories`), DataFrame file loading/saving (`load_dataframe`, `save_dataframe`), and an execution timer context manager (`ExecutionTimer`).
- **`src/data_quality.py`**: Automatically inspects raw CSV/Parquet files, infers entity grains, candidate keys, generates an ASCII Entity Relationship Diagram (ERD), audits data quality (missing values, duplicates, negative values, outliers), and documents historical era shifts (South Melbourne relocation, Fitzroy merger, Gold Coast/GWS expansion).
- **`src/preprocessing.py`**: Handles team name normalization (e.g. `Footscray` -> `Western Bulldogs`), physical attribute imputation (height/weight), and dataset merging.
- **`src/feature_engineering.py`**: Computes leakage-free pre-match rolling team form (win %, score, offense, defense) and player metrics over 3, 5, 10 games using `.shift(1)`. Exports `afl_feature_table.parquet` and `outputs/feature_dictionary.csv`.
- **`src/train_split.py`**: Implements `create_time_split()` supporting Train (1983–2022), Validation (2023), and Test (2024–2025) splits. Performs zero-leakage verification and generates `outputs/reports/leakage_report.md`.
- **`src/visualizations.py`**: Generates and saves 18 publication-quality charts to `outputs/figures/` (heatmaps, violin plots, box plots, scatterplots, correlation matrices, and time series).

---

## 🚀 Execution Instructions

### 1. Environment Setup & Dependency Installation
```bash
pip install -r requirements.txt
```

### 2. Run Main Pipeline (Populates Data, Figures & Reports)
```bash
python code.py
```

### 3. Open & Run Interactive Notebook
```bash
jupyter notebook notebooks/afl_data_foundation.ipynb
```

---

## 📊 Key Data Contracts & Targets

- **Match Winner Target (`target_home_win`):** Binary classification ($1 = \text{Home Win}, 0 = \text{Loss/Draw}$).
- **Score Margin Target (`target_score_margin`):** Regression ($\text{Home Score} - \text{Away Score}$).
- **AFL Fantasy Composite Index:**
  $$\text{Fantasy Score} = 3\text{K} + 2\text{HB} + 3\text{M} + 6\text{G} + 1\text{B} + 4\text{T} + 1\text{HO} + 3\text{Clr} + 3\text{I50} - 3\text{Clg} - 3\text{FA}$$
- **Time Split Boundaries:** Train (1983–2022, 92.5%), Validation (2023, 2.6%), Test (2024–2025, 4.9%).
- **Realistic Accuracy Ceiling:** **68%–72%** (Sports outcome variance & injury noise).
