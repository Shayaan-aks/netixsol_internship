# Week 4 · Day 1 — ML Foundations Summary
## Adult Census Income · Problem Framing → Baseline Results → Error Analysis

---

## 1. Problem Framing

**Business Objective:** A marketing team wants to identify high-income individuals (>50K/year) to send targeted premium offers. Contacting wrong leads wastes budget; the goal is a score-ranked list so the team can choose a contact threshold that fits their outreach spend.

**Target:** Income >50K = Positive (1) · Income ≤50K = Negative (0)

**Class Base Rate:** ~23.9% positive (moderately imbalanced)

---

## 2. Chosen Primary Metric — ROC AUC

| Metric | Verdict | Reason |
|--------|---------|--------|
| Accuracy | ❌ Misleading | 76% achievable by always predicting ≤50K |
| Precision | ❌ Partial | Ignores how many high-earners we find |
| Recall | ❌ Partial | Ignores wasted outreach costs |
| **ROC AUC** | ✅ **Primary** | Threshold-free ranking quality; lets the business pick its own operating point |
| F1 | ✅ Secondary | Useful at threshold = 0.5 |
| PR AUC | ✅ Secondary | Tracks precision–recall balance on minority class |

**Why precision over recall isn't the whole story:** In targeted marketing, neither pure precision (contact few, hit rate high but miss most earners) nor pure recall (contact everyone, high cost) is optimal in isolation. ROC AUC provides a holistic view across all thresholds, letting the business *slide* the cut-off to match budget. Our week target: **ROC AUC ≥ 0.88**.

**Stakeholder summary:** *"We score every customer by likelihood of earning >50K. Your team picks a cut-off to match your budget — higher cut-off = fewer contacts, higher hit rate. We measure model quality with ROC AUC (0.5 = random, 1.0 = perfect)."*

---

## 3. Data & EDA Highlights

| Statistic | Value |
|-----------|-------|
| Total records | 48,842 |
| Positive class (>50K) | 11,687 (23.93%) |
| Negative class (≤50K) | 37,155 (76.07%) |
| Missing: workclass | 2,799 (5.7%) |
| Missing: occupation | 2,809 (5.7%) |
| Missing: native-country | 857 (1.8%) |

**Key feature distributions:**
- **Age:** Mean age >50K = 44.3 yrs vs. ≤50K = 36.9 yrs (~7-year gap)
- **Education:** Bachelors holders earn >50K at 41.3%; HS-grads at only 15.9%
- **Marital status:** Married-civ-spouse has 44.6% high-earner rate (≈2× dataset avg)

---

## 4. Reproducible Splits

| Split | Rows | Positive Rate |
|-------|------|---------------|
| Training | ~35,168 | 23.93% |
| Dev | ~3,908 | 23.93% |
| **Test (hold-out)** | 9,769 | 23.93% |

- `random_state=42`, `stratify=y` ensures reproducibility and class balance across splits
- **Test set touched exactly once** — only for final evaluation

---

## 5. Baseline Results (Evaluated on Hold-Out Test Set)

| Model | Accuracy | Precision | Recall | F1 | ROC AUC | PR AUC |
|-------|----------|-----------|--------|----|---------|--------|
| Majority Class | 0.7607 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.2393 |
| **Rule-Based** | **0.7520** | **0.4852** | **0.5967** | **0.5352** | **0.7083** | **0.4258** |

**Rule:** Predict >50K if `capital-gain > 0` OR `education-num ≥ 13`

**Interpretation:** The rule-based classifier wins convincingly (ROC AUC 0.71 vs. 0.50). The majority classifier has 0% precision/recall for the positive class — it never predicts >50K at all. The rule delivers meaningful signal: it correctly ranks positives above negatives 71% of the time and achieves 60% recall, finding 3 out of every 5 actual high earners.

**Minimum improvement bar:** Any real model must achieve **ROC AUC > 0.71** and **F1 > 0.54** to be considered an improvement over the rule.

---

## 6. Error Analysis

### False Negatives (high earners the rule missed)
- Mean `education-num` = 9.5 (vs. 11.6 for all >50K) → high earners without degrees
- 89% are Married-civ-spouse — established mid-career workers in Craft-repair, Exec-managerial
- Many work 50–65 hrs/week — hours-per-week is an important signal the rule ignores

### False Positives (non-high-earners the rule wrongly flagged)
- ~79% triggered by `education-num ≥ 13` alone with zero capital gain
- These are young/early-career degree holders (Sales, Adm-clerical) who haven't yet converted credentials into high income
- Rule doesn't account for occupation or age-within-education-level

---

## 7. Issues to Fix (Day 2)

1. **Missing values** in `workclass`, `occupation`, `native-country` → encode as explicit `'Missing'` category
2. **Skewed numerics** — `capital-gain` / `capital-loss` (91% zeros, extreme tail) → `log1p` transform + binary indicators
3. **Redundant columns** — `education` and `education-num` carry identical info → drop `education`
4. **`fnlwgt` is census sampling weight, not a feature** → drop it
5. **High-cardinality `native-country`** (90%+ US) → group rare values into `'Other'`
6. **Non-linear age/hours relationships** → test polynomial features or age-band discretisation

---

## 8. Primary Metric for the Week

**→ ROC AUC** (primary), with F1 and PR AUC as secondary trackers.

Baseline rule-based ROC AUC = **0.71** · PR AUC = **0.43** (base rate = 0.24)
Week target: **ROC AUC ≥ 0.88** · **PR AUC ≥ 0.60**
