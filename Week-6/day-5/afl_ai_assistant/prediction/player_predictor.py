def predict_top_player(team: str) -> dict:
    """Mock player prediction."""
    return {
        "predicted_top_player": "Nick Daicos" if "Collingwood" in team else "Lachie Neale",
        "predicted_score": 120.5
    }
