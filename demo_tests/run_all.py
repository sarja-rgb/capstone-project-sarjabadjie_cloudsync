# demo_tests/run_all.py
# Runs the full demo pipeline and writes ONE combined log: demo_run_log.txt
# FIXED for Windows/Git Bash encoding issues + avoids Unicode crashes.

from __future__ import annotations
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Force UTF-8 output so terminals don’t crash on weird PDF characters
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_print(s: str) -> None:
    """Print safely even when terminal uses cp1252."""
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("cp1252", "replace").decode("cp1252", "replace"))


def run_and_log(cmd: list[str], cwd: Path, log_path: Path, title: str) -> int:
    header = (
        f"\n\n{'='*80}\n{title}\n"
        f"CMD: {' '.join(cmd)}\n"
        f"TIME: {datetime.now().isoformat()}\n"
        f"{'='*80}\n"
    )
    safe_print(header.strip())
    with open(log_path, "a", encoding="utf-8", errors="replace") as f:
        f.write(header)

    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    out_lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        safe_print(line.rstrip("\n"))
        out_lines.append(line)

    rc = proc.wait()
    footer = f"\nEXIT_CODE={rc}\n"
    with open(log_path, "a", encoding="utf-8", errors="replace") as f:
        f.writelines(out_lines)
        f.write(footer)
    return rc


def main() -> int:
    root = repo_root()
    log_path = root / "demo_run_log.txt"
    log_path.write_text(
        f"CloudSync Full Demo Log\nStarted: {datetime.now().isoformat()}\n\n",
        encoding="utf-8",
        errors="replace",
    )

    py = sys.executable

    scripts = {
        "1) spaCy PDF Test": root / "demo_tests" / "spacy_pdf_test.py",
        "2) spaCy -> SQLite Metadata": root / "demo_tests" / "demo_text_metadata_to_sqlite.py",
        "3) Build FAISS Vectors": root / "demo_tests" / "build_vectors.py",
        "4) Search FAISS Vectors": root / "demo_tests" / "search_vectors.py",
        "5) Ollama Test": root / "demo_tests" / "ollama_test.py",
        "6) RAG Q1": root / "demo_tests" / "rag_soundsoar_demo_fixed.py",
        "7) RAG Q2": root / "demo_tests" / "rag_soundsoar_demo_fixed.py",
    }

    required_files = [
        root / "SoundSoar.pdf",
        root / "cloudsync_metadata.db",
        scripts["1) spaCy PDF Test"],
        scripts["2) spaCy -> SQLite Metadata"],
        scripts["3) Build FAISS Vectors"],
        scripts["4) Search FAISS Vectors"],
        scripts["5) Ollama Test"],
        scripts["6) RAG Q1"],
    ]

    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        safe_print("ERROR: Missing required files:")
        for m in missing:
            safe_print(" - " + m)
        return 1

    # 1) spaCy PDF
    rc = run_and_log([py, str(scripts["1) spaCy PDF Test"])], root, log_path, "1) spaCy PDF Test")
    if rc != 0:
        return rc

    # 2) SQLite demo
    rc = run_and_log([py, str(scripts["2) spaCy -> SQLite Metadata"])], root, log_path, "2) spaCy -> SQLite Metadata")
    if rc != 0:
        return rc

    # 3) Build vectors (clean old files first)
    for name in ["vectors.index", "vectors_meta.json"]:
        fp = root / name
        if fp.exists():
            fp.unlink()

    rc = run_and_log(
        [py, str(scripts["3) Build FAISS Vectors"]), "--limit", "10"],
        root,
        log_path,
        "3) Build FAISS Vectors (LOCAL)",
    )
    if rc != 0:
        return rc

    # 4) Search vectors
    rc = run_and_log(
        [py, str(scripts["4) Search FAISS Vectors"]), "Spotify music trends", "--topk", "5"],
        root,
        log_path,
        "4) Search FAISS Vectors (LOCAL)",
    )
    if rc != 0:
        return rc

    # 5) Ollama test
    rc = run_and_log(
        [py, str(scripts["5) Ollama Test"]), "--model", "llama3.2:1b"],
        root,
        log_path,
        "5) Ollama Test",
    )
    if rc != 0:
        return rc

    # 6) RAG Q1
    rc = run_and_log(
        [py, str(scripts["6) RAG Q1"]), "--question", "What ML models are mentioned in the paper?", "--topk", "10"],
        root,
        log_path,
        "6) RAG Q1",
    )
    if rc != 0:
        return rc

    # 7) RAG Q2
    rc = run_and_log(
        [py, str(scripts["7) RAG Q2"]), "--question", "What evaluation metrics are reported in the paper?", "--topk", "10"],
        root,
        log_path,
        "7) RAG Q2",
    )
    if rc != 0:
        return rc

    safe_print(f"\nPASS: Full demo completed. Log saved to: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())