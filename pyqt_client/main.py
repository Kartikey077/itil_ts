import sys
from PyQt6.QtWidgets import QApplication
from auth_window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
