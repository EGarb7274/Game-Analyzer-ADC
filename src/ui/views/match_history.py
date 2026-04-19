from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal


class MatchHistoryView(QWidget):
    match_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        QVBoxLayout(self).addWidget(QLabel('Match History — coming soon'))
