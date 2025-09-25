# windows/incident_list.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QLabel, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import api

class IncidentList(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Back button
        back_btn = QPushButton("← Back to Raise Incident")
        back_btn.setStyleSheet(
            "background-color:#e67e22;color:white;padding:10px;border-radius:5px;font-weight:bold;"
        )
        back_btn.setFixedWidth(220)
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Container inside scroll area
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(10)
        self.container_layout.addStretch()
        self.scroll_area.setWidget(self.container)

    def load_incidents(self):
        resp = api.get_incidents()
        if resp.status_code != 200:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Failed to fetch incidents")
            return

        incidents = resp.json()
        # Clear previous
        for i in reversed(range(self.container_layout.count() - 1)):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not incidents:
            label = QLabel("No incidents found.")
            label.setFont(QFont("Arial", 12))
            self.container_layout.insertWidget(0, label)
            return

        # Add each incident
        for inc in incidents:
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.Box)
            frame.setStyleSheet("border:1px solid #bdc3c7; padding:5px;")
            frame_layout = QVBoxLayout(frame)
            frame_layout.setSpacing(3)

            # Incident main info
            title = QLabel(f"#{inc['id']} - {inc['title']}")
            title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            frame_layout.addWidget(title)

            # Status, Category, Urgency in one line
            info = QLabel(
                f"Status: {inc['status']} | "
                f"Category: {inc.get('category','N/A')} | "
                f"Urgency: {inc.get('urgency','N/A')}"
            )
            info.setFont(QFont("Arial", 11))
            # Color-code status
            color = {"Open":"blue", "In Progress":"orange", "Closed":"green"}.get(inc['status'], "black")
            info.setStyleSheet(f"color:{color};")
            frame_layout.addWidget(info)

            # Description
            desc = QLabel(inc['description'])
            desc.setFont(QFont("Arial", 11))
            desc.setWordWrap(True)
            frame_layout.addWidget(desc)

            self.container_layout.insertWidget(0, frame)
