import pandas as pd
from config import DATASET_PATH
from utils.helpers import fuzzy_match

class StructuredRetrieval:
    def __init__(self):
        self.df = pd.read_csv(DATASET_PATH)

    def get_player_stats(self, player_name: str) -> str:
        player_df = self.df[self.df['entity_type'] == 'player']
        players = player_df['player'].dropna().unique().tolist()
        matched_player = fuzzy_match(player_name, players)
        
        stats = player_df[player_df['player'] == matched_player]
        if stats.empty:
            return f"No statistics found for player {player_name}."
        
        result = []
        for _, row in stats.iterrows():
            result.append(f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
        return f"Stats for {matched_player}:\n" + "\n".join(result)

    def get_team_record(self, team_name: str) -> str:
        team_df = self.df[self.df['entity_type'] == 'team']
        teams = team_df['team'].dropna().unique().tolist()
        matched_team = fuzzy_match(team_name, teams)
        
        stats = team_df[team_df['team'] == matched_team]
        if stats.empty:
            return f"No records found for team {team_name}."
        
        result = []
        for _, row in stats.iterrows():
            result.append(f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
        return f"Records for {matched_team}:\n" + "\n".join(result)

    def get_match_result(self, team1: str, team2: str) -> str:
        match_df = self.df[self.df['entity_type'] == 'match']
        teams = match_df['team'].dropna().unique().tolist()
        matched_team1 = fuzzy_match(team1, teams)
        
        matches = match_df[match_df['team'] == matched_team1]
        if matches.empty:
            return f"No matches found involving {team1}."
            
        result = []
        for _, row in matches.iterrows():
            if 'result' in match_df.columns and pd.notna(row['result']):
               result.append(f"{row['context']} {row['season']}: {row['result']}")
        
        if not result:
             return f"Match result details missing for {team1} vs {team2}."
        return "\n".join(result)

structured_db = StructuredRetrieval()
