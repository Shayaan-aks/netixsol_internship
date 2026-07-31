def check_ambiguity(query: str) -> bool:
    """Check if the query is ambiguous and needs clarification."""
    ambiguous_terms = ["he", "she", "it", "they", "that team"]
    words = query.lower().split()
    return any(term in words for term in ambiguous_terms) and len(words) < 5
