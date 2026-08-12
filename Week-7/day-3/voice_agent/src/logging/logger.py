import logging
import json
import time
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)

    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Logs structured JSON for observability (Grafana/Datadog)"""
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            **details
        }
        # In production, this would go to a file or log forwarder
        print(json.dumps(log_entry))

    def log_latency(self, stage: str, duration_ms: float):
        self.log_event("latency", {"stage": stage, "duration_ms": duration_ms})
        
    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str, exc_info=True):
        self.logger.error(msg, exc_info=exc_info)

logger = StructuredLogger("voice_agent")
