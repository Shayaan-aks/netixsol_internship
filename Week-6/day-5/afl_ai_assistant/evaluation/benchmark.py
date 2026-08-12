"""
Naive Benchmark Comparison
===========================
Compares the AFL AI Assistant's mock ML prediction model against a simple
ladder-position naive baseline (higher-ranked team always wins).

This contextualises how "good enough" our model is without real historical data.
"""
from prediction.match_predictor import predict_match_winner

# Ladder positions in 2023 (1 = highest / best)
LADDER_2023 = {
    "Collingwood": 1,
    "Brisbane Lions": 2,
    "Carlton": 3,
    "GWS Giants": 4,
    "Melbourne": 5,
    "Adelaide": 6,
    "Sydney Swans": 7,
    "Geelong": 8,
    "Hawthorn": 16,
    "Richmond": 14,
    "Essendon": 11,
    "Port Adelaide": 9,
}

# Ground-truth results (from 2023 finals series)
MATCHUPS = [
    ("Collingwood",  "Brisbane Lions",  "Collingwood"),   # Grand Final
    ("Carlton",      "Melbourne",       "Carlton"),        # Elimination Final
    ("Brisbane Lions","Geelong",        "Brisbane Lions"), # Qualifying Final
    ("Collingwood",  "GWS Giants",      "Collingwood"),    # Semi Final
    ("Carlton",      "GWS Giants",      "Carlton"),        # Semi Final
    ("Sydney Swans", "GWS Giants",      "GWS Giants"),     # First Final
]

def naive_predict(home: str, away: str) -> str:
    """Ladder-position naive model: lower rank number wins."""
    home_pos = LADDER_2023.get(home, 18)
    away_pos = LADDER_2023.get(away, 18)
    return home if home_pos <= away_pos else away

def ml_predict(home: str, away: str) -> str:
    """Our mock ML model."""
    result = predict_match_winner(home, away)
    return result["predicted_winner"]

def run_benchmark():
    print("\n" + "="*72)
    print("  AFL Match Prediction: Benchmark Comparison")
    print("  Naive (Ladder Rank) vs. Mock ML Model")
    print("="*72)
    print(f"{'Matchup':<40} {'Actual':<18} {'Naive':<12} {'ML Model':<12}")
    print("-"*72)

    naive_correct = 0
    ml_correct = 0

    for home, away, actual in MATCHUPS:
        naive = naive_predict(home, away)
        ml = ml_predict(home, away)
        n_correct = "PASS" if naive == actual else "FAIL"
        m_correct = "PASS" if ml == actual else "FAIL"
        if naive == actual:
            naive_correct += 1
        if ml == actual:
            ml_correct += 1
        matchup = f"{home} vs {away}"
        print(f"  {matchup:<38} {actual:<18} {naive:<20} {n_correct:<6} {ml:<20} {m_correct}")


    total = len(MATCHUPS)
    print("-"*72)
    print(f"\n  Naive Model Accuracy:   {naive_correct}/{total} = {naive_correct/total*100:.1f}%")
    print(f"  Mock ML Model Accuracy: {ml_correct}/{total} = {ml_correct/total*100:.1f}%")
    print()
    print("  Interpretation:")
    print("  - Naive model is a strong baseline since ladder rank heavily")
    print("    predicts finals results in AFL.")
    print("  - A production ML model would need to beat this baseline")
    print("    using form, injury, and home-ground features.")
    print("  - Our mock model uses team name length as a proxy; a real")
    print("    XGBoost/LightGBM model trained on historical stats would")
    print("    target 65%+ accuracy to be meaningfully better than naive.")
    print("="*72 + "\n")

if __name__ == "__main__":
    run_benchmark()
