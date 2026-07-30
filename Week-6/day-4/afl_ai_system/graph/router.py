import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from prompts.router_prompt import ROUTER_PROMPT
from config import OPENAI_API_KEY, LLM_MODEL

class RouterOutput(BaseModel):
    intent: str = Field(description="The classified intent of the user query.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    reasoning: str = Field(description="Reasoning for the classification.")

def get_router():
    api_key = OPENAI_API_KEY if OPENAI_API_KEY else "dummy"
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0, api_key=api_key)
    structured_llm = llm.with_structured_output(RouterOutput)
    return structured_llm

def route_query(query: str, history: list = None) -> RouterOutput:
    router_llm = get_router()
    history_str = ""
    if history:
        history_str = "\nConversation History:\n" + "\n".join([f"{msg.type}: {msg.content}" for msg in history[-4:]])
    
    prompt = ROUTER_PROMPT + history_str + f"\n\nUser Query: {query}"
    
    try:
        result = router_llm.invoke(prompt)
        return result
    except Exception as e:
        # Fallback to factual_chat if router fails
        return RouterOutput(intent="factual_chat", confidence=0.0, reasoning=f"Router error: {str(e)}")
