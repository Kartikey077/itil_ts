# windows/incident_form.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
import api

class IncidentForm(QWidget):
    def __init__(self, on_submit, on_view):
        super().__init__()
        self.on_submit = on_submit
        self.on_view = on_view

        layout = QVBoxLayout(self)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Incident Title")
        self.title_input.setMinimumHeight(30)
        layout.addWidget(self.title_input)

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Incident Description")
        self.desc_input.setMinimumHeight(120)
        layout.addWidget(self.desc_input)

        # Submit button
        submit_btn = QPushButton("Submit Incident")
        submit_btn.setStyleSheet("background-color:#3498db;color:white;padding:10px;border-radius:5px;")
        submit_btn.clicked.connect(self.submit_incident)
        layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # View button
        view_btn = QPushButton("View My Incidents")
        view_btn.setStyleSheet("background-color:#2ecc71;color:white;padding:10px;border-radius:5px;")
        view_btn.clicked.connect(self.on_view)
        layout.addWidget(view_btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def submit_incident(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()

        if not title or not desc:
            QMessageBox.warning(self, "Error", "Please fill in both title and description")
            return

        resp = api.submit_incident(title, desc)
        if resp.status_code == 201:
            QMessageBox.information(self, "Success", "Incident submitted successfully")
            self.title_input.clear()
            self.desc_input.clear()
            self.on_submit()
        else:
            QMessageBox.warning(self, "Error", f"Failed to submit incident:\n{resp.text}")
