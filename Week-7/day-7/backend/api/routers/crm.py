"""
CRM Router — Customer profile management, lead scoring, interaction history.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from backend.api.middleware.auth import require_auth

# Import CRM from Day 4
from src.crm.repository import CRMRepository
from src.database.models import Customer, CallLog

router = APIRouter()


# ── Models ────────────────────────────────────────────────────────────────────

class CustomerProfile(BaseModel):
    customer_id: Optional[str] = None
    name: str = Field(..., example="Ali Ahmed")
    phone: str = Field(..., example="03001234567")
    email: Optional[str] = Field(None, example="ali@example.com")
    preferred_area: Optional[str] = Field(None, example="DHA Lahore")
    budget_min: Optional[int] = Field(None, example=10000000)
    budget_max: Optional[int] = Field(None, example=30000000)
    property_type: Optional[str] = Field(None, example="House")
    lead_score: int = Field(default=50, ge=0, le=100)
    status: str = Field(default="new", example="qualified")


class InteractionLog(BaseModel):
    session_id: str
    intent: str
    summary: str
    properties_shown: List[str] = []
    outcome: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/customers/{phone}",
    response_model=CustomerProfile,
    summary="Look up customer by phone number",
)
async def get_customer(phone: str, auth: dict = Depends(require_auth)):
    """Retrieve customer profile from CRM by phone number."""
    repo = CRMRepository()
    try:
        customer = repo.session.query(Customer).filter(Customer.phone == phone).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with phone {phone} not found in CRM.",
            )
        return CustomerProfile(
            customer_id=f"C{customer.id:03d}",
            name=customer.name or "Unknown",
            phone=customer.phone,
            email=customer.email,
            preferred_area=customer.preferred_area,
            budget_min=0, # Parse budget string if needed
            budget_max=int(customer.budget) if customer.budget and customer.budget.isdigit() else None,
            property_type="House",
            lead_score=customer.lead_score,
            status="hot_lead" if customer.lead_score >= 80 else ("qualified" if customer.lead_score >= 50 else "new")
        )
    finally:
        repo.close()


@router.post(
    "/customers",
    response_model=CustomerProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update customer profile",
)
async def upsert_customer(
    profile: CustomerProfile,
    auth: dict = Depends(require_auth),
):
    """Create a new customer or update existing profile. Upserts by phone number."""
    repo = CRMRepository()
    try:
        customer = repo.get_or_create_customer(phone=profile.phone, name=profile.name)
        if profile.email: customer.email = profile.email
        if profile.preferred_area: customer.preferred_area = profile.preferred_area
        if profile.budget_max: customer.budget = str(profile.budget_max)
        customer.lead_score = profile.lead_score
        repo.session.commit()
        profile.customer_id = f"C{customer.id:03d}"
        return profile
    finally:
        repo.close()


@router.put(
    "/customers/{customer_id}/lead-score",
    summary="Update customer lead score",
)
async def update_lead_score(
    customer_id: str,
    score: int = Query(..., ge=0, le=100),
    reason: str = Query(default="Manual update"),
    auth: dict = Depends(require_auth),
):
    repo = CRMRepository()
    try:
        db_id = int(customer_id.replace("C", "")) if customer_id.startswith("C") else 0
        customer = repo.session.query(Customer).filter(Customer.id == db_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        previous = customer.lead_score
        customer.lead_score = score
        repo.session.commit()
        return {
            "customer_id": customer_id,
            "previous_score": previous,
            "new_score": score,
            "reason": reason,
            "updated": True,
        }
    finally:
        repo.close()


@router.post(
    "/customers/{customer_id}/interactions",
    status_code=status.HTTP_201_CREATED,
    summary="Log a conversation interaction to CRM",
)
async def log_interaction(
    customer_id: str,
    log: InteractionLog,
    auth: dict = Depends(require_auth),
):
    """Records a conversation outcome to the customer's CRM history."""
    repo = CRMRepository()
    try:
        db_id = int(customer_id.replace("C", "")) if customer_id.startswith("C") else 0
        repo.log_call(customer_id=db_id, transcript=f"Intent: {log.intent}\nOutcome: {log.outcome}\nProperties Shown: {', '.join(log.properties_shown)}", summary=log.summary, duration=60)
        return {
            "customer_id": customer_id,
            "interaction_id": f"INT_{log.session_id[:8].upper()}",
            "logged": True,
            "crm_updated": True,
        }
    finally:
        repo.close()


@router.get(
    "/leads",
    summary="Get all leads sorted by lead score",
)
async def get_leads(
    status_filter: Optional[str] = Query(None, example="hot_lead"),
    min_score: int = Query(default=0, ge=0, le=100),
    limit: int = Query(default=20, ge=1, le=100),
    auth: dict = Depends(require_auth),
):
    """Returns all leads from CRM, optionally filtered by status and minimum lead score."""
    repo = CRMRepository()
    try:
        query = repo.session.query(Customer).filter(Customer.lead_score >= min_score)
        
        # We don't have a strict status column in DB, we infer it from lead_score
        # For filtering, we can apply after query or use strict conditions
        db_customers = query.order_by(Customer.lead_score.desc()).limit(limit).all()
        
        leads = []
        for c in db_customers:
            c_status = "hot_lead" if c.lead_score >= 80 else ("qualified" if c.lead_score >= 50 else "new")
            if status_filter and c_status != status_filter:
                continue
                
            leads.append({
                "customer_id": f"C{c.id:03d}",
                "name": c.name or "Unknown",
                "phone": c.phone,
                "lead_score": c.lead_score,
                "status": c_status,
                "preferred_area": c.preferred_area or "Not specified",
                "budget": f"{c.budget} PKR" if c.budget else "Unspecified",
                "last_contact": c.created_at.strftime("%Y-%m-%d")
            })
            
        return {
            "total": len(leads),
            "leads": leads,
        }
    finally:
        repo.close()
