from langchain_core.tools import tool
from retrieval.structured import structured_db
from utils.helpers import log_retrieval

@tool
def get_player_stats(player_name: str) -> str:
    """
    Retrieve the statistics (disposals, goals, etc.) for a specific AFL player.
    Example: get_player_stats(player_name="Nick Daicos")
    """
    result = structured_db.get_player_stats(player_name)
    log_retrieval(question=f"Get stats for {player_name}", tool_name="get_player_stats", returned_data=result)
    return result
