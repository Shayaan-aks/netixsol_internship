from retrieval.vector_store import vector_store

def retrieve_news(query: str) -> str:
    """
    Retrieve semantic information for narrative questions using embeddings.
    """
    if vector_store is None:
        return "Semantic retrieval is currently unavailable."
        
    docs = vector_store.similarity_search(query, k=2)
    if not docs:
        return "No relevant news found."
    
    res = []
    for doc in docs:
        res.append(f"Source: {doc.metadata.get('source', 'Unknown')}\nSnippet: {doc.page_content}")
        
    return "\n\n".join(res)
