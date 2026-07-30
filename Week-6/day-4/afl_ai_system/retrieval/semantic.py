import os
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from config import ARTICLES_DIR, OPENAI_API_KEY

def build_vector_store():
    documents = []
    if not os.path.exists(ARTICLES_DIR) or not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        return None
        
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(ARTICLES_DIR, filename))
            documents.extend(loader.load())
            
    if not documents:
        return None
        
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    
    vector_store = Chroma.from_documents(docs, OpenAIEmbeddings(api_key=OPENAI_API_KEY))
    return vector_store

try:
    vector_store = build_vector_store()
except:
    vector_store = None

def retrieve_news(query: str) -> str:
    if vector_store is None:
        return "Semantic retrieval is currently unavailable."
        
    docs = vector_store.similarity_search(query, k=2)
    if not docs:
        return "No relevant news found."
    
    res = []
    for doc in docs:
        res.append(f"Source: {doc.metadata.get('source', 'Unknown')}\nSnippet: {doc.page_content}")
        
    return "\n\n".join(res)
