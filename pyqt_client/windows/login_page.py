from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import api

class LoginPage(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login")
        self.resize(700, 600)  # Window size

        # Main layout to center content
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container layout to hold the form nicely
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)

        # Add a container widget to center
        container_widget = QWidget()
        container_widget.setLayout(container_layout)
        container_widget.setFixedWidth(300)  # Width of login form
        main_layout.addWidget(container_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("Welcome Back")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        # Username label and input
        username_label = QLabel("Username")
        username_label.setFont(QFont("Arial", 12))
        container_layout.addWidget(username_label)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        self.username.setFixedHeight(35)
        self.username.setStyleSheet(
            "QLineEdit { padding-left: 5px; border: 1px solid #ccc; border-radius: 5px; }"
        )
        container_layout.addWidget(self.username)

        # Password label and input
        password_label = QLabel("Password")
        password_label.setFont(QFont("Arial", 12))
        container_layout.addWidget(password_label)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(35)
        self.password.setStyleSheet(
            "QLineEdit { padding-left: 5px; border: 1px solid #ccc; border-radius: 5px; }"
        )
        container_layout.addWidget(self.password)

        # Spacer
        container_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(40)
        login_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 5px;
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
