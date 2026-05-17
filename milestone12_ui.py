<<<<<<< HEAD
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

class Milestone12Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CloudSync Manager - Milestone 12")
        self.setGeometry(300, 300, 500, 250)

        layout = QVBoxLayout()

        title = QLabel("CloudSync Manager")
        subtitle = QLabel("Milestone 12 UI Demo")
        details = QLabel(
            "This milestone demonstrates repository polishing,\n"
            "verification improvements, packaging updates,\n"
            "and AI/spaCy testing evidence integration."
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(details)

        self.setLayout(layout)

app = QApplication(sys.argv)
window = Milestone12Demo()
window.show()
sys.exit(app.exec_())
=======
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import sys

class Milestone12Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CloudSync Manager - Milestone 12")
        self.setGeometry(300, 300, 500, 250)

        layout = QVBoxLayout()

        title = QLabel("CloudSync Manager")
        subtitle = QLabel("Milestone 12 UI Demo")
        details = QLabel(
            "This milestone demonstrates repository polishing,\n"
            "verification improvements, packaging updates,\n"
            "and AI/spaCy testing evidence integration."
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(details)

        self.setLayout(layout)

app = QApplication(sys.argv)
window = Milestone12Demo()
window.show()
sys.exit(app.exec_())
>>>>>>> d67ca98e (Milestone 12: add verification and UI demo code)
