# Milestone 8 Submission – CloudSync Insight

For Milestone 8, I am submitting the latest functional build of my capstone project, **CloudSync Insight**. This milestone reflects continued development progress aligned with my **High-Level Design Document (HLDD)** scope and ongoing advisor guidance. The current build demonstrates meaningful functional progress toward the core Week 2 roadmap goals by extending the existing GUI and AWS S3 connectivity workflow into a more functional sync prototype.

## Build Version for Evaluation
- **Build Name:** `CloudSyncManager_M8.zip`
- **Repository:** https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync
- **Branch:** `main`

## Documentation
- **Milestone 8 Notes:**  
  https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/blob/main/MILESTONE8.md

## Direct Build Link
- **Build ZIP in Repo:**  
  https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/blob/main/CloudSyncManager_M8.zip
- **Direct Download (Raw):**  
  https://raw.githubusercontent.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/main/CloudSyncManager_M8.zip

## Version Control & Evidence
- **Key Commit (Milestone 8 Notes):**  
  https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/commit/e2c6681
- **Key Commit (Milestone 8 Build ZIP):**  
  https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/commit/29541cf
- **Commit History (main):**  
  https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync/commits/main

I have attached screenshot evidence showing my latest push/commit activity and confirmation that the Milestone 8 build has been posted for evaluation.

## Project Management
- **Trello Board:**  
  https://trello.com/b/J6Ouycx9/cloudsync-insight-cos650-sprint-board

## Build Functionality & Technical Progress
This Milestone 8 build demonstrates progress toward the HLDD Week 2 outcome of **S3 adapter + local scan + one-way sync prototype + tests**.

This build includes:
- working desktop GUI workflow for sync setup and testing
- configuration persistence using the local SQLite metadata database
- AWS S3 connectivity testing through the UI using a safe list operation
- local folder scan support for identifying files to sync
- one-way sync prototype progress from local storage to AWS S3
- output/log feedback in the GUI for status, progress, and controlled error handling

## How to Run
1. Install dependencies:
   `python -m pip install -r requirements.txt`
2. Run the main GUI:
   `python main.py`
3. Enter the local folder, S3 bucket, optional prefix, AWS profile, and region.
4. Click **Save Configuration**.
5. Click **Test S3 Access**.
6. Run the local scan / sync prototype workflow in the GUI.

## Screencast
- **Screencast:** `[Paste screencast link here]`

The screencast demonstrates the Milestone 8 build running, highlights the current GUI workflow, shows configuration saving, AWS S3 access testing, local scan / sync prototype progress, and briefly explains the technical work completed and next steps.
