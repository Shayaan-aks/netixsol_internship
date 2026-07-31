from langchain_core.tools import tool
from retrieval.structured import structured_db

@tool
def structured_retrieval_tool(entity_name: str, stat_type: str) -> str:
    """Retrieve structured statistics for an AFL team or player. Stat types can be: wins, losses, goals, disposals, score, ladder_position."""
    return structured_db.get_stat(entity_name, stat_type)
