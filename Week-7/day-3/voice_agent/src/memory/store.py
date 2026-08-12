from typing import Dict, List, Any

class MemoryStore:
    """
    Abstracts session memory (short-term) and persistent memory (long-term).
    For testing, this uses in-memory dicts, but the interface allows dropping in Redis/Postgres.
    """
    def __init__(self):
        self._session_state: Dict[str, Any] = {}
        self._history: List[Dict[str, str]] = []
        
    def add_interaction(self, role: str, content: str):
        self._history.append({"role": role, "content": content})
        
    def get_context_window(self, max_messages: int = 10) -> List[Dict[str, str]]:
        return self._history[-max_messages:]
        
    def update_state(self, key: str, value: Any):
        """Update Conversation State (e.g., Qualification, Budget)"""
        self._session_state[key] = value
        
    def get_state(self, key: str) -> Any:
        return self._session_state.get(key)

    def get_full_state_summary(self) -> str:
        """Returns string representation of known facts about the user."""
        if not self._session_state:
            return "No prior context."
        return ", ".join([f"{k}: {v}" for k, v in self._session_state.items()])
