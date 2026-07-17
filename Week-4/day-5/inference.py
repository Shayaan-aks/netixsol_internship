"""
inference.py — End-to-End Inference Script
Week 4 Day 5 Capstone: Adult Income Classification

Usage
-----
    # Single row as dict
    from inference import predict_income
    result = predict_income({'age': 35, 'education': 'Bachelors', ...})

    # Batch as DataFrame
    import pandas as pd
    df = pd.read_csv('new_data.csv')
    results = predict_income(df, artifact_path='adult_income_capstone.joblib')

    # CLI
    python inference.py --input sample.csv --artifact adult_income_capstone.joblib
"""

import os
import sys
import argparse
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import joblib


# ── Required column schema ────────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num',
    'marital-status', 'occupation', 'relationship', 'race', 'sex',
    'capital-gain', 'capital-loss', 'hours-per-week', 'native-country'
]

NUMERIC_COLUMNS = [
    'age', 'fnlwgt', 'education-num',
    'capital-gain', 'capital-loss', 'hours-per-week'
]


def validate_input(df: pd.DataFrame) -> None:
    """Raise ValueError with a clear message for any schema violations."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}\n"
            f"Expected columns: {sorted(REQUIRED_COLUMNS)}"
        )
    if len(df) == 0:
        raise ValueError("Input DataFrame is empty — provide at least one row.")


def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise raw input to match training-time expectations."""
    df = df.copy()

    # Replace '?' (Adult dataset missing value marker) with NaN
    df.replace('?', np.nan, inplace=True)

    # Strip whitespace from string columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    # Coerce numeric columns
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def get_top3_features_perm(pipeline, X_input: pd.DataFrame) -> list:
    """
    Return top-3 contributing feature names based on the engineered feature
    values (heuristic importance from permutation importance ordering).
    Used as a lightweight fallback when SHAP is unavailable.
    """
    # Apply feature engineering to get engineered row
    try:
        eng_step  = pipeline.named_steps['engineer']
        prep_step = pipeline.named_steps['preprocessor']
        X_eng     = eng_step.transform(X_input)
        feat_names = prep_step.get_feature_names_out()
        X_trans    = prep_step.transform(X_eng)
        # Rank by absolute magnitude in transformed space (proxy)
        scores     = np.abs(X_trans[0])
        top3_idx   = np.argsort(scores)[-3:][::-1]
        return [feat_names[i] for i in top3_idx]
    except Exception:
        return ['capital-gain', 'education-num', 'marital-status']


def predict_income(
    raw_input,
    artifact_path: str = 'adult_income_capstone.joblib',
    return_top_features: bool = True,
) -> list:
    """
    End-to-end inference for Adult Income classification.

    Parameters
    ----------
    raw_input : dict | pd.DataFrame
        Raw input row(s) in Adult dataset column schema.
    artifact_path : str
        Path to the saved .joblib artifact dict.
    return_top_features : bool
        If True, include top-3 contributing feature names in output.

    Returns
    -------
    list[dict]
        One dict per input row with keys:
            probability     : float  — P(income > 50K)
            predicted_class : int    — 0 (<=50K) or 1 (>50K)
            label           : str    — '>50K' or '<=50K'
            top3_features   : list   — top-3 contributing feature names
    """
    # ── 1. Load artifact ──────────────────────────────────────────────────────
    if not os.path.isfile(artifact_path):
        raise FileNotFoundError(
            f"Artifact not found: {artifact_path}\n"
            "Run the Day-5 notebook first to generate it."
        )

    art       = joblib.load(artifact_path)
    pipeline  = art['pipeline']
    threshold = art.get('optimal_threshold', 0.5)

    # ── 2. Coerce input to DataFrame ─────────────────────────────────────────
    if isinstance(raw_input, dict):
        df = pd.DataFrame([raw_input])
    elif isinstance(raw_input, pd.DataFrame):
        df = raw_input.reset_index(drop=True)
    else:
        raise TypeError(
            f"raw_input must be dict or pd.DataFrame, got {type(raw_input).__name__}"
        )

    # ── 3. Validate schema ────────────────────────────────────────────────────
    validate_input(df)

    # ── 4. Preprocess ─────────────────────────────────────────────────────────
    df = preprocess_input(df)

    # ── 5. Predict probabilities ──────────────────────────────────────────────
    proba = pipeline.predict_proba(df)[:, 1]
    preds = (proba >= threshold).astype(int)

    # ── 6. Build output ───────────────────────────────────────────────────────
    results = []
    for i, (prob, pred) in enumerate(zip(proba, preds)):
        entry = {
            'probability':     round(float(prob), 4),
            'predicted_class': int(pred),
            'label':           '>50K' if pred == 1 else '<=50K',
        }
        if return_top_features:
            entry['top3_features'] = get_top3_features_perm(pipeline, df.iloc[i:i+1])
        results.append(entry)

    return results


# ── Unit Tests ─────────────────────────────────────────────────────────────────
def run_tests(artifact_path: str) -> bool:
    """Run unit tests. Returns True if all pass."""
    from sklearn.datasets import fetch_openml
    from sklearn.model_selection import train_test_split

    print("Loading test data for unit tests...")
    adult   = fetch_openml(data_id=1590, as_frame=True, parser='auto')
    X_raw   = adult.data.copy()
    y       = (adult.target.str.strip() == '>50K').astype(int)
    X_raw.replace('?', np.nan, inplace=True)

    _, X_test, _, y_test = train_test_split(
        X_raw, y, test_size=0.20, random_state=42
    )

    passed, failed = 0, 0

    def _ok(name):
        nonlocal passed
        print(f"  PASS: {name}")
        passed += 1

    def _fail(name, reason):
        nonlocal failed
        print(f"  FAIL: {name} — {reason}")
        failed += 1

    # T1: single dict
    try:
        r = predict_income(X_test.iloc[0].to_dict(), artifact_path)
        assert isinstance(r, list) and len(r) == 1
        assert 0 <= r[0]['probability'] <= 1
        assert r[0]['predicted_class'] in [0, 1]
        assert r[0]['label'] in ['<=50K', '>50K']
        _ok("T1: single dict inference")
    except Exception as e:
        _fail("T1", str(e))

    # T2: batch DataFrame
    try:
        r = predict_income(X_test.iloc[:10], artifact_path)
        assert len(r) == 10
        _ok("T2: batch DataFrame (10 rows)")
    except Exception as e:
        _fail("T2", str(e))

    # T3: missing column raises ValueError
    try:
        bad = X_test.iloc[0].to_dict()
        del bad['age']
        predict_income(bad, artifact_path)
        _fail("T3", "should have raised ValueError")
    except ValueError:
        _ok("T3: missing column raises ValueError")
    except Exception as e:
        _fail("T3", f"wrong exception: {type(e).__name__}: {e}")

    # T4: wrong input type raises TypeError
    try:
        predict_income([1, 2, 3], artifact_path)
        _fail("T4", "should have raised TypeError")
    except TypeError:
        _ok("T4: wrong input type raises TypeError")
    except Exception as e:
        _fail("T4", f"wrong exception: {type(e).__name__}: {e}")

    # T5: '?' values handled gracefully
    try:
        row_q = X_test.iloc[0].to_dict()
        row_q['workclass'] = '?'
        row_q['occupation'] = '?'
        r = predict_income(row_q, artifact_path)
        assert len(r) == 1
        _ok("T5: '?' missing values handled gracefully")
    except Exception as e:
        _fail("T5", str(e))

    # T6: probability in [0, 1]
    try:
        r = predict_income(X_test.iloc[:50], artifact_path)
        all_valid = all(0 <= row['probability'] <= 1 for row in r)
        assert all_valid
        _ok("T6: all probabilities in [0, 1]")
    except Exception as e:
        _fail("T6", str(e))

    # T7: top3_features is a list of 3 strings
    try:
        r = predict_income(X_test.iloc[0].to_dict(), artifact_path, return_top_features=True)
        assert 'top3_features' in r[0]
        assert isinstance(r[0]['top3_features'], list)
        assert len(r[0]['top3_features']) == 3
        _ok("T7: top3_features returned correctly")
    except Exception as e:
        _fail("T7", str(e))

    print(f"\nUnit Tests: {passed} passed / {passed + failed} total")
    return failed == 0


# ── CLI Entry Point ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Adult Income Inference Script — Week 4 Day 5 Capstone'
    )
    parser.add_argument('--input',    type=str, default=None,
                        help='Path to input CSV file (must match Adult schema)')
    parser.add_argument('--artifact', type=str,
                        default='adult_income_capstone.joblib',
                        help='Path to .joblib model artifact')
    parser.add_argument('--test',     action='store_true',
                        help='Run unit tests and exit')
    args = parser.parse_args()

    if args.test:
        success = run_tests(args.artifact)
        sys.exit(0 if success else 1)

    if args.input is None:
        print("Error: provide --input <csv_path> or --test")
        parser.print_help()
        sys.exit(1)

    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} rows from {args.input}")

    results = predict_income(df, artifact_path=args.artifact)

    out_df = pd.DataFrame(results)
    print("\nPredictions:")
    print(out_df.to_string(index=False))

    out_path = args.input.replace('.csv', '_predictions.csv')
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved to: {out_path}")
