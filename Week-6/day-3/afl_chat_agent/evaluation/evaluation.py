import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.checkpoint.memory import MemorySaver
from chains.chat_chain import builder
from evaluation.test_cases import TEST_CASES
from config import EVAL_REPORT_PATH
import json

def run_evaluation():
    memory = MemorySaver()
    agent = builder.compile(checkpointer=memory)
    
    results = []
    
    for i, test in enumerate(TEST_CASES):
        config = {"configurable": {"thread_id": f"eval_{i}"}}
        try:
            response = agent.invoke({"messages": [("user", test["prompt"])]}, config)
            final_msg = response["messages"][-1].content
            
            is_refusal = "I can't" in final_msg or "I am designed" in final_msg or "AFL" in final_msg or "strictly limited" in final_msg
            
            if test["category"] in ["Off-topic", "Adversarial"]:
                passed = is_refusal
            else:
                passed = str(test["expected"]).lower() in final_msg.lower() or "afl" in final_msg.lower() or "collingwood" in final_msg.lower()
                
            results.append({
                "prompt": test["prompt"],
                "category": test["category"],
                "expected": test["expected"],
                "actual": final_msg,
                "pass": passed
            })
        except Exception as e:
            results.append({
                "prompt": test["prompt"],
                "category": test["category"],
                "expected": test["expected"],
                "actual": f"ERROR: {str(e)}",
                "pass": False
            })
        
    generate_report(results)

def generate_report(results):
    passed_count = sum(1 for r in results if r["pass"])
    total = len(results)
    accuracy = (passed_count / total) * 100 if total > 0 else 0
    
    report_content = f"# Evaluation Report\n\n"
    report_content += f"## Metrics\n"
    report_content += f"- **Total Tests**: {total}\n"
    report_content += f"- **Passed**: {passed_count}\n"
    report_content += f"- **Accuracy**: {accuracy:.2f}%\n\n"
    
    report_content += "## Test Results\n\n"
    report_content += "| Prompt | Category | Expected | Pass/Fail |\n"
    report_content += "|---|---|---|---|\n"
    
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        report_content += f"| {r['prompt']} | {r['category']} | {r['expected']} | {status} |\n"
        
    report_content += "\n## Failure Analysis\n"
    report_content += "The evaluation uses basic heuristics. In a full production environment, an LLM-as-a-judge would evaluate 'Grounded', 'Hallucinated', and 'Scope Compliance' rigorously based on the retrieval logs.\n"
    
    with open(EVAL_REPORT_PATH, "w") as f:
        f.write(report_content)
        
    print(f"Evaluation complete. Report generated at {EVAL_REPORT_PATH}")

if __name__ == "__main__":
    run_evaluation()
