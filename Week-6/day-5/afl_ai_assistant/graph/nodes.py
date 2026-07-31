from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState
from graph.router import route_query
from validation.abuse_handler import handle_abuse
from config import LLM_MODEL, GOOGLE_API_KEY
from tools.retrieval_tools import structured_retrieval_tool
from tools.prediction_tools import predict_match_tool, predict_player_tool

api_key = GOOGLE_API_KEY if GOOGLE_API_KEY else "dummy"
llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0, api_key=api_key)

tools = [structured_retrieval_tool, predict_match_tool, predict_player_tool]
llm_with_tools = llm.bind_tools(tools)

def router_node(state: AgentState):
    messages = state["messages"]
    if not messages:
        return state
    query = messages[-1].content
    
    abuse_check = handle_abuse(state)
    if abuse_check["status"] == "BLOCKED":
        return {"intent": "blocked", "final_response": abuse_check["message"]}
        
    router_out = route_query(query)
    
    updates = {
        "intent": router_out.intent,
        "router_confidence": router_out.confidence,
        "router_reasoning": router_out.reasoning,
    }
    
    if router_out.intent == "off_topic":
        updates["off_topic_count"] = state.get("off_topic_count", 0) + 1
        updates["final_response"] = "I can only answer questions related to the Australian Football League (AFL). Please ask an AFL-related question."
    elif router_out.intent == "injection_attempt":
        updates["injection_attempts"] = state.get("injection_attempts", 0) + 1
        updates["final_response"] = "Security alert: Prompt injection attempt detected. This action has been logged."
        updates["intent"] = "blocked"
        
    return updates

def tool_node(state: AgentState):
    messages = state["messages"]
    intent = state.get("intent")
    
    if intent in ["off_topic", "blocked"]:
        return state
        
    system_prompt = "You are an expert AFL AI assistant. Only answer questions about the Australian Football League."
    
    # Use the tool-bound LLM to decide on tool usage
    response = llm_with_tools.invoke([SystemMessage(content=system_prompt)] + messages)
    
    # If the LLM decided to call a tool, we execute it (simplification for this node, ideally we use ToolNode)
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        tool_result = ""
        try:
            if tool_name == "structured_retrieval_tool":
                tool_result = structured_retrieval_tool.invoke(tool_args)
            elif tool_name == "predict_match_tool":
                tool_result = predict_match_tool.invoke(tool_args)
            elif tool_name == "predict_player_tool":
                tool_result = predict_player_tool.invoke(tool_args)
        except Exception as e:
            tool_result = f"Error executing tool {tool_name}: {e}"
            
        return {"tool_output": tool_result, "tool_requested": tool_name}
    else:
        # LLM answered directly
        return {"final_response": response.content}

def generate_node(state: AgentState):
    if state.get("final_response"):
        return state
        
    messages = state["messages"]
    tool_output = state.get("tool_output", "")
    
    system_prompt = f"""You are an expert AFL AI assistant. 
    Use the following tool output to answer the user's question, if provided.
    Tool output: {tool_output}
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return {"final_response": response.content}
