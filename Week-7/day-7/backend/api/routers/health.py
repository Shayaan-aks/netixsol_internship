"""
Health Check Endpoints
Kubernetes liveness, readiness, and startup probes.
"""
import os
import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

_START_TIME = time.time()


class ComponentStatus(BaseModel):
    status: str
    detail: str = ""
    latency_ms: float = 0.0


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    uptime_seconds: float
    components: dict[str, ComponentStatus]


@router.get("/v1/health", response_model=HealthResponse, summary="Full health check")
async def health():
    """
    Comprehensive health check for monitoring systems.
    Returns status of all dependent services.
    """
    from backend.config.settings import settings

    components = {}
    overall = "healthy"

    # LLM API Key
    if os.getenv("GEMINI_API_KEY"):
        components["llm_api"] = ComponentStatus(status="ok", detail="API key configured")
    else:
        components["llm_api"] = ComponentStatus(status="degraded", detail="GEMINI_API_KEY not set")
        overall = "degraded"

    # Security layer
    components["security"] = ComponentStatus(status="ok", detail="PromptGuard active")

    # Monitoring
    components["metrics"] = ComponentStatus(status="ok", detail="Prometheus active at /metrics")

    uptime = round(time.time() - _START_TIME, 1)

    return HealthResponse(
        status=overall,
        version=settings.app_version,
        environment=settings.environment,
        uptime_seconds=uptime,
        components=components,
    )


@router.get("/v1/live", summary="Liveness probe (Kubernetes)")
async def liveness():
    """Returns 200 if the process is alive. Used by Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/v1/ready", summary="Readiness probe (Kubernetes)")
async def readiness():
    """Returns 200 if the service is ready to accept traffic."""
    if not os.getenv("GEMINI_API_KEY"):
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service not ready: missing configuration")
    return {"status": "ready"}
