from langchain_core.tools import tool
from prediction.predict_match import predict_match_winner
from prediction.predict_player import predict_top_player
from prediction.feature_explainer import explain_match_prediction, explain_player_prediction
from utils.aliases import resolve_team_alias
from utils.helpers import log_tool

@tool
def predict_match(home_team: str, away_team: str) -> str:
    """
    Predict the winner between two AFL teams.
    """
    home = resolve_team_alias(home_team) or home_team
    away = resolve_team_alias(away_team) or away_team
    
    raw_pred = predict_match_winner(home, away)
    explanation = explain_match_prediction(raw_pred, home, away)
    
    log_tool("predict_match", {"home": home, "away": away}, explanation)
    return explanation

@tool
def predict_player(team: str) -> str:
    """
    Predict the top performing player for a specific team.
    """
    resolved_team = resolve_team_alias(team) or team
    raw_pred = predict_top_player(resolved_team)
    explanation = explain_player_prediction(raw_pred, resolved_team)
    
    log_tool("predict_player", {"team": resolved_team}, explanation)
    return explanation
