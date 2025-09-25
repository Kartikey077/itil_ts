# windows/incident_list.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt
import api

class IncidentList(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back

        layout = QVBoxLayout(self)

        # Back button
        back_btn = QPushButton("Back to Raise Incident")
        back_btn.setStyleSheet("background-color:#e67e22;color:white;padding:10px;border-radius:5px;")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Incident display
        self.incident_display = QTextEdit()
        self.incident_display.setReadOnly(True)
        self.incident_display.setMinimumHeight(400)
        layout.addWidget(self.incident_display)

    def load_incidents(self):
        resp = api.get_incidents()
        if resp.status_code != 200:
            QMessageBox.warning(self, "Error", "Failed to fetch incidents")
            return

        incidents = resp.json()
        cursor = self.incident_display.textCursor()
        self.incident_display.clear()

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
