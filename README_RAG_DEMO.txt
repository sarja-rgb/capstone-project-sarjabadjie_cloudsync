RAG SoundSoar Demo (Fixed)

This demo always shows:
- PDF text extraction
- Chunking
- LOCAL embeddings (sentence-transformers)
- FAISS top-k retrieval with scores

Optional:
- If Ollama is installed and running (http://localhost:11434), it will also generate an answer.
- If Ollama is NOT available, it prints a PASS line and exits cleanly (no crash).

Install deps (from repo folder):
pip install -U pymupdf sentence-transformers faiss-cpu numpy requests

Run (from repo folder):
python rag_soundsoar_demo_fixed.py --question "What ML models are mentioned in the paper?"

To save retrieved chunks as JSON:
python rag_soundsoar_demo_fixed.py --save_debug
