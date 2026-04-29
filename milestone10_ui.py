import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit

class Milestone10Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CloudSync Manager - Milestone 10 Demo")
        self.resize(700, 500)

        layout = QVBoxLayout()

        self.title_label = QLabel("CloudSync Manager - Milestone 10")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.status_label = QLabel("Status: Ready")
        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)

        self.run_button = QPushButton("Run Milestone 10 Check")
        self.run_button.clicked.connect(self.run_check)

        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.info_box)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def run_check(self):
        repo_root = Path(__file__).resolve().parent
        files_to_check = [
            "main.py",
            "requirements.txt",
            "config_db.py",
            "s3_client.py",
            "README.md",
            "MILESTONE10.md",
            "milestone10.py",
        ]

        lines = []
        lines.append("Milestone 10 Demo Check")
        lines.append(f"Repository: {repo_root}")
        lines.append("")

        missing = []
        for file_name in files_to_check:
            path = repo_root / file_name
            if path.exists():
                lines.append(f"{file_name}: OK")
            else:
                lines.append(f"{file_name}: MISSING")
                missing.append(file_name)

        zip_name = "CloudSyncManager_M10.zip"
        zip_path = repo_root / zip_name
        lines.append("")
        if zip_path.exists():
            lines.append(f"{zip_name}: FOUND")
            zip_ok = True
        else:
            lines.append(f"{zip_name}: NOT FOUND in this folder")
            lines.append("Note: expected when running from an extracted build package.")
            zip_ok = False

        lines.append("")
        if missing:
            self.status_label.setText("Status: Incomplete - some required files are missing")
        else:
            if zip_ok:
                self.status_label.setText("Status: Milestone 10 files verified")
            else:
                self.status_label.setText("Status: Milestone 10 files verified (extracted package)")

        self.info_box.setPlainText("\n".join(lines))

def main():
    app = QApplication(sys.argv)
    window = Milestone10Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
