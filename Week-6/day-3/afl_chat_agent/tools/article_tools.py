from langchain_core.tools import tool
from retrieval.semantic import retrieve_news
from utils.helpers import log_retrieval

@tool
def retrieve_match_article(query: str) -> str:
    """
    Retrieve narrative information or news articles about AFL matches, players, or events.
    Use this for qualitative questions rather than exact statistics.
    Example: retrieve_match_article(query="Who won the Norm Smith medal in 2023?")
    """
    result = retrieve_news(query)
    log_retrieval(question=f"Search news: {query}", tool_name="retrieve_match_article", returned_data=result)
    return result
