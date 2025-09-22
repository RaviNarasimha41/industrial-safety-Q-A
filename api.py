# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search import Searcher
from reranker import HybridReranker
import re

app = FastAPI(title="Tiny Q&A over Industrial Safety PDFs")

# CORS middleware to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize searcher and reranker
searcher = Searcher()
reranker = HybridReranker(alpha=0.7)

# Abstain thresholds
BASELINE_THRESHOLD = 0.15
HYBRID_THRESHOLD = 0.25

# Request schema
class AskRequest(BaseModel):
    q: str
    k: int = 3
    mode: str = "hybrid"  # "baseline" or "hybrid"

@app.post("/ask")
def ask(req: AskRequest):
    q = req.q
    k = req.k
    mode = req.mode.lower()

    # 1️⃣ Baseline search
    baseline = searcher.baseline_search(q, k)
    contexts = []

    if mode == "baseline":
        for r in baseline:
            contexts.append({
                "chunk_id": r["id"],
                "source_title": r["source_title"],
                "source_url": r["source_url"],
                "text": r["chunk_text"],
                "score": r["score"]
            })

        if not contexts:
            return {"answer": None, "contexts": [], "reranker_used": "baseline", "abstained": True, "reason": "no_results"}

        top = contexts[0]

        # Abstain logic
        if top["score"] < BASELINE_THRESHOLD:
            return {
                "answer": None,
                "contexts": contexts,
                "reranker_used": "baseline",
                "abstained": True,
                "reason": "low_score",
                "threshold": BASELINE_THRESHOLD
            }

        answer = top["text"][:800]
        return {"answer": answer, "contexts": contexts, "reranker_used": "baseline", "abstained": False}

    # 2️⃣ Hybrid reranker mode
    reranked = reranker.rerank(q, k=k)
    contexts = []

    for r in reranked:
        contexts.append({
            "chunk_id": r["chunk_id"],
            "source_title": r["source_title"],
            "source_url": r["source_url"],
            "text": r["chunk_text"],
            "vector_score": r["vector_score"],
            "vector_score_norm": r["vector_score_norm"],
            "keyword_score_norm": r["keyword_score_norm"],
            "final_score": r["final_score"]
        })

    if not contexts:
        return {"answer": None, "contexts": [], "reranker_used": "hybrid", "abstained": True, "reason": "no_results"}

    top = contexts[0]

    # Abstain logic for hybrid
    if top["final_score"] < HYBRID_THRESHOLD:
        return {
            "answer": None,
            "contexts": contexts,
            "reranker_used": "hybrid",
            "abstained": True,
            "reason": "low_final_score",
            "threshold": HYBRID_THRESHOLD
        }

    # Extract short answer from best chunk
    q_terms = [t.lower() for t in q.split() if len(t) > 1]
    text = top["text"]
    sents = re.split(r'(?<=[.!?])\s+', text)
    best_sent = sents[0]
    best_score = -1
    for s in sents:
        cnt = sum(s.lower().count(t) for t in q_terms)
        if cnt > best_score:
            best_score = cnt
            best_sent = s

    answer = best_sent.strip() if best_score > 0 else text[:800].strip()

    return {"answer": answer, "contexts": contexts, "reranker_used": "hybrid", "abstained": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
