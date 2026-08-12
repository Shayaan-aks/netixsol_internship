import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Setup paths to ensure we can import from previous days
_WEEK7 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(_WEEK7, "day-7"))
sys.path.insert(0, os.path.join(_WEEK7, "day-2"))
sys.path.insert(0, os.path.join(_WEEK7, "day-4", "business_assistant"))

from backend.config.settings import settings
import generate_data
from src.database.models import Base, Customer
from src.crm.repository import engine, CRMRepository

def init_databases():
    print("--- Initializing Databases ---")
    
    # 1. RAG Databases (Day 2)
    # Generate real_estate.db and brochures_faqs.json in the backend directory
    # so they are easily accessible by the app.
    backend_dir = os.path.join(_WEEK7, "day-7", "backend")
    
    rag_db_path = os.path.join(backend_dir, "real_estate.db")
    rag_json_path = os.path.join(backend_dir, "brochures_faqs.json")
    
    print(f"Generating RAG data at {rag_db_path}...")
    generate_data.create_structured_data(rag_db_path)
    generate_data.create_unstructured_data(rag_json_path)
    
    # Optional: trigger the ChromaDB vectorization
    from rag_pipeline import setup_vector_rag
    print("Building ChromaDB vector store...")
    chroma_dir = os.path.join(backend_dir, "chroma_db")
    setup_vector_rag(json_path=rag_json_path, persist_directory=chroma_dir)
    print(f"ChromaDB initialized at {chroma_dir}")
    
    # 2. CRM Database (Day 4)
    print(f"Initializing CRM database at {settings.database_url}...")
    Base.metadata.create_all(bind=engine)
    
    # Add a sample customer to the CRM
    repo = CRMRepository()
    sample_phone = "03001234567"
    customer = repo.get_or_create_customer(phone=sample_phone, name="Ali Ahmed")
    print(f"Sample customer created: {customer.name} ({customer.phone})")
    repo.close()
    
    print("--- Database Initialization Complete ---")

if __name__ == "__main__":
    init_databases()
