import os
import json
import sqlite3
from typing import List, Dict, Any
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# Set up your OPENROUTER_API_KEY environment variable before running
# os.environ["OPENROUTER_API_KEY"] = "your_key_here"

# --- 1. SETUP VECTOR RAG (Unstructured) ---
def setup_vector_rag(json_path: str = "brochures_faqs.json", persist_directory: str = "./chroma_db"):
    """Loads JSON data, chunks it, and creates a ChromaDB vector store."""
    if not os.path.exists(json_path):
        print("Run generate_data.py first!")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = [Document(page_content=f"{item['title']}\n{item['content']}", metadata={"id": item['id']}) for item in data]
    
    # Chunking: Evaluating chunk sizes (e.g., 500 vs 1000)
    # We use 500 here since FAQs are generally short.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name=os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        model=os.environ.get("LLM_MODEL", "nvidia/nemotron-4-340b-instruct"),
        temperature=0.0
    )
    system_prompt = (
        "You are a helpful real estate assistant. Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. Do not hallucinate."
        "\n\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # LCEL pipeline replacing legacy create_retrieval_chain
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Return as dict to maintain compatibility with res["answer"] calls
    return rag_chain | (lambda x: {"answer": x})

# --- 2. SETUP SQL RAG (Structured) ---
def setup_sql_agent(db_path: str = "real_estate.db"):
    """Sets up an SQL agent to query the properties SQLite database."""
    if not os.path.exists(db_path):
        print("Run generate_data.py first!")
        return None
        
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        model=os.environ.get("LLM_MODEL", "nvidia/nemotron-4-340b-instruct"),
        temperature=0.0
    )
    
    agent_executor = create_sql_agent(llm, db=db, agent_type="zero-shot-react-description", verbose=True, max_iterations=4)
    return agent_executor


# --- 3. RECOMMENDATION ENGINE ---
def recommend_properties(budget: int = None, city: str = None, purpose: str = None) -> str:
    """A direct SQL query approach for recommendations without LLM overhead."""
    conn = sqlite3.connect("real_estate.db")
    cursor = conn.cursor()
    
    query = "SELECT name, price, area, bedrooms, amenities FROM properties WHERE status = 'Available'"
    params = []
    
    if budget:
        query += " AND price <= ?"
        params.append(budget)
    if city:
        query += " AND city COLLATE NOCASE = ?"
        params.append(city)
    if purpose:
        query += " AND purpose COLLATE NOCASE = ?"
        params.append(purpose)
        
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "No properties found matching your criteria."
        
    response = "Here are the recommended properties:\n"
    for r in results:
        response += f"- {r[0]} in {r[2]} ({r[3]} Beds). Price: {r[1]}. Amenities: {r[4]}\n"
    return response


# --- 4. ROUTER ---
class RAGRouter:
    def __init__(self, model_name=None, persist_directory="chroma_db"):
        self.vector_chain = setup_vector_rag(persist_directory=persist_directory)
        self.sql_agent = setup_sql_agent()
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            model=model_name or os.environ.get("LLM_MODEL", "nvidia/nemotron-4-340b-instruct"),
            temperature=0.1
        )
        
    def route_query(self, query: str) -> str:
        """Uses LLM to decide whether to route to SQL (structured) or Vector (unstructured)"""
        routing_prompt = f"""
        You are a smart router for a real estate agent.
        Determine if the user's query requires querying a SQL database (prices, availability, beds, agents, cities) 
        OR querying a Vector Database (FAQs, policies, payment plans, project descriptions, brochures).
        
        Reply strictly with either "SQL" or "VECTOR".
        
        Query: "{query}"
        """
        response = self.llm.invoke(routing_prompt).content.strip().upper()
        
        if "SQL" in response:
            print(f"Routing to: SQL Agent")
            try:
                res = self.sql_agent.invoke({"input": query})
                return res["output"]
            except Exception as e:
                return f"Error querying database: {e}"
        else:
            print(f"Routing to: Vector RAG")
            try:
                res = self.vector_chain.invoke({"input": query})
                return res["answer"]
            except Exception as e:
                return f"Error querying vector DB: {e}"

if __name__ == "__main__":
    # Test the router
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Please set OPENROUTER_API_KEY environment variable.")
    else:
        router = RAGRouter()
        
        print("\n--- Testing SQL Routing ---")
        q1 = "What is the price of the DHA Phase 8 Apartment?"
        print(f"Q: {q1}\nA: {router.route_query(q1)}")
        
        print("\n--- Testing Vector Routing ---")
        q2 = "What are the payment plans for overseas Pakistanis?"
        print(f"Q: {q2}\nA: {router.route_query(q2)}")
        
        print("\n--- Testing Recommendation Engine ---")
        print(recommend_properties(budget=60000000, city="Lahore", purpose="Sale"))
