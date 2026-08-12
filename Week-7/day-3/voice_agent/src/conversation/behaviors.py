import random
import asyncio

class ConversationalBehaviors:
    """Injects human-like imperfections and behaviors into the stream."""
    
    FILLERS = ["Hmm...", "Ji...", "Acha...", "Ek second..."]
    ACKNOWLEDGEMENTS = ["Ji sir.", "Bilkul.", "Right.", "Samajh gaya."]
    LAUGHS = ["Haha", "Hehe"]
    
    @classmethod
    def get_acknowledgement(cls) -> str:
        """Return a quick acknowledgement to play instantly while LLM thinks."""
        return random.choice(cls.ACKNOWLEDGEMENTS)
        
    @classmethod
    def get_filler_for_pause(cls) -> str:
        """Returns a hesitation sound for complex questions."""
        return random.choice(cls.FILLERS)
        
    @classmethod
    async def simulate_thinking_pause(cls, difficulty: str = "normal"):
        """Pauses async execution for 300-800ms before generating to sound natural."""
        if difficulty == "hard":
            await asyncio.sleep(random.uniform(0.3, 0.8))
        else:
            await asyncio.sleep(0.1)
