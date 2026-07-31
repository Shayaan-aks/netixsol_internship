def predict_match_winner(home_team: str, away_team: str) -> dict:
    """Mock match prediction."""
    prob = max(30, (len(home_team) * 5) % 100)
    return {
        'home_win_probability': float(prob / 100.0),
        'predicted_winner': home_team if prob >= 50 else away_team
    }
