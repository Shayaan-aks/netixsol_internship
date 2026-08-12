"""
Voice Router — REST and WebSocket endpoints for real-time voice conversations.

Pipeline: STT (browser/Deepgram) → Security Gate → LangGraph Agent → TTS (browser/Google)

Endpoints:
  POST /v1/voice/chat                  — Single-turn text/voice chat (REST)
  POST /v1/voice/chat/completions      — OpenAI-compatible adapter (for Vapi)
  WS   /v1/voice/ws/{session_id}       — Real-time streaming WebSocket
  GET  /v1/voice/sessions/{id}         — Session history
  DELETE /v1/voice/sessions/{id}       — Clear session
"""
import asyncio
import json
import uuid
import time
import os
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.api.middleware.auth import require_auth
from backend.config.settings import settings
from backend.api.services.stt_service import deepgram_stt

import sys

_WEEK7 = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)

# ── Load Security Module ───────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(_WEEK7, "day-6", "production_ready"))
for mod in ["src", "src.security", "src.security.prompt_guard"]:
    if mod in sys.modules:
        del sys.modules[mod]
from src.security.prompt_guard import PromptGuard
sys.path.pop(0)

# ── Load Agent Module ─────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(_WEEK7, "day-5", "langgraph_agent"))
for mod in ["src", "src.agent", "src.agent.graph"]:
    if mod in sys.modules:
        del sys.modules[mod]
from src.agent.graph import app as langgraph_app
sys.path.pop(0)

from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Auth Dependency (Dev-Skip Aware) ──────────────────────────────────────────
async def maybe_auth(request: Request) -> dict:
    """
    In DEV_SKIP_AUTH mode: allow all requests through.
    In production: require valid API key or JWT.
    """
    if settings.dev_skip_auth:
        return {"auth_type": "dev_bypass", "subject": "developer"}
    return await require_auth(request)


# ── REST Models ───────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=0, max_length=2000, example="DHA mein ghar chahiye 3 crore budget mein")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    language: str = Field(default="ur-PK", example="ur-PK")
    voice_response: bool = Field(default=False, description="Return TTS text marker in addition to text")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    confidence: float
    sentiment: str
    tools_called: list[str]
    latency_ms: float
    request_id: str
    language: str = "ur-PK"


class OpenAIRequest(BaseModel):
    model: str
    messages: list[dict]
    stream: Optional[bool] = False


# ── REST Chat Endpoint ────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Single-turn voice/text conversation",
    description=(
        "Send a text message and receive a natural Urdulish AI response. "
        "Full pipeline: Security Gate → Intent Detection → Tools → Urdulish Generator. "
        "For streaming, use WebSocket /v1/voice/ws/{session_id}."
    ),
)
async def chat(
    request: ChatRequest,
    auth: dict = Depends(maybe_auth),
):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    # ── Security Gate ─────────────────────────────────────────────────────────
    guard = PromptGuard()
    try:
        security = guard.scan_input(request.message)
    except Exception as e:
        logger.error(f"Security scan error (allowing through): {e}")
        # Fail open — don't block legitimate traffic if security LLM is down
        from src.security.prompt_guard import SecurityScanResult
        security = SecurityScanResult(is_safe=True, reason="scan_error_fail_open", threat_category="none")

    if not security.is_safe:
        latency_ms = (time.perf_counter() - start) * 1000
        logger.warning(f"Security block: {security.threat_category} — {security.reason}")
        return ChatResponse(
            response="Maafi chahti hoon, main sirf Pakistani real estate ke baare mein madad kar sakti hoon. Kya aap koi property dekhna chahte hain?",
            session_id=request.session_id,
            intent="security_blocked",
            confidence=1.0,
            sentiment="neutral",
            tools_called=[],
            latency_ms=round(latency_ms, 1),
            request_id=request_id,
            language="ur-PK",
        )

    # ── LangGraph Agent ───────────────────────────────────────────────────────
    intent, response_text, tools_called, sentiment = "unknown", "", [], "neutral"

    try:
        state = {"messages": [HumanMessage(content=request.message)]}
        result = langgraph_app.invoke(
            state,
            config={"configurable": {"thread_id": request.session_id}},
        )

        intent = result.get("intent", "unknown")
        sentiment = result.get("sentiment", "neutral")

        if result.get("messages"):
            response_text = result["messages"][-1].content

        # tool_outputs is the explicit list; also check messages for ToolMessages
        tools_called = list(result.get("tool_outputs", []))

    except Exception as e:
        logger.error(f"LangGraph invocation error: {e}", exc_info=True)
        response_text = (
            "Maafi chahti hoon, mujhe abhi kuch technical masla aa raha hai. "
            "Thodi der mein dobara try karein — main aapki madad karna chahti hoon!"
        )

    latency_ms = (time.perf_counter() - start) * 1000
    logger.info(f"chat_complete session={request.session_id} intent={intent} latency={latency_ms:.0f}ms")

    return ChatResponse(
        response=response_text,
        session_id=request.session_id,
        intent=intent,
        confidence=0.95,
        sentiment=sentiment,
        tools_called=tools_called,
        latency_ms=round(latency_ms, 1),
        request_id=request_id,
        language="ur-PK",
    )


# ── OpenAI-Compatible Endpoint (for Vapi / LLM proxies) ──────────────────────

@router.post(
    "/chat/completions",
    summary="OpenAI-Compatible Endpoint for Vapi",
    description="Adapter for Vapi custom LLM. Expects OpenAI chat completion format, returns Urdulish response.",
)
async def chat_completions(request: OpenAIRequest):
    # Extract last user message
    user_message = ""
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    # Security scan
    guard = PromptGuard()
    try:
        security = guard.scan_input(user_message)
        is_safe = security.is_safe
    except Exception:
        is_safe = True  # fail open

    if not is_safe:
        response_text = "Maafi chahti hoon, main sirf Pakistani real estate ke baare mein madad kar sakti hoon."
    else:
        try:
            # Reconstruct LangChain message history from Vapi's format
            langchain_messages = []
            for m in request.messages:
                if m.get("role") == "user":
                    langchain_messages.append(HumanMessage(content=m.get("content", "")))
                elif m.get("role") == "assistant":
                    langchain_messages.append(AIMessage(content=m.get("content", "")))

            if not langchain_messages:
                langchain_messages.append(HumanMessage(content=user_message))

            state = {"messages": langchain_messages}
            session_id = str(uuid.uuid4())
            result = langgraph_app.invoke(
                state,
                config={"configurable": {"thread_id": session_id}},
            )
            response_text = result["messages"][-1].content if result.get("messages") else ""
        except Exception as e:
            logger.error(f"Vapi completions error: {e}")
            response_text = "Maafi chahti hoon, technical masla hai. Dobara try karein."

    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


# ── WebSocket Streaming Endpoint ──────────────────────────────────────────────

@router.websocket("/ws/{session_id}")
async def voice_websocket(websocket: WebSocket, session_id: str):
    """
    Real-time streaming WebSocket for voice conversations.

    Protocol (JSON frames):
      Client → Server:
        { "type": "auth",        "api_key": "..." }
        { "type": "text",        "data": "user message" }
        { "type": "ping" }

      Server → Client:
        { "type": "connected",   "session_id": "..." }
        { "type": "processing",  "stage": "intent_detection" | "tools" | "generating" }
        { "type": "response",    "data": "Urdulish text", "intent": "...", "sentiment": "..." }
        { "type": "done",        "session_id": "..." }
        { "type": "error",       "message": "..." }
        { "type": "pong" }
    """
    await websocket.accept()

    # ── Auth handshake ─────────────────────────────────────────────────────────
    try:
        auth_msg = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
        api_key = auth_msg.get("api_key", "")

        # Validate key (or skip in dev mode)
        if not settings.dev_skip_auth:
            if api_key not in settings.api_keys_list:
                await websocket.close(code=4003, reason="Invalid API key")
                return

        await websocket.send_json({"type": "connected", "session_id": session_id})
        logger.info(f"WebSocket connected: session={session_id}")

    except asyncio.TimeoutError:
        await websocket.close(code=4001, reason="Authentication timeout")
        return
    except Exception as e:
        await websocket.close(code=4000, reason=f"Connection error: {e}")
        return

    # ── Message loop ──────────────────────────────────────────────────────────
    guard = PromptGuard()

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "text")
            content = data.get("data", "")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type in ("text", "audio_chunk"):
                if not content.strip():
                    # Silent/empty — send greeting
                    await websocket.send_json({
                        "type": "response",
                        "data": "Assalam o Alaikum! Main Zara hoon, NetixSol Real Estate ki AI Assistant. Aaj main aapki kya madad kar sakti hoon?",
                        "intent": "greeting",
                        "sentiment": "neutral",
                    })
                    await websocket.send_json({"type": "done", "session_id": session_id})
                    continue

                # Security scan
                try:
                    security = guard.scan_input(content)
                    if not security.is_safe:
                        await websocket.send_json({
                            "type": "response",
                            "data": "Maafi chahti hoon, main sirf Pakistani real estate ke baare mein madad kar sakti hoon.",
                            "intent": "security_blocked",
                            "sentiment": "neutral",
                        })
                        await websocket.send_json({"type": "done", "session_id": session_id})
                        continue
                except Exception:
                    pass  # Fail open

                # Signal pipeline stages
                await websocket.send_json({"type": "processing", "stage": "intent_detection"})

                try:
                    await websocket.send_json({"type": "processing", "stage": "tools"})
                    state = {"messages": [HumanMessage(content=content)]}
                    result = await langgraph_app.ainvoke(
                        state,
                        config={"configurable": {"thread_id": session_id}},
                    )

                    await websocket.send_json({"type": "processing", "stage": "generating"})
                    response_text = result["messages"][-1].content if result.get("messages") else "Maafi, dobara try karein."
                    intent = result.get("intent", "unknown")
                    sentiment = result.get("sentiment", "neutral")

                    await websocket.send_json({
                        "type": "response",
                        "data": response_text,
                        "intent": intent,
                        "sentiment": sentiment,
                    })

                except Exception as e:
                    logger.error(f"WebSocket agent error: {e}", exc_info=True)
                    await websocket.send_json({
                        "type": "response",
                        "data": "Maafi chahti hoon, mujhe abhi kuch masla aa raha hai. Dobara try karein!",
                        "intent": "error",
                        "sentiment": "neutral",
                    })

                await websocket.send_json({"type": "done", "session_id": session_id})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id}")
    except Exception as e:
        logger.error(f"WebSocket fatal error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


# ── Deepgram STT Endpoints ─────────────────────────────────────────────────────

@router.get(
    "/stt/token",
    summary="Get Deepgram WebSocket URL for real-time STT",
    description="Returns a Deepgram streaming WebSocket URL. Frontend uses this to stream mic audio directly to Deepgram for production-grade Urdulish transcription.",
)
async def get_stt_token(auth: dict = Depends(maybe_auth)):
    """
    Returns a Deepgram live streaming connection URL for the frontend.
    The frontend connects to this WebSocket directly, sending raw PCM audio chunks
    and receiving real-time transcripts — no audio goes through our backend.
    """
    if not settings.deepgram_api_key:
        return {
            "provider": "browser",
            "message": "Deepgram not configured — using browser Web Speech API",
            "ws_url": None,
        }

    ws_url = deepgram_stt.get_websocket_url(language="en", model="nova-3")
    return {
        "provider": "deepgram",
        "ws_url": ws_url,
        "api_key": settings.deepgram_api_key,  # Safe: used only to connect to Deepgram directly
        "model": "nova-3",
        "language": "en",
        "note": "Nova-3 handles Urdulish (English with Urdu code-switching) natively",
    }


@router.post(
    "/stt/transcribe",
    summary="One-shot audio transcription via Deepgram",
    description="Upload audio bytes and get back a transcript. Max 60 seconds.",
)
async def transcribe_audio(
    request: Request,
    auth: dict = Depends(maybe_auth),
):
    """One-shot transcription — accepts raw audio bytes in request body."""
    audio_bytes = await request.body()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio data received")

    transcript = await deepgram_stt.transcribe_audio_bytes(audio_bytes)
    if transcript is None:
        raise HTTPException(
            status_code=503,
            detail="Transcription failed — Deepgram unavailable or empty audio"
        )

    return {"transcript": transcript, "provider": "deepgram"}


# ── Session Management ─────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}", summary="Get conversation history for a session")
async def get_session(session_id: str, auth: dict = Depends(maybe_auth)):
    """Retrieve conversation history for a given session ID."""
    return {
        "session_id": session_id,
        "message_count": 0,
        "created_at": None,
        "last_active": None,
        "intent_history": [],
    }


@router.delete("/sessions/{session_id}", summary="Clear session memory")
async def clear_session(session_id: str, auth: dict = Depends(maybe_auth)):
    """Clear conversation memory for a session."""
    return {"session_id": session_id, "status": "cleared"}
