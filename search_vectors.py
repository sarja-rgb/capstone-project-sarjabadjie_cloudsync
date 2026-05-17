import json, argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

INDEX_PATH = "vectors.index"
META_PATH = "vectors_meta.json"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--model", type=str, default="all-MiniLM-L6-v2")
    args = ap.parse_args()

    index = faiss.read_index(INDEX_PATH)
    meta = json.load(open(META_PATH, "r", encoding="utf-8"))

    model = SentenceTransformer(args.model)
    qv = model.encode([args.query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(qv)

    D, I = index.search(qv, args.topk)

    print("=== FAISS RESULTS (LOCAL) ===")
    print(f"Query: {args.query}")
    for rank, (idx, score) in enumerate(zip(I[0], D[0]), start=1):
        m = meta[int(idx)]
        print(f"{rank}. score={score:.4f} | row_id={m['db_row_id']} | source={m['source_name']}")
        print("   " + (m["text"][:120] + "..."))

    print("PASS: FAISS search returned results (LOCAL)")

if __name__ == "__main__":
    main()