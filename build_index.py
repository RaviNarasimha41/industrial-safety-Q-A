import sqlite3
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = "chunks.db"
INDEX_PATH = "faiss.index"
META_PATH = "id_map.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, chunk_text FROM chunks")
    rows = c.fetchall()
    conn.close()

    ids = []
    texts = []
    for row in rows:
        ids.append(row[0])
        texts.append(row[1])

    print(f"[INFO] Encoding {len(texts)} chunks...")

    # Load model & create embeddings
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # Create FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product = cosine if vectors normalized
    index.add(embeddings)

    # Save index
    faiss.write_index(index, INDEX_PATH)

    # Save mapping from FAISS idx -> chunk_id
    with open(META_PATH, "w") as f:
        json.dump(ids, f)

    print(f"[INFO] FAISS index built with {len(ids)} vectors.")


if __name__ == "__main__":
    main()
