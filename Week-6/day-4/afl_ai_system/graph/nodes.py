from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from graph.state import AgentState
from graph.router import route_query
from config import LLM_MODEL, GOOGLE_API_KEY
from prompts.system_prompt import SYSTEM_PROMPT
from validation.validator import validate_output
from validation.ambiguity import check_ambiguity
from utils.helpers import log_trace
from tools.retrieval_tools import get_structured_stat, retrieve_news_article
from tools.prediction_tools import predict_match, predict_player

# Fail gracefully
api_key = GOOGLE_API_KEY if GOOGLE_API_KEY else "dummy_key"
llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0, api_key=api_key)

def router_node(state: AgentState):
    messages = state.get("messages", [])
    query = messages[-1].content
    
    # 1. Check for ambiguity first
    clarification = check_ambiguity(query)
    if clarification:
        state["intent"] = "clarification_needed"
        state["clarification_request"] = clarification
        log_trace(state)
        return state

    # 2. Route query
    router_out = route_query(query, messages[:-1])
    state["intent"] = router_out.intent
    state["router_confidence"] = router_out.confidence
    state["router_reasoning"] = router_out.reasoning
    
    log_trace(state)
    return state

def structured_retrieval_node(state: AgentState):
    state["selected_node"] = "structured_retrieval_node"
    
    prompt = f"Extract the entity (team or player) and the stat type (wins, losses, disposals, goals, score) from this query: {state['messages'][-1].content}. Return format: Entity,StatType"
    try:
        extraction = llm.invoke([HumanMessage(content=prompt)]).content
        parts = extraction.split(',')
        if len(parts) >= 2:
            entity, stat = parts[0].strip(), parts[1].strip()
            state["tool_requested"] = "get_structured_stat"
            state["tool_output"] = get_structured_stat.invoke({"entity_name": entity, "stat_type": stat})
        else:
            state["tool_output"] = "Error extracting entities for structured search."
    except Exception as e:
        state["tool_output"] = f"Error: {e}"
        
    log_trace(state)
    return state

def semantic_retrieval_node(state: AgentState):
    state["selected_node"] = "semantic_retrieval_node"
    state["tool_requested"] = "retrieve_news_article"
    state["tool_output"] = retrieve_news_article.invoke({"query": state["messages"][-1].content})
    log_trace(state)
    return state

def prediction_node(state: AgentState):
    state["selected_node"] = "prediction_node"
    intent = state.get("intent")
    query = state["messages"][-1].content
    
    try:
        if intent == "match_prediction":
             prompt = f"Extract home_team and away_team from: {query}. Return format: Home,Away"
             extraction = llm.invoke([HumanMessage(content=prompt)]).content
             parts = extraction.split(',')
             if len(parts) >= 2:
                  state["tool_requested"] = "predict_match"
                  state["tool_output"] = predict_match.invoke({"home_team": parts[0].strip(), "away_team": parts[1].strip()})
             else:
                  state["tool_output"] = "Failed to extract teams."
        elif intent == "player_prediction":
             prompt = f"Extract the team from: {query}. Return format: Team"
             team = llm.invoke([HumanMessage(content=prompt)]).content.strip()
             state["tool_requested"] = "predict_player"
             state["tool_output"] = predict_player.invoke({"team": team})
    except Exception as e:
         state["tool_output"] = f"Prediction error: {e}"
         
    log_trace(state)
    return state

def factual_chat_node(state: AgentState):
    state["selected_node"] = "factual_chat_node"
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    state["final_response"] = response.content
    log_trace(state)
    return state

def off_topic_node(state: AgentState):
    state["selected_node"] = "off_topic_node"
    state["final_response"] = "I'm designed specifically for AFL questions, so I can't help with that topic. Feel free to ask me about AFL teams, fixtures, or stats!"
    log_trace(state)
    return state
    
def clarification_node(state: AgentState):
    state["selected_node"] = "clarification_node"
    state["final_response"] = state.get("clarification_request", "Could you please clarify your request?")
    log_trace(state)
    return state
    
def validation_node(state: AgentState):
    out = state.get("tool_output", "")
    status = validate_output(out)
    state["validation_status"] = status
    log_trace(state)
    return state

def response_formatter_node(state: AgentState):
    if state.get("validation_status") == "FAIL":
        state["final_response"] = f"I couldn't find the requested information in my AFL dataset. Details: {state.get('tool_output')}"
        log_trace(state)
        return state
        
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"] + [HumanMessage(content=f"Context from tools:\n{state.get('tool_output')}\nFormulate a natural, factual, concise response.")]
    response = llm.invoke(messages)
    state["final_response"] = response.content
    log_trace(state)
    return state
