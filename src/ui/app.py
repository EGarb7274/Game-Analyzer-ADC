from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QListWidget, QStackedWidget, QStatusBar
)
from PyQt6.QtGui import QFont

from src.ui.views.dashboard import DashboardView
from src.ui.views.match_history import MatchHistoryView
from src.ui.views.match_detail import MatchDetailView
from src.ui.views.builds_panel import BuildsPanelView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LoL ADC Analyzer')
        self.setMinimumSize(1200, 800)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setFont(QFont('Segoe UI', 11))
        for item in ['Dashboard', 'Match History', 'Builds & Runes']:
            self.sidebar.addItem(item)
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self._on_nav_changed)

        # Stacked views
        self.stack = QStackedWidget()
        self.dashboard_view = DashboardView(self)
        self.match_history_view = MatchHistoryView(self)
        self.match_detail_view = MatchDetailView(self)
        self.builds_panel_view = BuildsPanelView(self)

        self.stack.addWidget(self.dashboard_view)     # index 0
        self.stack.addWidget(self.match_history_view) # index 1
        self.stack.addWidget(self.builds_panel_view)  # index 2

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.match_history_view.match_selected.connect(self._on_match_selected)

    def _on_nav_changed(self, index: int):
        self.stack.setCurrentIndex(index)

    def _on_match_selected(self, match_id: str):
        self.match_detail_view.load_match(match_id)
        self.stack.insertWidget(1, self.match_detail_view)
        self.stack.setCurrentWidget(self.match_detail_view)

    def show_status(self, message: str):
        self.status_bar.showMessage(message, 5000)

    def show_settings(self):
        from src.ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec()
