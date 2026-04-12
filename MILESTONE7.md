# CloudSync Manager — Milestone 7 (Week 1)

**Student:** Sarja Badjie  
**Milestone:** 7 (Week 1)  
**Release Tag:** `v0.7-m7`  
**Build Name:** `CloudSyncManager_M7.zip`

---

## Direct Links
- Release: https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/releases/tag/v0.7-m7
- Direct Download: https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/releases/download/v0.7-m7/CloudSyncManager_M7.zip

## Repository Links
- Repo: https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync
- Commits: https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/commits/main
- Key commit (Milestone 7 UI demo): https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/commit/2d76d9b
- Key commit (.gitignore update): https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/commit/6be8516

## Project Management
- Trello: https://trello.com/b/J6Ouycx9/cloudsync-insight-cos650-sprint-board

## What This Build Demonstrates
- Desktop GUI supports config workflow and logging/output
- SQLite configuration persistence (loads last saved settings)
- AWS S3 connectivity test via “Test S3 Connection”
- Milestone 7 demo UI (`milestone7_ui.py`) with progress/status + completion state

## How to Run
```bash
python -m pip install -r requirements.txt
python main.py
python milestone7_ui.py
