from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Dict, List

import faiss
import fitz  # PyMuPDF
import numpy as np
import requests
import streamlit as st
import docx2txt
from sentence_transformers import SentenceTransformer


APP_TITLE = "CloudSync Multi-Document RAG (Demo)"
DEFAULT_SURVEY_URL = "https://www.surveymonkey.com/r/TC6L3GF"


@dataclass
class Chunk:
    doc_name: str
    chunk_id: int
    text: str


def init_state() -> None:
    if "docs" not in st.session_state:
        st.session_state.docs: Dict[str, List[Chunk]] = {}

    if "chunk_lookup" not in st.session_state:
        st.session_state.chunk_lookup: List[Chunk] = []

    if "index" not in st.session_state:
        st.session_state.index = None


@st.cache_resource(show_spinner=False)
def get_embed_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def clean_text(text: str) -> str:
    return " ".join((text or "").replace("\x00", " ").split())


def extract_pdf(uploaded_file) -> str:
    pdf_bytes = uploaded_file.getvalue()
    text_parts = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))

    return clean_text("\n".join(text_parts))


def extract_docx(uploaded_file) -> str:
    suffix = ".docx"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name

    try:
        return clean_text(docx2txt.process(temp_path))
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def extract_txt(uploaded_file) -> str:
    return clean_text(uploaded_file.getvalue().decode("utf-8", errors="replace"))


def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_pdf(uploaded_file)

    if name.endswith(".docx"):
        return extract_docx(uploaded_file)

    if name.endswith(".txt"):
        return extract_txt(uploaded_file)

    return ""


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def build_index(all_chunks: List[Chunk], model: SentenceTransformer) -> faiss.Index:
    texts = [chunk.text for chunk in all_chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Normalized embeddings + inner product = cosine similarity
    index.add(embeddings)

    return index


def score_to_match_percent(score: float) -> float:
    """
    FAISS IndexFlatIP with normalized embeddings returns similarity.
    Higher score is better. This converts it into a readable percentage.
    """
    try:
        score = float(score)
    except Exception:
        return 0.0

    percent = score * 100.0
    return max(0.0, min(100.0, percent))


def retrieve_chunks(question: str, scope: str, topk: int) -> List[dict]:
    model = get_embed_model()

    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype("float32")

    max_search = min(max(topk * 5, topk), len(st.session_state.chunk_lookup))
    distances, indexes = st.session_state.index.search(query_embedding, max_search)

    results = []

    for score, idx in zip(distances[0], indexes[0]):
        if idx < 0:
            continue

        chunk = st.session_state.chunk_lookup[idx]

        if scope != "All documents" and chunk.doc_name != scope:
            continue

        results.append(
            {
                "source": chunk.doc_name,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "score": float(score),
                "match_percent": score_to_match_percent(float(score)),
            }
        )

    results = sorted(results, key=lambda item: item["match_percent"], reverse=True)
    return results[:topk]


def make_prompt(question: str, retrieved: List[dict]) -> str:
    context_blocks = []

    for rank, item in enumerate(retrieved, start=1):
        context_blocks.append(
            f"[{rank}] Source: {item['source']} | "
            f"Match: {item['match_percent']:.1f}% | "
            f"Chunk: {item['chunk_id']}\n"
            f"{item['text']}"
        )

    context = "\n\n".join(context_blocks)

    return f"""
You are helping answer questions about uploaded documents.

Use only the document context below. If the answer is not supported by the context, say that the answer is not found in the uploaded documents.

Question:
{question}

Document context:
{context}

Answer clearly and briefly. Mention the source document name when useful.
""".strip()


def call_ollama(prompt: str, model_name: str, server_url: str) -> str:
    url = server_url.rstrip("/") + "/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(url, json=payload, timeout=180)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()


def call_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "Answer using only the retrieved document context.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content.strip()


def generate_answer(question: str, retrieved: List[dict], answer_mode: str, ollama_model: str, ollama_server: str) -> str:
    prompt = make_prompt(question, retrieved)

    try:
        if answer_mode.startswith("OpenAI"):
            return call_openai(prompt)

        return call_ollama(prompt, ollama_model, ollama_server)

    except Exception as error:
        fallback = " ".join(item["text"] for item in retrieved[:2])
        if fallback:
            return (
                "The local generator could not finish the answer, but the retrieval step worked. "
                "Here is the strongest retrieved evidence: "
                + fallback[:900]
                + f"\n\nGenerator error: {error}"
            )

        return f"No answer could be generated. Error: {error}"


def render_evidence(evidence_box, retrieved: List[dict]) -> None:
    with evidence_box:
        if not retrieved:
            st.info("No citation evidence was retrieved for this question.")
            return

        for rank, item in enumerate(retrieved, start=1):
            label = (
                f"{rank}) [{item['source']}] — "
                f"{item['match_percent']:.1f}% match — "
                f"chunk {item['chunk_id']}"
            )

            with st.expander(label, expanded=(rank == 1)):
                st.write(item["text"])


def main() -> None:
    st.set_page_config(
        page_title="CloudSync RAG Demo",
        page_icon="💬",
        layout="wide",
    )

    init_state()

    st.sidebar.title("CloudSync RAG Demo")

    survey_url = st.sidebar.text_input(
        "Feedback survey URL (SurveyMonkey)",
        value=DEFAULT_SURVEY_URL,
    )

    answer_mode = st.sidebar.selectbox(
        "Answer mode",
        ["Local (FAISS + Ollama)", "OpenAI (FAISS + OpenAI)"],
    )

    topk = st.sidebar.slider("Top-K chunks", min_value=3, max_value=12, value=6)

    ollama_model = st.sidebar.text_input("Ollama model", value="llama3.2:1b")
    ollama_server = st.sidebar.text_input("Ollama server", value="http://localhost:11434")

    st.sidebar.divider()
    st.sidebar.subheader("Upload documents")

    uploaded_files = st.sidebar.file_uploader(
        "Upload PDF / DOCX / TXT (multiple allowed)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        all_chunks: List[Chunk] = []
        st.session_state.docs = {}

        for uploaded_file in uploaded_files:
            try:
                text = extract_text(uploaded_file)
                parts = chunk_text(text)
                chunks = [
                    Chunk(doc_name=uploaded_file.name, chunk_id=i, text=part)
                    for i, part in enumerate(parts)
                ]

                st.session_state.docs[uploaded_file.name] = chunks
                all_chunks.extend(chunks)

            except Exception as error:
                st.sidebar.error(f"Could not process {uploaded_file.name}: {error}")

        if all_chunks:
            with st.spinner("Building document index..."):
                model = get_embed_model()
                st.session_state.index = build_index(all_chunks, model)
                st.session_state.chunk_lookup = all_chunks

            st.sidebar.success(
                f"Indexed {len(all_chunks)} chunks across {len(st.session_state.docs)} documents."
            )

    st.title("💬 CloudSync Multi-Document RAG (Demo)")
    st.caption(
        "Upload docs → select a doc (or all) → ask questions → see match %, source documents, citations/evidence, and feedback link."
    )

    left_col, right_col = st.columns([1.45, 1])

    with left_col:
        document_options = ["All documents"] + list(st.session_state.docs.keys())

        scope = st.selectbox(
            "Choose document scope",
            document_options,
            index=0,
        )

        st.subheader("Chat")

        question = st.text_input(
            "Ask a question about your uploaded documents...",
            placeholder="Example: Which document has the strongest match for skills or experience?",
        )

        ask_clicked = st.button("Ask", type="primary", use_container_width=True)

        st.info(
            "Tester note: This demo runs retrieval locally using FAISS + local embeddings. "
            "Local mode uses Ollama on this machine for generation."
        )

        answer_placeholder = st.empty()
        feedback_placeholder = st.empty()

    with right_col:
        st.subheader("Citations / Evidence")
        st.caption("Retrieved chunks are sorted by match percentage from highest to lowest.")
        evidence_box = st.container()

    if ask_clicked:
        if not uploaded_files or st.session_state.index is None or not st.session_state.chunk_lookup:
            st.warning("Please upload documents first.")
            return

        if not question.strip():
            st.warning("Please enter a question.")
            return

        retrieved = retrieve_chunks(question.strip(), scope, topk)

        if not retrieved:
            st.warning("No relevant chunks found for that document scope.")
            return

        with st.spinner("Generating answer..."):
            answer = generate_answer(
                question=question.strip(),
                retrieved=retrieved,
                answer_mode=answer_mode,
                ollama_model=ollama_model,
                ollama_server=ollama_server,
            )

        with answer_placeholder.container():
            st.subheader("Answer")
            st.write(answer)

        with feedback_placeholder.container():
            st.subheader("Feedback")
            st.link_button("Give Feedback (Survey)", survey_url)

        render_evidence(evidence_box, retrieved)


if __name__ == "__main__":
    main()
