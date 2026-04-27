from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from home import TicketingHome
from login_page import MainWindow
from user_dashboard import UserDashboard

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Ticketing System")
        self.resize(1200, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.home_page = TicketingHome(self)
        self.login_page = MainWindow(self)
        self.dashboard_page = None   # created after login

        self.stack.addWidget(self.home_page)   # index 0
        self.stack.addWidget(self.login_page)  # index 1

        self.stack.setCurrentIndex(0)

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_dashboard(self, user_data):
        # Remove old dashboard if exists
        if self.dashboard_page:
            self.stack.removeWidget(self.dashboard_page)
            self.dashboard_page.deleteLater()

        # Create new dashboard
        self.dashboard_page = UserDashboard(user_data, self)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.dashboard_page)

    def show_employee_dashboard(self, employee_data):
        from employee_dashboard import EmployeeDashboard

        if hasattr(self, "employee_dashboard"):
            self.stack.removeWidget(self.employee_dashboard)
            self.employee_dashboard.deleteLater()

        self.employee_dashboard = EmployeeDashboard(employee_data)
        self.stack.addWidget(self.employee_dashboard)
        self.stack.setCurrentWidget(self.employee_dashboard)



    def show_admin_dashboard(self ,admin_data):
        from admin_page import AdminPanel

        if self.centralWidget():
            self.centralWidget().deleteLater()

        self.admin_dashboard = AdminPanel(admin_data)
        self.setCentralWidget(self.admin_dashboard)
        

