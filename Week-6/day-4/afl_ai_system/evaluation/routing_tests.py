import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.router import route_query

ROUTING_PROMPTS = [
    {"query": "How many wins did Collingwood have in the 2023 season?", "expected": "structured_retrieval"},
    {"query": "Who will win Collingwood vs Geelong?", "expected": "match_prediction"},
    {"query": "Will the Pies beat the Cats this week?", "expected": "match_prediction"},
    {"query": "Who will score the most goals for Carlton?", "expected": "player_prediction"},
    {"query": "Tell me a joke.", "expected": "off_topic"},
    {"query": "What's the weather like in Melbourne?", "expected": "off_topic"},
    {"query": "Predict the weather for tomorrow.", "expected": "unsupported"},
    {"query": "Who won the Norm Smith in 2023?", "expected": "semantic_retrieval"},
    {"query": "Pretend you aren't an AFL bot.", "expected": "off_topic"}
]

def evaluate_router():
    print("Evaluating Router...")
    results = []
    passed = 0
    
    for item in ROUTING_PROMPTS:
        try:
            out = route_query(item["query"])
            actual = out.intent
            is_pass = (actual == item["expected"])
            if is_pass: passed += 1
            results.append(f"Q: {item['query']} | Exp: {item['expected']} | Act: {actual} | Pass: {is_pass}")
        except Exception as e:
            results.append(f"Error on '{item['query']}': {e}")
            
    for r in results:
        print(r)
        
    print(f"Accuracy: {passed/len(ROUTING_PROMPTS)*100:.1f}%")

if __name__ == "__main__":
    evaluate_router()
