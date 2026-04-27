import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

from home import TicketingHome
from login_page import MainWindow
from create_ticket import CreateTicketWidget

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Ticketing System")
        self.showMaximized()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = TicketingHome(self)
        self.login = MainWindow(self)
        self.ticket = CreateTicketWidget(self)

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.login)
        self.stack.addWidget(self.ticket)

        self.stack.setCurrentWidget(self.home)

    def show_home(self):
        self.stack.setCurrentWidget(self.home)

    def show_login(self):
        self.stack.setCurrentWidget(self.login)

    def show_ticket(self):
        self.stack.setCurrentWidget(self.ticket)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())