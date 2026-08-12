import time
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from graph.graph import app_graph
from memory.conversation_memory import get_memory_saver
from langchain_core.messages import HumanMessage
from monitoring.logging import log_interaction, log_abuse_event

router = APIRouter()

def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token."""
    return max(1, len(text) // 4)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    start_time = time.time()
    try:
        config = {"configurable": {"thread_id": req.thread_id}}

        # Fetch previous state (for abuse counters)
        current_state = app_graph.get_state(config)
        state_values = current_state.values if current_state else {}

        inputs = {
            "messages": [HumanMessage(content=req.query)],
            "off_topic_count": state_values.get("off_topic_count", 0),
            "injection_attempts": state_values.get("injection_attempts", 0),
        }

        # Stream through LangGraph to execute it
        for output in app_graph.stream(inputs, config=config):
            pass  # Wait for execution to finish

        # Safely fetch the full accumulated state
        full_state = app_graph.get_state(config).values
        if not full_state:
            raise HTTPException(status_code=500, detail="No state returned from agent graph.")

        intent = full_state.get("intent", "unknown")
        
        # If final_response is empty or None, fallback to the default text
        response_text = full_state.get("final_response")
        if not response_text:
            response_text = "I'm sorry, I could not generate a response."

        latency = time.time() - start_time
        token_usage = _estimate_tokens(req.query) + _estimate_tokens(response_text)

        # Log security events separately
        if intent == "blocked":
            log_abuse_event(
                query=req.query,
                event_type="injection_attempt",
                session_id=req.thread_id,
            )
        elif intent == "off_topic":
            log_abuse_event(
                query=req.query,
                event_type="off_topic",
                session_id=req.thread_id,
            )

        log_interaction(
            query=req.query,
            intent=intent,
            response=response_text,
            latency=latency,
            metadata={"thread_id": req.thread_id, "tool": full_state.get("tool_requested")},
            token_usage=token_usage,
        )

        return ChatResponse(
            response=response_text,
            intent=intent,
            latency=round(latency, 4),
            token_usage=token_usage,
            metadata={
                "tool_requested": full_state.get("tool_requested"),
                "router_confidence": full_state.get("router_confidence"),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        latency = time.time() - start_time
        log_interaction(req.query, "error", str(e), latency)
        raise HTTPException(status_code=500, detail=str(e))
