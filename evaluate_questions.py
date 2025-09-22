import json
import requests

# -------------------------
# Config
# -------------------------
API_URL = "http://127.0.0.1:8000/ask"
QUESTIONS_FILE = "eight_questions.json"  # put in project root or public folder
K = 3  # top-k
MODES = ["baseline", "hybrid"]  # run baseline first, then reranker

# -------------------------
# Load questions
# -------------------------
with open(QUESTIONS_FILE, "r") as f:
    questions = json.load(f)

# -------------------------
# Evaluation function
# -------------------------
def ask_question(q, mode):
    payload = {"q": q, "k": K, "mode": mode}
    try:
        res = requests.post(API_URL, json=payload)
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer") or ""
        abstained = data.get("abstained", False)
        reranker_used = data.get("reranker_used", "N/A")
        return answer, abstained, reranker_used
    except Exception as e:
        print(f"[ERROR] Question '{q}' failed: {e}")
        return "Error", True, "N/A"

# -------------------------
# Run evaluation
# -------------------------
results = []

for q in questions:
    row = {"Question": q}
    for mode in MODES:
        answer, abstained, reranker_used = ask_question(q, mode)
        row[f"{mode}_answer"] = answer
        row[f"{mode}_abstained"] = "Yes" if abstained else "No"
    results.append(row)

# -------------------------
# Print markdown table
# -------------------------
print("\n## 8-Question Evaluation Results\n")
headers = ["Question"] + [f"{m}_{h}" for m in MODES for h in ["answer", "abstained"]]
print("| " + " | ".join(headers) + " |")
print("|" + "|".join(["---"] * len(headers)) + "|")
for r in results:
    print("| " + " | ".join(r.get(h, "") for h in headers) + " |")


with open("evaluation_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n[INFO] Evaluation completed. Results saved to evaluation_results.json")
