import logging
import pandas as pd
import numpy as np

def prepare_match_winner_data(df):
    """
    Prepare data for the Match Winner Prediction Model.
    Target: home_win (1 if home team wins, 0 otherwise)
    Returns: X, y, meta
    """
    logger = logging.getLogger("prediction_models")
    
    # We create the target 'home_win' if it doesn't exist explicitly
    # Assuming we have 'home_team_score' and 'away_team_score' from the original dataset
    # Wait, the feature table from day 1 should already contain rolling stats and results.
    # If the day-1 feature table already has 'home_win', we use it. 
    # Let's assume it has 'home_team_score' and 'away_team_score' or 'margin'
    if 'home_win' not in df.columns:
        df['home_win'] = (df['home_team_score'] > df['away_team_score']).astype(int)
    
    y = df['home_win']
    
    # Exclude leakage features (post-match stats) and non-predictive metadata
    leakage_cols = [
        'home_team_score', 'away_team_score', 'margin', 'home_win', 
        'home_goals', 'home_behinds', 'away_goals', 'away_behinds',
        'composite_fantasy_score', 'player_name', 'player_id', # player level stats
    ]
    meta_cols = ['match_id', 'date', 'season', 'round', 'venue', 'home_team', 'away_team']
    
    drop_cols = [c for c in leakage_cols + meta_cols if c in df.columns]
    X = df.drop(columns=drop_cols)
    meta = df[[c for c in meta_cols if c in df.columns]]
    
    # Keep only rolling stats, ladder pos, etc (all starting with rolling_, home_, away_ etc)
    # Exclude any other player specific rows if the dataframe is at player-match level.
    # We should aggregate or drop player specific rows. We assume the input df here is match-level.
    # If it's player level, we need to group by match.
    
    return X, y, meta

def get_feature_types(X):
    """Identify numerical and categorical columns for the pipeline."""
    num_cols = X.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    cat_cols = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    return num_cols, cat_cols
