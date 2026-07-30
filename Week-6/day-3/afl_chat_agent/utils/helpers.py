import os
import json
from datetime import datetime
from config import RETRIEVAL_LOG_PATH

def log_retrieval(question: str, tool_name: str, returned_data: str, final_answer: str = "", status: str = "PASS"):
    """
    Logs every retrieval for traceability and grounding verification.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "tool_called": tool_name,
        "returned_data": returned_data,
        "final_answer": final_answer,
        "verification_status": status
    }
    
    with open(RETRIEVAL_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def fuzzy_match(query: str, choices: list) -> str:
    """
    Simple typo correction/fuzzy match for player or team names.
    """
    query_lower = query.lower()
    for choice in choices:
        if query_lower in str(choice).lower():
            return choice
    return query
