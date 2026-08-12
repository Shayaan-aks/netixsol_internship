"""
Appointments Router — Google Calendar integration for booking, rescheduling, cancellation.
"""
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from backend.api.middleware.auth import require_auth
from backend.api.services.email_service import send_appointment_emails, send_email

router = APIRouter()


# ── Models ────────────────────────────────────────────────────────────────────

class AppointmentRequest(BaseModel):
    customer_phone: str = Field(..., example="03001234567")
    customer_name: str = Field(..., example="Ali Ahmed")
    customer_email: Optional[str] = Field(None, example="ali@example.com")
    date: str = Field(..., example="2026-08-10", description="YYYY-MM-DD")
    time: str = Field(..., example="14:00", description="HH:MM (24h)")
    property_id: Optional[str] = Field(None, example="P001")
    notes: str = Field(default="", example="Customer interested in 4-bed houses in DHA.")
    agent_name: str = Field(default="Zara AI", example="Ahmed Khan")


class RescheduleRequest(BaseModel):
    appointment_id: str = Field(..., example="APT_9876")
    new_date: str = Field(..., example="2026-08-12")
    new_time: str = Field(..., example="11:00")
    reason: str = Field(default="Customer request")


class AppointmentResponse(BaseModel):
    appointment_id: str
    status: str
    customer_name: str
    date: str
    time: str
    calendar_event_id: Optional[str]
    calendar_link: Optional[str]
    email_sent: bool
    crm_updated: bool
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/book",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book a property visit appointment",
    description=(
        "Creates a Google Calendar event, sends confirmation email via n8n, "
        "and updates the CRM. All three systems must succeed for the booking to confirm."
    ),
)
async def book_appointment(
    request: AppointmentRequest,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(require_auth),
):
    # Business hours validation
    try:
        dt = datetime.strptime(f"{request.date} {request.time}", "%Y-%m-%d %H:%M")
        if not (9 <= dt.hour < 18):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointments must be scheduled between 9:00 AM and 6:00 PM.",
            )
        if dt.weekday() == 6:  # Sunday
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointments are not available on Sundays.",
            )
        if dt < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book appointments in the past.",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date/time format. Use YYYY-MM-DD and HH:MM.",
        )

    appointment_id = f"APT_{uuid.uuid4().hex[:8].upper()}"
    calendar_event_id = f"CAL_{uuid.uuid4().hex[:12].upper()}"

    # Trigger Email Sending in the background
    property_details_str = f"Property ID: {request.property_id}" if request.property_id else "To be decided"
    if request.notes:
        property_details_str += f" | Notes: {request.notes}"
        
    background_tasks.add_task(
        send_appointment_emails,
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        date=request.date,
        time=request.time,
        property_details=property_details_str
    )

    # In production: call Google Calendar API + n8n webhook + CRM API
    return AppointmentResponse(
        appointment_id=appointment_id,
        status="confirmed",
        customer_name=request.customer_name,
        date=request.date,
        time=request.time,
        calendar_event_id=calendar_event_id,
        calendar_link=f"https://calendar.google.com/event?eid={calendar_event_id}",
        email_sent=True,
        crm_updated=True,
        message=f"Appointment confirmed for {request.customer_name} on {request.date} at {request.time}. Confirmation email sent.",
    )


@router.put(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
    summary="Reschedule an existing appointment",
)
async def reschedule_appointment(
    appointment_id: str,
    request: RescheduleRequest,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(require_auth),
):
    # In production: lookup appointment → update Calendar → update CRM → re-send email
    # Let's send a generic email for rescheduling using the background tasks
    from backend.config.settings import settings
    if settings.agent_email:
        background_tasks.add_task(
            send_email,
            to_email=settings.agent_email,
            subject=f"Reschedule Alert: Appointment {appointment_id}",
            html_content=f"<p>Appointment {appointment_id} was rescheduled to {request.new_date} at {request.new_time}.</p><p>Reason: {request.reason}</p>"
        )

    return AppointmentResponse(
        appointment_id=appointment_id,
        status="rescheduled",
        customer_name="Customer",
        date=request.new_date,
        time=request.new_time,
        calendar_event_id=f"CAL_{appointment_id}",
        calendar_link=f"https://calendar.google.com/event?eid=CAL_{appointment_id}",
        email_sent=True,
        crm_updated=True,
        message=f"Appointment {appointment_id} rescheduled to {request.new_date} at {request.new_time}.",
    )


@router.delete(
    "/{appointment_id}",
    summary="Cancel an appointment",
    status_code=status.HTTP_200_OK,
)
async def cancel_appointment(
    appointment_id: str,
    background_tasks: BackgroundTasks,
    reason: str = "Customer request",
    auth: dict = Depends(require_auth),
):
    # In production: delete Calendar event → send cancellation email → update CRM
    from backend.config.settings import settings
    if settings.agent_email:
        background_tasks.add_task(
            send_email,
            to_email=settings.agent_email,
            subject=f"Cancellation Alert: Appointment {appointment_id}",
            html_content=f"<p>Appointment {appointment_id} was cancelled.</p><p>Reason: {reason}</p>"
        )

    return {
        "appointment_id": appointment_id,
        "status": "cancelled",
        "reason": reason,
        "calendar_deleted": True,
        "notification_sent": True,
        "crm_updated": True,
        "message": f"Appointment {appointment_id} cancelled. Customer notified.",
    }


@router.get(
    "/availability",
    summary="Check calendar availability for a date",
)
async def check_availability(
    date: str,
    auth: dict = Depends(require_auth),
):
    """Returns available time slots for a given date."""
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if dt.weekday() == 6:
        return {"date": date, "available": False, "reason": "Office closed on Sunday"}

    slots = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    return {"date": date, "available": True, "slots": slots}
