from langchain_core.tools import tool
from retrieval.structured import structured_db
from utils.helpers import log_retrieval

@tool
def get_team_record(team_name: str) -> str:
    """
    Retrieve the record (wins, losses, ladder position) for an AFL team.
    Example: get_team_record(team_name="Collingwood")
    """
    result = structured_db.get_team_record(team_name)
    log_retrieval(question=f"Get record for {team_name}", tool_name="get_team_record", returned_data=result)
    return result

@tool
def get_match_result(team1: str, team2: str) -> str:
    """
    Retrieve the result of a match between two AFL teams.
    Example: get_match_result(team1="Collingwood", team2="Brisbane Lions")
    """
    result = structured_db.get_match_result(team1, team2)
    log_retrieval(question=f"Get match between {team1} and {team2}", tool_name="get_match_result", returned_data=result)
    return result
