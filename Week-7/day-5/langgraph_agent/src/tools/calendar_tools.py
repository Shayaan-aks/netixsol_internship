from langchain_core.tools import tool
import datetime
import json

@tool
def check_calendar_availability(date: str, time: str) -> str:
    """
    Checks if a specific date and time is available on the employee calendar.
    Format: date YYYY-MM-DD, time HH:MM.
    """
    # Validation logic via Rules engine (mocked here for demonstration)
    try:
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        if not (9 <= dt.hour < 18):
            return json.dumps({"status": "unavailable", "reason": "Outside working hours (9 AM - 6 PM)."})
        # Mocking available result
        return json.dumps({"status": "available", "message": "Time slot is free."})
    except ValueError:
        return json.dumps({"status": "error", "reason": "Invalid date format."})

@tool
def book_appointment_tool(customer_phone: str, date: str, time: str, notes: str) -> str:
    """
    Books an appointment in the Google Calendar and syncs to CRM.
    Requires customer phone, date, time, and notes.
    """
    # Mocking successful booking integration
    return json.dumps({
        "status": "success",
        "appointment_id": "APT_9876",
        "message": f"Appointment booked successfully for {date} at {time}."
    })
