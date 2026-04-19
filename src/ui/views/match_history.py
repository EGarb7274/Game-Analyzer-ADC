from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

import config
from src.db.schema import open_db
from src.db import cache as db_cache
from src.analysis.stats import extract_match_stats

DB_PATH = str(Path.home() / '.lol_adc_analyzer' / 'matches.db')

COLUMNS = ['Champion', 'Result', 'KDA', 'CS/min', 'Damage', 'Duration', 'Items']


class MatchHistoryView(QWidget):
    match_selected = pyqtSignal(str)   # emits match_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._match_ids: list[str] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        top_row = QHBoxLayout()
        self._status_label = QLabel('Load a summoner from the Dashboard first.')
        self._refresh_btn = QPushButton('Refresh')
        self._refresh_btn.clicked.connect(self.refresh)
        top_row.addWidget(self._status_label)
        top_row.addStretch()
        top_row.addWidget(self._refresh_btn)
        layout.addLayout(top_row)

        self._table = QTableWidget(0, len(COLUMNS))
        self._table.setHorizontalHeaderLabels(COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.cellDoubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self._table)

    def refresh(self):
        """Reload match history from cache for the currently loaded summoner."""
        conn = open_db(DB_PATH)
        row = conn.execute(
            'SELECT puuid, game_name, tag_line FROM summoners '
            'ORDER BY last_updated DESC LIMIT 1'
        ).fetchone()
        if not row:
            self._status_label.setText('No summoner loaded.')
            conn.close()
            return

        puuid = row['puuid']
        match_ids = db_cache.get_cached_match_ids(conn, puuid)
        self._match_ids = match_ids

        self._table.setRowCount(0)
        for mid in match_ids:
            data = db_cache.get_match(conn, mid)
            if data is None:
                continue
            try:
                stats = extract_match_stats(data, puuid)
            except (ValueError, KeyError):
                continue
            self._add_row(mid, stats)

        conn.close()
        self._status_label.setText(
            f'{self._table.rowCount()} matches loaded. Double-click a row for details.')

    def _add_row(self, match_id: str, stats: dict):
        row = self._table.rowCount()
        self._table.insertRow(row)

        def cell(text: str) -> QTableWidgetItem:
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return item

        duration_min = stats['game_duration'] // 60
        duration_sec = stats['game_duration'] % 60
        items_str = ' | '.join(str(i) for i in stats['items'] if i != 0)
        kda_str = f"{stats['kills']}/{stats['deaths']}/{stats['assists']}"

        self._table.setItem(row, 0, cell(stats['champion']))
        result_item = cell('WIN' if stats['win'] else 'LOSS')
        result_item.setForeground(
            QColor('#00cc44') if stats['win'] else QColor('#cc2200'))
        self._table.setItem(row, 1, result_item)
        self._table.setItem(row, 2, cell(kda_str))
        self._table.setItem(row, 3, cell(str(stats['cs_per_min'])))
        self._table.setItem(row, 4, cell(f"{stats['damage_dealt']:,}"))
        self._table.setItem(row, 5, cell(f'{duration_min}:{duration_sec:02d}'))
        self._table.setItem(row, 6, cell(items_str))

        # Store match_id in row for retrieval on double-click
        self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, match_id)

    def _on_row_double_clicked(self, row: int, _col: int):
        item = self._table.item(row, 0)
        if item:
            match_id = item.data(Qt.ItemDataRole.UserRole)
            if match_id:
                self.match_selected.emit(match_id)
