Vector Store Scripts (FAISS) - CloudSync Insight

Files:
- build_vectors.py   -> builds vectors.index + vectors_meta.json from SQLite ai_text_metadata summary column
- search_vectors.py  -> queries FAISS and prints top-k matches

Run (Git Bash, from repo folder):
cd /c/Users/sajab/capstone-project-sarjabadjie_cloudsync

# Install deps (once)
pip install faiss-cpu numpy openai

# Set key (each session)
export OPENAI_API_KEY="YOUR_KEY_HERE"

# Ensure SQLite has ai_text_metadata rows
python demo_text_metadata_to_sqlite.py

# Build index
python build_vectors.py --limit 10
ls -lh vectors.index vectors_meta.json

# Search
python search_vectors.py "Spotify music trends" --topk 5
