# CloudSync Manager — Demo/Test Run Sheet (Repo Root)

Run everything from the repo root:

```bash
cd /c/Users/sajab/capstone-project-sarjabadjie_cloudsync
```

## 1) spaCy PDF test (SoundSoar)
```bash
python spacy_pdf_test.py
notepad spacy_pdf_test_output.txt
```

## 2) spaCy → SQLite demo
```bash
python demo_text_metadata_to_sqlite.py
```

## 3) Vector store (FAISS) build + search
```bash
python build_vectors.py --limit 10
ls -lh vectors.index vectors_meta.json
python search_vectors.py "Spotify music trends" --topk 5
```

## 4) Ollama smoke test (server + generate)
PowerShell:
```powershell
ollama --version
ollama list
Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing
```
Git Bash:
```bash
python ollama_test.py
```

## 5) RAG on SoundSoar (retrieval + answer)
```bash
python rag_soundsoar_demo_fixed.py --question "What ML models are mentioned in the paper?" --topk 10
python rag_soundsoar_demo_fixed.py --question "What evaluation metrics are reported in the paper?" --topk 10
```

## 6) Optional: S3 smoke test
```bash
python s3_smoke_test.py --profile cloudsync-demo --bucket fsocloudstore1 --prefix testuploads/
```
