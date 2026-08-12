import structlog
import logging
import sys
from src.monitoring.metrics import record_request, record_security_violation, record_api_failure


def setup_logging():
    """Configures structured JSON logging for Prometheus/Grafana/Loki aggregation."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),  # Output as structured JSON for log aggregators
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    return structlog.get_logger(name)


class MetricLogger:
    """
    Combines structured logging + Prometheus metric emission in a single call.
    Use this in FastAPI endpoints and agent nodes for full observability.
    """

    def __init__(self, name: str):
        self.log = get_logger(name)

    def request_success(self, session_id: str, latency_ms: float, intent: str = "unknown"):
        """Log + metric for a successful agent response."""
        record_request(status="success", latency_seconds=latency_ms / 1000)
        self.log.info(
            "request_success",
            session_id=session_id,
            latency_ms=round(latency_ms, 1),
            intent=intent,
        )

    def request_failure(self, session_id: str, error: str, service: str = "agent"):
        """Log + metric for a failed request."""
        record_request(status="error")
        record_api_failure(service=service)
        self.log.error(
            "request_failure",
            session_id=session_id,
            error=error,
            service=service,
        )

    def security_violation(self, session_id: str, reason: str, threat_category: str = "unknown"):
        """Log + metric for a blocked security violation."""
        record_security_violation(threat_category=threat_category)
        self.log.warning(
            "security_violation",
            session_id=session_id,
            reason=reason,
            threat_category=threat_category,
        )

    def rag_miss(self, session_id: str, query: str):
        """Log a RAG knowledge miss (no relevant chunks found)."""
        self.log.warning("rag_miss", session_id=session_id, query=query[:100])

    def calendar_failure(self, session_id: str, error: str):
        """Log + metric for a Google Calendar API failure."""
        record_api_failure("calendar")
        self.log.error("calendar_failure", session_id=session_id, error=error)

    def email_failure(self, session_id: str, error: str):
        """Log + metric for an email dispatch failure."""
        record_api_failure("email")
        self.log.error("email_failure", session_id=session_id, error=error)

    def booking_success(self, session_id: str, appointment_time: str):
        """Log a successful appointment booking."""
        self.log.info("booking_success", session_id=session_id, appointment_time=appointment_time)
