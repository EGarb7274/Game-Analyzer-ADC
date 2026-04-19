from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class MatchDetailView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        QVBoxLayout(self).addWidget(QLabel('Match Detail — coming soon'))

    def load_match(self, match_id: str):
        pass
