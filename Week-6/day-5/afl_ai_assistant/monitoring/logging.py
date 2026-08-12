import json
import time
from config import STRUCTURED_LOG_PATH

def log_interaction(
    query: str,
    intent: str,
    response: str,
    latency: float,
    metadata: dict = None,
    token_usage: int = 0,
):
    """Write a structured JSON log entry for every chat interaction."""
    log_entry = {
        "timestamp": time.time(),
        "query": query,
        "intent": intent,
        "response_preview": response[:200] if response else "",
        "latency_seconds": round(latency, 4),
        "token_usage": token_usage,
        "metadata": metadata or {},
    }
    with open(STRUCTURED_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def log_abuse_event(query: str, event_type: str, session_id: str = ""):
    """Log a security/abuse event separately for compliance tracking."""
    log_entry = {
        "timestamp": time.time(),
        "event_type": event_type,          # 'off_topic' | 'injection_attempt' | 'blocked'
        "query_preview": query[:100],
        "session_id": session_id,
    }
    abuse_log_path = STRUCTURED_LOG_PATH.replace("assistant.log", "abuse.log")
    with open(abuse_log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
