from pathlib import Path
import platform
import sys

REQUIRED_FILES = [
    "main.py",
    "requirements.txt",
    "config_db.py",
    "s3_client.py",
    "README.md",
    "MILESTONE10.md",
    "milestone10_ui.py",
]

def main():
    repo_root = Path(__file__).resolve().parent

    print("=== CloudSync Manager - Milestone 10 Verification ===")
    print(f"Repo root: {repo_root}")
    print()

    print("[1] Required file check:")
    missing = []
    for name in REQUIRED_FILES:
        p = repo_root / name
        if p.exists():
            print(f" - {name}: OK")
        else:
            print(f" - {name}: MISSING")
            missing.append(name)
    print()

    print("[2] Build package check:")
    zip_name = "CloudSyncManager_M10.zip"
    zip_path = repo_root / zip_name

    if zip_path.exists():
        print(f" - {zip_name}: FOUND")
        zip_status = "found"
    else:
        print(f" - {zip_name}: NOT FOUND in this folder")
        print(" - Note: this is expected when running from an extracted build package.")
        zip_status = "not_found_extracted_ok"
    print()

    print("[3] Environment check:")
    print(f" - Python: {sys.version.split()[0]}")
    print(f" - Platform: {platform.system()} {platform.release()}")
    print(f" - Working dir: {Path.cwd()}")
    print()

    print("[4] Summary:")
    if not missing:
        print(" - Milestone 10 verification passed for required files.")
        if zip_status == "found":
            print(" - Build ZIP is present in this folder.")
        else:
            print(" - Build ZIP is not in this extracted folder, which is acceptable for packaged build testing.")
    else:
        print(" - Milestone 10 verification incomplete.")
        print(" - Missing files:", ", ".join(missing))

    print()
    print("Milestone 10 verification complete.")

if __name__ == "__main__":
    main()
