import datetime

class BusinessRules:
    """Centralized rules engine to validate state before transitions."""
    
    @staticmethod
    def validate_appointment_time(dt: datetime.datetime) -> bool:
        """Rule: Appointments must be within 9 AM to 6 PM, Monday to Saturday."""
        if dt.weekday() == 6: # Sunday
            return False
        if not (9 <= dt.hour < 18):
            return False
        return True
        
    @staticmethod
    def validate_budget_provided(state: dict) -> bool:
        """Rule: We cannot recommend properties if budget is missing."""
        profile = state.get("customer_profile", {})
        return bool(profile.get("budget"))
