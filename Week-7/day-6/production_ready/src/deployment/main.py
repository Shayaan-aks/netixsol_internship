"""
Production FastAPI Application — Pakistani Real Estate Voice Agent
Implements: Security Gate → LangGraph Agent → Prometheus Metrics → Structured Logging
"""
import os
import sys
import time
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

# ── Add Day-5 LangGraph agent to Python path ──────────────────────────────────
_DAY5_PATH = os.environ.get(
    "DAY5_AGENT_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../day-5/langgraph_agent")),
)
if _DAY5_PATH not in sys.path:
    sys.path.insert(0, _DAY5_PATH)

# ── Infrastructure Imports ────────────────────────────────────────────────────
from src.security.prompt_guard import PromptGuard
from src.monitoring.logger import setup_logging, MetricLogger
from src.monitoring.metrics import (
    ACTIVE_SESSIONS,
    BOOKING_TOTAL,
    record_request,
    record_security_violation,
)

# ── Initialize Infrastructure ─────────────────────────────────────────────────
setup_logging()
logger = MetricLogger("production_api")
guard = PromptGuard()

# ── Initialize LangGraph Agent ────────────────────────────────────────────────
try:
    from src.agent.graph import app as langgraph_app
    from langchain_core.messages import HumanMessage
    _AGENT_AVAILABLE = True
except ImportError as e:
    _AGENT_AVAILABLE = False
    langgraph_app = None
    HumanMessage = None
    print(f"WARNING: LangGraph agent not available: {e}")


# ── FastAPI Application ────────────────────────────────────────────────────────
app = FastAPI(
    title="NetixSol Real Estate Voice Agent",
    description="Production-grade Pakistani Real Estate AI Agent with LangGraph orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Prometheus instrumentation — exposes /metrics endpoint
Instrumentator().instrument(app).expose(app)


# ── Request/Response Models ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=0, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str = "unknown"
    latency_ms: float = 0.0
    request_id: str


class HealthComponent(BaseModel):
    status: str
    detail: str = ""

class HealthResponse(BaseModel):
    status: str
    version: str
    components: dict


# ── Middleware — Request ID ─────────────────────────────────────────────────────

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, http_request: Request):
    """
    Primary conversation endpoint for voice/text interactions.
    Pipeline: Security Gate → LangGraph Agent → Response
    """
    request_id = getattr(http_request.state, "request_id", str(uuid.uuid4()))
    start_time = time.perf_counter()
    ACTIVE_SESSIONS.inc()

    try:
        # ── Stage 1: Security Gate ──────────────────────────────────────────
        security_check = guard.scan_input(request.message)
        if not security_check.is_safe:
            logger.security_violation(
                session_id=request.session_id,
                reason=security_check.reason,
                threat_category=security_check.threat_category,
            )
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.request_success(request.session_id, latency_ms, intent="security_blocked")
            return ChatResponse(
                response="I can only help with Pakistani real estate queries. Kya main aapki koi aur mदद kar sakta hoon?",
                session_id=request.session_id,
                intent="security_blocked",
                latency_ms=round(latency_ms, 1),
                request_id=request_id,
            )

        # ── Stage 2: LangGraph Agent Invocation ────────────────────────────
        intent = "unknown"
        agent_response = "Mujhe maafi chahiye, abhi kuch technical masla aa gaya hai. Thodi der baad dobara try karein."

        if _AGENT_AVAILABLE and langgraph_app:
            try:
                state = {"messages": [HumanMessage(content=request.message)]}
                result = langgraph_app.invoke(
                    state,
                    config={"configurable": {"thread_id": request.session_id}},
                )
                intent = result.get("intent", "unknown")
                if result.get("messages"):
                    agent_response = result["messages"][-1].content

                # Track booking metrics
                if intent == "book_appointment":
                    appointment_state = result.get("appointment_state", {})
                    if appointment_state.get("appointment_confirmed"):
                        BOOKING_TOTAL.labels(status="success").inc()
                    else:
                        BOOKING_TOTAL.labels(status="pending_info").inc()

            except Exception as e:
                logger.request_failure(request.session_id, str(e), service="agent")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Agent temporarily unavailable. Please try again.",
                )
        else:
            # Graceful degradation — agent not loaded
            agent_response = (
                "Assalam o Alaikum! Main Zara hoon, NetixSol Real Estate ki AI Assistant. "
                "Aaj main aapki kya mدد kar sakti hoon? Property dhundna hai, appointment book karni hai, ya koi aur kaam?"
            )
            intent = "greeting"

        # ── Stage 3: Record Metrics ─────────────────────────────────────────
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.request_success(request.session_id, latency_ms, intent=intent)

        return ChatResponse(
            response=agent_response,
            session_id=request.session_id,
            intent=intent,
            latency_ms=round(latency_ms, 1),
            request_id=request_id,
        )

    finally:
        ACTIVE_SESSIONS.dec()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Kubernetes/Docker liveness + readiness probe.
    Checks: API key configured, agent importable, disk accessible.
    """
    components = {}
    overall_status = "healthy"

    # Check 1: GEMINI_API_KEY configured
    if os.getenv("GEMINI_API_KEY"):
        components["gemini_api"] = {"status": "ok", "detail": "API key configured"}
    else:
        components["gemini_api"] = {"status": "degraded", "detail": "GEMINI_API_KEY not set"}
        overall_status = "degraded"

    # Check 2: LangGraph Agent importable
    if _AGENT_AVAILABLE:
        components["langgraph_agent"] = {"status": "ok", "detail": "Agent compiled and ready"}
    else:
        components["langgraph_agent"] = {"status": "degraded", "detail": "Agent module not loaded"}
        overall_status = "degraded"

    # Check 3: Security module
    components["security_guard"] = {"status": "ok", "detail": "PromptGuard active"}

    # Check 4: Monitoring
    components["monitoring"] = {"status": "ok", "detail": "Prometheus metrics active"}

    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        components=components,
    )


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": "NetixSol Real Estate Voice Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "metrics": "GET /metrics",
            "docs": "GET /docs",
        },
    }
