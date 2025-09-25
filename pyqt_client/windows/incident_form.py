# windows/incident_form.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QComboBox, QLabel
)
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
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Incident Description")
        self.desc_input.setMinimumHeight(120)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)

        # Category Dropdown
        self.category_input = QComboBox()
        self.category_input.addItems([
            "Hardware", "Software", "Network", "Access", "Other"
        ])
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_input)

        # Urgency Dropdown
        self.urgency_input = QComboBox()
        self.urgency_input.addItems([
            "Low", "Medium", "High", "Critical"
        ])
        layout.addWidget(QLabel("Urgency:"))
        layout.addWidget(self.urgency_input)

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
        category = self.category_input.currentText()
        urgency = self.urgency_input.currentText()

        if not title or not desc:
            QMessageBox.warning(self, "Error", "Please fill in both title and description")
            return

        # send category + urgency to API as well
        resp = api.submit_incident(title, desc, category, urgency)
        if resp.status_code == 201:
            QMessageBox.information(self, "Success", "Incident submitted successfully")
            self.title_input.clear()
            self.desc_input.clear()
            self.category_input.setCurrentIndex(0)
            self.urgency_input.setCurrentIndex(0)
            self.on_submit()
        else:
            QMessageBox.warning(self, "Error", f"Failed to submit incident:\n{resp.text}")
