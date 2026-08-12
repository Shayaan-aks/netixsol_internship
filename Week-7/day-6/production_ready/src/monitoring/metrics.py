"""
Prometheus Metrics — Pakistani Real Estate Voice Agent
All counters/histograms tracked by the production FastAPI application.
"""
from prometheus_client import Counter, Histogram, Gauge, REGISTRY

# ─── Request Metrics ────────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "agent_requests_total",
    "Total number of chat requests processed",
    ["method", "status"],
)

REQUEST_LATENCY = Histogram(
    "agent_request_latency_seconds",
    "Latency of chat requests in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# ─── Business Metrics ───────────────────────────────────────────────────────────
BOOKING_TOTAL = Counter(
    "agent_bookings_total",
    "Total appointment bookings attempted",
    ["status"],  # labels: "success", "failure", "blocked_by_rules"
)

BOOKING_SUCCESS_RATE = Gauge(
    "agent_booking_success_rate",
    "Rolling booking success rate (0.0 to 1.0)",
)

# ─── AI Quality Metrics ─────────────────────────────────────────────────────────
RAG_QUERIES = Counter(
    "agent_rag_queries_total",
    "Total RAG knowledge base queries",
    ["result"],  # labels: "hit", "miss"
)

HALLUCINATION_COUNT = Counter(
    "agent_hallucinations_total",
    "Number of detected hallucinations in agent responses",
)

LLM_LATENCY = Histogram(
    "agent_llm_latency_seconds",
    "Latency of LLM calls in seconds",
    ["model", "node"],  # labels: model name, graph node
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# ─── API Failure Metrics ────────────────────────────────────────────────────────
API_FAILURES = Counter(
    "agent_api_failures_total",
    "API call failures by service",
    ["service"],  # labels: "gemini", "calendar", "email", "n8n", "crm"
)

CALENDAR_FAILURES = Counter(
    "agent_calendar_failures_total",
    "Google Calendar API failures",
)

EMAIL_FAILURES = Counter(
    "agent_email_failures_total",
    "Email dispatch failures",
)

# ─── Security Metrics ───────────────────────────────────────────────────────────
SECURITY_VIOLATIONS = Counter(
    "agent_security_violations_total",
    "Blocked prompt injection and security attempts",
    ["threat_category"],  # labels: "prompt_injection", "jailbreak", "data_extraction", etc.
)

# ─── Voice/Audio Quality Metrics ────────────────────────────────────────────────
VOICE_QUALITY_SCORE = Histogram(
    "agent_voice_quality_score",
    "Voice response quality score (0.0 to 1.0)",
    buckets=[0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0],
)

# ─── Active Sessions ────────────────────────────────────────────────────────────
ACTIVE_SESSIONS = Gauge(
    "agent_active_sessions",
    "Number of currently active conversation sessions",
)


def record_request(status: str = "success", latency_seconds: float = 0):
    """Helper to atomically record a completed request."""
    REQUEST_COUNT.labels(method="POST", status=status).inc()
    REQUEST_LATENCY.observe(latency_seconds)


def record_security_violation(threat_category: str = "unknown"):
    """Helper to record a detected security threat."""
    SECURITY_VIOLATIONS.labels(threat_category=threat_category).inc()


def record_api_failure(service: str):
    """Helper to record an API failure for a given service."""
    API_FAILURES.labels(service=service).inc()
    if service == "calendar":
        CALENDAR_FAILURES.inc()
    elif service == "email":
        EMAIL_FAILURES.inc()
