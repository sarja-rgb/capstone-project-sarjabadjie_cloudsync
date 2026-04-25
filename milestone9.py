
"""
milestone9.py - Milestone 9 verification runner (CLI)

Run:
  python milestone9.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    print("=== CloudSync Manager - Milestone 9 Verification ===")
    print(f"Repo root: {repo_root}")

    required_files = [
        "main.py",
        "requirements.txt",
        "config_db.py",
        "s3_client.py",
        "MILESTONE9.md",
    ]

    print("\n[1] Required file check:")
    missing = []
    for name in required_files:
        p = repo_root / name
        ok = p.exists() and p.is_file()
        print(f" - {name}: {'OK' if ok else 'MISSING'}")
        if not ok:
            missing.append(name)

    print("\n[2] Build ZIP check:")
    build_zip = repo_root / "CloudSyncManager_M9.zip"
    print(f" - CloudSyncManager_M9.zip: {'FOUND' if build_zip.exists() else 'NOT FOUND'}")

    print("\n[3] Environment check:")
    print(f" - Python: {sys.version.split()[0]}")
    print(f" - Platform: {sys.platform}")
    print(f" - Working dir: {Path.cwd()}")

    print("\n[4] AWS env vars present (optional):")
    for v in ["AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION"]:
        print(f" - {v}: {'SET' if os.getenv(v) else 'NOT SET'}")

    if missing:
        print("\nRESULT: FAIL (missing required files above)")
        return 1

    print("\nRESULT: PASS (Milestone 9 verification checks completed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())