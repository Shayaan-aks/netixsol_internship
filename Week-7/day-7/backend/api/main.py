"""
Production FastAPI Application — NetixSol Real Estate AI Platform v1.0.0

Architecture:
  Nginx → FastAPI → Security Gate → LangGraph Agent → Tools (RAG/Calendar/CRM)
                 → Prometheus Metrics
                 → Structured JSON Logs
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
import time
import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

# ── Path Setup ────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_WEEK7 = os.path.join(_ROOT, "..")
_PATHS = [
    _ROOT,
    os.path.join(_WEEK7, "day-2"),
    os.path.join(_WEEK7, "day-4", "business_assistant"),
    os.path.join(_WEEK7, "day-5", "langgraph_agent"),
    os.path.join(_WEEK7, "day-6", "production_ready"),
]
for path in _PATHS:
    if path not in sys.path:
        sys.path.insert(0, path)

# ── Internal Imports ──────────────────────────────────────────────────────────
from backend.config.settings import settings
from backend.api.routers import health, voice, properties, appointments, crm
from backend.api.middleware.rate_limit import RateLimitMiddleware

# ── Logging Setup ─────────────────────────────────────────────────────────────
import logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger("platform.api")


# ── Lifespan (Startup / Shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Startup and graceful shutdown logic."""
    logger.info("platform_starting", version=settings.app_version, env=settings.environment)

    # Startup: verify critical services
    startup_checks = []

    # Check GEMINI_API_KEY
    if settings.gemini_api_key:
        startup_checks.append(("gemini_api_key", "ok"))
    else:
        startup_checks.append(("gemini_api_key", "missing"))
        logger.error("startup_warning", issue="GEMINI_API_KEY not set")

    for check, result in startup_checks:
        logger.info("startup_check", check=check, result=result)

    logger.info("platform_ready", checks=len(startup_checks))
    yield

    # Graceful shutdown
    logger.info("platform_shutting_down", reason="SIGTERM received")
    await asyncio.sleep(0.1)  # Allow in-flight requests to complete
    logger.info("platform_stopped")


# ── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "Production-grade AI Voice Platform for Pakistani Real Estate. "
        "LangGraph-orchestrated agent with RAG knowledge base, Google Calendar, "
        "CRM integration, and streaming voice capabilities."
    ),
    version=settings.app_version,
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
    lifespan=lifespan,
)

# ── Middleware Stack ──────────────────────────────────────────────────────────

# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_per_minute,
    burst_size=settings.rate_limit_burst,
)

# 3. Prometheus instrumentation — /metrics endpoint
Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/v1/health", "/metrics"],
).instrument(app).expose(app, endpoint="/metrics")

# ── Request ID Middleware ─────────────────────────────────────────────────────
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Attach X-Request-ID to every request and response."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    request.state.start_time = time.perf_counter()

    response = await call_next(request)

    latency_ms = (time.perf_counter() - request.state.start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(round(latency_ms, 1))
    return response


# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "unhandled_exception",
        request_id=request_id,
        path=str(request.url),
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "request_id": request_id,
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(voice.router, prefix="/v1/voice", tags=["Voice"])
app.include_router(properties.router, prefix="/v1/properties", tags=["Properties"])
app.include_router(appointments.router, prefix="/v1/appointments", tags=["Appointments"])
app.include_router(crm.router, prefix="/v1/crm", tags=["CRM"])


# ── Root Endpoint ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "platform": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
        "docs": "/v1/docs",
        "health": "/v1/health",
        "metrics": "/metrics",
    }
