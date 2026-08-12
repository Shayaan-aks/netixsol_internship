import pytest
import datetime
from src.scheduler.manager import SchedulerManager

# NOTE: These tests use the mock implementation of Google Calendar since we don't have credentials.json

def test_booking_outside_working_hours():
    scheduler = SchedulerManager()
    
    # Try to book at 8 PM (20:00)
    start_time = datetime.datetime.now().replace(hour=20, minute=0, second=0)
    
    result = scheduler.book_appointment(
        customer_phone="03001234567",
        property_id="PROP123",
        start_time=start_time,
        notes="Test booking"
    )
    
    assert result["success"] == False
    assert "9 AM and 6 PM" in result["message"]

def test_booking_within_working_hours():
    scheduler = SchedulerManager()
    
    # Try to book at 2 PM (14:00)
    start_time = datetime.datetime.now().replace(hour=14, minute=0, second=0)
    
    result = scheduler.book_appointment(
        customer_phone="03001234567",
        property_id="PROP123",
        start_time=start_time,
        notes="Test valid booking"
    )
    
    assert result["success"] == True
    assert "confirmed" in result["message"]
    
def test_cancellation():
    scheduler = SchedulerManager()
    # Mock cancel using an arbitrary ID
    # Since we are using an in-memory test DB, we must book it first.
    start_time = datetime.datetime.now().replace(hour=10, minute=0, second=0)
    book_res = scheduler.book_appointment("03000000000", "P1", start_time, "Notes")
    
    app_id = book_res["appointment_id"]
    
    cancel_res = scheduler.cancel_appointment(app_id)
    assert cancel_res["success"] == True
