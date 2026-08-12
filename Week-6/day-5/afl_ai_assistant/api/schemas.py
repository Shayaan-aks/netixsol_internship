from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's input query.")
    thread_id: str = Field(..., description="A unique identifier for the conversation thread.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The assistant's final response.")
    intent: Optional[str] = Field(None, description="The classified intent.")
    latency: Optional[float] = Field(None, description="Processing time in seconds.")
    token_usage: Optional[int] = Field(0, description="Estimated token count for this request.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional debug info.")
