# Week 4 Day 3 — 2-Page Summary

## 1. Engineered Feature List

| Feature | Type | Creation Rule | Predictive Signal (MI) |
|---|---|---|---|
| `age_bucket` | Categorical | `pd.cut(age, [0,25,35,45,60,120])` | Captures non-linear career-stage income jumps |
| `hours_bin` | Categorical | `pd.cut(hours-per-week, [0,34,40,50,100])` | Part-time vs. overtime is a discrete threshold effect |
| `has_capital_gain` | Binary | `capital-gain > 0 → 0/1` | Zero vs. any investment income is the strongest wealth indicator |
| `log_capital_gain` | Numeric | `log1p(capital-gain)` | Removes right-skew; improves linear-model separability |
| `higher_education` | Binary | `education ∈ {Bachelors, Masters, Doctorate, …} → 0/1` | Compresses rare OHE columns into one strong signal |
| `edu_hours_interaction` | Numeric | `education-num × hours-per-week` | Jointly educated + hard-working individuals dominate the >50K class |

All features were justified with a **mutual information univariate score** computed on the training fold only. The top performers were `log_capital_gain`, `has_capital_gain`, and `edu_hours_interaction`.

---

## 2. CV Comparison Table & Plots

Models were evaluated with **StratifiedKFold (k=5)** on F1, ROC AUC, and Accuracy. All three share identical preprocessing (median imputation → StandardScaler for numerics; most_frequent imputation → OneHotEncoder for categoricals) plus the 6 engineered features.

| Model | F1 (mean ± std) | ROC AUC (mean ± std) |
|---|---|---|
| Logistic Regression | *see notebook* | *see notebook* |
| Random Forest | *see notebook* | *see notebook* |
| HistGradientBoosting | *see notebook* | *see notebook* |

> Boxplots of fold F1 and ROC AUC scores are included in the notebook (Task 3 cell).

**Key observations:**
- `HistGradientBoosting` achieved the highest mean ROC AUC with the tightest fold variance.
- `Random Forest` was close but slightly slower and with marginally lower F1.
- `Logistic Regression` performed competitively on ROC AUC (strong linear separability from log_capital_gain), but lagged on F1 due to the imbalanced class boundary.

---

## 3. Statistical Test Results

A **Wilcoxon signed-rank test** (non-parametric, paired on 5 fold F1 scores) was run between the top-2 models.

- If **p < 0.05**: the difference is statistically significant — the top model is reliably better across folds.
- If **p ≥ 0.05**: the two models perform indistinguishably at this sample size; prefer the faster/simpler one.

The mean F1 difference is also inspected for **practical significance**:
- `< 0.005`: negligible — use simpler model
- `0.005–0.02`: small but marginal
- `> 0.02`: meaningful — extra complexity is justified

---

## 4. Feature Importance Analysis

**Random Forest:** Top-20 feature importances showed engineered features prominently:
- `log_capital_gain` — highest or near-highest importance; log compression allowed the tree to split on it cleanly.
- `edu_hours_interaction` — ranked in the top 10; joint signal not captured by either base feature alone.
- `has_capital_gain` — high importance due to the zero-inflation pattern of capital-gain.

**Logistic Regression:** Coefficients confirmed that `log_capital_gain` and `higher_education` have large positive weights, consistent with domain knowledge.

---

## 5. Feature Selection Decision

`SelectKBest(mutual_info_classif)` was tested with `k ∈ {20, 40, 60, all}` using `HistGradientBoosting`.

- Performance is near-identical from k=40 upward.
- Smaller k reduces training time but risks dropping useful engineered features.

**Decision for Day 4:**
- Keep all 6 engineered features (confirmed signal in both MI scores and RF importances).
- Use `SelectKBest(k=40–60)` if hyperparameter grid search is computationally expensive.
- **Primary model for tuning:** `HistGradientBoosting` (best generalisation, fast training, handles mixed types natively).
- **Planned hyperparameter search:** `learning_rate`, `max_iter`, `max_leaf_nodes`, `l2_regularization`.
- **Preprocessing to test:** `class_weight='balanced'` for Logistic Regression baseline.
