DISCLAIMER = "\n\n> **Disclaimer:** This prediction is generated from AFL dataset statistics and represents a probability estimate, not a certainty."

def explain_match_prediction(prediction: dict, home: str, away: str) -> str:
    prob = prediction['home_win_probability'] * 100
    winner = prediction['predicted_winner']
    loser = away if winner == home else home

    home_wins = prediction.get("home_wins", "?")
    away_wins = prediction.get("away_wins", "?")
    home_ladder = prediction.get("home_ladder", "?")
    away_ladder = prediction.get("away_ladder", "?")

    reasoning = (
        f"{winner} is predicted to win against {loser} "
        f"with a {prob:.1f}% probability.\n\n"
        f"Key factors:\n"
        f"- {home}: {home_wins} wins, Ladder position #{home_ladder} (2023 season)\n"
        f"- {away}: {away_wins} wins, Ladder position #{away_ladder} (2023 season)\n"
        f"- Home-ground advantage applied to {home}."
    )
    return reasoning + DISCLAIMER

def explain_player_prediction(prediction: dict, team: str) -> str:
    player = prediction.get('predicted_top_player', 'Unknown')
    score = prediction.get('predicted_score', 0.0)
    stat_basis = prediction.get('stat_basis', 'performance')
    reasoning_text = prediction.get('reasoning', 'AFL dataset stats')

    exp = (
        f"{player} is predicted to be the top performer for {team}.\n\n"
        f"Dataset basis: {stat_basis} value of {score:.0f} — {reasoning_text}"
    )
    return exp + DISCLAIMER
