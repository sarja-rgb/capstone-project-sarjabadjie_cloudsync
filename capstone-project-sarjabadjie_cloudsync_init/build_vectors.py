# REAL CODE GOES HERE (same full script I provided)
import os, json, sqlite3, argparse
import numpy as np
import faiss
from openai import OpenAI

DB_PATH = "cloudsync_metadata.db"
TABLE = "ai_text_metadata"
INDEX_PATH = "vectors.index"
META_PATH = "vectors_meta.json"

def fetch_rows(limit: int):
    con = sqlite3.connect(DB_PATH)
    try:
        rows = con.execute(f"SELECT id, source_name, summary FROM {TABLE} ORDER BY id DESC").fetchall()
        return rows[:limit]
    finally:
        con.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--model", type=str, default="text-embedding-3-small")
    args = ap.parse_args()

    if not os.path.exists(DB_PATH):
        raise SystemExit("ERROR: cloudsync_metadata.db not found (run demo_text_metadata_to_sqlite.py first).")

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("ERROR: OPENAI_API_KEY not set.")

    rows = fetch_rows(args.limit)
    texts = []
    meta = []

    for row_id, source_name, summary in rows:
        s = (summary or "").strip()
        if not s:
            continue
        texts.append(s)
        meta.append({"db_row_id": row_id, "source_name": source_name, "text": s})

    if not texts:
        raise SystemExit("ERROR: No summary text found in ai_text_metadata.")

    client = OpenAI(api_key=key)
    resp = client.embeddings.create(model=args.model, input=texts)
    vecs = np.array([d.embedding for d in resp.data], dtype="float32")

    faiss.normalize_L2(vecs)
    dim = vecs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vecs)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("PASS: vectors.index and vectors_meta.json created")

if __name__ == "__main__":
    main()