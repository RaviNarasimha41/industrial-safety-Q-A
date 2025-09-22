import json
import requests

API_URL = "http://127.0.0.1:8000/ask"

with open("questions.json") as f:
    questions = json.load(f)

results = []

for q in questions:
    # Baseline
    resp_baseline = requests.post(API_URL, json={"q": q, "k": 3, "mode": "baseline"}).json()
    answer_baseline = resp_baseline.get("answer", None)
    
    # Hybrid reranker
    resp_hybrid = requests.post(API_URL, json={"q": q, "k": 3, "mode": "hybrid"}).json()
    answer_hybrid = resp_hybrid.get("answer", None)
    
    results.append({
        "question": q,
        "baseline_answer": answer_baseline,
        "hybrid_answer": answer_hybrid,
        "baseline_sources": [c["source_title"] for c in resp_baseline.get("contexts", [])],
        "hybrid_sources": [c["source_title"] for c in resp_hybrid.get("contexts", [])]
    })

# Save results
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Evaluation complete. Check results.json")
