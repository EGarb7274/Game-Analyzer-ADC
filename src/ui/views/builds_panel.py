from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class BuildsPanelView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        QVBoxLayout(self).addWidget(QLabel('Builds & Runes — coming soon'))
