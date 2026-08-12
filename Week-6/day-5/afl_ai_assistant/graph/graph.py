from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import router_node, tool_node, generate_node
from memory.conversation_memory import get_memory_saver

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("tool_executor", tool_node)
    workflow.add_node("generator", generate_node)
    
    workflow.set_entry_point("router")
    
    def route_after_router(state: AgentState):
        intent = state.get("intent")
        if intent in ["off_topic", "blocked"]:
            return "generator"
        return "tool_executor"
        
    def route_after_tool(state: AgentState):
        if state.get("final_response"):
            return END
        return "generator"
        
    workflow.add_conditional_edges("router", route_after_router)
    workflow.add_conditional_edges("tool_executor", route_after_tool)
    workflow.add_edge("generator", END)
    
    checkpointer = get_memory_saver()
    return workflow.compile(checkpointer=checkpointer)

app_graph = build_graph()
