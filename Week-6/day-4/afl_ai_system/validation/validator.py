def validate_output(tool_output: str) -> str:
    """
    Validates if the tool executed successfully and found data.
    Returns 'PASS', 'FAIL', or 'CLARIFY'.
    """
    if not tool_output or "No records found" in tool_output or "Dataset missing" in tool_output or "missing" in tool_output:
        return "FAIL"
    if "unavailable" in tool_output.lower() or "error" in tool_output.lower():
         return "FAIL"
    return "PASS"
