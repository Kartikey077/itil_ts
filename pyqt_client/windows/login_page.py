from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import api


class LoginPage(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")

        # Outer layout (fills whole screen)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Center everything vertically
        outer_layout.addStretch()

        # Horizontal layout to center form in the middle
        hbox = QHBoxLayout()
        hbox.addStretch()  # left spacer

        # Form container
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)

        container_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        container_widget.setMaximumWidth(500)  # reasonable max width

        hbox.addWidget(container_widget)
        hbox.addStretch()  # right spacer
        outer_layout.addLayout(hbox)

        # Center everything vertically
        outer_layout.addStretch()

        # ---- FORM CONTENT ----
        title = QLabel("Welcome Back")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        # Username
        username_label = QLabel("Username")
        username_label.setFont(QFont("Arial", 12))
        container_layout.addWidget(username_label)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        self.username.setFixedHeight(40)
        self.username.setStyleSheet(
            "QLineEdit { padding-left: 8px; border: 1px solid #ccc; border-radius: 6px; }"
        )
        container_layout.addWidget(self.username)

        # Password
        password_label = QLabel("Password")
        password_label.setFont(QFont("Arial", 12))
        container_layout.addWidget(password_label)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(40)
        self.password.setStyleSheet(
            "QLineEdit { padding-left: 8px; border: 1px solid #ccc; border-radius: 6px; }"
        )
        container_layout.addWidget(self.password)

        # Spacer inside form
        container_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
            """
        )
        login_btn.clicked.connect(self.login)
        container_layout.addWidget(login_btn)

    def login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return

        resp = api.login(username, password)
        if resp.status_code == 200:
            QMessageBox.information(self, "Success", "Login successful")
            self.on_login_success()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")
