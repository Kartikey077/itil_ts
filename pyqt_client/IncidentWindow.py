from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt
import api

class IncidentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Incident Manager")
        self.resize(650, 550)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.setup_form()  # Show the raise-incident form initially

    def setup_form(self):
        """Create input form for raising incident."""
        # Clear layout
        self.clear_layout()

        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Incident Title")
        self.title_input.setMinimumHeight(30)
        self.main_layout.addWidget(self.title_input)

        # Description input
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Incident Description")
        self.desc_input.setMinimumHeight(120)
        self.main_layout.addWidget(self.desc_input)

        # Submit button
        submit_btn = QPushButton("Submit Incident")
        submit_btn.setStyleSheet("background-color:#3498db;color:white;padding:10px;border-radius:5px;")
        submit_btn.clicked.connect(self.submit_incident)
        self.main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # View incidents button
        view_btn = QPushButton("View My Incidents")
        view_btn.setStyleSheet("background-color:#2ecc71;color:white;padding:10px;border-radius:5px;")
        view_btn.clicked.connect(self.view_incidents)
        self.main_layout.addWidget(view_btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def setup_incident_list(self, incidents):
        """Show incidents in the same window."""
        self.clear_layout()

        # Back button to return to form
        back_btn = QPushButton("Back to Raise Incident")
        back_btn.setStyleSheet("background-color:#e67e22;color:white;padding:10px;border-radius:5px;")
        back_btn.clicked.connect(self.setup_form)
        self.main_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Incident display
        self.incident_display = QTextEdit()
        self.incident_display.setReadOnly(True)
        self.incident_display.setMinimumHeight(400)
        self.main_layout.addWidget(self.incident_display)

        # Fill the incident display
        self.incident_display.clear()
        cursor = self.incident_display.textCursor()

        if not incidents:
            self.incident_display.setText("No incidents found.")
            return

        for inc in incidents:
            fmt = QTextCharFormat()
            if inc['status'] == 'Open':
                fmt.setForeground(QColor("blue"))
            elif inc['status'] == 'In Progress':
                fmt.setForeground(QColor("orange"))
            else:
                fmt.setForeground(QColor("green"))

            cursor.insertText(f"#{inc['id']} {inc['title']} ", fmt)
            cursor.insertText(f"({inc['status']})\n")
            cursor.insertText(f"{inc['description']}\n")
            cursor.insertText("-" * 50 + "\n")

        self.incident_display.moveCursor(QTextCursor.MoveOperation.Start)

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
        else:
            QMessageBox.warning(self, "Error", f"Failed to submit incident:\n{resp.text}")

    def view_incidents(self):
        resp = api.get_incidents()
        if resp.status_code != 200:
            QMessageBox.warning(self, "Error", "Failed to fetch incidents")
            return
        incidents = resp.json()
        self.setup_incident_list(incidents)

    def clear_layout(self):
        """Remove all widgets from the main layout."""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
