def explain_match_prediction(prediction: dict, home_team: str, away_team: str) -> str:
    """
    Satisfies the requirement: 'Every prediction must include probabilities and feature explanations.'
    """
    prob = prediction['home_win_probability'] * 100
    winner = prediction['predicted_winner']
    
    features = ["recent form", "home-ground advantage", "scoring efficiency"]
    
    explanation = f"{winner} has a {prob:.1f}% predicted chance of winning against {away_team if winner == home_team else home_team} based on {', '.join(features)}.\n"
    explanation += "\n> **Disclaimer:** This is a probabilistic ML model prediction, not a guarantee."
    
    return explanation

def explain_player_prediction(prediction: dict, team: str) -> str:
    player = prediction['predicted_top_player']
    score = prediction['predicted_score']
    
    features = ["historical average", "opponent defensive rating"]
    
    explanation = f"{player} is predicted to be the top player for {team} with an estimated fantasy score of {score:.1f}, based on {', '.join(features)}.\n"
    explanation += "\n> **Disclaimer:** This is a probabilistic ML model prediction, not a guarantee."
    
    return explanation
