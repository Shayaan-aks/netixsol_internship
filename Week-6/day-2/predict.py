import os
import joblib
import pandas as pd
import numpy as np

# Load models at module level to avoid loading them per request
MATCH_WINNER_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models/match_winner.joblib')
TOP_PLAYER_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models/top_player.joblib')

_match_winner_model = None
_top_player_model = None

def _load_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Please train it first.")
    return joblib.load(model_path)

def predict_match_winner(match_data: dict) -> dict:
    """
    Predict the probability of the home team winning.
    
    Args:
        match_data (dict): A dictionary containing match features.
        
    Returns:
        dict: A dictionary containing 'home_win_probability', 'predicted_winner'
    """
    global _match_winner_model
    if _match_winner_model is None:
        _match_winner_model = _load_model(MATCH_WINNER_MODEL_PATH)
        
    # Convert dict to DataFrame
    df = pd.DataFrame([match_data])
    
    # Identify categorical and numeric columns
    # We assume the input dictionary has the same columns as the training data
    
    prob = _match_winner_model.predict_proba(df)[0, 1]
    
    return {
        'home_win_probability': float(prob),
        'predicted_winner': 'Home' if prob >= 0.5 else 'Away'
    }

def predict_top_player(match_players_data: list[dict]) -> list[dict]:
    """
    Predict the fantasy score and rank players for a match.
    
    Args:
        match_players_data (list[dict]): A list of dictionaries containing player features for a match.
        
    Returns:
        list[dict]: The input list augmented with 'predicted_score' and 'predicted_rank', sorted by rank.
    """
    global _top_player_model
    if _top_player_model is None:
        _top_player_model = _load_model(TOP_PLAYER_MODEL_PATH)
        
    df = pd.DataFrame(match_players_data)
    
    preds = _top_player_model.predict(df)
    df['predicted_score'] = preds
    
    # Sort and rank
    df = df.sort_values('predicted_score', ascending=False)
    df['predicted_rank'] = np.arange(1, len(df) + 1)
    
    return df.to_dict(orient='records')
