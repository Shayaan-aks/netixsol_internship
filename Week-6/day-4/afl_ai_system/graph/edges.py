from graph.state import AgentState

def route_from_router(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "structured_retrieval":
        return "structured_retrieval_node"
    elif intent == "semantic_retrieval":
        return "semantic_retrieval_node"
    elif intent in ["match_prediction", "player_prediction"]:
        return "prediction_node"
    elif intent == "off_topic" or intent == "unsupported":
        return "off_topic_node"
    elif intent == "clarification_needed":
        return "clarification_node"
    else:
        return "factual_chat_node"
        
def route_from_validation(state: AgentState) -> str:
    return "response_formatter_node"
