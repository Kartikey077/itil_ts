from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
import api
from IncidentWindow import IncidentWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def login(self):
        resp = api.login(self.username.text(), self.password.text())
        if resp.status_code == 200:
            QMessageBox.information(self, "Success", "Login successful")
            self.hide()
            self.main = IncidentWindow()
            self.main.show()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")
