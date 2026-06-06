import requests

API_URL = "http://localhost:8000/api/rag"

# Define validation ground-truth evaluation pairs
test_suite = [
    {
        "question": "How often should I save my vector database?",
        "expected_keywords": ["snapshot", "24 hours", "crashes"]
    },
    {
        "question": "What metrics do serving systems monitor?",
        "expected_keywords": ["latency", "error", "anomaly"]
    }
]

def run_evaluation():
    print("?? Launching Automated System Retrieval Evaluation Testing...")
    passed_tests = 0
    
    for idx, test in enumerate(test_suite, start=1):
        print(f"\n[Test #{idx}] Evaluating: '{test['question']}'")
        try:
            res = requests.post(API_URL, json={"question": test["question"]})
            if res.status_code == 200:
                data = res.json()
                context = data["matched_context"].lower()
                
                # Evaluation metric check (Keyword match verification inside context block)
                matched = [kw for kw in test["expected_keywords"] if kw in context]
                accuracy_ratio = len(matched) / len(test["expected_keywords"])
                
                print(f" -> Retrieval Score: {data['similarity_score']:.4f}")
                print(f" -> Keyword Relevance Score: {accuracy_ratio * 100:.1f}%")
                
                if accuracy_ratio >= 0.5:
                    print(" ? TEST PASSED")
                    passed_tests += 1
                else:
                    print(" ? TEST FAILED - Irrelevant context node pulled.")
            else:
                print(" ? TEST FAILED - Backend API hit an error.")
        except Exception as e:
            print(f" ? Connection Failure to API: {e}")
            
    print(f"\n=====================================")
    print(f"FINAL RAG PLATFORM SCORE: {passed_tests}/{len(test_suite)} PASSED")
    print(f"=====================================")

if __name__ == "__main__":
    run_evaluation()
