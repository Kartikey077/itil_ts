from windows.main_window import AppWindow

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
