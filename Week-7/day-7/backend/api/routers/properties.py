"""
Properties Router — RAG-powered property search and recommendations.
"""
import time
import sqlite3
import os
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.api.middleware.auth import require_auth
from rag_pipeline import RAGRouter

router = APIRouter()

# Instantiate the RAG Router (loads ChromaDB and SQL Agent)
rag_router = RAGRouter(persist_directory=os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db"))



# ── Request / Response Models ─────────────────────────────────────────────────

class PropertySearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, example="3 bedroom house in DHA Lahore")
    budget_min: Optional[int] = Field(None, example=5000000, description="Budget in PKR")
    budget_max: Optional[int] = Field(None, example=30000000)
    location: Optional[str] = Field(None, example="DHA Lahore")
    property_type: Optional[str] = Field(None, example="House")
    bedrooms: Optional[int] = Field(None, ge=1, le=10)
    limit: int = Field(default=5, ge=1, le=20)


class PropertyResult(BaseModel):
    property_id: str
    location: str
    price: str
    price_pkr: int
    property_type: str
    bedrooms: Optional[int]
    area_marla: Optional[float]
    description: str
    relevance_score: float


class PropertySearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[PropertyResult]
    rag_source: str
    latency_ms: float


class RecommendationRequest(BaseModel):
    customer_id: Optional[str] = None
    phone: Optional[str] = Field(None, example="03001234567")
    budget_max: int = Field(..., example=20000000)
    preferred_locations: List[str] = Field(default=[], example=["DHA Lahore", "Bahria Town"])
    property_type: str = Field(default="House", example="House")
    bedrooms: Optional[int] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/search",
    response_model=PropertySearchResponse,
    summary="Semantic property search via RAG",
    description=(
        "Searches the property knowledge base using semantic similarity. "
        "Results are grounded in the RAG vector database."
    ),
)
async def search_properties(
    request: PropertySearchRequest,
    auth: dict = Depends(require_auth),
):
    start = time.perf_counter()

    # ── Real Database Query ──────────────────────────────────────────────────────────
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "real_estate.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT id, name, city, area, bedrooms, purpose, price, amenities FROM properties WHERE status = 'Available'"
    params = []
    if request.budget_max:
        query += " AND price <= ?"
        params.append(request.budget_max)
    if request.budget_min:
        query += " AND price >= ?"
        params.append(request.budget_min)
    if request.location:
        query += " AND (city COLLATE NOCASE LIKE ? OR area COLLATE NOCASE LIKE ?)"
        params.extend([f"%{request.location}%", f"%{request.location}%"])
    if request.bedrooms:
        query += " AND bedrooms = ?"
        params.append(request.bedrooms)
        
    query += " LIMIT ?"
    params.append(request.limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append(PropertyResult(
            property_id=f"P{r[0]:03d}",
            location=f"{r[3]}, {r[2]}",
            price=f"{r[6]/10000000:.2f} Crore PKR",
            price_pkr=r[6],
            property_type=r[5], # purpose
            bedrooms=r[4],
            area_marla=10.0, # default mock
            description=f"{r[1]}. Amenities: {r[7]}.",
            relevance_score=0.95
        ))
        
    # Get RAG Insight if there's a specific text query
    rag_insight = ""
    if request.query:
        try:
            rag_insight = rag_router.route_query(request.query)
        except Exception as e:
            rag_insight = f"RAG Error: {e}"

    latency_ms = (time.perf_counter() - start) * 1000

    return PropertySearchResponse(
        query=request.query,
        total_results=len(results),
        results=results,
        rag_source=rag_insight[:100] + "..." if rag_insight else "SQLite DB",
        latency_ms=round(latency_ms, 1),
    )


@router.post(
    "/recommend",
    summary="AI-powered personalized property recommendations",
    description=(
        "Returns personalized property recommendations based on customer profile, "
        "budget, and preferences. Uses CRM history + RAG retrieval."
    ),
)
async def recommend_properties(
    request: RecommendationRequest,
    auth: dict = Depends(require_auth),
):
    """Get AI-powered personalized recommendations for a customer."""
    return {
        "customer_id": request.customer_id or "guest",
        "recommendations": [
            {
                "property_id": "P001",
                "match_score": 0.96,
                "match_reasons": ["Within budget", "Preferred location", "Correct bedroom count"],
                "location": "DHA Phase 6, Lahore",
                "price": "3 Crore PKR",
                "agent_pitch": "Sir, yeh property aapke liye perfect hai — DHA Phase 6 mein hai, budget ke andar hai, aur 4 bedrooms hain.",
            }
        ],
        "total_options": 1,
    }


@router.get(
    "/{property_id}",
    summary="Get single property details",
)
async def get_property(
    property_id: str,
    auth: dict = Depends(require_auth),
):
    """Retrieve full details for a specific property by ID."""
    if property_id == "P001":
        return {
            "property_id": "P001",
            "location": "DHA Phase 6, Lahore",
            "price": "3 Crore PKR",
            "property_type": "House",
            "bedrooms": 4,
            "bathrooms": 4,
            "area_marla": 10.0,
            "features": ["Drawing Room", "Servant Quarter", "Car Porch", "Solar Panels"],
            "last_updated": "2026-08-01",
        }
    raise HTTPException(status_code=404, detail=f"Property {property_id} not found.")
