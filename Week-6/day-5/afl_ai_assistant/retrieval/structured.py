import pandas as pd
from config import DATASET_PATH

class StructuredRetrieval:
    def __init__(self):
        try:
            self.df = pd.read_csv(DATASET_PATH)
        except:
            self.df = pd.DataFrame()
            
    def get_stat(self, entity_name: str, stat_type: str) -> str:
        if self.df.empty: return "Dataset missing."
        
        matches = self.df[(self.df['team'].str.contains(entity_name, case=False, na=False)) | (self.df['player'].str.contains(entity_name, case=False, na=False))]
        if matches.empty: return f"No records found for {entity_name}."
        
        stats = matches[matches['stat_type'] == stat_type]
        if stats.empty: return f"No {stat_type} found for {entity_name}."
        
        res = []
        for _, row in stats.iterrows():
            res.append(f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
        return "\n".join(res)

structured_db = StructuredRetrieval()
