import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox

LOG_FILE = "sync_log.txt"

def log_event(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} - {msg}\n")

class Milestone5Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CloudSync Insight - Milestone 7")

        self.status = QLabel("Status: Idle")
        self.progress = QProgressBar()
        self.progress.setValue(0)

        self.btn = QPushButton("Run Sync (Milestone 7 Demo)")
        self.btn.clicked.connect(self.run_sync)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def run_sync(self):
        self.status.setText("Status: Syncing...")
        self.progress.setValue(10)
        log_event("Sync started (Milestone 7)")

        self.progress.setValue(40)
        log_event("Scanning local metadata")

        self.progress.setValue(70)
        log_event("Comparing with remote state")

        self.progress.setValue(100)
        log_event("Sync completed successfully")
        self.status.setText("Status: Sync complete ✅")

        QMessageBox.information(self, "Milestone 7", "Sync finished.\nLog written to sync_log.txt")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Milestone5Window()
    w.resize(450, 220)
    w.show()
    sys.exit(app.exec_())