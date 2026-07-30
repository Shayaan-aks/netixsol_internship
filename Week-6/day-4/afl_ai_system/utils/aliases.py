import difflib

TEAM_ALIASES = {
    "pies": "Collingwood",
    "collingwood": "Collingwood",
    "cats": "Geelong",
    "geelong": "Geelong",
    "blues": "Carlton",
    "carlton": "Carlton",
    "bombers": "Essendon",
    "essendon": "Essendon",
    "lions": "Brisbane Lions",
    "brisbane": "Brisbane Lions",
}

def resolve_team_alias(query_team: str) -> str:
    """
    Resolve common team aliases, abbreviations, and fuzzy matches.
    Never guess if confidence is extremely low; return None to trigger clarification.
    """
    q_lower = query_team.lower().strip()
    if q_lower in TEAM_ALIASES:
        return TEAM_ALIASES[q_lower]
        
    # Fuzzy match
    matches = difflib.get_close_matches(q_lower, TEAM_ALIASES.keys(), n=1, cutoff=0.7)
    if matches:
        return TEAM_ALIASES[matches[0]]
        
    return None

def resolve_date_alias(temporal_phrase: str) -> str:
    """
    Mock temporal phrase resolution.
    Maps 'this week', 'next round' etc. to concrete fixtures.
    """
    phrase = temporal_phrase.lower().strip()
    if phrase in ["this week", "next round", "upcoming fixture", "tomorrow", "next game"]:
        return "Round 1, 2024" # Mock resolution
    return None
