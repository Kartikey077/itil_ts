from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from windows.login_page import LoginPage
from windows.incident_form import IncidentForm
from windows.incident_list import IncidentList


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ITIL Ticketing System")

        # ✅ Set a good minimum & default size
        self.setMinimumSize(900, 600)  # prevents "mobile" tiny window
        self.resize(1200, 800)         # when not maximized, use this size

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Page 0 → Login
        self.login_page = LoginPage(on_login_success=self.show_incident_page)
        self.stack.addWidget(self.login_page)

        # Page 1 → Incident Manager (form + list)
        self.form_view = IncidentForm(on_submit=self.refresh_form, on_view=self.show_list)
        self.list_view = IncidentList(on_back=self.show_form)

        self.incident_container = QWidget()
        vbox = QVBoxLayout(self.incident_container)
        vbox.addWidget(self.form_view)
        vbox.addWidget(self.list_view)
        self.stack.addWidget(self.incident_container)

        self.show_login_page()

        # ✅ Always start maximized (like modern desktop software)
        self.showMaximized()

    def show_login_page(self):
        self.stack.setCurrentIndex(0)

    def show_incident_page(self):
        self.show_form()
        self.stack.setCurrentIndex(1)

    def show_form(self):
        self.form_view.show()
        self.list_view.hide()

    def show_list(self):
        self.list_view.load_incidents()
        self.form_view.hide()
        self.list_view.show()

    def refresh_form(self):
        pass
