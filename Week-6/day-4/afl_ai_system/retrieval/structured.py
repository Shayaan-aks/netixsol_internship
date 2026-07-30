import pandas as pd
from config import DATASET_PATH
from utils.aliases import resolve_team_alias

class StructuredRetrieval:
    def __init__(self):
        try:
            self.df = pd.read_csv(DATASET_PATH)
        except Exception:
            self.df = pd.DataFrame()

    def get_stat(self, entity_name: str, stat_type: str) -> str:
        if self.df.empty:
            return "Dataset missing."
            
        entity = resolve_team_alias(entity_name) or entity_name
        
        matches = self.df[(self.df['team'] == entity) | (self.df['player'] == entity)]
        if matches.empty:
            return f"No records found for {entity_name}."
            
        stats = matches[matches['stat_type'] == stat_type]
        if stats.empty:
            return f"No {stat_type} found for {entity_name}."
            
        res = []
        for _, row in stats.iterrows():
            res.append(f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
        return "\n".join(res)

structured_db = StructuredRetrieval()
