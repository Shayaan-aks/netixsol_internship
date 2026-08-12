import pandas as pd
from config import DATASET_PATH

class StructuredRetrieval:
    def __init__(self):
        try:
            self.df = pd.read_csv(DATASET_PATH)
        except Exception:
            self.df = pd.DataFrame()

    def get_stat(self, entity_name: str, stat_type: str) -> str:
        if self.df.empty:
            return "Dataset is currently unavailable."

        matches = self.df[
            (self.df['team'].str.contains(entity_name, case=False, na=False)) |
            (self.df['player'].str.contains(entity_name, case=False, na=False))
        ]
        if matches.empty:
            return f"No records found for '{entity_name}' in the AFL dataset."

        if stat_type:
            stats = matches[matches['stat_type'] == stat_type]
            if not stats.empty:
                res = []
                for _, row in stats.iterrows():
                    res.append(f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
                return "\n".join(res)

        # No stat_type match — return ALL stats for entity
        res = []
        for _, row in matches.iterrows():
            res.append(
                f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})"
            )
        return "\n".join(res) if res else f"No stats found for '{entity_name}'."

    def get_all_for_entity(self, entity_name: str) -> str:
        """Return all rows matching entity name (team or player)."""
        if self.df.empty:
            return "Dataset is currently unavailable."
        matches = self.df[
            (self.df['team'].str.contains(entity_name, case=False, na=False)) |
            (self.df['player'].str.contains(entity_name, case=False, na=False))
        ]
        if matches.empty:
            return f"No records found for '{entity_name}' in the AFL dataset."
        res = []
        for _, row in matches.iterrows():
            res.append(f"{row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
        return "\n".join(res)

    def get_team_summary(self, team_name: str) -> dict:
        """Return a dict of key stats for a team — used for predictions."""
        if self.df.empty:
            return {}
        rows = self.df[self.df['team'].str.contains(team_name, case=False, na=False)]
        summary = {}
        for _, row in rows.iterrows():
            summary[row['stat_type']] = row['value']
        return summary

    def get_dataset_context(self) -> str:
        """Return a full readable dump of the dataset for LLM reasoning."""
        if self.df.empty:
            return "Dataset unavailable."
        lines = []
        for _, row in self.df.iterrows():
            entity = row['player'] if pd.notna(row.get('player')) else row['team']
            lines.append(f"- {entity} | {row['stat_type']}: {row['value']} ({row['context']} {row['season']})")
        return "\n".join(lines)

structured_db = StructuredRetrieval()
