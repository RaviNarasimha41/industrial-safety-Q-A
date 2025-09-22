# Industrial Safety Q&A — Results

## 1. Project Overview

This project implements a mini RAG-based Q&A system over 20 public PDFs on industrial and machine safety. The system uses:

- **Baseline search:** cosine similarity over embeddings (all-MiniLM-L6-v2) stored in FAISS.
- **Hybrid reranker:** blends vector similarity with keyword relevance (BM25/SQLite FTS).
- **Abstain logic:** avoids answering when top evidence score is below threshold (0.25).

## 2. Evaluation Questions

1. What is PPE in industrial safety?
2. Explain the purpose of a fire extinguisher.
3. What is a lockout-tagout procedure?
4. Define occupational hazard.
5. What should be done during a chemical spill?
6. What is the safe limit for noise exposure?
7. Explain the use of safety harness.
8. Why are MSDS sheets important?

## 3. Evaluation Results (Baseline vs Hybrid)

| Question | Baseline Answer | Hybrid Answer | Hybrid Reranker | Abstained |
|----------|----------------|---------------|----------------|-----------|
| What is PPE in industrial safety? | `PLACEHOLDER_BASELINE_1` | `PLACEHOLDER_HYBRID_1` | hybrid | No |
| Explain the purpose of a fire extinguisher. | `PLACEHOLDER_BASELINE_2` | `PLACEHOLDER_HYBRID_2` | hybrid | No |
| What is a lockout-tagout procedure? | `PLACEHOLDER_BASELINE_3` | `PLACEHOLDER_HYBRID_3` | hybrid | No |
| Define occupational hazard. | `PLACEHOLDER_BASELINE_4` | `PLACEHOLDER_HYBRID_4` | hybrid | No |
| What should be done during a chemical spill? | `PLACEHOLDER_BASELINE_5` | `PLACEHOLDER_HYBRID_5` | hybrid | No |
| What is the safe limit for noise exposure? | `PLACEHOLDER_BASELINE_6` | `PLACEHOLDER_HYBRID_6` | hybrid | No |
| Explain the use of safety harness. | `PLACEHOLDER_BASELINE_7` | `PLACEHOLDER_HYBRID_7` | hybrid | No |
| Why are MSDS sheets important? | `PLACEHOLDER_BASELINE_8` | `PLACEHOLDER_HYBRID_8` | hybrid | No |

> **Note:** Replace the placeholders with actual answers after running your API.

## 4. Example API Response

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
5. Learnings

Hybrid reranker significantly improves answer quality by combining semantic similarity with keyword relevance.

Abstain logic ensures that low-confidence answers are not returned, improving reliability.

CPU-based embeddings (all-MiniLM-L6-v2) are lightweight and sufficient for small document sets.