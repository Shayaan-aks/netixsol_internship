from langgraph.checkpoint.memory import MemorySaver

# Instantiate the shared memory checkpointer
memory_saver = MemorySaver()

def get_memory_saver():
    return memory_saver
