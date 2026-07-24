"""
app.py — FastAPI Production API Wrapper for Enterprise Client Onboarding System
Week 5 Day 5 Capstone Project

Exposes endpoints:
  POST /api/v1/onboard         : Submit client brief & initialize onboarding graph
  POST /api/v1/approve         : Approve human checkpoint & dispatch final contract
  GET  /api/v1/status/{thread} : Query thread execution status & proposal draft
  GET  /api/v1/metrics         : Production telemetry metrics (error rate, token usage, costs)
  GET  /health                 : Service health check endpoint
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import Core Agent Engine
from agent_engine import build_onboarding_graph, ClientOnboardingState, sanitize_input, query_client_database

app = FastAPI(
    title="Enterprise Client Onboarding Agent API",
    description="Production-ready FastAPI service wrapping a Hybrid LangGraph + CrewAI Multi-Agent System.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory Production Telemetry & Thread Store
THREAD_STORE: Dict[str, ClientOnboardingState] = {}
METRICS_STORE = {
    "total_requests": 0,
    "successful_onboardings": 0,
    "injection_attempts_blocked": 0,
    "malformed_briefs_rejected": 0,
    "human_approvals_granted": 0,
    "total_tokens_consumed": 0,
    "accumulated_cost_usd": 0.0,
    "total_latency_seconds": 0.0
}

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class OnboardRequest(BaseModel):
    client_name: str = Field(..., example="Web3Geeks", description="Name of the client enterprise")
    project_title: str = Field(..., example="DeFi Liquid Staking dApp", description="Title of the project brief")
    raw_brief: str = Field(..., example="We need a Solidity liquid staking protocol with React dApp frontend...", description="Raw requirement brief text")


class ApprovalRequest(BaseModel):
    thread_id: str = Field(..., example="thread-84920412", description="Unique execution thread ID")
    approved: bool = Field(True, description="Human sign-off approval flag")
    reviewer_notes: Optional[str] = Field(None, example="Approved with standard 10% VIP discount.")


class OnboardResponse(BaseModel):
    thread_id: str
    client_name: str
    project_title: str
    validation_status: str
    validation_error: Optional[str]
    quality_score: float
    is_approved: bool
    status: str  # "paused_awaiting_approval", "dispatched", "rejected"
    proposal_draft: str
    commercial_terms: Dict[str, Any]
    execution_logs: List[str]
    latency_sec: float
    cost_usd: float


# ─────────────────────────────────────────────────────────────────────────────
# Logging Middleware
# ─────────────────────────────────────────────────────────────────────────────

@app.middleware("http")
async import_telemetry_middleware(request: Request, call_next):
    start_time = time.time()
    METRICS_STORE["total_requests"] += 1
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    METRICS_STORE["total_latency_seconds"] += duration
    
    print(f"[API Log] {request.method} {request.url.path} -> Status: {response.status_code} ({duration:.3f}s)")
    return response


# ─────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for container orchestrators."""
    return {
        "status": "healthy",
        "service": "Client-Onboarding-Agent-API",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


@app.post("/api/v1/onboard", response_model=OnboardResponse, tags=["Onboarding Workflow"])
def onboard_client(payload: OnboardRequest):
    """
    Submits a client brief, sanitizes input, queries client database, and generates proposal draft.
    Pauses execution at Human-in-the-Loop checkpoint before contract dispatch.
    """
    start_time = time.time()
    thread_id = f"thread-{uuid.uuid4().hex[:8]}"
    
    initial_state: ClientOnboardingState = {
        "thread_id": thread_id,
        "client_name": payload.client_name,
        "project_title": payload.project_title,
        "raw_brief": payload.raw_brief,
        "sanitized_brief": "",
        "validation_status": "valid",
        "validation_error": None,
        "client_history": {},
        "proposal_draft": "",
        "technical_architecture": "",
        "commercial_terms": {},
        "quality_score": 0.0,
        "revision_count": 0,
        "max_revisions": 2,
        "is_approved": False,  # Pause at HITL gate
        "final_contract_payload": {},
        "execution_logs": [],
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "estimated_cost_usd": 0.0
    }
    
    app_graph = build_onboarding_graph()
    final_state = app_graph.invoke(initial_state)
    
    # Store state snapshot in thread memory
    THREAD_STORE[thread_id] = final_state
    
    # Update Telemetry Metrics
    if final_state["validation_status"] == "flagged_injection":
        METRICS_STORE["injection_attempts_blocked"] += 1
    elif final_state["validation_status"] == "malformed":
        METRICS_STORE["malformed_briefs_rejected"] += 1
    else:
        METRICS_STORE["successful_onboardings"] += 1
        
    p_tok = final_state.get("prompt_tokens", 1450)
    c_tok = final_state.get("completion_tokens", 520)
    METRICS_STORE["total_tokens_consumed"] += (p_tok + c_tok)
    METRICS_STORE["accumulated_cost_usd"] += final_state.get("estimated_cost_usd", 0.00065)

    elapsed = round(time.time() - start_time, 3)
    status_str = "paused_awaiting_approval" if final_state["validation_status"] == "valid" else "rejected"

    return OnboardResponse(
        thread_id=thread_id,
        client_name=final_state["client_name"],
        project_title=final_state["project_title"],
        validation_status=final_state["validation_status"],
        validation_error=final_state["validation_error"],
        quality_score=final_state.get("quality_score", 0.0),
        is_approved=final_state.get("is_approved", False),
        status=status_str,
        proposal_draft=final_state.get("proposal_draft", ""),
        commercial_terms=final_state.get("commercial_terms", {}),
        execution_logs=final_state.get("execution_logs", []),
        latency_sec=elapsed,
        cost_usd=final_state.get("estimated_cost_usd", 0.00065)
    )


@app.post("/api/v1/approve", tags=["Human-in-the-Loop Approval"])
def approve_proposal(payload: ApprovalRequest):
    """
    Human-in-the-loop approval endpoint. Mutates thread state to approved and resumes graph to dispatch payload.
    """
    if payload.thread_id not in THREAD_STORE:
        raise HTTPException(status_code=404, detail=f"Thread ID '{payload.thread_id}' not found.")
        
    state = THREAD_STORE[payload.thread_id]
    
    if state["validation_status"] != "valid":
        raise HTTPException(status_code=400, detail=f"Cannot approve thread with validation status '{state['validation_status']}'.")
        
    # Mutate State with Human Approval
    state["is_approved"] = payload.approved
    state["execution_logs"].append(f"[API HITL Sign-off] Approved by Account Manager. Notes: {payload.reviewer_notes or 'None'}")
    
    # Resume Graph execution
    app_graph = build_onboarding_graph()
    updated_state = app_graph.invoke(state)
    THREAD_STORE[payload.thread_id] = updated_state
    
    METRICS_STORE["human_approvals_granted"] += 1
    
    return {
        "thread_id": payload.thread_id,
        "status": "DISPATCHED" if payload.approved else "REJECTED_BY_HUMAN",
        "final_contract_payload": updated_state.get("final_contract_payload", {}),
        "execution_logs": updated_state.get("execution_logs", [])
    }


@app.get("/api/v1/status/{thread_id}", tags=["Thread State Monitoring"])
def get_thread_status(thread_id: str):
    """Retrieves current checkpoint state of an onboarding thread."""
    if thread_id not in THREAD_STORE:
        raise HTTPException(status_code=404, detail=f"Thread ID '{thread_id}' not found.")
    return THREAD_STORE[thread_id]


@app.get("/api/v1/metrics", tags=["Production Telemetry"])
def get_production_metrics():
    """Returns production operational metrics for monitoring dashboards."""
    total_req = max(1, METRICS_STORE["total_requests"])
    avg_latency = round(METRICS_STORE["total_latency_seconds"] / total_req, 3)
    
    return {
        "telemetry_metrics": {
            "total_requests_processed": METRICS_STORE["total_requests"],
            "successful_onboardings": METRICS_STORE["successful_onboardings"],
            "security_injections_blocked": METRICS_STORE["injection_attempts_blocked"],
            "malformed_briefs_rejected": METRICS_STORE["malformed_briefs_rejected"],
            "human_approvals_granted": METRICS_STORE["human_approvals_granted"],
            "average_latency_seconds": avg_latency,
            "total_tokens_consumed": METRICS_STORE["total_tokens_consumed"],
            "total_cost_usd": round(METRICS_STORE["accumulated_cost_usd"], 6)
        },
        "monitoring_thresholds": {
            "max_p95_latency_seconds": 15.0,
            "max_error_rate_percent": 2.0,
            "max_cost_per_request_usd": 0.05
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Enterprise Agent Server on http://localhost:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
