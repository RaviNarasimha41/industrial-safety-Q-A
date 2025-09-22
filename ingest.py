import os
import io
import json
import sqlite3
import zipfile
from tqdm import tqdm
from PyPDF2 import PdfReader

DB_PATH = "chunks.db"
DATA_DIR = "data"
ZIP_PATH = os.path.join(DATA_DIR, "industrial-safety-pdfs.zip")
SOURCES_JSON = os.path.join(DATA_DIR, "sources.json")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text = ""
    with io.BytesIO(pdf_bytes) as pdf_stream:
        reader = PdfReader(pdf_stream)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def chunk_text(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    start = 0
    while start < len(text):
        end = start + size
        yield text[start:end].strip()
        start += size - overlap


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_title TEXT,
            source_url TEXT,
            chunk_text TEXT
        )"""
    )
    conn.commit()
    return conn


def main():
    if not os.path.exists(ZIP_PATH):
        raise FileNotFoundError(f"ZIP file not found at {ZIP_PATH}")

    with open(SOURCES_JSON, "r") as f:
        raw_sources = json.load(f)

    conn = init_db()
    c = conn.cursor()

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        # Only real PDFs, skip __MACOSX
        files = [f for f in z.namelist() if f.lower().endswith(".pdf") and not f.startswith("__MACOSX")]
        print(f"Found {len(files)} PDFs to process.")

        for idx, fname in enumerate(tqdm(files)):
            raw = z.read(fname)
            try:
                text = extract_text_from_pdf_bytes(raw)
            except Exception as e:
                print(f"[WARN] Failed to extract {fname}: {e}")
                continue

            if not text.strip():
                print(f"[WARN] No text extracted from {fname}")
                continue

            fname_only = os.path.basename(fname)
            # Map by order to sources.json
            if idx < len(raw_sources):
                source_info = {
                    "title": raw_sources[idx].get("title", fname_only),
                    "url": raw_sources[idx].get("url")
                }
            else:
                source_info = {"title": fname_only, "url": None}

            for chunk in chunk_text(text):
                c.execute(
                    "INSERT INTO chunks (source_title, source_url, chunk_text) VALUES (?, ?, ?)",
                    (source_info["title"], source_info["url"], chunk),
                )

    conn.commit()
    conn.close()
    print(f"[INFO] Finished writing chunks to {DB_PATH}")


if __name__ == "__main__":
    main()
