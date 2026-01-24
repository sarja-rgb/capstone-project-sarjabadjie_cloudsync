"""
CloudSync Manager - Milestone 1 Prototype
Author: Sarja Badjie

This is a minimal but functional starter implementation for your Capstone
Milestone 1. It provides:

- A PyQt GUI window
- Fields to configure a local folder and AWS S3 bucket
- SQLite-based storage of the latest configuration
- A simple "Test S3 Connection" that lists object keys (first 20) in the GUI

To run locally:

1. Create a virtual environment
   python -m venv venv
   venv\Scripts\activate   (Windows)
   source venv/bin/activate (Mac/Linux)

2. Install requirements
   pip install -r requirements.txt

3. Make sure you have AWS credentials configured (e.g., via AWS CLI)
   aws configure   (or use a named profile)

4. Run:
   python main.py
"""

import sys
import traceback
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QGridLayout,
    QMessageBox,
)
from PyQt5.QtCore import Qt

import config_db
import s3_client


class CloudSyncConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CloudSync Manager - Milestone 1")
        self.resize(800, 500)

        self._build_ui()
        self._load_existing_config()

    def _build_ui(self):
        layout = QGridLayout()
        row = 0

        # Local folder
        layout.addWidget(QLabel("Local Folder:"), row, 0)
        self.local_folder_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.local_folder_edit, row, 1)
        layout.addWidget(browse_btn, row, 2)
        row += 1

        # S3 bucket
        layout.addWidget(QLabel("S3 Bucket:"), row, 0)
        self.bucket_edit = QLineEdit()
        layout.addWidget(self.bucket_edit, row, 1, 1, 2)
        row += 1

        # Prefix
        layout.addWidget(QLabel("S3 Prefix (optional):"), row, 0)
        self.prefix_edit = QLineEdit()
        layout.addWidget(self.prefix_edit, row, 1, 1, 2)
        row += 1

        # AWS profile
        layout.addWidget(QLabel("AWS Profile (optional):"), row, 0)
        self.profile_edit = QLineEdit()
        layout.addWidget(self.profile_edit, row, 1, 1, 2)
        row += 1

        # Region
        layout.addWidget(QLabel("Region (optional):"), row, 0)
        self.region_edit = QLineEdit()
        layout.addWidget(self.region_edit, row, 1, 1, 2)
        row += 1

        # Buttons
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self.save_configuration)

        self.test_btn = QPushButton("Test S3 Connection")
        self.test_btn.clicked.connect(self.test_connection)

        layout.addWidget(self.save_btn, row, 1)
        layout.addWidget(self.test_btn, row, 2)
        row += 1

        # Output log
        layout.addWidget(QLabel("Output / Logs:"), row, 0, 1, 3)
        row += 1

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box, row, 0, 1, 3)

        self.setLayout(layout)

    def append_log(self, text: str):
        self.output_box.append(text)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Local Folder")
        if folder:
            self.local_folder_edit.setText(folder)

    def _load_existing_config(self):
        cfg = config_db.get_latest_config()
        if cfg:
            self.local_folder_edit.setText(cfg.get("local_folder", ""))
            self.bucket_edit.setText(cfg.get("bucket", ""))
            self.prefix_edit.setText(cfg.get("prefix", ""))
            self.profile_edit.setText(cfg.get("profile", ""))
            self.region_edit.setText(cfg.get("region", ""))
            self.append_log("Loaded last saved configuration from database.")
        else:
            self.append_log("No saved configuration found yet. Please create one.")

    def _read_form_config(self) -> dict:
        return {
            "local_folder": self.local_folder_edit.text().strip(),
            "bucket": self.bucket_edit.text().strip(),
            "prefix": self.prefix_edit.text().strip(),
            "profile": self.profile_edit.text().strip() or None,
            "region": self.region_edit.text().strip() or None,
        }

    def save_configuration(self):
        cfg = self._read_form_config()
        if not cfg["local_folder"]:
            QMessageBox.warning(self, "Missing Info", "Please select a local folder.")
            return
        if not cfg["bucket"]:
            QMessageBox.warning(self, "Missing Info", "Please enter an S3 bucket name.")
            return

        try:
            config_db.save_config(cfg)
            self.append_log("Configuration saved to SQLite database (cloudsync_metadata.db).")
            QMessageBox.information(self, "Saved", "Configuration saved successfully.")
        except Exception as exc:
            traceback.print_exc()
            QMessageBox.critical(self, "Error saving configuration", str(exc))

    def test_connection(self):
        cfg = self._read_form_config()
        if not cfg["bucket"]:
            QMessageBox.warning(self, "Missing Info", "Please enter an S3 bucket name.")
            return

        try:
            self.append_log("Testing connection to S3 bucket '{}'...".format(cfg["bucket"]))
            client = s3_client.build_s3_client(profile_name=cfg["profile"], region_name=cfg["region"])
            keys = s3_client.list_objects_simple(client, bucket=cfg["bucket"], prefix=cfg["prefix"])
            if not keys:
                self.append_log("Connected successfully, but no objects found for this bucket/prefix.")
            else:
                self.append_log("Connected successfully. Showing up to 20 object keys:")
                for key in keys[:20]:
                    self.append_log(f" - {key}")
        except Exception as exc:
            traceback.print_exc()
            self.append_log("Error testing S3 connection:")
            self.append_log(str(exc))
            QMessageBox.critical(self, "Connection Error", str(exc))


def main():
    # Ensure DB schema exists
    config_db.init_db()

    app = QApplication(sys.argv)
    window = CloudSyncConfigWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
