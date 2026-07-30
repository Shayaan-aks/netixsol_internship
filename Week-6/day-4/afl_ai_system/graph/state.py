from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Optional[str]
    router_confidence: Optional[float]
    router_reasoning: Optional[str]
    selected_node: Optional[str]
    tool_requested: Optional[str]
    tool_output: Optional[str]
    prediction_output: Optional[dict]
    validation_status: Optional[str] # 'PASS', 'FAIL', 'CLARIFY'
    clarification_request: Optional[str]
    final_response: Optional[str]
    errors: Optional[list]
    metadata: Optional[dict]
