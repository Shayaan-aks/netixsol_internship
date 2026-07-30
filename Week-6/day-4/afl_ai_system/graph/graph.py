from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from graph.nodes import (
    router_node,
    structured_retrieval_node,
    semantic_retrieval_node,
    prediction_node,
    factual_chat_node,
    off_topic_node,
    clarification_node,
    validation_node,
    response_formatter_node
)
from graph.edges import route_from_router, route_from_validation

def compile_graph():
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("router", router_node)
    builder.add_node("structured_retrieval_node", structured_retrieval_node)
    builder.add_node("semantic_retrieval_node", semantic_retrieval_node)
    builder.add_node("prediction_node", prediction_node)
    builder.add_node("factual_chat_node", factual_chat_node)
    builder.add_node("off_topic_node", off_topic_node)
    builder.add_node("clarification_node", clarification_node)
    builder.add_node("validation_node", validation_node)
    builder.add_node("response_formatter_node", response_formatter_node)
    
    # Define edges
    builder.add_edge(START, "router")
    
    builder.add_conditional_edges(
        "router",
        route_from_router,
        {
            "structured_retrieval_node": "structured_retrieval_node",
            "semantic_retrieval_node": "semantic_retrieval_node",
            "prediction_node": "prediction_node",
            "factual_chat_node": "factual_chat_node",
            "off_topic_node": "off_topic_node",
            "clarification_node": "clarification_node"
        }
    )
    
    # Direct routing to END
    builder.add_edge("factual_chat_node", END)
    builder.add_edge("off_topic_node", END)
    builder.add_edge("clarification_node", END)
    
    # Tools route to validation
    builder.add_edge("structured_retrieval_node", "validation_node")
    builder.add_edge("semantic_retrieval_node", "validation_node")
    builder.add_edge("prediction_node", "validation_node")
    
    # Validation routes to formatter
    builder.add_conditional_edges("validation_node", route_from_validation)
    
    # Formatter to END
    builder.add_edge("response_formatter_node", END)
    
    return builder

graph_builder = compile_graph()
