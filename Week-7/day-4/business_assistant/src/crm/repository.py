from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from src.database.models import Base, Customer, Appointment, CallLog
from src.config.settings import settings
import datetime

# Setup DB
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
Base.metadata.create_all(bind=engine)

class CRMRepository:
    """Handles all CRM business logic securely."""
    
    def __init__(self):
        self.session = Session(autocommit=False, autoflush=False, bind=engine)
        
    def get_or_create_customer(self, phone: str, name: str = None) -> Customer:
        customer = self.session.query(Customer).filter(Customer.phone == phone).first()
        if not customer:
            customer = Customer(phone=phone, name=name)
            self.session.add(customer)
            self.session.commit()
            self.session.refresh(customer)
        return customer
        
    def log_call(self, customer_id: int, transcript: str, summary: str, duration: int):
        log = CallLog(customer_id=customer_id, transcript=transcript, summary=summary, duration_seconds=duration)
        self.session.add(log)
        self.session.commit()
        
    def create_appointment(self, customer_id: int, property_id: str, employee_name: str, meeting_time: datetime.datetime, event_id: str = None) -> Appointment:
        app = Appointment(
            customer_id=customer_id,
            property_id=property_id,
            employee_name=employee_name,
            meeting_time=meeting_time,
            google_event_id=event_id
        )
        self.session.add(app)
        self.session.commit()
        self.session.refresh(app)
        return app
        
    def get_upcoming_appointments(self, customer_id: int):
        now = datetime.datetime.utcnow()
        return self.session.query(Appointment).filter(
            Appointment.customer_id == customer_id,
            Appointment.meeting_time > now,
            Appointment.status == "Scheduled"
        ).all()
        
    def cancel_appointment(self, appointment_id: int):
        app = self.session.query(Appointment).filter(Appointment.id == appointment_id).first()
        if app:
            app.status = "Cancelled"
            self.session.commit()
        return app
        
    def close(self):
        self.session.close()
