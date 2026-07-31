import time
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse
from graph.graph import app_graph
from memory.conversation_memory import get_memory_saver
from langchain_core.messages import HumanMessage
from monitoring.logging import log_interaction

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    start_time = time.time()
    try:
        config = {"configurable": {"thread_id": req.thread_id}}
        
        # Get current state to fetch abuse counters
        current_state = app_graph.get_state(config)
        state_values = current_state.values if current_state else {}
        
        # Build initial input
        inputs = {
            "messages": [HumanMessage(content=req.query)],
            "off_topic_count": state_values.get("off_topic_count", 0),
            "injection_attempts": state_values.get("injection_attempts", 0)
        }
        
        # Stream or invoke through LangGraph
        final_state = None
        for output in app_graph.stream(inputs, config=config):
            for key, value in output.items():
                final_state = value

        if not final_state:
            raise HTTPException(status_code=500, detail="No response from agent graph.")

        intent = final_state.get("intent", "unknown")
        response_text = final_state.get("final_response", "I'm sorry, I could not generate a response.")
        
        latency = time.time() - start_time
        
        # Log interaction
        log_interaction(
            query=req.query,
            intent=intent,
            response=response_text,
            latency=latency,
            metadata={"thread_id": req.thread_id}
        )

        return ChatResponse(
            response=response_text,
            intent=intent,
            latency=latency,
            metadata={"tool_requested": final_state.get("tool_requested")}
        )

    except Exception as e:
        latency = time.time() - start_time
        log_interaction(req.query, "error", str(e), latency)
        raise HTTPException(status_code=500, detail=str(e))
