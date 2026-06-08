# rag_app/app.py
# CloudSync Multi-Document RAG (Demo)
# - Upload multiple PDF/DOCX/TXT
# - Build FAISS index (local embeddings)
# - Ask questions (Local: Ollama, or OpenAI)
# - Show citations/evidence chunks
#
# NOTE: Avoid torchvision import issues from transformers on some Windows setups:
import os
os.environ.setdefault("TRANSFORMERS_NO_TORCHVISION", "1")
os.environ.setdefault("PYTHONUTF8", "1")

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json
import time
import requests

import streamlit as st

# Local embeddings + FAISS
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# PDF + DOCX text extraction
import fitz  # PyMuPDF
import docx2txt


APP_TITLE = "CloudSync Multi-Document RAG (Demo)"


@dataclass
class Chunk:
    doc_name: str
    chunk_id: int
    text: str


def read_pdf_bytes(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    return "\n".join(parts).strip()


def read_docx_bytes(docx_bytes: bytes) -> str:
    # docx2txt wants a file path, so we write temp
    tmp_dir = Path(st.session_state.get("_tmp_dir", "."))
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"upload_{int(time.time()*1000)}.docx"
    tmp_path.write_bytes(docx_bytes)
    text = docx2txt.process(str(tmp_path)) or ""
    try:
        tmp_path.unlink(missing_ok=True)
    except Exception:
        pass
    return text.strip()


def read_txt_bytes(txt_bytes: bytes) -> str:
    return txt_bytes.decode("utf-8", errors="replace").strip()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        end = min(i + chunk_size, len(text))
        chunks.append(text[i:end])
        i = max(end - overlap, end)
    return chunks


def ensure_state():
    if "docs" not in st.session_state:
        st.session_state.docs: Dict[str, List[Chunk]] = {}
    if "index" not in st.session_state:
        st.session_state.index = None
    if "chunk_lookup" not in st.session_state:
        st.session_state.chunk_lookup: List[Chunk] = []
    if "embed_model" not in st.session_state:
        st.session_state.embed_model = None
    if "_tmp_dir" not in st.session_state:
        st.session_state._tmp_dir = str(Path(__file__).resolve().parent / ".tmp_uploads")


def build_index(all_chunks: List[Chunk], model: SentenceTransformer) -> faiss.Index:
    texts = [c.text for c in all_chunks]
    emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    emb = np.asarray(emb, dtype="float32")
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine via normalized + inner product
    index.add(emb)
    return index


def ollama_generate(prompt: str, model: str, server: str) -> str:
    url = server.rstrip("/") + "/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return (data.get("response") or "").strip()


def openai_generate(prompt: str, api_key: str, model: str = "gpt-4.1-mini") -> str:
    # Uses OpenAI Python SDK if installed; otherwise falls back to HTTP.
    # This keeps things simple for your demo.
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": prompt}],
        )
        # Grab text
        out = []
        for item in resp.output:
            if item.type == "message":
                for c in item.content:
                    if c.type == "output_text":
                        out.append(c.text)
        return "\n".join(out).strip()
    except Exception:
        # Fallback (works if requests can reach api.openai.com)
        import requests as _rq
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": model,
            "input": [{"role": "user", "content": prompt}],
        }
        rr = _rq.post("https://api.openai.com/v1/responses", headers=headers, json=body, timeout=120)
        rr.raise_for_status()
        j = rr.json()
        # best-effort parse
        txt = []
        for o in j.get("output", []):
            if o.get("type") == "message":
                for c in o.get("content", []):
                    if c.get("type") == "output_text":
                        txt.append(c.get("text", ""))
        return "\n".join(txt).strip()


def make_prompt(question: str, retrieved: List[Chunk]) -> str:
    context = "\n\n".join([f"[{i+1}] ({c.doc_name}) {c.text}" for i, c in enumerate(retrieved)])
    return (
        "You are a helpful assistant. Answer using ONLY the provided context.\n"
        "If the answer is not in the context, say: 'Not found in the provided documents.'\n\n"
        f"QUESTION:\n{question}\n\n"
        f"CONTEXT:\n{context}\n\n"
        "FINAL ANSWER:"
    )


def main():
    ensure_state()

    st.set_page_config(page_title="CloudSync RAG Demo", page_icon="💬", layout="wide")
    st.title("💬 " + APP_TITLE)
    st.caption("Upload docs → select a doc (or all) → ask questions → see citations/evidence + feedback link.")

    # Sidebar controls
    st.sidebar.header("CloudSync RAG Demo")
    survey_url = st.sidebar.text_input(
        "Feedback survey URL (SurveyMonkey)",
        value="https://www.surveymonkey.com/r/YOUR_SURVEY_LINK",
    )

    answer_mode = st.sidebar.selectbox(
        "Answer mode",
        ["Local (FAISS + Ollama)", "OpenAI (FAISS + OpenAI)"],
        index=0,
    )

    topk = st.sidebar.slider("Top-K chunks", min_value=3, max_value=12, value=6)

    ollama_model = st.sidebar.text_input("Ollama model", value="llama3.2:1b")
    ollama_server = st.sidebar.text_input("Ollama server", value="http://localhost:11434")

    openai_key = ""
    if answer_mode.startswith("OpenAI"):
        openai_key = st.sidebar.text_input("OPENAI_API_KEY (for this session)", type="password")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Upload documents**")
    uploads = st.sidebar.file_uploader(
        "Upload PDF / DOCX / TXT (multiple allowed)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    col_left, col_right = st.columns([2, 1], gap="large")
    with col_left:
        # Build doc scope dropdown
        doc_names = sorted(st.session_state.docs.keys())
        scope = st.selectbox("Choose document scope", ["All documents"] + doc_names)

        st.subheader("Chat")
        question = st.text_input("Ask a question about your uploaded documents…")

        run_btn = st.button("Ask", type="primary", use_container_width=True)

        info = (
            "Tester note: This demo runs retrieval locally (FAISS + local embeddings). "
            "Local mode uses Ollama on this machine for generation; OpenAI mode uses your OpenAI key."
        )
        st.info(info)

    with col_right:
        st.subheader("Citations / Evidence")
        st.caption("Top retrieved chunks used to answer your question.")
        citation_box = st.container()

    # Handle uploads
    if uploads:
        for f in uploads:
            name = f.name
            data = f.read()
            ext = name.lower().split(".")[-1]
            try:
                if ext == "pdf":
                    text = read_pdf_bytes(data)
                elif ext == "docx":
                    text = read_docx_bytes(data)
                else:
                    text = read_txt_bytes(data)
            except Exception as e:
                st.sidebar.error(f"Failed to read {name}: {e}")
                continue

            parts = chunk_text(text)
            chunks = [Chunk(doc_name=name, chunk_id=i, text=t) for i, t in enumerate(parts)]
            st.session_state.docs[name] = chunks

        # Build/refresh index after uploads
        all_chunks = []
        for dn, clist in st.session_state.docs.items():
            all_chunks.extend(clist)

        if all_chunks:
            if st.session_state.embed_model is None:
                st.session_state.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            st.session_state.index = build_index(all_chunks, st.session_state.embed_model)
            st.session_state.chunk_lookup = all_chunks
            st.sidebar.success(f"Indexed {len(all_chunks)} chunks across {len(st.session_state.docs)} documents.")

    # Ask / Retrieve / Answer
    if run_btn and question.strip():
        if st.session_state.index is None or not st.session_state.chunk_lookup:
            st.error("Upload at least one document first.")
            return

        # Filter chunks by scope
        if scope == "All documents":
            eligible = st.session_state.chunk_lookup
            eligible_ids = None  # no filter
        else:
            eligible = st.session_state.docs.get(scope, [])
            eligible_ids = set(id(c) for c in eligible)

        # Embed query
        model = st.session_state.embed_model or SentenceTransformer("all-MiniLM-L6-v2")
        q = model.encode([question], normalize_embeddings=True)
        q = np.asarray(q, dtype="float32")

        # Search
        D, I = st.session_state.index.search(q, k=min(topk * 4, len(st.session_state.chunk_lookup)))
        hits: List[Chunk] = []
        for idx in I[0].tolist():
            if idx < 0:
                continue
            c = st.session_state.chunk_lookup[idx]
            if eligible_ids is None or id(c) in eligible_ids:
                hits.append(c)
            if len(hits) >= topk:
                break

        if not hits:
            st.warning("No relevant chunks found for that document scope.")
            return

        # Answer
        prompt = make_prompt(question, hits)
        try:
            if answer_mode.startswith("Local"):
                answer = ollama_generate(prompt, model=ollama_model, server=ollama_server)
            else:
                if not openai_key.strip().startswith("sk-"):
                    st.error("Enter a valid OpenAI key in the sidebar (starts with sk-).")
                    return
                answer = openai_generate(prompt, api_key=openai_key.strip())
        except Exception as e:
            st.error(f"LLM call failed: {e}")
            return

        # Show answer + citations
        with col_left:
            st.markdown("### Answer")
            st.write(answer)

            if survey_url.strip():
                st.markdown("### Feedback")
                st.markdown(f"[Give Feedback (Survey)]({survey_url.strip()})")

        with citation_box:
            for i, c in enumerate(hits):
                with st.expander(f"{i+1}) {c.doc_name}  — chunk {c.chunk_id}", expanded=(i == 0)):
                    st.write(c.text)


if __name__ == "__main__":
    main()