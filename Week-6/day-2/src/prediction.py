import pandas as pd
import numpy as np

def predict_match_probability(pipeline, X_new):
    """
    Predict probability of home team winning.
    """
    return pipeline.predict_proba(X_new)[:, 1]

def predict_match_class(pipeline, X_new, threshold=0.5):
    """
    Predict binary class based on threshold.
    """
    probs = predict_match_probability(pipeline, X_new)
    return (probs >= threshold).astype(int)

def predict_top_players_ranking(pipeline, X_new, match_meta):
    """
    Predict fantasy scores and return a ranked dataframe.
    match_meta should contain 'match_id', 'player_id', 'player_name', etc.
    """
    preds = pipeline.predict(X_new)
    
    df_res = match_meta.copy()
    df_res['predicted_score'] = preds
    
    # Sort descending per match
    df_res = df_res.sort_values(['match_id', 'predicted_score'], ascending=[True, False])
    
    # Create rank column
    df_res['predicted_rank'] = df_res.groupby('match_id').cumcount() + 1
    
    return df_res
