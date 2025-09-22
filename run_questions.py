# run_questions.py
import requests, json, time
from pprint import pprint

# Ensure API is running at localhost:8000
API = "http://127.0.0.1:8000/ask"

with open("eight_questions.json", "r", encoding="utf8") as f:
    qs = json.load(f)

results = []
for q in qs:
    print("Q:", q)
    # baseline
    b = requests.post(API, json={"q": q, "k": 3, "mode": "baseline"}).json()
    h = requests.post(API, json={"q": q, "k": 3, "mode": "hybrid"}).json()
    results.append({"q": q, "baseline": b, "hybrid": h})
    time.sleep(0.2)

# pretty print results to a file
with open("run_results.json", "w", encoding="utf8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Saved run_results.json. Summary:")
for r in results:
    print("Question:", r["q"])
    print(" baseline abstained:", r["baseline"].get("abstained", False))
    print(" hybrid abstained:", r["hybrid"].get("abstained", False))
    print(" baseline answer:", (r["baseline"]["answer"] or "")[:200].replace("\n"," "))
    print(" hybrid answer:", (r["hybrid"]["answer"] or "")[:200].replace("\n"," "))
    print("-"*60)

