from langchain_core.tools import tool
import json

@tool
def search_property_knowledge(query: str, filters: dict = None) -> str:
    """
    Searches the RAG knowledge base for property details, prices, or locations.
    query: The semantic search query.
    filters: Optional dictionary containing budget or location filters.
    """
    # Mocking RAG retrieval based on Day 2 architecture
    if "dha" in query.lower():
        results = [
            {"property_id": "P1", "location": "DHA Phase 6", "price": "3 Crore", "type": "House", "bedrooms": 3}
        ]
        return json.dumps({"status": "success", "data": results})
    return json.dumps({"status": "success", "data": [], "message": "No matching properties found in knowledge base."})
