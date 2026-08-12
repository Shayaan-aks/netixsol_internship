from langchain_core.tools import tool
import json

@tool
def lookup_customer_profile(phone: str) -> str:
    """
    Looks up a customer profile in the CRM using their phone number.
    Returns previous interactions, preferences, and lead score.
    """
    # Mocking CRM lookup
    if phone == "03001234567":
        return json.dumps({
            "name": "Ali Ahmed",
            "phone": phone,
            "lead_score": 85,
            "preferred_area": "DHA Lahore",
            "budget": "3 Crore"
        })
    return json.dumps({"status": "not_found", "message": "New customer detected."})
