# We simply use the MemorySaver from langgraph.checkpoint.memory in the main app.
# This file serves as a logical grouping for memory configuration if it were more complex.
from langgraph.checkpoint.memory import MemorySaver

def get_memory_saver():
    return MemorySaver()
