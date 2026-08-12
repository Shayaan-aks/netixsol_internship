"""
Graph Routing Logic — Determines which node executes after intent detection.

Routes:
  - Intents that need tool data (property_search, booking) → tools node
  - All conversational intents → generator node directly
  - Safety checks run BEFORE routing to tools (e.g., require phone for booking)
"""
from src.agent.state import AgentState
from src.validation.rules import BusinessRules


# Intents that require tool calls (need external data before generating response)
TOOL_INTENTS = {
    "property_search",
    "investor_inquiry",
    "rental_inquiry",
    "seller_inquiry",
}

# Intents handled purely by the generator (no tools needed)
GENERATOR_INTENTS = {
    "greeting",
    "complaint",
    "clarification",
    "unknown",
    "cancel_appointment",
    "reschedule_appointment",
}


def route_based_on_intent(state: AgentState) -> str:
    """
    Conditional edge: routes the graph based on detected intent.
    
    Returns:
        "tools"     — if tools should be called to fetch data
        "generator" — if we should go straight to response generation
    """
    intent = state.get("intent", "greeting")

    # ── Appointment Booking ───────────────────────────────────────────────────
    if intent == "book_appointment":
        profile = state.get("customer_profile", {})
        if not profile.get("phone"):
            # Cannot book without phone — generator will ask for it
            return "generator"
        return "tools"

    # ── Property Search ───────────────────────────────────────────────────────
    if intent == "property_search":
        if not BusinessRules.validate_budget_provided(state):
            # Cannot search meaningfully without a budget — ask first
            return "generator"
        return "tools"

    # ── Investor / Rental / Seller — always call tools for data ───────────────
    if intent in ("investor_inquiry", "rental_inquiry"):
        if not BusinessRules.validate_budget_provided(state):
            return "generator"
        return "tools"

    if intent == "seller_inquiry":
        # Seller inquiries always go to generator to gather info conversationally
        return "generator"

    # ── Conversational intents — skip tools, go straight to generator ─────────
    if intent in GENERATOR_INTENTS:
        return "generator"

    # ── Safe default fallback — never crash ───────────────────────────────────
    return "generator"
