def handle_abuse(state_dict: dict) -> dict:
    """
    Checks the abuse counters. If thresholds are exceeded, flags the state as BLOCKED.
    """
    off_topic_count = state_dict.get("off_topic_count", 0)
    injection_attempts = state_dict.get("injection_attempts", 0)
    
    if injection_attempts >= 2:
        return {"status": "BLOCKED", "message": "Access restricted due to repeated policy violations."}
        
    if off_topic_count >= 3:
        return {"status": "BLOCKED", "message": "You have exceeded the limit for non-AFL questions. Please stay on topic."}
        
    return {"status": "OK"}
