from PyQt6.QtWidgets import QMessageBox

def show_info(parent, title, message):
    QMessageBox.information(parent, title, message)

def show_error(parent, title, message):
    QMessageBox.warning(parent, title, message)
