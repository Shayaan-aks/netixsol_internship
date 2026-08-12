import datetime
from src.calendar.google_cal import GoogleCalendarClient
from src.crm.repository import CRMRepository

class SchedulerManager:
    """
    Business Logic Layer for Scheduling.
    Validates business rules before interacting with the Calendar and CRM.
    """
    def __init__(self):
        self.calendar = GoogleCalendarClient()
        self.crm = CRMRepository()
        
    def book_appointment(self, customer_phone: str, property_id: str, start_time: datetime.datetime, notes: str) -> dict:
        """Full booking flow: Validation -> Calendar -> CRM"""
        # 1. Business Rule: Must be during working hours (9 AM - 6 PM)
        if not (9 <= start_time.hour < 18):
            return {"success": False, "message": "Appointments can only be booked between 9 AM and 6 PM."}
            
        # 2. Check Calendar Availability
        end_time = start_time + datetime.timedelta(minutes=30)
        if not self.calendar.check_availability(start_time, end_time):
            return {"success": False, "message": "This slot is already booked. Please choose another time."}
            
        # 3. Create Calendar Event
        title = f"Site Visit: Property {property_id} ({customer_phone})"
        try:
            event_id = self.calendar.create_event(title=title, start_time=start_time, duration_minutes=30, description=notes)
        except ValueError as e:
            return {"success": False, "message": str(e)}
            
        # 4. Save to CRM
        customer = self.crm.get_or_create_customer(phone=customer_phone)
        appointment = self.crm.create_appointment(
            customer_id=customer.id, 
            property_id=property_id,
            employee_name="Assigned Agent", 
            meeting_time=start_time,
            event_id=event_id
        )
        
        return {
            "success": True, 
            "message": "Appointment confirmed and calendar updated.",
            "appointment_id": appointment.id
        }
        
    def cancel_appointment(self, appointment_id: int) -> dict:
        """Cancellation Flow: CRM Update -> Calendar Delete"""
        app = self.crm.cancel_appointment(appointment_id)
        if app and app.google_event_id:
            self.calendar.delete_event(app.google_event_id)
            return {"success": True, "message": "Appointment cancelled successfully."}
        return {"success": False, "message": "Appointment not found."}
