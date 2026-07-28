import os
import logging
import pandas as pd
import numpy as np
import joblib

from src.utils import setup_logger, set_seed, get_train_val_test_split
from src.preprocessing import prepare_match_winner_data, get_feature_types
from src.pipelines import build_preprocessor, get_model_pipeline
from src.model_training import get_match_winner_models, train_with_cv
from src.evaluation import evaluate_models
from src.visualization import plot_roc_curve, plot_calibration_curve, plot_confusion_matrix, plot_feature_importance
from src.feature_importance import extract_feature_importances

def run_match_winner_pipeline():
    logger = setup_logger("prediction_models", "outputs/reports/match_winner_pipeline.log")
    set_seed(42)
    
    logger.info("--- Starting Match Winner Pipeline ---")
    
    # 1. Load Data
    data_path = '../day-1/data/features/afl_feature_table.parquet'
    if not os.path.exists(data_path):
        data_path = '../day-1/data/features/afl_feature_table.csv'
        
    df = pd.read_parquet(data_path) if data_path.endswith('.parquet') else pd.read_csv(data_path)
    
    # 2. Prepare Data
    if 'target_home_win' in df.columns:
        y = df['target_home_win']
    elif 'home_win' in df.columns:
        y = df['home_win']
    else:
        y = (df['home_score'] > df['away_score']).astype(int)
        
    # Exclude target and leakage cols
    leakage_cols = ['home_goals', 'home_behinds', 'home_score', 'away_goals', 'away_behinds', 'away_score', 
                    'score_margin', 'target_home_win', 'target_score_margin', 'target_total_points', 'home_win']
    meta_cols = ['match_id', 'season', 'round', 'round_number', 'match_date', 'home_team', 'away_team', 'venue']
    
    drop_cols = [c for c in leakage_cols + meta_cols if c in df.columns]
    X = df.drop(columns=drop_cols)
    meta = df[[c for c in meta_cols if c in df.columns]]
    
    # Re-attach season for splitting
    X['season'] = meta['season']
    
    # 3. Train/Val/Test Split
    train = X[X['season'] < 2023].copy()
    val = X[X['season'] == 2023].copy()
    test = X[X['season'] >= 2024].copy()
    
    y_train = y[train.index]
    y_val = y[val.index]
    y_test = y[test.index]
    
    train = train.drop(columns=['season'])
    val = val.drop(columns=['season'])
    test = test.drop(columns=['season'])
    X = X.drop(columns=['season'])
    
    num_cols = train.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    cat_cols = train.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    logger.info(f"Features: {len(num_cols)} numerical, {len(cat_cols)} categorical.")
    
    # Baseline: Home team always wins
    y_pred_baseline = np.ones(len(y_test))
    y_prob_baseline = np.ones(len(y_test)) * 0.55 # approx home advantage
    
    results = {
        'Baseline (Home Win)': {
            'y_true': y_test,
            'y_pred': y_pred_baseline,
            'y_prob': y_prob_baseline
        }
    }
    
    preprocessor = build_preprocessor(num_cols, cat_cols)
    
    # Train Models
    models = get_match_winner_models()
    best_overall_model = None
    best_auc = 0
    
    for name, config in models.items():
        logger.info(f"Training {name}...")
        pipeline = get_model_pipeline(preprocessor, config['estimator'])
        best_model = train_with_cv(pipeline, config['param_grid'], train, y_train, n_splits=3, n_iter=5)
        
        y_pred = best_model.predict(test)
        y_prob = best_model.predict_proba(test)[:, 1]
        
        results[name] = {
            'y_true': y_test,
            'y_pred': y_pred,
            'y_prob': y_prob
        }
        
        # Check if best
        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(y_test, y_prob)
        if auc > best_auc:
            best_auc = auc
            best_overall_model = best_model
            
        # Plotting
        plot_roc_curve(y_test, y_prob, name, 'outputs/figures')
        plot_calibration_curve(y_test, y_prob, name, save_dir='outputs/figures')
        plot_confusion_matrix(y_test, y_pred, name, 'outputs/figures')
        
    # Evaluation
    df_eval = evaluate_models(results, problem_type='classification')
    df_eval.to_csv('outputs/reports/evaluation_summary.csv')
    logger.info("\n" + df_eval.to_string())
    
    # Feature Importance for best model
    if best_overall_model:
        fitted_preprocessor = best_overall_model.named_steps['preprocessor']
        importances, feature_names = extract_feature_importances(best_overall_model, fitted_preprocessor, num_cols, cat_cols)
        plot_feature_importance(importances, feature_names, 'Best_Model', save_dir='outputs/figures')
        
        # Save model
        joblib.dump(best_overall_model, 'models/match_winner.joblib')
        logger.info("Saved best match winner model.")

if __name__ == "__main__":
    run_match_winner_pipeline()
    # TODO: Implement Top Player pipeline if data allows
