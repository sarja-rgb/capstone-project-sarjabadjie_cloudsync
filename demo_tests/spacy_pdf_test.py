"""
spacy_pdf_test.py
Runs the repo's existing run_spacy_pdf.py and ensures spacy_pdf_test_output.txt exists.

Run from repo root:
    python demo_tests/spacy_pdf_test.py
"""
from pathlib import Path
import subprocess
import sys


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main():
    root = repo_root()
    script = root / "run_spacy_pdf.py"
    out = root / "spacy_pdf_test_output.txt"

    if not script.exists():
        raise SystemExit(f"ERROR: missing {script}")

    subprocess.check_call([sys.executable, str(script)], cwd=str(root))

    if out.exists() and out.stat().st_size > 0:
        print("PASS: spacy_pdf_test_output.txt generated.")
        print(f"Output: {out}")
    else:
        raise SystemExit("FAIL: spacy_pdf_test_output.txt was not created or is empty.")


if __name__ == "__main__":
    main()
