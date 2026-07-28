import os
import logging
import pandas as pd
import numpy as np
import joblib

from src.utils import setup_logger, set_seed
from src.pipelines import build_preprocessor, get_model_pipeline
from src.model_training import get_top_player_models, train_with_cv
from src.evaluation import evaluate_models
from src.feature_importance import extract_feature_importances
from src.visualization import plot_feature_importance

def run_top_player_pipeline():
    logger = setup_logger("prediction_models", "outputs/reports/top_player_pipeline.log")
    set_seed(42)
    
    logger.info("--- Starting Top Player Pipeline ---")
    
    data_path = '../day-1/data/raw/merged_players.csv'
    if not os.path.exists(data_path):
        logger.error("Player data not found.")
        return
        
    df = pd.read_csv(data_path)
    
    # We want to predict Next Year's Fantasy Points
    # Create target by shifting
    df = df.sort_values(['player_id', 'year'])
    df['next_year_fantasy'] = df.groupby('player_id')['avg_fantasy_points'].shift(-1)
    
    # Drop rows where target is NaN (player didn't play next year or last year in dataset)
    df = df.dropna(subset=['next_year_fantasy'])
    
    y = df['next_year_fantasy']
    
    # Features (all current year stats)
    drop_cols = ['id', 'player_id', 'player_name', 'player_full_name', 'first_name', 'last_name',
                 'born_date', 'debut_date', 'last_date', 'player_link', 'player_common_names', 'player_teams',
                 'next_year_fantasy']
    
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    # Train/Val/Test
    train = X[X['year'] < 2023].copy()
    val = X[X['year'] == 2023].copy()
    test = X[X['year'] >= 2024].copy()
    
    y_train = y[train.index]
    y_val = y[val.index]
    y_test = y[test.index]
    
    train = train.drop(columns=['year'])
    val = val.drop(columns=['year'])
    test = test.drop(columns=['year'])
    X = X.drop(columns=['year'])
    
    num_cols = train.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    cat_cols = train.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    logger.info(f"Features: {len(num_cols)} numerical, {len(cat_cols)} categorical.")
    
    # Baselines
    y_pred_baseline = test['avg_fantasy_points'].values
    
    # For evaluate_ranking, we need a df_true and df_pred that have match_id.
    # Since we are doing season level, we can rank within the 'year' 2024.
    df_true = df.loc[test.index].copy()
    df_true['match_id'] = df_true['year'] # Rank within the year instead of match
    df_true['composite_fantasy_score'] = y_test
    
    results = {
        'Baseline (Current Year Score)': {
            'df_true': df_true,
            'df_pred': y_pred_baseline
        }
    }
    
    preprocessor = build_preprocessor(num_cols, cat_cols)
    models = get_top_player_models()
    
    best_overall_model = None
    best_ndcg = -1
    
    for name, config in models.items():
        logger.info(f"Training {name}...")
        pipeline = get_model_pipeline(preprocessor, config['estimator'])
        
        # We use negative MSE for scoring
        best_model = train_with_cv(pipeline, config['param_grid'], train, y_train, n_splits=3, n_iter=5, scoring='neg_mean_squared_error')
        
        y_pred = best_model.predict(test)
        
        results[name] = {
            'df_true': df_true,
            'df_pred': y_pred
        }
        
        # Quick eval of NDCG
        from src.metrics import evaluate_ranking
        res = evaluate_ranking(df_true, y_pred, target_col='composite_fantasy_score', pred_col='predicted_score')
        ndcg = res['NDCG']
        if not np.isnan(ndcg) and ndcg > best_ndcg:
            best_ndcg = ndcg
            best_overall_model = best_model
            
    df_eval = evaluate_models(results, problem_type='ranking')
    df_eval.to_csv('outputs/reports/top_player_evaluation.csv')
    logger.info("\n" + df_eval.to_string())
    
    if best_overall_model:
        fitted_preprocessor = best_overall_model.named_steps['preprocessor']
        importances, feature_names = extract_feature_importances(best_overall_model, fitted_preprocessor, num_cols, cat_cols)
        plot_feature_importance(importances, feature_names, 'Best_Top_Player_Model', save_dir='outputs/figures')
        
        joblib.dump(best_overall_model, 'models/top_player.joblib')
        logger.info("Saved best top player model.")

if __name__ == "__main__":
    run_top_player_pipeline()
