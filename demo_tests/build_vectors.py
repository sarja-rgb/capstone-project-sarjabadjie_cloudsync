"""
build_vectors.py (LOCAL embeddings -> FAISS)
Reads rows from cloudsync_metadata.db (ai_text_metadata) and builds:
- vectors.index
- vectors_meta.json

Run from repo root:
    python demo_tests/build_vectors.py --limit 10
"""
import argparse, json, sqlite3
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def fetch_rows(limit: int):
    db = repo_root() / "cloudsync_metadata.db"
    if not db.exists():
        raise SystemExit(f"ERROR: DB not found: {db}")

    con = sqlite3.connect(str(db))
    cur = con.cursor()

    # Schema (your DB): id, source_name, created_utc, summary, keywords, entities
    q = """
    SELECT id, source_name, summary
    FROM ai_text_metadata
    ORDER BY id DESC
    LIMIT ?
    """
    rows = cur.execute(q, (limit,)).fetchall()
    con.close()

    if not rows:
        raise SystemExit("ERROR: ai_text_metadata has no rows. Run: python demo_text_metadata_to_sqlite.py")

    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10, help="How many DB rows to embed")
    ap.add_argument("--model", type=str, default="all-MiniLM-L6-v2", help="SentenceTransformer model")
    args = ap.parse_args()

    rows = fetch_rows(args.limit)
    texts = [r[2] if r[2] else "" for r in rows]

    print("Embedding rows (LOCAL)...")
    model = SentenceTransformer(args.model)
    emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=True, normalize_embeddings=True)

    # Cosine similarity with normalized vectors => inner product index
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb.astype(np.float32))

    root = repo_root()
    index_path = root / "vectors.index"
    meta_path = root / "vectors_meta.json"

    faiss.write_index(index, str(index_path))

    meta = []
    for (row_id, source_name, summary) in rows:
        meta.append({
            "row_id": int(row_id),
            "source": str(source_name),
            "preview": (summary or "")[:180],
        })

    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("PASS: vectors.index and vectors_meta.json created (LOCAL embeddings)")
    print(f"Index: {index_path}")
    print(f"Meta : {meta_path}")


if __name__ == "__main__":
    main()
