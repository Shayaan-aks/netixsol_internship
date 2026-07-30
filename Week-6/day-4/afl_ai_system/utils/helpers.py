import json
from datetime import datetime
from config import TRACE_LOG_PATH, ROUTER_LOG_PATH, TOOL_LOG_PATH

def log_trace(state: dict):
    with open(TRACE_LOG_PATH, "a") as f:
        summary = {
            "timestamp": datetime.now().isoformat(),
            "intent": state.get("intent"),
            "selected_node": state.get("selected_node"),
            "tool_requested": state.get("tool_requested"),
            "validation_status": state.get("validation_status")
        }
        f.write(json.dumps(summary) + "\n")

def log_router(query: str, intent: str, confidence: float, reasoning: str):
    with open(ROUTER_LOG_PATH, "a") as f:
        f.write(json.dumps({"timestamp": datetime.now().isoformat(), "query": query, "intent": intent, "confidence": confidence, "reasoning": reasoning}) + "\n")

def log_tool(tool_name: str, args: dict, output: str):
    with open(TOOL_LOG_PATH, "a") as f:
        f.write(json.dumps({"timestamp": datetime.now().isoformat(), "tool": tool_name, "args": args, "output": str(output)}) + "\n")
