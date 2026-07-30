from langchain_core.tools import tool
from retrieval.structured import structured_db
from retrieval.semantic import retrieve_news
from utils.helpers import log_tool

@tool
def get_structured_stat(entity_name: str, stat_type: str) -> str:
    """
    Retrieve structured statistics for a team or player (e.g. wins, losses, goals, disposals).
    """
    res = structured_db.get_stat(entity_name, stat_type)
    log_tool("get_structured_stat", {"entity": entity_name, "stat": stat_type}, res)
    return res

@tool
def retrieve_news_article(query: str) -> str:
    """
    Retrieve semantic information for narrative questions.
    """
    res = retrieve_news(query)
    log_tool("retrieve_news_article", {"query": query}, res)
    return res
