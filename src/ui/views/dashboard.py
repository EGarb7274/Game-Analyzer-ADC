from collections import Counter
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

import config
from src.api.riot_client import RiotClient
from src.db.schema import open_db
from src.db import cache as db_cache
from src.analysis.stats import extract_match_stats
from src.ui.theme import StatCard, section_label, TEXT_SEC, TYPE_SMALL

DB_PATH = str(Path.home() / '.lol_adc_analyzer' / 'matches.db')


class FetchWorker(QThread):
    """Background thread: fetch and cache new match data."""
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, puuid: str, client: RiotClient, cfg: dict):
        super().__init__()
        self.puuid = puuid
        self.client = client
        self.cfg = cfg

    def run(self):
        try:
            conn = open_db(DB_PATH)
            self.progress.emit('Fetching match list...')
            match_ids = self.client.get_match_ids(
                self.puuid, count=self.cfg['match_count']
            )
            db_cache.save_match_ids(conn, self.puuid, match_ids)
            uncached = db_cache.get_uncached_match_ids(conn, self.puuid)
            for i, mid in enumerate(uncached):
                self.progress.emit(f'Fetching match {i + 1}/{len(uncached)}...')
                match_data = self.client.get_match(mid)
                timeline_data = self.client.get_timeline(mid)
                db_cache.save_match(conn, mid, match_data)
                db_cache.save_timeline(conn, mid, timeline_data)
            conn.close()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(16)

        # Page title
        title = QLabel('Dashboard')
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        self._layout.addWidget(title)

        # Riot ID input row — labels above fields per form principles
        id_row = QHBoxLayout()
        id_row.setSpacing(8)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(QLabel('Game Name'))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText('e.g. Faker')
        name_col.addWidget(self._name_input)

        tag_col = QVBoxLayout()
        tag_col.setSpacing(4)
        tag_col.addWidget(QLabel('Tag'))
        self._tag_input = QLineEdit()
        self._tag_input.setPlaceholderText('NA1')
        self._tag_input.setFixedWidth(88)
        tag_col.addWidget(self._tag_input)

        self._load_btn = QPushButton('Fetch Matches')
        self._load_btn.setObjectName('cta_btn')
        self._load_btn.clicked.connect(self._on_load)
        self._load_btn.setFixedHeight(40)
        self._load_btn.setMinimumWidth(120)

        self._settings_btn = QPushButton('Settings')
        self._settings_btn.clicked.connect(self._open_settings)
        self._settings_btn.setFixedHeight(40)

        id_row.addLayout(name_col)
        id_row.addLayout(tag_col)
        id_row.addWidget(self._load_btn, 0, Qt.AlignmentFlag.AlignBottom)
        id_row.addStretch()
        id_row.addWidget(self._settings_btn, 0, Qt.AlignmentFlag.AlignBottom)
        self._layout.addLayout(id_row)

        self._status_label = QLabel('')
        self._status_label.setStyleSheet(f'color: {TEXT_SEC}; font-size: {TYPE_SMALL}px;')
        self._layout.addWidget(self._status_label)

        self._layout.addWidget(section_label('Stats Overview'))
        self._stats_grid = QGridLayout()
        self._stats_grid.setSpacing(16)
        self._layout.addLayout(self._stats_grid)
        self._layout.addStretch()

    def _open_settings(self):
        self.window().show_settings()

    def _on_load(self):
        cfg = config.load_config()
        if not cfg.get('api_key'):
            QMessageBox.warning(self, 'No API Key',
                                'Please set your Riot API key in Settings first.')
            self._open_settings()
            return

        game_name = self._name_input.text().strip()
        tag_line = self._tag_input.text().strip()
        if not game_name or not tag_line:
            self._status_label.setText('Enter a Game Name and TAG.')
            return

        self._load_btn.setEnabled(False)
        self._status_label.setText('Resolving Riot ID...')

        try:
            client = RiotClient(cfg['api_key'], cfg['region'], cfg['match_region'])
            conn = open_db(DB_PATH)
            summoner = db_cache.get_summoner_by_name(conn, game_name, tag_line)
            if not summoner:
                account = client.get_puuid(game_name, tag_line)
                db_cache.upsert_summoner(conn, account['puuid'], game_name, tag_line)
                puuid = account['puuid']
            else:
                puuid = summoner['puuid']
            conn.close()

            self._worker = FetchWorker(puuid, client, cfg)
            self._worker.progress.connect(self._status_label.setText)
            self._worker.finished.connect(
                lambda: self._on_fetch_done(puuid, game_name, tag_line))
            self._worker.error.connect(self._on_fetch_error)
            self._worker.start()
        except Exception as e:
            self._status_label.setText(f'Error: {e}')
            self._load_btn.setEnabled(True)

    def _on_fetch_error(self, message: str):
        self._status_label.setText(f'Error: {message}')
        self._load_btn.setEnabled(True)

    def _on_fetch_done(self, puuid: str, game_name: str, tag_line: str):
        self._status_label.setText('Done. Computing stats...')
        self._load_btn.setEnabled(True)
        self._render_stats(puuid, game_name, tag_line)

    def _render_stats(self, puuid: str, game_name: str, tag_line: str):
        conn = open_db(DB_PATH)
        match_ids = db_cache.get_cached_match_ids(conn, puuid)

        all_stats = []
        for mid in match_ids:
            data = db_cache.get_match(conn, mid)
            if data is None:
                continue
            try:
                all_stats.append(extract_match_stats(data, puuid))
            except (ValueError, KeyError):
                continue
        conn.close()

        if not all_stats:
            self._status_label.setText('No match data found.')
            return

        wins = sum(1 for s in all_stats if s['win'])
        win_rate = round(wins / len(all_stats) * 100)
        avg_kda = (
            round(sum(s['kills'] for s in all_stats) / len(all_stats), 1),
            round(sum(s['deaths'] for s in all_stats) / len(all_stats), 1),
            round(sum(s['assists'] for s in all_stats) / len(all_stats), 1),
        )
        avg_cs = round(sum(s['cs_per_min'] for s in all_stats) / len(all_stats), 1)
        top_champs = Counter(s['champion'] for s in all_stats).most_common(3)

        while self._stats_grid.count():
            item = self._stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._stats_grid.addWidget(
            StatCard('Summoner', f'{game_name}#{tag_line}'), 0, 0)
        self._stats_grid.addWidget(
            StatCard('Win Rate', f'{win_rate}%  ({wins}/{len(all_stats)})'), 0, 1)
        self._stats_grid.addWidget(
            StatCard('Avg KDA', f'{avg_kda[0]}/{avg_kda[1]}/{avg_kda[2]}'), 0, 2)
        self._stats_grid.addWidget(
            StatCard('Avg CS/min', str(avg_cs)), 0, 3)
        top_champ_str = ', '.join(f'{c} ({n})' for c, n in top_champs)
        self._stats_grid.addWidget(
            StatCard('Top Champions', top_champ_str), 1, 0, 1, 4)

        self._status_label.setText(f'{len(all_stats)} matches loaded.')
