import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from prompts.system_prompt import SYSTEM_PROMPT
from tools.team_tools import get_team_record, get_match_result
from tools.player_tools import get_player_stats
from tools.article_tools import retrieve_match_article
from memory.conversation_memory import AgentState
from config import LLM_MODEL, TEMPERATURE, OPENAI_API_KEY

# Fail gracefully later if no API key
api_key = OPENAI_API_KEY if OPENAI_API_KEY else "dummy_key"

llm = ChatOpenAI(model=LLM_MODEL, temperature=TEMPERATURE, api_key=api_key)

# Register tools
tools = [
    get_team_record,
    get_match_result,
    get_player_stats,
    retrieve_match_article
]

llm_with_tools = llm.bind_tools(tools)

def assistant(state: AgentState):
    messages = state["messages"]
    # Ensure system prompt is the first message
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Build the LangGraph
builder = StateGraph(AgentState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph with memory checkout in app.py
chat_agent = builder.compile()
