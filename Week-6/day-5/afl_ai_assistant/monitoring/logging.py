import json
import time
from config import STRUCTURED_LOG_PATH

def log_interaction(query: str, intent: str, response: str, latency: float, metadata: dict = None):
    log_entry = {
        "timestamp": time.time(),
        "query": query,
        "intent": intent,
        "response": response,
        "latency": latency,
        "metadata": metadata or {}
    }
    with open(STRUCTURED_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
