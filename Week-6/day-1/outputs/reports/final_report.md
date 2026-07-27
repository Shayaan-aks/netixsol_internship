# Executive Engineering Report: AFL Production Data Foundations & Feature Engineering

**Author:** Senior Machine Learning & Sports Analytics Engineer  
**Date:** Week 6, Day 1  
**Project:** AFL Production Analytics Foundation  
**Target Systems:** Match Winner Model, Top Player Predictor, Domain-Locked LangGraph AI Assistant & RAG Pipelines  

---

## 1. Executive Summary & Architecture Overview

This project establishes the production data foundations and feature engineering pipeline for the **Australian Football League (AFL)** dataset spanning 42 seasons (1983–2025). The architecture is designed for enterprise modularity, zero data leakage, and high reproducibility—decoupling processing logic into a dedicated Python package (`src/`) that feeds downstream machine learning models, fantasy index estimators, and LLM-powered RAG agents.

```
project/
├── notebooks/
│   └── afl_data_foundation.ipynb
├── data/
│   ├── raw/           (merged_players.csv, players_info.csv)
│   ├── processed/     (afl_cleaned_dataset.csv)
│   └── features/      (afl_feature_table.parquet / .csv)
├── src/               (config, utils, data_quality, preprocessing, feature_engineering, train_split, visualizations)
└── outputs/           (figures/, reports/, feature_dictionary.csv, data_dictionary.md)
```

---

## 2. Task 1: Data Inventory, ERD & Historical Era Analysis

### Data Inventory Summary

- **Match Level (`afl_matches.csv`):** 8,532 matches across 42 seasons (1983–2025). Primary key `match_id`. Foreign keys `home_team`, `away_team`, `season`.
- **Player Season Level (`merged_players.csv`):** 25,481 records. Primary key `(player_id, year, team)`.
- **Player Profile Level (`players_info.csv`):** 2,843 profiles. Primary key `id`.

### Entity Relationship Diagram (ERD)

```
 ┌─────────────────────────┐               ┌─────────────────────────┐
 │    afl_matches.csv      │               │   merged_players.csv    │
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
```

### Historical Structural Eras & Relocations Documented

1. **South Melbourne VFL Relocation (1982):** Relocated to Sydney SCG as **Sydney Swans**.
2. **Fitzroy & Brisbane Bears Merger (1996):** Formed the **Brisbane Lions**.
3. **Modern 18-Team Expansion (2011–2012):** Introduction of **Gold Coast Suns** (2011) and **GWS Giants** (2012).
4. **Interchange Cap Shift (2014–2021):** Interchange rotations capped at 120 (2014), 90 (2016), and 75 (2021), elevating disposal volume for elite midfielders.

---

## 3. Task 2: Prediction Targets Contract

### Data Contract Table

| Target Name | Definition | Formula / Logic | Target Type | Level |
|---|---|---|---|---|
| **`target_home_win`** | Binary indicator if home team won. | $\mathbb{I}(\text{home\_score} > \text{away\_score})$ | Classification ($0/1$) | Match Level |
| **`target_score_margin`** | Final score point differential. | $\text{home\_score} - \text{away\_score}$ | Regression ($\mathbb{R}$) | Match Level |
| **`target_top_disposals`** | Player average disposals $\ge 25.0$. | $\mathbb{I}(\text{avg\_disposals} \ge 25.0)$ | Classification ($0/1$) | Player-Season |
| **`target_top_goals`** | Player average goals $\ge 2.0$. | $\mathbb{I}(\text{avg\_goals} \ge 2.0)$ | Classification ($0/1$) | Player-Season |
| **`composite_fantasy_score`**| AFL Fantasy composite score. | $3\text{K} + 2\text{HB} + 3\text{M} + 6\text{G} + 1\text{B} + 4\text{T} + 1\text{HO}$ | Continuous Index ($\mathbb{R}^+$) | Player-Season |

> **Classification vs. Margin Regression Justification:** Classification directly outputs win probability $P(\text{Home Win})$ for betting and Q&A tipping. Margin regression provides stronger loss function gradients during model training. On Day 2, we will use margin regression converted to probabilities via sigmoid mapping.

---

## 4. Task 3: Exploratory Data Analysis (EDA) Insights

- **Home-Ground Advantage:** Home teams win **75.5%** of venue-aligned matches (**58.4%** league baseline), scoring **+9.73 points** higher on average.
- **Interstate Travel Penalty:** Non-Victorian teams playing in Melbourne face a **-7.2 point margin penalty** due to flight travel fatigue.
- **Player Positions:** Midfielders lead disposals (22.4 avg), Forwards lead goals (2.8 avg) and marks inside 50, Defenders lead rebound 50s.
- **Historical Leaders:** Scott Pendlebury (Disposals), Lance Franklin (Goals), Patrick Dangerfield (AFL Fantasy).

---

## 5. Task 4: Zero Data Leakage Feature Pipeline

All rolling features are calculated using pre-match historical windows strictly prior to match kickoff date (`.shift(1)` logic):

- **Team Rolling Form (`feat_home_form_last3`, `feat_home_form_last5`):** 3-game and 5-game rolling win percentages.
- **Form Difference (`feat_form_diff_last5`):** Net momentum advantage ($\text{Home Form} - \text{Away Form}$).
- **Head-to-Head Win Rate (`feat_h2h_home_win_rate`):** Historical win % against opponent.
- **Rest Days Differential (`feat_rest_days_diff`):** Days of rest advantage ($\text{Home Rest} - \text{Away Rest}$).
- **Categorical Encoding:** Label encoding applied to teams, venues, and states.

**Saved Dataset:** `data/features/afl_feature_table.parquet` (8,532 rows x 33 columns).

---

## 6. Task 5: Time Split & Accuracy Ceiling Rationale

### Reusable Time Split Logic
- **Train Set (1983–2022):** 7,896 matches (~92.5%).
- **Validation Set (2023):** 222 matches (~2.6%).
- **Test Set (2024–2025):** 414 matches (~4.9%).

### Leakage & Accuracy Ceiling
> In sports forecasting, random K-Fold cross-validation leaks future tactical and roster information into past training folds. Strict time-based splitting is mandatory.
> 
> The realistic accuracy ceiling for AFL match prediction is **68% to 72%**. AFL outcomes contain inherent stochastic noise (weather shifts, in-game injuries, umpire decisions). Any model reporting **> 85% or 100% accuracy** indicates severe **future data leakage** (e.g. including match-day disposals or final goals in the pre-match feature matrix).
