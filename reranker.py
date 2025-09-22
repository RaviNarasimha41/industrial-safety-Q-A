import numpy as np
from search import Searcher  # make sure Searcher is the class in search.py

class HybridReranker:
    """
    Simple hybrid reranker:
    final_score = alpha * vector_score_norm + (1-alpha) * keyword_score_norm
    """

    def __init__(self, alpha=0.7):
        self.alpha = alpha
        self.searcher = Searcher()

    def _keyword_score(self, chunk_text, query):
        """Simple keyword overlap score"""
        q_terms = [t.lower() for t in query.split() if len(t) > 1]
        if not q_terms:
            return 0.0
        text = chunk_text.lower()
        matches = sum(text.count(t) for t in q_terms)
        return min(1.0, matches / len(q_terms))

    def rerank(self, query, k=3):
        baseline = self.searcher.baseline_search(query, k*5)  # overfetch for reranking
        if not baseline:
            return []

        # Normalize vector scores
        vec_scores = np.array([max(0, r["score"]) for r in baseline])
        vec_scores_norm = vec_scores / vec_scores.max() if vec_scores.max() > 0 else vec_scores

        reranked = []
        for i, r in enumerate(baseline):
            keyword_score = self._keyword_score(r["chunk_text"], query)
            final_score = self.alpha * vec_scores_norm[i] + (1 - self.alpha) * keyword_score
            reranked.append({
                "chunk_id": r["id"],
                "chunk_text": r["chunk_text"],
                "source_title": r["source_title"],
                "source_url": r["source_url"],
                "vector_score": r["score"],
                "vector_score_norm": float(vec_scores_norm[i]),
                "keyword_score_norm": float(keyword_score),
                "final_score": float(final_score)
            })

        # Sort by final score descending
        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked[:k]
