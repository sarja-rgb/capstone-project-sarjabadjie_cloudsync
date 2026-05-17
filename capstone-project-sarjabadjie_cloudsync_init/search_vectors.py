# REAL CODE GOES HERE (same full script I provided)
import os, json, argparse
import numpy as np
import faiss
from openai import OpenAI

INDEX_PATH = "vectors.index"
META_PATH = "vectors_meta.json"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--model", type=str, default="text-embedding-3-small")
    args = ap.parse_args()

    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        raise SystemExit("ERROR: vectors.index / vectors_meta.json missing (run build_vectors.py first).")

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("ERROR: OPENAI_API_KEY not set.")

    index = faiss.read_index(INDEX_PATH)
    meta = json.load(open(META_PATH, "r", encoding="utf-8"))

    client = OpenAI(api_key=key)
    q = client.embeddings.create(model=args.model, input=[args.query])
    qv = np.array(q.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(qv)

    D, I = index.search(qv, args.topk)

    print("=== FAISS RESULTS ===")
    for rank, (idx, score) in enumerate(zip(I[0], D[0]), start=1):
        m = meta[int(idx)]
        print(f"{rank}. score={score:.4f} | row_id={m['db_row_id']} | source={m['source_name']}")
        print("   " + (m["text"][:120] + "..."))

    print("PASS: FAISS search returned results")

if __name__ == "__main__":
    main()