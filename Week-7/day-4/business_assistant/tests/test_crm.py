import pytest
from src.crm.repository import CRMRepository
from src.database.models import Customer, Appointment

def test_crm_customer_creation():
    crm = CRMRepository()
    
    customer = crm.get_or_create_customer(phone="03112223333", name="Ali Ahmed")
    assert customer.id is not None
    assert customer.name == "Ali Ahmed"
    
    # Second fetch should return the exact same customer ID
    customer_again = crm.get_or_create_customer(phone="03112223333")
    assert customer_again.id == customer.id

def test_crm_log_call():
    crm = CRMRepository()
    customer = crm.get_or_create_customer(phone="03224445555")
    
    crm.log_call(customer.id, "Hello I need a house", "User looking for house", 120)
    # If it commits without error, the test passes
    assert True
