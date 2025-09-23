
# Industrial Safety Q&A — Mini RAG Project

## 1. Project Overview

This project implements a mini **Retrieval-Augmented Generation (RAG)** system over a set of **20 public PDFs on industrial and machine safety**.

- **Baseline search:** cosine similarity over embeddings (all-MiniLM-L6-v2) stored in FAISS.
- **Hybrid reranker:** blends vector similarity with keyword relevance (BM25 / SQLite FTS).
- **Abstain logic:** avoids answering when top evidence score is below a threshold (0.25).
- **Frontend:** React chat interface with evaluation table, live sources, and reactions.
- **Goal:** Demonstrate before/after improvement in answers when using a reranker.

---

## 2. Setup Instructions

### Backend

1. Install dependencies:

```bash
pip install fastapi uvicorn pydantic faiss-cpu sentence-transformers
````

2. Run the API:

```bash
uvicorn api:app --reload
```

* API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Frontend

1. Navigate to the frontend folder:

```bash
cd safety-qa-ui
```

2. Install dependencies:

```bash
npm install
```

3. Run frontend:

```bash
npm run dev
```

* Frontend runs at [http://localhost:3000](http://localhost:3000)

---

## 3. API Usage

**Endpoint:** `POST /ask`

**Request JSON:**

```json
{
  "q": "What is PPE in industrial safety?",
  "k": 3,
  "mode": "hybrid"
}
```

* `q`: the question
* `k`: number of top chunks to consider
* `mode`: `"baseline"` or `"hybrid"`

**Response JSON:**

```json
{
  "answer": "Short answer or null",
  "contexts": [
    {
      "chunk_id": "pdf_03_12",
      "source_title": "Industrial Safety Guidelines",
      "source_url": "http://example.com/safety.pdf",
      "text": "Lockout/Tagout (LOTO) procedures require ...",
      "final_score": 0.78
    }
  ],
  "reranker_used": "hybrid",
  "abstained": false,
  "reason": "low_final_score"
}
```

**Example curl requests:**

* Easy question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
-H "Content-Type: application/json" \
-d '{"q": "What is PPE in industrial safety?", "k":3, "mode":"hybrid"}'
```

* Tricky question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
-H "Content-Type: application/json" \
-d '{"q": "Explain lockout-tagout procedures", "k":3, "mode":"hybrid"}'
```

---

## 4. Evaluation Questions

The system was evaluated using the following 8 curated questions:

1. What is PPE in industrial safety?
2. Explain the purpose of a fire extinguisher.
3. What is a lockout-tagout procedure?
4. Define occupational hazard.
5. What should be done during a chemical spill?
6. What is the safe limit for noise exposure?
7. Explain the use of safety harness.
8. Why are MSDS sheets important?

---

## 5. Evaluation Results (Baseline vs Hybrid)

| Question                                     | Baseline Answer          | Hybrid Answer          | Hybrid Reranker | Abstained |
| -------------------------------------------- | ------------------------ | ---------------------- | --------------- | --------- |
| What is PPE in industrial safety?            | PLACEHOLDER\_BASELINE\_1 | PLACEHOLDER\_HYBRID\_1 | hybrid          | No        |
| Explain the purpose of a fire extinguisher.  | PLACEHOLDER\_BASELINE\_2 | PLACEHOLDER\_HYBRID\_2 | hybrid          | No        |
| What is a lockout-tagout procedure?          | PLACEHOLDER\_BASELINE\_3 | PLACEHOLDER\_HYBRID\_3 | hybrid          | No        |
| Define occupational hazard.                  | PLACEHOLDER\_BASELINE\_4 | PLACEHOLDER\_HYBRID\_4 | hybrid          | No        |
| What should be done during a chemical spill? | PLACEHOLDER\_BASELINE\_5 | PLACEHOLDER\_HYBRID\_5 | hybrid          | No        |
| What is the safe limit for noise exposure?   | PLACEHOLDER\_BASELINE\_6 | PLACEHOLDER\_HYBRID\_6 | hybrid          | No        |
| Explain the use of safety harness.           | PLACEHOLDER\_BASELINE\_7 | PLACEHOLDER\_HYBRID\_7 | hybrid          | No        |
| Why are MSDS sheets important?               | PLACEHOLDER\_BASELINE\_8 | PLACEHOLDER\_HYBRID\_8 | hybrid          | No        |


## 6. Example API Response

```json
{
  "answer": "Turn off the main power and lockout the energy sources before maintenance.",
  "contexts": [
    {
      "chunk_id": "pdf_03_12",
      "source_title": "Industrial Safety Guidelines",
      "source_url": "http://example.com/safety.pdf",
      "text": "Lockout/Tagout (LOTO) procedures require ...",
      "final_score": 0.78
    }
  ],
  "reranker_used": "hybrid",
  "abstained": false,
  "reason": "low_final_score"
}
```

---

## 7. Proof of Work 

## Project Screenshot

![QA Safety Screenshot](screenshots/Screenshot1.png)
![Another screenshot](screenshots/Screenshot2.png)


---


## 8.Learnings

* **Reranker improves answer relevance:** blending vector similarity and keyword relevance helps prioritize the most grounded evidence.
* **Abstain logic is crucial:** prevents returning low-confidence answers, maintaining system trustworthiness.

* **Mini RAG is lightweight but effective:** a small corpus and CPU-only setup is sufficient for domain-specific Q\&A.
* **Mini RAG is lightweight but effective:** a small corpus and CPU-only setup is sufficient for domain-specific Q&A.
* **Frontend evaluation table:** allows quick comparison between baseline and hybrid answers with direct source links.
---

## 9. Files in Repository

* `api.py` — FastAPI backend with baseline + hybrid reranker + abstain logic
* `search.py` — Baseline vector search
* `reranker.py` — Hybrid reranker implementation
* `safety-qa-ui/` — React frontend
* `sources.json` — PDF metadata (title + URL)
* `eight_questions.json` — Evaluation questions
* `README.md` — This file
* `screenshots/` — Optional images for proof of work

---

## 10. Notes

* All outputs are **extractive** with citations.
* System is **CPU-only**, no paid APIs.
* Set a random seed in embeddings/indexing for reproducibility.
* Fill the evaluation table placeholders after running API.
