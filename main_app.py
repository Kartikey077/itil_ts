import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

from home import TicketingHome
from login_page import MainWindow
from user_dashboard import UserDashboard   # ✅ added
from admin_page import AdminPanel
from employee_dashboard import EmployeeDashboard
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Ticketing System")
        self.resize(1280, 800)

        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = TicketingHome(self)
        self.login = MainWindow(self)
        self.dashboard = None # ✅ added
        self.admin_dashboard = None
        self.employee_dashboard = None
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.login)

        self.stack.setCurrentWidget(self.home)

    def show_home(self):
        self.showNormal() 
        self.stack.setCurrentWidget(self.home)

    def show_login(self):
        self.showNormal() 
        self.stack.setCurrentWidget(self.login)

    def show_dashboard(self, user_data):   # ✅ added
        if self.dashboard:
            self.stack.removeWidget(self.dashboard)
            self.dashboard.deleteLater()

        self.dashboard = UserDashboard(user_data, self)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)
        self.showMaximized()

    def show_employee_dashboard(self, employee_data):
            if self.employee_dashboard:
                self.stack.removeWidget(self.employee_dashboard)
                self.employee_dashboard.deleteLater()

            self.employee_dashboard = EmployeeDashboard(employee_data, self)

            self.stack.addWidget(self.employee_dashboard)
            self.stack.setCurrentWidget(self.employee_dashboard)

            self.resize(1280, 800)
            self.showNormal()

    def show_admin_dashboard(self, admin_data):
            if self.admin_dashboard:
                self.stack.removeWidget(self.admin_dashboard)
                self.admin_dashboard.deleteLater()

            self.admin_dashboard = AdminPanel(admin_data, self)
            self.stack.addWidget(self.admin_dashboard)
            self.stack.setCurrentWidget(self.admin_dashboard)

            self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
