from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    budget = Column(String, nullable=True)
    preferred_area = Column(String, nullable=True)
    lead_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="customer")
    calls = relationship("CallLog", back_populates="customer")


class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    employee_name = Column(String)
    property_id = Column(String)
    meeting_time = Column(DateTime)
    status = Column(String, default="Scheduled") # Scheduled, Rescheduled, Cancelled, Completed
    google_event_id = Column(String, nullable=True)
    
    customer = relationship("Customer", back_populates="appointments")


class CallLog(Base):
    __tablename__ = 'call_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    transcript = Column(Text)
    summary = Column(Text)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="calls")
