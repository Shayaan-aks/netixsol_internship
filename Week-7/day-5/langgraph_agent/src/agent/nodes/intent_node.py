"""
Intent Detection Node — Classifies user message intent and sentiment.

Uses a structured LLM output to extract:
  - intent: one of the defined real-estate intents
  - confidence: 0.0–1.0
  - sentiment: user's emotional tone

Falls back to 'greeting' intent on any LLM failure so the graph
never crashes on the first turn.
"""
import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.agent.state import AgentState
from src.tools.calendar_tools import check_calendar_availability, book_appointment_tool
from src.tools.rag_tools import search_property_knowledge
from src.tools.crm_tools import lookup_customer_profile
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── LLM Setup (xAI Grok) ───────────────────────────────────────────────────
_llm = ChatOpenAI(
    base_url="https://api.x.ai/v1",
    api_key=os.environ.get("XAI_API_KEY", ""),
    model=os.environ.get("LLM_MODEL", "grok-3-mini"),
    temperature=0.1,
    timeout=30,
    max_retries=1,  # Fail fast on auth errors
)

# ── Schema ────────────────────────────────────────────────────────────────────
VALID_INTENTS = [
    "greeting",
    "book_appointment",
    "cancel_appointment",
    "reschedule_appointment",
    "property_search",
    "seller_inquiry",
    "investor_inquiry",
    "rental_inquiry",
    "complaint",
    "clarification",
    "unknown",
]

VALID_SENTIMENTS = ["positive", "neutral", "frustrated", "angry", "confused"]


class IntentExtraction(BaseModel):
    intent: str = Field(
        description=(
            "Classify the user's intent. Must be exactly one of: "
            "'greeting', 'book_appointment', 'cancel_appointment', 'reschedule_appointment', "
            "'property_search', 'seller_inquiry', 'investor_inquiry', "
            "'rental_inquiry', 'complaint', 'clarification', 'unknown'"
        )
    )
    confidence: float = Field(
        description="Confidence score from 0.0 to 1.0",
        ge=0.0,
        le=1.0,
    )
    sentiment: str = Field(
        description=(
            "User's emotional tone. Must be exactly one of: "
            "'positive', 'neutral', 'frustrated', 'angry', 'confused'"
        )
    )


# ── Node Function ─────────────────────────────────────────────────────────────
def detect_intent(state: AgentState) -> AgentState:
    """
    Analyzes the latest message and determines intent + sentiment.
    
    Gracefully handles:
      - Empty state (first call with no messages)
      - Empty/silent messages (voice dropouts)
      - LLM failures (network error, quota exceeded)
    """
    messages = state.get("messages", [])

    # No messages at all — return a safe greeting state
    if not messages:
        return {
            "intent": "greeting",
            "confidence_score": 1.0,
            "sentiment": "neutral",
            "current_node": "intent_node",
            "tool_outputs": [],
            "errors": [],
        }

    latest_msg = messages[-1].content if messages else ""

    # Handle empty / silent callers gracefully (common in voice)
    if not latest_msg or not latest_msg.strip() or latest_msg.strip() in ["?", ".", "...", " "]:
        return {
            "intent": "greeting",
            "confidence_score": 0.9,
            "sentiment": "neutral",
            "current_node": "intent_node",
            "tool_outputs": [],
            "errors": [],
        }

    # ── LLM Structured Classification ─────────────────────────────────────────
    try:
        structured_llm = _llm.with_structured_output(IntentExtraction)
        prompt = (
            "You are an intent classifier for a Pakistani Real Estate Voice Agent called Zara. "
            "The agent handles: property buying, selling, renting, appointments, investor inquiries. "
            "Users often speak in Urdulish (mix of Urdu and English). "
            f"\nClassify the intent and sentiment of this user message: '{latest_msg}'"
        )
        result = structured_llm.invoke(prompt)

        # Validate the returned intent is in our schema
        intent = result.intent if result.intent in VALID_INTENTS else "unknown"
        sentiment = result.sentiment if result.sentiment in VALID_SENTIMENTS else "neutral"

        return {
            "intent": intent,
            "confidence_score": result.confidence,
            "sentiment": sentiment,
            "current_node": "intent_node",
            "tool_outputs": [],
            "errors": [],
        }

    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        return {
            "intent": "greeting",
            "confidence_score": 0.5,
            "sentiment": "neutral",
            "current_node": "intent_node",
            "tool_outputs": [],
            "errors": [f"intent_node_error: {str(e)}"],
        }
