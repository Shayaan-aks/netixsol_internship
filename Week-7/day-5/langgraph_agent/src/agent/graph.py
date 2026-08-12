from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.agent.state import AgentState
from src.agent.nodes.intent_node import detect_intent
from src.agent.nodes.generator_node import generate_response
from src.agent.routing import route_based_on_intent
from src.tools.calendar_tools import check_calendar_availability, book_appointment_tool
from src.tools.rag_tools import search_property_knowledge
from src.tools.crm_tools import lookup_customer_profile
from langgraph.checkpoint.memory import MemorySaver

# 1. Initialize Tools
tools = [
    check_calendar_availability, 
    book_appointment_tool, 
    search_property_knowledge, 
    lookup_customer_profile
]
tool_node = ToolNode(tools)

# 2. Define Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("intent_detector", detect_intent)
workflow.add_node("tools", tool_node)
workflow.add_node("generator", generate_response)

# 3. Add Edges
workflow.add_edge(START, "intent_detector")

# Conditional Edge from Intent Detector
workflow.add_conditional_edges(
    "intent_detector",
    route_based_on_intent,
    {
        "tools": "tools",
        "generator": "generator"
    }
)

# After tools finish, always generate a response to summarize
workflow.add_edge("tools", "generator")
workflow.add_edge("generator", END)

# 4. Compile with Checkpointer (MemorySaver) for state persistence
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Expose 'app' for tests and deployment
