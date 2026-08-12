from typing import Annotated, Sequence, TypedDict, List, Optional
from langchain_core.messages import BaseMessage
import operator


class CustomerProfile(TypedDict, total=False):
    customer_id: int
    name: str
    phone: str
    email: str
    preferred_area: str
    budget: str
    lead_score: int


class AppointmentState(TypedDict, total=False):
    booking_requested: bool
    appointment_confirmed: bool
    meeting_date: str
    meeting_time: str
    assigned_employee: str
    calendar_event_id: str


class AgentState(TypedDict, total=False):
    """
    The central state object for the LangGraph agent.
    
    All fields are optional (total=False) so the graph can be invoked
    with just {"messages": [...]} without crashing on missing keys.
    """

    # ── Core conversational state ─────────────────────────────────────────────
    # Required: must be seeded before invoking
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # ── Extracted metadata ────────────────────────────────────────────────────
    intent: str              # e.g. 'greeting', 'property_search', 'book_appointment'
    confidence_score: float  # 0.0 – 1.0
    sentiment: str           # 'positive' | 'neutral' | 'frustrated' | 'angry' | 'confused'

    # ── Domain-specific memory ────────────────────────────────────────────────
    customer_profile: CustomerProfile
    appointment_state: AppointmentState

    # ── Graph execution trace ─────────────────────────────────────────────────
    current_node: str
    next_node: str

    # Accumulator lists — safe to reduce over multiple turns
    tool_outputs: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
