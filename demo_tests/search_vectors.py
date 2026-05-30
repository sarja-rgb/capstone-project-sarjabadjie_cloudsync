"""
search_vectors.py (LOCAL embeddings -> FAISS search)
Run from repo root:
    python demo_tests/search_vectors.py "Spotify music trends" --topk 5
"""
import argparse, json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", type=str)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--model", type=str, default="all-MiniLM-L6-v2")
    args = ap.parse_args()

    root = repo_root()
    index_path = root / "vectors.index"
    meta_path = root / "vectors_meta.json"

    if not index_path.exists() or not meta_path.exists():
        raise SystemExit("ERROR: vectors.index / vectors_meta.json missing (run build_vectors.py first).")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    index = faiss.read_index(str(index_path))

    model = SentenceTransformer(args.model)
    q = model.encode([args.query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

    scores, idxs = index.search(q, args.topk)

    print("=== FAISS RESULTS (LOCAL) ===")
    print(f"Query: {args.query}")

    for rank, (i, s) in enumerate(zip(idxs[0], scores[0]), start=1):
        if i < 0 or i >= len(meta):
            continue
        m = meta[i]
        print(f"{rank}. score={float(s):.4f} | row_id={m.get('row_id')} | source={m.get('source')}")
        print(f"   {m.get('preview','')[:140]}...")

    if len(meta) > 0 and len(idxs[0]) > 0 and idxs[0][0] >= 0:
        print("PASS: FAISS search returned results (LOCAL)")
    else:
        print("WARN: No results returned.")


if __name__ == "__main__":
    main()
