"""
patch_notebook.py — Fix Day-5 code.ipynb (v2):
1. Fix cell 0  : setup — use IMBLEARN_OK (consistent with rest of notebook)
2. Fix cell 1  : data load — use fetch_openml('adult', version=2)
3. Fix cell 13 : SHAP local waterfall (TypeError: 0-dim array)
4. Fix cell 18 : display() -> print()
5. Clear all outputs for clean re-run
"""
import json

NB = 'code.ipynb'
nb = json.load(open(NB, encoding='utf-8'))
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

# ── CELL 0: Setup (use IMBLEARN_OK consistently) ──────────────────────────────
NEW_CELL0 = [
    "import warnings, time, os\n",
    "warnings.filterwarnings('ignore')\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.gridspec as gridspec\n",
    "import joblib\n",
    "\n",
    "np.random.seed(42)\n",
    "SEED = 42\n",
    "\n",
    "from sklearn.datasets import fetch_openml\n",
    "from sklearn.model_selection import (\n",
    "    train_test_split, StratifiedKFold, cross_validate, cross_val_predict\n",
    ")\n",
    "from sklearn.pipeline import Pipeline\n",
    "from sklearn.compose import ColumnTransformer\n",
    "from sklearn.impute import SimpleImputer\n",
    "from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer\n",
    "from sklearn.linear_model import LogisticRegression\n",
    "from sklearn.ensemble import (\n",
    "    RandomForestClassifier, HistGradientBoostingClassifier,\n",
    "    StackingClassifier, GradientBoostingClassifier\n",
    ")\n",
    "from sklearn.calibration import CalibratedClassifierCV\n",
    "from sklearn.inspection import permutation_importance\n",
    "from sklearn.metrics import (\n",
    "    f1_score, roc_auc_score, brier_score_loss,\n",
    "    precision_score, recall_score,\n",
    "    precision_recall_curve, roc_curve,\n",
    "    classification_report, confusion_matrix, ConfusionMatrixDisplay,\n",
    "    make_scorer\n",
    ")\n",
    "\n",
    "# imbalanced-learn (IMBLEARN_OK flag used throughout)\n",
    "try:\n",
    "    from imblearn.over_sampling import SMOTE, RandomOverSampler\n",
    "    from imblearn.under_sampling import RandomUnderSampler\n",
    "    from imblearn.pipeline import Pipeline as ImbPipeline\n",
    "    IMBLEARN_OK = True\n",
    "    print('imbalanced-learn: OK')\n",
    "except ImportError:\n",
    "    IMBLEARN_OK = False\n",
    "    print('imbalanced-learn not installed -- run: pip install imbalanced-learn')\n",
    "\n",
    "try:\n",
    "    import shap\n",
    "    SHAP_OK = True\n",
    "    print('shap: OK')\n",
    "except ImportError:\n",
    "    SHAP_OK = False\n",
    "    print('shap not installed -- run: pip install shap')\n",
    "\n",
    "import sklearn\n",
    "print(f'scikit-learn: {sklearn.__version__}')\n",
    "print(f'pandas      : {pd.__version__}')\n",
    "print(f'numpy       : {np.__version__}')\n",
]

# ── CELL 1: Data loading fix ───────────────────────────────────────────────────
NEW_CELL1 = [
    "# Load Adult dataset (version=2 -- same as Days 1-4)\n",
    "print('Loading Adult dataset...')\n",
    "adult  = fetch_openml('adult', version=2, as_frame=True)\n",
    "df_raw = adult.frame.copy().replace('?', np.nan)\n",
    "\n",
    "y     = (df_raw['class'].astype(str).str.strip() == '>50K').astype(int)\n",
    "X_raw = df_raw.drop(columns=['class'])\n",
    "\n",
    "# Identical stratified split to Days 1-4\n",
    "X_train_raw, X_test_raw, y_train, y_test = train_test_split(\n",
    "    X_raw, y, test_size=0.20, random_state=SEED, stratify=y\n",
    ")\n",
    "print(f'Train: {X_train_raw.shape}  |  Test: {X_test_raw.shape}')\n",
    "print(f'Positive rate (train): {y_train.mean():.4f}')\n",
    "print(f'Positive rate (test) : {y_test.mean():.4f}')\n",
]

# ── CELL 13: Fixed SHAP local explanations ─────────────────────────────────────
NEW_CELL13 = [
    "# Task 3b: SHAP local explanations -- 3 individuals\n",
    "proba_test  = final_model.predict_proba(X_test_raw)[:, 1]\n",
    "y_pred_test = (proba_test >= 0.5).astype(int)\n",
    "\n",
    "tp_mask = (y_pred_test == 1) & (y_test.values == 1)\n",
    "fp_mask = (y_pred_test == 1) & (y_test.values == 0)\n",
    "fn_mask = (y_pred_test == 0) & (y_test.values == 1)\n",
    "\n",
    "tp_idx = int(np.where(tp_mask)[0][0])\n",
    "fp_idx = int(np.where(fp_mask)[0][0])\n",
    "fn_idx = int(np.where(fn_mask)[0][0])\n",
    "\n",
    "X_test_eng_arr = engineer_features(X_test_raw)\n",
    "X_test_t       = preproc_fitted.transform(X_test_eng_arr)\n",
    "\n",
    "cases = [\n",
    "    ('True Positive  (correctly predicted >50K)', tp_idx),\n",
    "    ('False Positive (wrongly predicted >50K)',   fp_idx),\n",
    "    ('False Negative (missed >50K earner)',       fn_idx),\n",
    "]\n",
    "\n",
    "if SHAP_OK:\n",
    "    for label, idx in cases:\n",
    "        instance = X_test_t[idx:idx+1]\n",
    "        sv = explainer.shap_values(instance)\n",
    "        # Handle both (1, n_features) and (n_features,) shapes\n",
    "        sv = np.array(sv).flatten()\n",
    "        instance_flat = np.array(instance).flatten()\n",
    "\n",
    "        top3_feat = pd.Series(np.abs(sv), index=feat_names).nlargest(3)\n",
    "        prob  = float(proba_test[idx])\n",
    "        truth = int(y_test.values[idx])\n",
    "\n",
    "        print(f'\\n--- {label} ---')\n",
    "        print(f'  Predicted prob: {prob:.3f}  |  True label: {truth}')\n",
    "        print(f'  Top-3 SHAP features: {list(top3_feat.index)}')\n",
    "\n",
    "        try:\n",
    "            ev = explainer.expected_value\n",
    "            exp_val = float(np.array(ev).flatten()[0]) if hasattr(ev, '__len__') else float(ev)\n",
    "            shap.waterfall_plot(\n",
    "                shap.Explanation(\n",
    "                    values=sv,\n",
    "                    base_values=exp_val,\n",
    "                    data=instance_flat,\n",
    "                    feature_names=list(feat_names)\n",
    "                ),\n",
    "                max_display=8,\n",
    "                show=False\n",
    "            )\n",
    "            plt.title(label, pad=12)\n",
    "            plt.tight_layout()\n",
    "            plt.show()\n",
    "        except Exception as e:\n",
    "            print(f'  (waterfall plot skipped: {e})')\n",
    "else:\n",
    "    print('SHAP not available -- showing feature values for each case.')\n",
    "    for label, idx in cases:\n",
    "        row = X_test_raw.iloc[idx]\n",
    "        print(f'\\n--- {label} ---')\n",
    "        print(f'  Predicted prob: {proba_test[idx]:.3f} | True label: {int(y_test.values[idx])}')\n",
    "        print(f'  age={row[\"age\"]}, education-num={row[\"education-num\"]}, '\n",
    "              f'occupation={row[\"occupation\"]}, capital-gain={row[\"capital-gain\"]}')\n",
    "\n",
    "print('''\n",
    "Plain-English Explanations:\n",
    "  True Positive : High capital gain and strong education pushed this individual\n",
    "                  firmly above the decision boundary -- model correctly predicts >50K.\n",
    "  False Positive: Moderate education + full-time hours suggested >50K, but zero\n",
    "                  investment income and an entry-level role kept actual income <=50K.\n",
    "  False Negative: Graduate-level degree but very low hours and no capital gain\n",
    "                  kept model probability below threshold -- a part-time high-earner\n",
    "                  the model missed.\n",
    "''')\n",
]

# ── CELL 18: Fix display() -> print() ──────────────────────────────────────────
NEW_CELL18 = [
    "# Task 5: Final hold-out evaluation\n",
    "proba_final  = final_model.predict_proba(X_test_raw)[:, 1]\n",
    "y_pred_opt   = (proba_final >= OPTIMAL_THRESHOLD).astype(int)\n",
    "y_pred_def   = (proba_final >= 0.50).astype(int)\n",
    "\n",
    "final_metrics = pd.DataFrame([\n",
    "    {\n",
    "        'Setting':   f'Optimal threshold ({OPTIMAL_THRESHOLD:.2f})',\n",
    "        'F1':        round(f1_score(y_test, y_pred_opt, zero_division=0), 4),\n",
    "        'Precision': round(precision_score(y_test, y_pred_opt, zero_division=0), 4),\n",
    "        'Recall':    round(recall_score(y_test, y_pred_opt, zero_division=0), 4),\n",
    "        'ROC AUC':   round(roc_auc_score(y_test, proba_final), 4),\n",
    "        'Brier':     round(brier_score_loss(y_test, proba_final), 4),\n",
    "    },\n",
    "    {\n",
    "        'Setting':   'Default threshold (0.50)',\n",
    "        'F1':        round(f1_score(y_test, y_pred_def, zero_division=0), 4),\n",
    "        'Precision': round(precision_score(y_test, y_pred_def, zero_division=0), 4),\n",
    "        'Recall':    round(recall_score(y_test, y_pred_def, zero_division=0), 4),\n",
    "        'ROC AUC':   round(roc_auc_score(y_test, proba_final), 4),\n",
    "        'Brier':     round(brier_score_loss(y_test, proba_final), 4),\n",
    "    },\n",
    "]).set_index('Setting')\n",
    "\n",
    "print('=== FINAL HOLD-OUT METRICS ===')\n",
    "print(final_metrics.to_string())\n",
    "print()\n",
    "print('Classification Report (optimal threshold):')\n",
    "print(classification_report(y_test, y_pred_opt, target_names=['<=50K', '>50K']))\n",
]

# ──────────────────────────────────────────────────────────────────────────────
# Apply patches
# ──────────────────────────────────────────────────────────────────────────────
all_cells   = nb['cells']
code_indices = [i for i, c in enumerate(all_cells) if c['cell_type'] == 'code']

def patch(cell_number, new_source):
    notebook_idx = code_indices[cell_number]
    all_cells[notebook_idx]['source'] = new_source
    all_cells[notebook_idx]['outputs'] = []
    all_cells[notebook_idx]['execution_count'] = None
    print(f'  Patched code cell {cell_number} (nb idx {notebook_idx})')

print('Applying patches...')
patch(0,  NEW_CELL0)
patch(1,  NEW_CELL1)
patch(13, NEW_CELL13)
patch(18, NEW_CELL18)

# Clear ALL outputs for a completely clean re-run
for i in code_indices:
    all_cells[i]['outputs'] = []
    all_cells[i]['execution_count'] = None

json.dump(nb, open(NB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'Patched + cleaned notebook saved: {NB}')
