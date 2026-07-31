from langchain_core.tools import tool
from prediction.match_predictor import predict_match_winner
from prediction.player_predictor import predict_top_player
from prediction.feature_explainer import explain_match_prediction, explain_player_prediction

@tool
def predict_match_tool(home_team: str, away_team: str) -> str:
    """Predicts the winner of an AFL match."""
    prediction = predict_match_winner(home_team, away_team)
    return explain_match_prediction(prediction, home_team, away_team)

@tool
def predict_player_tool(team: str) -> str:
    """Predicts the top performing player for a given AFL team."""
    prediction = predict_top_player(team)
    return explain_player_prediction(prediction, team)
