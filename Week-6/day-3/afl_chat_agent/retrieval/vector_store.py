import os
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from config import ARTICLES_DIR, OPENAI_API_KEY

def build_vector_store():
    documents = []
    if not os.path.exists(ARTICLES_DIR):
        return None
        
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(ARTICLES_DIR, filename))
            documents.extend(loader.load())
            
    if not documents:
        return None
        
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    
    if not OPENAI_API_KEY:
        return None # Prevent failure if no API key is provided yet
        
    vector_store = Chroma.from_documents(docs, OpenAIEmbeddings())
    return vector_store

try:
    vector_store = build_vector_store()
except Exception as e:
    vector_store = None
