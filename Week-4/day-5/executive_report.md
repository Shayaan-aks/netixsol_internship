# Week 4 Day 5 — Executive Report

## Adult Income Classifier · Capstone Summary

**Author:** Shayaan  
**Date:** Week 4, Day 5  
**Dataset:** UCI Adult Income (48,842 records, 14 features)  
**Business Goal:** Predict whether an individual earns >$50K/year to enable targeted financial product personalisation.

---

## 1. Business Context & Problem Framing

The Adult Census Income dataset approximates a binary classification problem
representative of many real-world income-segment targeting tasks. Correct positive
identifications (>50K earners) allow personalised offer routing; false negatives
(missed high earners) represent lost revenue opportunities, while false positives
waste campaign spend on low-earners.

**Primary metric chosen: F1 (positive class)**  
Rationale: The dataset is class-imbalanced (~24% positive). F1 balances precision
and recall, aligning with the business trade-off between missed opportunities
(recall) and wasted spend (precision). Accuracy would be misleading (naive
majority baseline achieves ~76% accuracy at zero F1).

---

## 2. Data & Feature Engineering

**Base features (14):** age, workclass, fnlwgt, education, education-num,
marital-status, occupation, relationship, race, sex, capital-gain, capital-loss,
hours-per-week, native-country.

**6 Engineered features added (Days 3–4):**

| Feature | Type | Rationale |
|---|---|---|
| `age_bucket` | Categorical | Non-linear income thresholds by career stage |
| `hours_bin` | Categorical | Part-time vs. overtime is a discrete income signal |
| `has_capital_gain` | Binary | Zero vs. any investment income is the strongest wealth indicator |
| `log_capital_gain` | Numeric | Log-compression removes right-skew for better linear separability |
| `higher_education` | Binary | Compresses sparse OHE education columns into one strong signal |
| `edu_hours_interaction` | Numeric | Joint educated + hard-working signal dominates >50K class |

All engineering is performed inside the sklearn Pipeline (no data leakage).

---

## 3. Model Selection & Ensemble Comparison

Three models were trained with Day-4 tuned hyperparameters (RandomizedSearchCV,
n_iter=60, StratifiedKFold-5, optimised on F1):

| Model | F1 | ROC AUC | Precision | Recall | Fit Time | Inf/row |
|---|---|---|---|---|---|---|
| Random Forest (tuned) | ~0.71 | ~0.92 | ~0.72 | ~0.70 | ~45s | ~0.8ms |
| HistGradientBoosting (tuned) | ~0.73 | ~0.93 | ~0.71 | ~0.75 | ~12s | ~0.2ms |
| Stacking (RF+HGB+LR → LR meta) | ~0.73 | ~0.93 | ~0.72 | ~0.74 | ~90s | ~1.0ms |

**Winner: HistGradientBoosting** — virtually identical F1 to Stacking but 7× faster
to train and 5× faster at inference. The marginal gain from Stacking does not
justify the added complexity and maintenance overhead in production.

---

## 4. Class Imbalance Handling

Imbalance ratio: **3.14:1** (negatives:positives).

Four strategies were compared inside cross-validation:

| Strategy | CV F1 | HO F1 | HO ROC AUC | Precision | Recall |
|---|---|---|---|---|---|
| class_weight='balanced' | ~0.726 | ~0.730 | ~0.930 | ~0.710 | ~0.751 |
| RandomOverSampler | ~0.720 | ~0.722 | ~0.928 | ~0.705 | ~0.740 |
| RandomUnderSampler | ~0.700 | ~0.695 | ~0.915 | ~0.680 | ~0.712 |
| SMOTE | ~0.718 | ~0.720 | ~0.927 | ~0.703 | ~0.738 |

**Chosen: `class_weight='balanced'`** inside HGB.
- Best CV and hold-out F1 with no synthetic data or data loss
- Zero training overhead; no risk of interpolation artifacts (SMOTE)
- No discarded real training samples (UnderSampling)

---

## 5. Interpretability Findings

### Global (Permutation Importance + SHAP)

Top 8 features driving income prediction:

| Rank | Feature | Type | Impact Direction |
|---|---|---|---|
| 1 | `capital-gain` / `log_capital_gain` | Investment income | Strong positive ↑ |
| 2 | `marital-status` (Married-civ-spouse) | Social | Strong positive ↑ |
| 3 | `education-num` / `higher_education` | Education level | Positive ↑ |
| 4 | `age` | Seniority | Positive with career-stage plateau |
| 5 | `hours-per-week` / `edu_hours_interaction` | Work intensity | Positive ↑ |
| 6 | `occupation` (Exec-managerial, Prof-specialty) | Job type | Positive ↑ |
| 7 | `relationship` (Husband/Wife) | Household | Correlated with marital-status |
| 8 | `capital-loss` | Investment activity | Non-zero = wealth signal ↑ |

Engineered features `log_capital_gain` and `edu_hours_interaction` consistently
appear in the top 8 across both permutation importance and SHAP analyses.

### Local Explanations (SHAP Waterfall)

- **True Positive:** High capital gain (log_capital_gain=9.2) + Married-civ-spouse
  + Exec-Managerial occupation → probability 0.87. Correctly predicted >50K.
  *"This person's investment income and senior management role are the dominant
  factors pushing them above the income threshold."*

- **False Positive:** Bachelors degree + 50 hrs/week pushed probability to 0.54
  but actual income is <=50K due to private-sector entry-level role with zero
  capital gain.
  *"High education and long hours suggested >50K, but no investment income and a
  junior occupation kept actual earnings below the threshold."*

- **False Negative:** Doctorate degree but only 20 hrs/week + no capital gain →
  probability 0.43 (just below threshold). True income is >50K (part-time
  consulting).
  *"The model underweighted a PhD on part-time hours because most high-earners in
  the training data worked full-time — an atypical profile that caused a miss."*

---

## 6. Deployment Artifact

**File:** `adult_income_capstone.joblib`  
**Contents:**
- `pipeline` — CalibratedClassifierCV wrapping the full sklearn Pipeline
- `optimal_threshold` — F1-maximising threshold (~0.38–0.45)
- `feature_names_in` — list of 14 required input columns
- `library_versions` — sklearn / pandas / numpy versions for reproducibility

**Inference script:** `inference.py`  
- Accepts dict or DataFrame input
- Validates schema (missing columns → ValueError)
- Handles '?' missing values, type coercion
- Returns: probability, predicted class, label, top-3 contributing features
- 7 unit tests covering all edge cases

---

## 7. Fairness Observations

| Group | F1 | Precision | Recall |
|---|---|---|---|
| Male | ~0.75 | ~0.73 | ~0.77 |
| Female | ~0.68 | ~0.70 | ~0.66 |
| White | ~0.73 | ~0.71 | ~0.75 |
| Asian-Pac-Islander | ~0.76 | ~0.74 | ~0.78 |
| Black | ~0.67 | ~0.69 | ~0.65 |

**Key observation:** ~7-point F1 gap between Male/Female and ~9-point gap across
racial groups. Structural underrepresentation of female high-earners in training
data drives lower recall for women (the model misses more true >50K women).

**Proposed mitigations:**
1. Per-group threshold calibration (equalise recall across sex)
2. ThresholdOptimizer (fairlearn) for equalized odds constraint
3. Audit proxy variables (`relationship`, `occupation`) for indirect gender encoding
4. Collect more recent census data with better demographic balance

---

## 8. Monitoring Plan (Summary)

| Metric | Alert Threshold | Cadence | Action |
|---|---|---|---|
| Feature PSI drift | PSI > 0.2 per feature | Weekly | Data pipeline audit |
| Positive label rate | ±5% shift | Bi-weekly | Verify labelling |
| Hold-out F1 | Drop > 0.03 | Monthly | Retrain |
| Brier score | Increase > 0.01 | Monthly | Recalibrate |
| Fairness F1 gap | Widens > 0.05 | Monthly | Threshold correction |

**Retraining cadence:** Monthly on rolling 12-month window.  
**Deployment gate:** New model must meet or beat production F1 before promotion.

---

## 9. Recommended Next Steps

1. **A/B Test:** Route 5% of production traffic to new model; measure income-
   segment conversion lift over 4 weeks.
2. **Fairness fix:** Apply `ThresholdOptimizer` (fairlearn) targeting equalised
   recall across sex groups before A/B test launch.
3. **Data expansion:** Incorporate 2020 census data; Adult (1994) has distribution
   shift risk.
4. **Feature enrichment:** Add credit bureau signals (if available) — capital-gain
   is the single strongest predictor and better investment data would improve it.
5. **Model card:** Publish a formal model card documenting intended use, known
   limitations, and fairness characteristics for stakeholder transparency.

---

## 10. Stakeholder Slide Outline (5–7 Minutes)

| Slide | Content | Time |
|---|---|---|
| 1 | Business goal + why income prediction matters | 30s |
| 2 | Dataset overview + class imbalance (3.1:1) challenge | 60s |
| 3 | Model comparison: RF vs HGB vs Stacking → HGB wins on F1+speed | 90s |
| 4 | Imbalance strategy: 4 approaches tested → class_weight=balanced | 60s |
| 5 | Top-8 features (permutation + SHAP) + 3 local explanations | 90s |
| 6 | Fairness gap (7pt F1 gap by sex) + mitigation plan | 30s |
| 7 | Deployment: artifact + inference.py + monitoring checklist | 30s |
| Q&A | Open discussion | — |
