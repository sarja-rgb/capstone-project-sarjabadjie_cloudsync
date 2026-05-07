import tkinter as tk
from tkinter import ttk
from pathlib import Path

REQUIRED_FILES = [
    "main.py",
    "requirements.txt",
    "README.md",
    "MILESTONE11.md",
    "SoundSoar.pdf",
    "performance_cpu_m10_ui.html",
    "performance_cpu_main.html",
    "CloudSyncManager_M11.zip",
]

def build_status_text():
    root = Path.cwd()
    lines = []
    lines.append("CloudSync Manager - Milestone 11 UI Demo")
    lines.append("=" * 48)
    lines.append(f"Project Root: {root}")
    lines.append("")
    lines.append("Milestone Focus:")
    lines.append("- AI-supported PDF testing evidence using spaCy")
    lines.append("- Performance profiling evidence")
    lines.append("- Repository cleanup and verification package")
    lines.append("- Advisor-aligned implementation progress")
    lines.append("")
    lines.append("File Verification:")
    for file_name in REQUIRED_FILES:
        status = "FOUND" if (root / file_name).exists() else "MISSING"
        lines.append(f"- {file_name}: {status}")
    lines.append("")
    lines.append("Repository:")
    lines.append("https://github.com/sarja-rgb/capstone-project-sarjabadjie_cloudsync")
    lines.append("")
    lines.append("Trello:")
    lines.append("https://trello.com/b/J6Ouycx9/cloudsync-insight-cos650-sprint-board")
    return "\n".join(lines)

def main():
    window = tk.Tk()
    window.title("CloudSync Manager - Milestone 11 Demo")
    window.geometry("850x600")

    title = ttk.Label(
        window,
        text="CloudSync Manager - Milestone 11 Demo",
        font=("Segoe UI", 16, "bold")
    )
    title.pack(pady=12)

    subtitle = ttk.Label(
        window,
        text="AI PDF Testing, Performance Evidence, and Repository Verification",
        font=("Segoe UI", 10)
    )
    subtitle.pack(pady=4)

    text_box = tk.Text(window, wrap="word", font=("Consolas", 10))
    text_box.pack(expand=True, fill="both", padx=16, pady=16)
    text_box.insert("1.0", build_status_text())
    text_box.config(state="disabled")

    close_button = ttk.Button(window, text="Close", command=window.destroy)
    close_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()