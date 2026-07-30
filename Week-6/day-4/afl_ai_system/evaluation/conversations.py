import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.checkpoint.memory import MemorySaver
from graph.graph import graph_builder
from config import EVAL_REPORT_PATH

def evaluate_conversations():
    memory = MemorySaver()
    agent = graph_builder.compile(checkpointer=memory)
    
    conversations = [
        {"id": "conv_1", "queries": ["How many wins did Collingwood have in 2023?", "Who will win Collingwood vs Brisbane?"]},
        {"id": "conv_2", "queries": ["Who is the Prime Minister?", "Okay, what about AFL? Who will be the top player for Carlton?"]}
    ]
    
    log = []
    
    for conv in conversations:
        config = {"configurable": {"thread_id": conv["id"]}}
        for q in conv["queries"]:
            try:
                response = agent.invoke({"messages": [("user", q)]}, config)
                final_msg = response.get("final_response", "Error: No response")
                log.append(f"User ({conv['id']}): {q}\nAgent: {final_msg}\n")
            except Exception as e:
                log.append(f"User ({conv['id']}): {q}\nAgent Error: {e}\n")
                
    with open(EVAL_REPORT_PATH, "w") as f:
        f.write("# Conversation Evaluation\n\n")
        f.write("\n".join(log))
        
    print(f"Conversation evaluation complete. See {EVAL_REPORT_PATH}")

if __name__ == "__main__":
    evaluate_conversations()
