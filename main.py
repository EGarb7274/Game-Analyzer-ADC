import sys
from PyQt6.QtWidgets import QApplication
from src.ui.app import MainWindow
from src.ui.theme import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
