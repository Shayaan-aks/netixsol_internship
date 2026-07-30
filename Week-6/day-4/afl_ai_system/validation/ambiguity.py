def check_ambiguity(query: str) -> str:
    # A simple check for unresolved pronouns without context or highly ambiguous requests
    if query.lower() in ["who will win?", "who will score?"]:
        return "Could you please specify which teams or players you are referring to?"
    return None
