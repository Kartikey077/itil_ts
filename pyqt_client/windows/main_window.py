# windows/main_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from windows.incident_form import IncidentForm
from windows.incident_list import IncidentList

class IncidentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Incident Manager")
        self.resize(650, 550)

        self.layout = QVBoxLayout(self)
        self.form_view = IncidentForm(on_submit=self.refresh_form, on_view=self.show_list)
        self.list_view = IncidentList(on_back=self.show_form)

        self.layout.addWidget(self.form_view)
        self.layout.addWidget(self.list_view)

        self.show_form()

    def show_form(self):
        self.form_view.show()
        self.list_view.hide()

    def show_list(self):
        self.list_view.load_incidents()
        self.form_view.hide()
        self.list_view.show()

    def refresh_form(self):
        """Optional hook if you want to refresh form after submission"""
        pass
