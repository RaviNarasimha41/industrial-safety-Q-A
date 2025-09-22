# search.py
import sqlite3
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DB_PATH = "chunks.db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class Searcher:
    def __init__(self):
        # Load chunks from SQLite
        self.conn = sqlite3.connect(DB_PATH)
        c = self.conn.cursor()
        c.execute("SELECT id, chunk_text, source_title, source_url FROM chunks")
        rows = c.fetchall()
        self.chunks = [
            {"id": r[0], "chunk_text": r[1], "source_title": r[2], "source_url": r[3]}
            for r in rows
        ]
        # Load embedding model
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        # Compute embeddings
        self.embeddings = self.model.encode(
            [c["chunk_text"] for c in self.chunks], convert_to_numpy=True
        )
        # Build FAISS index
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)

    def baseline_search(self, query, k=3):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, k)
        results = []
        for score, idx in zip(D[0], I[0]):
            chunk = self.chunks[idx]
            results.append({
                "id": chunk["id"],
                "chunk_text": chunk["chunk_text"],
                "source_title": chunk["source_title"],
                "source_url": chunk["source_url"],
                "score": float(score)
            })
        return results
