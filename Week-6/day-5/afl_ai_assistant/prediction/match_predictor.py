from retrieval.structured import structured_db

def predict_match_winner(home_team: str, away_team: str) -> dict:
    """Data-driven match prediction using ladder position and win percentage."""
    home_stats = structured_db.get_team_summary(home_team)
    away_stats = structured_db.get_team_summary(away_team)

    home_wins = float(home_stats.get("wins", 10))
    away_wins = float(away_stats.get("wins", 10))
    home_losses = float(home_stats.get("losses", 10))
    away_losses = float(away_stats.get("losses", 10))
    home_pos = float(home_stats.get("ladder_position", 9))
    away_pos = float(away_stats.get("ladder_position", 9))

    # Win rate contribution (50% weight)
    home_games = home_wins + home_losses if (home_wins + home_losses) > 0 else 1
    away_games = away_wins + away_losses if (away_wins + away_losses) > 0 else 1
    home_win_rate = home_wins / home_games
    away_win_rate = away_wins / away_games

    # Ladder position contribution (50% weight) — lower is better
    home_pos_score = 1 - ((home_pos - 1) / 17)
    away_pos_score = 1 - ((away_pos - 1) / 17)

    # Combined score
    home_score = 0.5 * home_win_rate + 0.5 * home_pos_score
    away_score = 0.5 * away_win_rate + 0.5 * away_pos_score

    total = home_score + away_score if (home_score + away_score) > 0 else 1
    home_prob = home_score / total

    # Apply small home-ground advantage
    home_prob = min(0.95, home_prob + 0.05)

    return {
        "home_win_probability": round(home_prob, 2),
        "away_win_probability": round(1 - home_prob, 2),
        "predicted_winner": home_team if home_prob >= 0.5 else away_team,
        "home_wins": int(home_wins),
        "away_wins": int(away_wins),
        "home_ladder": int(home_pos),
        "away_ladder": int(away_pos),
    }
