from pathlib import Path
import sys
import platform
from datetime import datetime

REQUIRED_FILES = [
    "main.py",
    "requirements.txt",
    "README.md",
    "MILESTONE11.md",
    "SoundSoar.pdf",
    "performance_cpu_m10_ui.html",
    "performance_cpu_main.html",
    "milestone11_ui.py",
]

ZIP_FILE = "CloudSyncManager_M11.zip"

def check_file(path: Path) -> str:
    return "OK" if path.exists() else "MISSING"

def main():
    root = Path.cwd()

    print("=== CloudSync Manager - Milestone 11 Verification ===")
    print(f"Run time: {datetime.now()}")
    print(f"Repo root: {root}")
    print()

    print("[1] Environment check:")
    print(f" - Python: {sys.version.split()[0]}")
    print(f" - Platform: {platform.platform()}")
    print(f" - Working dir: {root}")
    print()

    print("[2] Required file check:")
    missing = []
    for file_name in REQUIRED_FILES:
        path = root / file_name
        status = check_file(path)
        print(f" - {file_name}: {status}")
        if status == "MISSING":
            missing.append(file_name)

    print()
    print("[3] Build ZIP check:")
    zip_path = root / ZIP_FILE
    if zip_path.exists():
        print(f" - {ZIP_FILE}: FOUND")
    else:
        print(f" - {ZIP_FILE}: MISSING")
        missing.append(ZIP_FILE)

    print()
    if missing:
        print("RESULT: Some Milestone 11 files are missing.")
        print("Missing files:")
        for item in missing:
            print(f" - {item}")
        return 1

    print("RESULT: PASS - Milestone 11 verification files are present.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())