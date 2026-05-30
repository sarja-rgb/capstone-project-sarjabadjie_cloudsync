"""
rag_soundsoar_demo_fixed.py
RAG demo: read SoundSoar.pdf -> chunk -> embed (LOCAL) -> retrieve top-k -> ask Ollama.

Run from repo root:
    python demo_tests/rag_soundsoar_demo_fixed.py --question "What ML models are mentioned in the paper?" --topk 10
"""
import argparse, json, re, sys
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

import urllib.request


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_pdf_text(pdf_path: Path) -> str:
    if fitz is None:
        raise SystemExit("ERROR: PyMuPDF not installed. pip install pymupdf")
    doc = fitz.open(str(pdf_path))
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    doc.close()
    return "\n".join(parts)


def chunk_text(text: str, max_chars=1200, overlap=150):
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+max_chars]
        chunks.append(chunk)
        i += max_chars - overlap
    return chunks


def ollama_generate(prompt: str, server="http://localhost:11434", model="llama3.2:1b", timeout=120) -> str:
    url = server.rstrip("/") + "/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        j = json.loads(resp.read().decode("utf-8"))
    return (j.get("response") or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--topk", type=int, default=10)
    ap.add_argument("--embed_model", default="all-MiniLM-L6-v2")
    ap.add_argument("--ollama_server", default="http://localhost:11434")
    ap.add_argument("--ollama_model", default="llama3.2:1b")
    args = ap.parse_args()

    root = repo_root()
    pdf = root / "SoundSoar.pdf"
    if not pdf.exists():
        raise SystemExit(f"ERROR: Missing {pdf}")

    print("Reading PDF...")
    text = read_pdf_text(pdf)
    chunks = chunk_text(text, max_chars=1200, overlap=150)
    print(f"Chunked into {len(chunks)} chunks.")

    print("Embedding chunks (LOCAL)...")
    model = SentenceTransformer(args.embed_model)
    X = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=True).astype(np.float32)

    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)

    q = model.encode([args.question], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    scores, idxs = index.search(q, args.topk)

    print("\n=== QUESTION ===")
    print(args.question)

    print("\n=== TOP-K RETRIEVAL ===")
    context_parts = []
    for rank, (i, s) in enumerate(zip(idxs[0], scores[0]), start=1):
        snippet = chunks[int(i)][:220].replace("\n", " ")
        print(f"{rank}. score={float(s):.4f} | chunk={int(i)} | {snippet}...")
        context_parts.append(chunks[int(i)])

    context = "\n\n---\n\n".join(context_parts)
    prompt = (
        "You are helping with a class demo. Answer the question using ONLY the context.\n"
        "If the answer is not in the context, say: Not found in provided context.\n\n"
        f"QUESTION:\n{args.question}\n\n"
        f"CONTEXT:\n{context}\n\n"
        "ANSWER:"
    )

    print("\nCalling local LLM (Ollama)...")
    answer = ollama_generate(prompt, server=args.ollama_server, model=args.ollama_model)

    print("\n=== ANSWER (OLLAMA) ===")
    print(answer if answer else "(empty)")

    log = root / "rag_soundsoar_log.txt"
    log.write_text(
        f"Q: {args.question}\n\nTOPK={args.topk}\n\nANSWER:\n{answer}\n",
        encoding="utf-8"
    )
    print("PASS: Retrieval + LLM answer completed.")
    print(f"Saved log: {log}")


if __name__ == "__main__":
    main()
