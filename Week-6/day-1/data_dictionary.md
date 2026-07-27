# AFL Data Foundations — Data Dictionary & Target Contract

**Version:** 1.0 (Week 6 Day 1 Contract)  
**Storage Path:** `netixsol_internship/Week-6/day-1/data/afl_feature_table.parquet`  
**Primary Granularity:** Match-Level (`match_id`) & Player-Season Level (`player_id`, `season`)  

---

## 1. Prediction Targets Contract (Day 2 Modeling Specification)

| Target Name | Definition | Mathematical Formula / Logic | Target Type | Aggregation Level |
|---|---|---|---|---|
| **`target_home_win`** | Binary indicator if the home team won the match. | $\mathbb{I}(\text{home\_score} > \text{away\_score})$ | Binary Classification ($0$ or $1$) | Match Level (`match_id`) |
| **`target_score_margin`** | Final point score differential between home and away team. | $\text{home\_score} - \text{away\_score}$ | Continuous Regression ($\mathbb{R}$) | Match Level (`match_id`) |
| **`target_total_points`** | Total combined score recorded in the match. | $\text{home\_score} + \text{away\_score}$ | Continuous Regression ($\mathbb{R}^+$) | Match Level (`match_id`) |
| **`target_top_disposals`** | Indicator if player averaged 25+ disposals per game. | $\mathbb{I}(\text{avg\_disposals} \ge 25.0)$ | Binary Classification ($0$ or $1$) | Player-Season Level |
| **`target_top_goals`** | Indicator if player averaged 2.0+ goals per game. | $\mathbb{I}(\text{avg\_goals} \ge 2.0)$ | Binary Classification ($0$ or $1$) | Player-Season Level |
| **`composite_fantasy_score`** | AFL SuperCoach / Fantasy Points composite index. | $3(\text{K}) + 2(\text{HB}) + 3(\text{M}) + 6(\text{G}) + 1(\text{B}) + 4(\text{T}) + 1(\text{HO})$ | Continuous Score ($\mathbb{R}^+$) | Player-Season Level |

---

## 2. Engineered Predictor Features (Leakage-Free Pre-Match Window)

All engineered features are computed strictly using historical data available **prior to the match kickoff date** (`.shift(1)` logic).

| Feature Name | Description | Computation Window | Source Columns | Feature Type |
|---|---|---|---|---|
| **`feat_home_form_last3`** | Home team win percentage over its last 3 completed matches. | Last 3 matches pre-kickoff | `score_margin`, `home_team`, `away_team` | Float ($0.0 \dots 1.0$) |
| **`feat_away_form_last3`** | Away team win percentage over its last 3 completed matches. | Last 3 matches pre-kickoff | `score_margin`, `home_team`, `away_team` | Float ($0.0 \dots 1.0$) |
| **`feat_home_form_last5`** | Home team win percentage over its last 5 completed matches. | Last 5 matches pre-kickoff | `score_margin`, `home_team`, `away_team` | Float ($0.0 \dots 1.0$) |
| **`feat_away_form_last5`** | Away team win percentage over its last 5 completed matches. | Last 5 matches pre-kickoff | `score_margin`, `home_team`, `away_team` | Float ($0.0 \dots 1.0$) |
| **`feat_form_diff_last5`** | Net momentum difference between home and away team. | $\text{feat\_home\_form\_last5} - \text{feat\_away\_form\_last5}$ | Pre-match rolling form | Float ($-1.0 \dots +1.0$) |
| **`feat_home_win_streak`** | Consecutive win count for home team coming into the match. | Pre-match streak | `score_margin` | Integer ($\ge 0$) |
| **`feat_away_win_streak`** | Consecutive win count for away team coming into the match. | Pre-match streak | `score_margin` | Integer ($\ge 0$) |
| **`feat_h2h_home_win_rate`**| Historical win percentage for home team against this specific opponent. | All historical matchups | `home_team`, `away_team`, `score_margin` | Float ($0.0 \dots 1.0$) |
| **`feat_rest_days_diff`** | Days of rest advantage for home team relative to away team. | $\text{home\_rest\_days} - \text{away\_rest\_days}$ | `home_rest_days`, `away_rest_days` | Integer ($-3 \dots +3$) |
| **`is_interstate`** | Flag indicating if away team traveled interstate to venue. | Match location metadata | `home_state`, `away_state` | Binary ($0$ or $1$) |

---

## 3. Data Entities, Primary Keys & Joins

```
   ┌───────────────────────┐           ┌───────────────────────┐
   │    afl_matches.csv    │           │  merged_players.csv   │
   ├───────────────────────┤           ├───────────────────────┤
   │ PK: match_id          │           │ PK: player_id, year   │
   │ FK: home_team, season │◄─────────►│ FK: team, year        │
   └───────────────────────┘           └───────────┬───────────┘
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │   players_info.csv    │
                                       ├───────────────────────┤
                                       │ PK: player_id         │
                                       │ Attributes: height... │
                                       └───────────────────────┘
```

---

## 4. Train / Hold-Out Split Specification

- **Split Strategy:** Strict Time-Based Cutoff.
- **Train Set:** Seasons `1983` to `2023` inclusive (8,118 matches, ~95.1%).
- **Hold-Out Evaluation Set:** Seasons `2024` to `2025` inclusive (414 matches, ~4.9%).
- **Split Function:** `get_time_split(df, cut_year=2024)` in `code.py`.
- **Leakage Prevention:** Random K-fold splitting is strictly prohibited as it would expose future seasonal form and player roster context into past training folds.
