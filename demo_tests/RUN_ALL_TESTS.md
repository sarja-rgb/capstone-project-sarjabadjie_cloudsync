# CloudSync Demo – Run All Tests (Quick Script)

## IMPORTANT
- Run **commands in the terminal**, not inside `.py` files.
- Use **Git Bash** for the `cd /c/...` paths shown below.
- Use **PowerShell** for `Invoke-WebRequest` and `$env:OPENAI_API_KEY=...` style commands.

---

## Git Bash (Repo root)

```bash
cd /c/Users/sajab/capstone-project-sarjabadjie_cloudsync || exit

# 1) spaCy PDF test (creates spacy_pdf_test_output.txt)
python demo_tests/spacy_pdf_test.py
notepad spacy_pdf_test_output.txt

# 2) SQLite demo write
python demo_text_metadata_to_sqlite.py

# 3) Build + search vector store (LOCAL embeddings)
rm -f vectors.index vectors_meta.json
python demo_tests/build_vectors.py --limit 10
ls -lh vectors.index vectors_meta.json
python demo_tests/search_vectors.py "Spotify music trends" --topk 5

# 4) Ollama test (server + model)
python demo_tests/ollama_test.py --model llama3.2:1b

# 5) RAG demo (SoundSoar.pdf -> retrieve -> Ollama answer)
python demo_tests/rag_soundsoar_demo_fixed.py --question "What ML models are mentioned in the paper?" --topk 10
python demo_tests/rag_soundsoar_demo_fixed.py --question "What evaluation metrics are reported in the paper?" --topk 10

# 6) (Optional) S3 smoke test
python demo_tests/s3_smoke_test.py --profile cloudsync-demo --bucket fsocloudstore1 --prefix testuploads/
```

---

## PowerShell (Ollama sanity check)

```powershell
ollama --version
ollama list
Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing
```
