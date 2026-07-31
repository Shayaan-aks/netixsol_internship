from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Optional[str]
    router_confidence: Optional[float]
    router_reasoning: Optional[str]
    selected_node: Optional[str]
    tool_requested: Optional[str]
    tool_output: Optional[str]
    validation_status: Optional[str] # 'PASS', 'FAIL', 'CLARIFY', 'BLOCKED'
    clarification_request: Optional[str]
    final_response: Optional[str]
    metadata: Optional[Dict[str, Any]]
    # Abuse handling counters
    off_topic_count: int
    injection_attempts: int
