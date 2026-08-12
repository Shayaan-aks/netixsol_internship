"""
Pytest configuration and shared fixtures for production readiness test suite.
Mocks LLM calls to avoid API quota consumption during CI/CD.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# ── Python Path Setup ─────────────────────────────────────────────────────────
# Ensure Day 5 agent is on path for integration tests
DAY5_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../day-5/langgraph_agent")
)
if DAY5_PATH not in sys.path:
    sys.path.insert(0, DAY5_PATH)

# Set a fake API key if not provided (for unit tests that mock LLM calls)
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "test_fake_key_for_unit_tests"


# ── Shared Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def mock_safe_security_result():
    """Returns a mock SecurityScanResult indicating a safe message."""
    result = MagicMock()
    result.is_safe = True
    result.reason = "Message is about real estate — safe."
    result.threat_category = "none"
    return result


@pytest.fixture
def mock_unsafe_security_result():
    """Returns a mock SecurityScanResult indicating a prompt injection attempt."""
    result = MagicMock()
    result.is_safe = False
    result.reason = "Matched threat pattern [prompt_injection]: 'ignore all previous instructions'"
    result.threat_category = "prompt_injection"
    return result


@pytest.fixture
def mock_prompt_guard(mock_safe_security_result):
    """Returns a PromptGuard instance with LLM mocked to return safe result."""
    with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_safe_security_result
        mock_llm_class.return_value = mock_llm

        from src.security.prompt_guard import PromptGuard
        guard = PromptGuard()
        guard.security_llm = mock_llm.with_structured_output.return_value
        yield guard


@pytest.fixture
def sample_agent_state():
    """Returns a minimal valid AgentState dict for routing tests."""
    from langchain_core.messages import HumanMessage
    return {
        "messages": [HumanMessage(content="Hello, I want to buy a house.")],
        "intent": "greeting",
        "confidence_score": 0.95,
        "sentiment": "positive",
        "customer_profile": {},
        "appointment_state": {},
        "current_node": "intent_node",
        "next_node": "",
        "tool_outputs": [],
        "errors": [],
    }
