import os
from rag_pipeline import RAGRouter
from langchain_google_genai import ChatGoogleGenerativeAI

def evaluate_hallucinations():
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        print("Please set GEMINI_API_KEY environment variable.")
        return

    router = RAGRouter()
    judge_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
    
    # 20 Test Questions
    # 10 Structured, 10 Unstructured (with some intended to test hallucination via out-of-scope)
    questions = [
        # Structured
        ("What is the price of the Gulberg Greens Villa?", "SQL", "65000000"),
        ("Who is the agent for the Clifton Flat?", "SQL", "Zara Ahmed"),
        ("How many bedrooms does the Bahria Town House have?", "SQL", "5"),
        ("Are there any 10-bedroom houses available?", "SQL", "No/None"),
        ("What properties are available for rent in Islamabad?", "SQL", "Blue Area Office Space"),
        ("Is the Clifton Flat currently available?", "SQL", "Rented/No"),
        ("What are the amenities of the DHA Phase 8 Apartment?", "SQL", "Gym, Backup Generator"),
        ("What is the cheapest property available?", "SQL", "Clifton Flat"),
        ("Show me properties over 100 million.", "SQL", "None"),
        ("Who is the agent for Blue Area Office Space?", "SQL", "Ali Khan"),
        
        # Unstructured
        ("What is the down payment for overseas Pakistanis?", "VECTOR", "20%"),
        ("Is a NICOP required for overseas booking?", "VECTOR", "Yes"),
        ("What is the transfer fee policy?", "VECTOR", "1%"),
        ("Does Gulberg Greens have a hospital?", "VECTOR", "Yes"),
        ("Is there a theme park in Bahria Town Lahore?", "VECTOR", "Yes"),
        ("Does Bahria Town Karachi have a zoo?", "VECTOR", "Don't know/Not mentioned"), # Hallucination test
        ("What discount do remittances get?", "VECTOR", "2%"),
        ("Are there farmhouses in Gulberg Greens?", "VECTOR", "Yes"),
        ("What is the policy for late installments?", "VECTOR", "Don't know/Not mentioned"), # Hallucination test
        ("Does the overseas plan apply to locals?", "VECTOR", "Don't know/Not mentioned"), # Hallucination test
    ]

    results = []
    
    for idx, (query, expected_route, expected_fact) in enumerate(questions):
        print(f"[{idx+1}/20] Testing: {query}")
        
        # Get Answer
        answer = router.route_query(query)
        
        # Judge prompt to check if answer is grounded and contains expected fact
        judge_prompt = f"""
        Question: {query}
        Expected Fact/Outcome: {expected_fact}
        System Answer: {answer}
        
        Evaluate the System Answer based on:
        1. Grounding: Did the system answer based ONLY on the context/expected outcome, or did it invent details?
        2. Accuracy: Did it retrieve and provide the correct expected fact?
        3. Hallucination: Did it provide a confident, false answer for something out of scope (like a zoo in Karachi or late installment policy)?
        
        Respond with a JSON object ONLY, in this format:
        {{"grounded": 1 or 0, "accurate": 1 or 0, "hallucinated": 1 or 0}}
        """
        
        try:
            eval_res = judge_llm.invoke(judge_prompt).content
            import json
            metrics = json.loads(eval_res.replace("```json","").replace("```","").strip())
            results.append(metrics)
        except Exception as e:
            print(f"Eval Error: {e}")
            results.append({"grounded": 0, "accurate": 0, "hallucinated": 1})

    # Calculate metrics
    total = len(results)
    grounded_rate = sum(r["grounded"] for r in results) / total * 100
    accuracy_rate = sum(r["accurate"] for r in results) / total * 100
    hallucination_rate = sum(r["hallucinated"] for r in results) / total * 100

    print("\n" + "="*40)
    print("EVALUATION METRICS:")
    print(f"Grounding Rate:     {grounded_rate:.1f}%")
    print(f"Retrieval Accuracy: {accuracy_rate:.1f}%")
    print(f"Hallucination Rate: {hallucination_rate:.1f}%")
    print("="*40)

if __name__ == "__main__":
    evaluate_hallucinations()
