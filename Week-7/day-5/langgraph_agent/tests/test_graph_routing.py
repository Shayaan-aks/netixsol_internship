import pytest
from langchain_core.messages import HumanMessage
from src.agent.routing import route_based_on_intent
from src.agent.state import AgentState

def test_greeting_routes_to_generator():
    """If the intent is a greeting, the agent should bypass tools and go straight to response generator."""
    state = AgentState(intent="greeting")
    next_node = route_based_on_intent(state)
    assert next_node == "generator"

def test_booking_without_phone_routes_to_generator():
    """If user wants to book, but we don't have their phone, we should NOT call the booking tool. We must ask."""
    state = AgentState(
        intent="book_appointment",
        customer_profile={} # Phone is missing
    )
    next_node = route_based_on_intent(state)
    assert next_node == "generator"

def test_booking_with_phone_routes_to_tools():
    """If user wants to book AND we have their phone, proceed to tool execution."""
    state = AgentState(
        intent="book_appointment",
        customer_profile={"phone": "03001234567"}
    )
    next_node = route_based_on_intent(state)
    assert next_node == "tools"

def test_search_without_budget_routes_to_generator():
    """Business Rule: Cannot search property without a budget."""
    state = AgentState(
        intent="property_search",
        customer_profile={} # Budget missing
    )
    next_node = route_based_on_intent(state)
    assert next_node == "generator"
