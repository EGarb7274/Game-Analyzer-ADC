from pathlib import Path

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.db.schema import open_db
from src.db import cache as db_cache
from src.analysis.stats import extract_match_stats, get_participant
from src.analysis.timeline import (
    get_participant_id, extract_item_timings, extract_position_events
)
from src.api.data_dragon import DataDragon

DB_PATH = str(Path.home() / '.lol_adc_analyzer' / 'matches.db')
# League of Legends map coordinate bounds
MAP_WIDTH = 14820
MAP_HEIGHT = 14881


class MatchDetailView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragon = DataDragon()
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        # Back button
        back_btn = QPushButton('← Back to Match History')
        back_btn.clicked.connect(self._go_back)
        outer.addWidget(back_btn)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        self._title_label = QLabel('Select a match from Match History')
        self._title_label.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        self._content_layout.addWidget(self._title_label)

        # Stats grid
        self._stats_grid = QGridLayout()
        self._content_layout.addLayout(self._stats_grid)

        # Item timing chart
        self._content_layout.addWidget(QLabel('Item Timing'))
        self._timing_canvas = FigureCanvas(Figure(figsize=(10, 3)))
        self._content_layout.addWidget(self._timing_canvas)

        # Heatmap
        self._content_layout.addWidget(QLabel('Positioning (Kills/Deaths/Assists)'))
        self._heatmap_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self._content_layout.addWidget(self._heatmap_canvas)

        # Runes
        self._runes_label = QLabel('')
        self._runes_label.setWordWrap(True)
        self._content_layout.addWidget(QLabel('Runes Used'))
        self._content_layout.addWidget(self._runes_label)
        self._content_layout.addStretch()

    def _go_back(self):
        self.window().stack.setCurrentIndex(1)

    def load_match(self, match_id: str):
        conn = open_db(DB_PATH)
        match_data = db_cache.get_match(conn, match_id)
        timeline_data = db_cache.get_timeline(conn, match_id)

        # Get the current summoner's puuid
        row = conn.execute(
            'SELECT puuid FROM summoners ORDER BY last_updated DESC LIMIT 1'
        ).fetchone()
        conn.close()

        if not match_data or not row:
            self._title_label.setText('Match data not found.')
            return

        puuid = row['puuid']
        try:
            stats = extract_match_stats(match_data, puuid)
        except (ValueError, KeyError) as e:
            self._title_label.setText(f'Error loading match: {e}')
            return

        result_str = 'WIN' if stats['win'] else 'LOSS'
        self._title_label.setText(
            f"{stats['champion']} — {result_str} — "
            f"{stats['game_duration'] // 60}m {stats['game_duration'] % 60}s"
        )

        self._render_stats(stats)

        if timeline_data:
            participant_id = get_participant_id(match_data, puuid)
            timings = extract_item_timings(timeline_data, participant_id)
            positions = extract_position_events(timeline_data, participant_id)
            self._render_item_timing(timings, stats['items'])
            self._render_heatmap(positions)

        self._render_runes(stats['perks'])

    def _render_stats(self, stats: dict):
        while self._stats_grid.count():
            item = self._stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        def card(title: str, value: str) -> QFrame:
            f = QFrame()
            f.setFrameShape(QFrame.Shape.Box)
            v = QVBoxLayout(f)
            lbl_t = QLabel(title)
            lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_v = QLabel(value)
            lbl_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_v.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
            v.addWidget(lbl_t)
            v.addWidget(lbl_v)
            return f

        kda = f"{stats['kills']}/{stats['deaths']}/{stats['assists']}"
        self._stats_grid.addWidget(card('KDA', kda), 0, 0)
        self._stats_grid.addWidget(card('CS/min', str(stats['cs_per_min'])), 0, 1)
        self._stats_grid.addWidget(card('Damage Share', f"{stats['damage_share']}%"), 0, 2)
        self._stats_grid.addWidget(card('Gold Earned', f"{stats['gold_earned']:,}"), 0, 3)
        self._stats_grid.addWidget(card('Vision Score', str(stats['vision_score'])), 0, 4)
        self._stats_grid.addWidget(
            card('Kill Participation', f"{stats['kill_participation']}%"), 0, 5)

    def _render_item_timing(self, timings: list[dict], item_ids: list[int]):
        fig = self._timing_canvas.figure
        fig.clear()
        fig.patch.set_facecolor('#1a1a2e')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#16213e')

        if not timings:
            ax.text(0.5, 0.5, 'No item timing data', ha='center', va='center',
                    color='#aaaaaa', fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            times = [t['timestamp_min'] for t in timings]
            names = [self._dragon.get_item_name(t['item_id']) for t in timings]

            # Timeline spine
            x_max = max(times) + 3
            ax.hlines(0, 0, x_max, colors='#c89b3c', linewidth=2, zorder=1)

            # Alternating above/below label placement to reduce overlap
            for i, (t, name) in enumerate(zip(times, names)):
                above = i % 2 == 0
                y_dot = 0
                y_label = 0.55 if above else -0.55
                y_line_start = 0.08 if above else -0.08
                y_line_end = 0.45 if above else -0.45

                # Connector line
                ax.vlines(t, y_line_start, y_line_end,
                          colors='#c89b3c', linewidth=1, alpha=0.6, zorder=2)
                # Gold dot on the timeline
                ax.scatter([t], [y_dot], s=80, color='#c89b3c',
                           zorder=3, edgecolors='#fff6e0', linewidths=0.8)
                # Item name label
                ax.text(t, y_label, name,
                        ha='center', va='bottom' if above else 'top',
                        fontsize=7.5, color='#e8d5a3',
                        fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#0f3460',
                                  edgecolor='#c89b3c', alpha=0.85, linewidth=0.8))
                # Minute label below/above dot
                ax.text(t, -0.14 if above else 0.14,
                        f'{t:.1f}m', ha='center',
                        va='top' if above else 'bottom',
                        fontsize=6.5, color='#aaaaaa')

            ax.set_xlim(-1, x_max)
            ax.set_ylim(-1.1, 1.1)
            ax.set_xlabel('Game Time (minutes)', color='#aaaaaa', fontsize=8)
            ax.tick_params(colors='#aaaaaa', labelsize=7)
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_edgecolor('#333355')
            ax.set_title('Item Purchase Timeline', color='#c89b3c',
                         fontsize=10, fontweight='bold', pad=6)

        try:
            fig.tight_layout()
        except Exception:
            pass
        self._timing_canvas.draw()

    def _render_heatmap(self, positions: dict):
        fig = self._heatmap_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        # Try to load minimap background
        try:
            minimap_path = self._dragon.get_minimap_path()
            img = mpimg.imread(str(minimap_path))
            # Image origin is top-left; LoL coords have (0,0) at bottom-left,
            # so set extent with y going 0 (bottom) -> MAP_HEIGHT (top) and
            # use origin='upper' so the image rows map correctly.
            ax.imshow(img, extent=[0, MAP_WIDTH, MAP_HEIGHT, 0],
                      aspect='auto', zorder=0)
        except Exception:
            ax.set_facecolor('#1a3a1a')

        def plot_points(points, color, marker, label):
            if points:
                xs = [p['x'] for p in points]
                ys = [p['y'] for p in points]
                ax.scatter(xs, ys, c=color, marker=marker,
                           s=60, label=label, zorder=2, alpha=0.8)

        plot_points(positions['kills'], '#00cc44', 'o', 'Kill')
        plot_points(positions['deaths'], '#cc2200', 'x', 'Death')
        plot_points(positions['assists'], '#ffcc00', '^', 'Assist')

        ax.set_xlim(0, MAP_WIDTH)
        ax.set_ylim(MAP_HEIGHT, 0)  # flipped to match image origin at top-left
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Positioning Heatmap')
        if any([positions['kills'], positions['deaths'], positions['assists']]):
            ax.legend(loc='upper right', fontsize=8)

        try:
            fig.tight_layout()
        except Exception:
            pass
        self._heatmap_canvas.draw()

    def _render_runes(self, perks: dict):
        if not perks or not perks.get('styles'):
            self._runes_label.setText('No rune data available.')
            return
        lines = []
        for style in perks.get('styles', []):
            desc = style.get('description', '')
            selections = style.get('selections', [])
            perk_ids = [str(s.get('perk', '')) for s in selections]
            lines.append(f"{desc}: {', '.join(perk_ids)}")
        self._runes_label.setText('\n'.join(lines))
