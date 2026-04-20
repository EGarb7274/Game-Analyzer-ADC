from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.analysis.builds import list_champions, get_champion_build
from src.api.data_dragon import DataDragon
from src.ui.theme import section_label


class BuildsPanelView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragon = DataDragon()
        self._build_ui()
        self._load_champion_list()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Champion list (left panel)
        left = QVBoxLayout()
        left.setSpacing(8)
        left.addWidget(section_label('ADC Champions'))
        self._champ_list = QListWidget()
        self._champ_list.setObjectName('champ_list')
        self._champ_list.setFixedWidth(168)
        self._champ_list.currentTextChanged.connect(self._on_champion_selected)
        left.addWidget(self._champ_list)
        layout.addLayout(left)

        # Build detail (right panel, scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._detail_widget = QWidget()
        self._detail_layout = QVBoxLayout(self._detail_widget)
        self._detail_layout.setContentsMargins(0, 0, 16, 0)
        self._detail_layout.setSpacing(8)
        scroll.setWidget(self._detail_widget)
        layout.addWidget(scroll)

        placeholder = QLabel('Select a champion to view their recommended build.')
        placeholder.setWordWrap(True)
        self._detail_layout.addWidget(placeholder)
        self._detail_layout.addStretch()

    def _load_champion_list(self):
        for champ in list_champions():
            self._champ_list.addItem(champ)

    def _on_champion_selected(self, champion: str):
        if not champion:
            return
        build = get_champion_build(champion)
        if not build:
            return
        self._render_build(champion, build)

    def _render_build(self, champion: str, build: dict):
        while self._detail_layout.count():
            item = self._detail_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        title = QLabel(champion)
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        self._detail_layout.addWidget(title)

        self._detail_layout.addWidget(section_label('Build Path'))
        item_ids = build.get('build', [])
        item_names = [self._dragon.get_item_name(iid) for iid in item_ids]
        build_label = QLabel('  →  '.join(item_names) if item_names else 'N/A')
        build_label.setWordWrap(True)
        self._detail_layout.addWidget(build_label)

        self._detail_layout.addWidget(section_label('Starting Items'))
        start_ids = build.get('starting_items', [])
        start_names = [self._dragon.get_item_name(iid) for iid in start_ids]
        self._detail_layout.addWidget(QLabel(', '.join(start_names) or 'N/A'))

        self._detail_layout.addWidget(section_label('Skill Order'))
        self._detail_layout.addWidget(QLabel(build.get('skill_order', 'N/A')))

        runes = build.get('runes', {})
        self._detail_layout.addWidget(section_label('Runes'))
        rune_lines = [
            f"Keystone: {runes.get('keystone', 'N/A')}",
            f"Primary Path: {runes.get('primary_path', 'N/A')}",
            f"Primary: {', '.join(runes.get('primary_runes', []))}",
            f"Secondary Path: {runes.get('secondary_path', 'N/A')}",
            f"Secondary: {', '.join(runes.get('secondary_runes', []))}",
            f"Shards: {', '.join(runes.get('shards', []))}",
        ]
        for line in rune_lines:
            lbl = QLabel(line)
            lbl.setWordWrap(True)
            self._detail_layout.addWidget(lbl)

        self._detail_layout.addStretch()
