# Performance Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "Performance" sidebar tab that shows rolling-window trend charts and three weakness panels (Laning Phase, Death Patterns, Vision Control) with auto-generated insights.

**Architecture:** One new view (`src/ui/views/performance.py`) wired into the existing sidebar stack. Two existing analysis modules are extended with new extraction functions. All data comes from the local SQLite cache — no new API calls.

**Tech Stack:** PyQt6, matplotlib (FigureCanvas + GridSpec), SQLite via existing `db_cache` helpers.

---

## File Map

| Action | File | What changes |
|--------|------|-------------|
| Modify | `src/analysis/stats.py` | Add `wards_placed`, `control_wards` to `extract_match_stats()` return |
| Modify | `tests/test_stats.py` | Update fixture + add test for new fields |
| Modify | `src/analysis/timeline.py` | Add `extract_early_stats()` |
| Modify | `tests/test_timeline.py` | Add fixture + tests for `extract_early_stats()` |
| Create | `src/ui/views/performance.py` | Full `PerformanceView` widget |
| Modify | `src/ui/app.py` | Import + wire `PerformanceView` into sidebar and stack |

---

## Task 1: Add wards fields to extract_match_stats()

**Files:**
- Modify: `src/analysis/stats.py`
- Modify: `tests/test_stats.py`

- [ ] **Step 1: Update the SAMPLE_MATCH fixture in test_stats.py**

Add `wardsPlaced` and `visionWardsBoughtInGame` to both participants so the fixture matches real match data:

```python
# In SAMPLE_MATCH['info']['participants'][0] (player1):
'wardsPlaced': 8,
'visionWardsBoughtInGame': 2,

# In SAMPLE_MATCH['info']['participants'][1] (player2):
'wardsPlaced': 12,
'visionWardsBoughtInGame': 3,
```

The full updated player1 dict in SAMPLE_MATCH becomes:
```python
{
    'puuid': 'player1',
    'participantId': 1,
    'teamId': 100,
    'championName': 'Jinx',
    'win': True,
    'kills': 10,
    'deaths': 2,
    'assists': 5,
    'totalMinionsKilled': 200,
    'neutralMinionsKilled': 10,
    'totalDamageDealtToChampions': 30000,
    'goldEarned': 15000,
    'visionScore': 25,
    'wardsPlaced': 8,
    'visionWardsBoughtInGame': 2,
    'item0': 3031, 'item1': 3046, 'item2': 3094,
    'item3': 3036, 'item4': 3072, 'item5': 0, 'item6': 0,
    'perks': {'styles': []},
},
```

Player2:
```python
{
    'puuid': 'player2',
    'participantId': 2,
    'teamId': 100,
    'championName': 'Lulu',
    'win': True,
    'kills': 1,
    'deaths': 3,
    'assists': 12,
    'totalMinionsKilled': 30,
    'neutralMinionsKilled': 0,
    'totalDamageDealtToChampions': 10000,
    'goldEarned': 8000,
    'visionScore': 60,
    'wardsPlaced': 12,
    'visionWardsBoughtInGame': 3,
    'item0': 0, 'item1': 0, 'item2': 0,
    'item3': 0, 'item4': 0, 'item5': 0, 'item6': 0,
    'perks': {'styles': []},
},
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_stats.py`:

```python
def test_extract_match_stats_includes_wards():
    stats = extract_match_stats(SAMPLE_MATCH, 'player1')
    assert stats['wards_placed'] == 8
    assert stats['control_wards'] == 2
```

- [ ] **Step 3: Run test to confirm it fails**

```
pytest tests/test_stats.py::test_extract_match_stats_includes_wards -v
```

Expected: `FAILED — KeyError: 'wards_placed'`

- [ ] **Step 4: Add the two fields to extract_match_stats() in stats.py**

```python
def extract_match_stats(match_data: dict, puuid: str) -> dict:
    participant = get_participant(match_data, puuid)
    duration = match_data['info']['gameDuration']
    return {
        'champion': participant['championName'],
        'win': participant['win'],
        'kills': participant['kills'],
        'deaths': participant['deaths'],
        'assists': participant['assists'],
        'cs_per_min': calc_cs_per_min(participant, duration),
        'damage_dealt': participant['totalDamageDealtToChampions'],
        'damage_share': calc_damage_share(participant, match_data),
        'gold_earned': participant['goldEarned'],
        'vision_score': participant['visionScore'],
        'kill_participation': calc_kill_participation(participant, match_data),
        'game_duration': duration,
        'items': [participant[f'item{i}'] for i in range(7)],
        'perks': participant.get('perks', {}),
        'wards_placed': participant.get('wardsPlaced', 0),
        'control_wards': participant.get('visionWardsBoughtInGame', 0),
    }
```

- [ ] **Step 5: Run all stats tests**

```
pytest tests/test_stats.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/analysis/stats.py tests/test_stats.py
git commit -m "feat: add wards_placed and control_wards to extract_match_stats"
```

---

## Task 2: Add extract_early_stats() to timeline.py

**Files:**
- Modify: `src/analysis/timeline.py`
- Modify: `tests/test_timeline.py`

- [ ] **Step 1: Add the early-stats timeline fixture to test_timeline.py**

Append to `tests/test_timeline.py` after the existing fixtures:

```python
SAMPLE_MATCH_WITH_TEAMS = {
    'info': {
        'participants': [
            {'puuid': 'player1', 'participantId': 1, 'teamId': 100},
            {'puuid': 'player2', 'participantId': 2, 'teamId': 200},
        ]
    }
}

SAMPLE_TIMELINE_EARLY = {
    'info': {
        'frames': [
            {
                'timestamp': 0,
                'participantFrames': {
                    '1': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
                    '2': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
                },
                'events': [],
            },
            {
                'timestamp': 600000,  # 10 min
                'participantFrames': {
                    '1': {'minionsKilled': 60, 'jungleMinionsKilled': 3, 'totalGold': 3500},
                    '2': {'minionsKilled': 40, 'jungleMinionsKilled': 0, 'totalGold': 3000},
                },
                'events': [],
            },
            {
                'timestamp': 900000,  # 15 min
                'participantFrames': {
                    '1': {'minionsKilled': 95, 'jungleMinionsKilled': 5, 'totalGold': 5200},
                    '2': {'minionsKilled': 70, 'jungleMinionsKilled': 0, 'totalGold': 4800},
                },
                'events': [],
            },
        ]
    }
}
```

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_timeline.py`:

```python
from src.analysis.timeline import extract_early_stats

def test_extract_early_stats_cs():
    stats = extract_early_stats(SAMPLE_TIMELINE_EARLY, participant_id=1,
                                match_data=SAMPLE_MATCH_WITH_TEAMS)
    assert stats['cs_at_10'] == 63   # 60 + 3
    assert stats['cs_at_15'] == 100  # 95 + 5


def test_extract_early_stats_gold_diff():
    stats = extract_early_stats(SAMPLE_TIMELINE_EARLY, participant_id=1,
                                match_data=SAMPLE_MATCH_WITH_TEAMS)
    assert stats['gold_diff_at_10'] == 500   # 3500 - 3000
    assert stats['gold_diff_at_15'] == 400   # 5200 - 4800


def test_extract_early_stats_missing_frame_returns_zeros():
    short_timeline = {'info': {'frames': [
        {'timestamp': 0,
         'participantFrames': {
             '1': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
             '2': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
         },
         'events': []}
    ]}}
    stats = extract_early_stats(short_timeline, participant_id=1,
                                match_data=SAMPLE_MATCH_WITH_TEAMS)
    assert stats['cs_at_15'] == 0
    assert stats['gold_diff_at_15'] == 0
```

- [ ] **Step 3: Run tests to confirm they fail**

```
pytest tests/test_timeline.py::test_extract_early_stats_cs -v
```

Expected: `FAILED — ImportError: cannot import name 'extract_early_stats'`

- [ ] **Step 4: Implement extract_early_stats() in timeline.py**

Append to `src/analysis/timeline.py`:

```python
def extract_early_stats(timeline_data: dict, participant_id: int,
                        match_data: dict) -> dict:
    """Returns CS and gold differential at 10 and 15 minutes.

    Gold diff = player total gold - average enemy team gold at that timestamp.
    Returns zeros for any timestamp not reached in the timeline.
    """
    pid_str = str(participant_id)

    player_team_id = next(
        p['teamId'] for p in match_data['info']['participants']
        if p['participantId'] == participant_id
    )
    enemy_ids = [
        str(p['participantId'])
        for p in match_data['info']['participants']
        if p['teamId'] != player_team_id
    ]

    def last_frame_at(target_ms: int):
        best = None
        for frame in timeline_data['info']['frames']:
            if frame['timestamp'] <= target_ms:
                best = frame
            else:
                break
        return best

    def cs(frame) -> int:
        if frame is None:
            return 0
        pf = frame['participantFrames'].get(pid_str, {})
        return pf.get('minionsKilled', 0) + pf.get('jungleMinionsKilled', 0)

    def gold_diff(frame) -> int:
        if frame is None or not enemy_ids:
            return 0
        pf = frame['participantFrames'].get(pid_str, {})
        player_gold = pf.get('totalGold', 0)
        enemy_gold = [
            frame['participantFrames'].get(eid, {}).get('totalGold', 0)
            for eid in enemy_ids
        ]
        avg_enemy = sum(enemy_gold) / len(enemy_gold)
        return round(player_gold - avg_enemy)

    f10 = last_frame_at(10 * 60 * 1000)
    f15 = last_frame_at(15 * 60 * 1000)

    return {
        'cs_at_10': cs(f10),
        'cs_at_15': cs(f15),
        'gold_diff_at_10': gold_diff(f10),
        'gold_diff_at_15': gold_diff(f15),
    }
```

- [ ] **Step 5: Run all timeline tests**

```
pytest tests/test_timeline.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/analysis/timeline.py tests/test_timeline.py
git commit -m "feat: add extract_early_stats() for laning phase analysis"
```

---

## Task 3: Create PerformanceView

**Files:**
- Create: `src/ui/views/performance.py`

- [ ] **Step 1: Create the file with imports and class skeleton**

Create `src/ui/views/performance.py`:

```python
from pathlib import Path

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.db.schema import open_db
from src.db import cache as db_cache
from src.analysis.stats import extract_match_stats
from src.analysis.timeline import (
    get_participant_id, extract_early_stats, extract_position_events
)
from src.ui.theme import section_label, TEXT_SEC, TYPE_SMALL

DB_PATH = str(Path.home() / '.lol_adc_analyzer' / 'matches.db')

_CHART_BG   = '#1a1a2e'
_AXES_BG    = '#16213e'
_ACCENT     = '#c89b3c'
_TEXT_DIM   = '#aaaaaa'
_SPINE      = '#333355'
_GOLD_COLOR = '#c89b3c'
_GOOD       = '#c89b3c'
_BAD        = '#cc3300'
_GREEN      = '#00cc44'


class PerformanceView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._window = 20
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(0)

        title = QLabel('Performance')
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        outer.addWidget(title)
        outer.addSpacing(4)

        self._subtitle_label = QLabel('')
        self._subtitle_label.setStyleSheet(
            f'color: {TEXT_SEC}; font-size: {TYPE_SMALL}px;')
        outer.addWidget(self._subtitle_label)
        outer.addSpacing(16)

        # Window selector
        selector_row = QHBoxLayout()
        selector_row.setSpacing(8)
        self._window_btns: list[tuple[QPushButton, int]] = []
        for label, n in [('Last 10', 10), ('Last 20', 20), ('Last 50', 50)]:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda checked, w=n: self._set_window(w))
            self._window_btns.append((btn, n))
            selector_row.addWidget(btn)
        selector_row.addStretch()
        outer.addLayout(selector_row)
        outer.addSpacing(8)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 8, 16, 0)
        self._content_layout.setSpacing(8)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        self._no_data_label = QLabel(
            'Load a summoner from the Dashboard first.')
        self._content_layout.addWidget(self._no_data_label)

        # Trends
        self._content_layout.addWidget(section_label('Trends'))
        self._trends_canvas = FigureCanvas(Figure(figsize=(12, 9)))
        self._trends_canvas.setMinimumHeight(480)
        self._trends_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content_layout.addWidget(self._trends_canvas)

        # Laning
        self._content_layout.addWidget(section_label('Laning Phase'))
        self._laning_canvas = FigureCanvas(Figure(figsize=(12, 4)))
        self._laning_canvas.setMinimumHeight(240)
        self._laning_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content_layout.addWidget(self._laning_canvas)
        self._laning_insight = QLabel('')
        self._laning_insight.setStyleSheet(
            f'color: {TEXT_SEC}; font-style: italic;')
        self._laning_insight.setWordWrap(True)
        self._content_layout.addWidget(self._laning_insight)

        # Deaths
        self._content_layout.addWidget(section_label('Death Patterns'))
        self._deaths_canvas = FigureCanvas(Figure(figsize=(12, 3)))
        self._deaths_canvas.setMinimumHeight(200)
        self._deaths_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content_layout.addWidget(self._deaths_canvas)
        self._death_insight = QLabel('')
        self._death_insight.setStyleSheet(
            f'color: {TEXT_SEC}; font-style: italic;')
        self._death_insight.setWordWrap(True)
        self._content_layout.addWidget(self._death_insight)

        # Vision
        self._content_layout.addWidget(section_label('Vision Control'))
        self._vision_canvas = FigureCanvas(Figure(figsize=(12, 4)))
        self._vision_canvas.setMinimumHeight(240)
        self._vision_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content_layout.addWidget(self._vision_canvas)
        self._vision_insight = QLabel('')
        self._vision_insight.setStyleSheet(
            f'color: {TEXT_SEC}; font-style: italic;')
        self._vision_insight.setWordWrap(True)
        self._content_layout.addWidget(self._vision_insight)

        self._content_layout.addStretch()
        self._update_btn_styles()

    # ── Window selector ────────────────────────────────────────────────────────

    def _set_window(self, n: int):
        self._window = n
        self._update_btn_styles()
        self.refresh()

    def _update_btn_styles(self):
        for btn, n in self._window_btns:
            btn.setObjectName('cta_btn' if n == self._window else '')
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Data loading ───────────────────────────────────────────────────────────

    def refresh(self):
        conn = open_db(DB_PATH)
        row = conn.execute(
            'SELECT puuid FROM summoners ORDER BY last_updated DESC LIMIT 1'
        ).fetchone()
        if not row:
            self._no_data_label.setVisible(True)
            conn.close()
            return

        self._no_data_label.setVisible(False)
        puuid = row['puuid']
        match_ids = db_cache.get_cached_match_ids(conn, puuid)[-self._window:]

        stats_list, early_stats_list, all_deaths = [], [], []

        for mid in match_ids:
            match_data = db_cache.get_match(conn, mid)
            if match_data is None:
                continue
            try:
                stats = extract_match_stats(match_data, puuid)
                stats_list.append(stats)
            except (ValueError, KeyError):
                continue

            timeline_data = db_cache.get_timeline(conn, mid)
            if timeline_data:
                try:
                    pid = get_participant_id(match_data, puuid)
                    early_stats_list.append(
                        extract_early_stats(timeline_data, pid, match_data))
                    positions = extract_position_events(timeline_data, pid)
                    all_deaths.extend(positions['deaths'])
                except (ValueError, KeyError):
                    pass

        conn.close()

        n = len(stats_list)
        self._subtitle_label.setText(
            f'Showing {n} of last {self._window} matches'
            if n < self._window else f'Last {self._window} matches'
        )

        if stats_list:
            self._render_trends(stats_list)
            self._render_vision(stats_list)
            self._vision_insight.setText(
                self._generate_vision_insight(stats_list))

        if early_stats_list:
            self._render_laning(early_stats_list)
            self._laning_insight.setText(
                self._generate_laning_insight(early_stats_list))

        if all_deaths:
            self._render_deaths(all_deaths)
            self._death_insight.setText(
                self._generate_death_insight(all_deaths))

    # ── Chart rendering ────────────────────────────────────────────────────────

    def _render_trends(self, stats_list: list[dict]):
        fig = self._trends_canvas.figure
        fig.clear()
        fig.patch.set_facecolor(_CHART_BG)

        gs = GridSpec(3, 2, figure=fig, hspace=0.6, wspace=0.35)
        axes_data = [
            (fig.add_subplot(gs[0, 0]),
             [int(s['win']) * 100 for s in stats_list], 'Win Rate (%)', 50),
            (fig.add_subplot(gs[0, 1]),
             [round((s['kills'] + s['assists']) / max(s['deaths'], 1), 2)
              for s in stats_list], 'KDA', 3.0),
            (fig.add_subplot(gs[1, 0]),
             [s['cs_per_min'] for s in stats_list], 'CS / min', 7.0),
            (fig.add_subplot(gs[1, 1]),
             [s['damage_share'] for s in stats_list], 'Damage Share (%)', 25),
            (fig.add_subplot(gs[2, :]),
             [s['vision_score'] for s in stats_list], 'Vision Score', 25),
        ]

        xs = list(range(1, len(stats_list) + 1))
        for ax, values, title, target in axes_data:
            ax.set_facecolor(_AXES_BG)
            colors = [_GOOD if v >= target else _BAD for v in values]
            ax.plot(xs, values, color='#555577', linewidth=1, zorder=2)
            ax.scatter(xs, values, c=colors, s=40, zorder=3)
            ax.axhline(target, color=_ACCENT, linewidth=1,
                       linestyle='--', alpha=0.5, zorder=1)
            ax.set_title(title, color=_ACCENT, fontsize=10,
                         fontweight='bold', pad=4)
            ax.set_xlim(0, len(stats_list) + 1)
            ax.tick_params(colors=_TEXT_DIM, labelsize=8)
            ax.set_xlabel('Match', color=_TEXT_DIM, fontsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(_SPINE)

        try:
            fig.tight_layout()
        except Exception:
            pass
        self._trends_canvas.draw()

    def _render_laning(self, early_stats_list: list[dict]):
        fig = self._laning_canvas.figure
        fig.clear()
        fig.patch.set_facecolor(_CHART_BG)

        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)

        xs = list(range(1, len(early_stats_list) + 1))
        cs10 = [s['cs_at_10'] for s in early_stats_list]
        cs15 = [s['cs_at_15'] for s in early_stats_list]
        gd15 = [s['gold_diff_at_15'] for s in early_stats_list]

        for ax in (ax1, ax2):
            ax.set_facecolor(_AXES_BG)
            ax.tick_params(colors=_TEXT_DIM, labelsize=8)
            ax.set_xlabel('Match', color=_TEXT_DIM, fontsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(_SPINE)

        ax1.plot(xs, cs10, color=_ACCENT, label='CS @10',
                 linewidth=1.5, marker='o', markersize=4)
        ax1.plot(xs, cs15, color='#e8d5a3', label='CS @15',
                 linewidth=1.5, marker='o', markersize=4)
        ax1.axhline(70, color=_ACCENT, linestyle='--', alpha=0.4, linewidth=1)
        ax1.axhline(100, color='#e8d5a3', linestyle='--', alpha=0.4, linewidth=1)
        ax1.set_title('CS at 10 / 15 min', color=_ACCENT,
                      fontsize=10, fontweight='bold', pad=4)
        ax1.legend(fontsize=8, labelcolor=_TEXT_DIM,
                   facecolor=_AXES_BG, edgecolor=_SPINE)

        bar_colors = [_GREEN if v >= 0 else _BAD for v in gd15]
        ax2.bar(xs, gd15, color=bar_colors, alpha=0.85)
        ax2.axhline(0, color=_TEXT_DIM, linewidth=0.8)
        ax2.set_title('Gold Diff @ 15 min', color=_ACCENT,
                      fontsize=10, fontweight='bold', pad=4)

        try:
            fig.tight_layout()
        except Exception:
            pass
        self._laning_canvas.draw()

    def _render_deaths(self, all_deaths: list[dict]):
        fig = self._deaths_canvas.figure
        fig.clear()
        fig.patch.set_facecolor(_CHART_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(_AXES_BG)

        buckets = {'0–10 min': 0, '10–20 min': 0,
                   '20–30 min': 0, '30+ min': 0}
        for d in all_deaths:
            t = d['t']
            if t < 10:
                buckets['0–10 min'] += 1
            elif t < 20:
                buckets['10–20 min'] += 1
            elif t < 30:
                buckets['20–30 min'] += 1
            else:
                buckets['30+ min'] += 1

        labels = list(buckets.keys())
        values = list(buckets.values())
        peak = max(values) if values else 0
        colors = [_BAD if v == peak and v > 0 else '#555577' for v in values]

        ax.barh(labels, values, color=colors, height=0.5)
        ax.set_title('Deaths by Game Phase', color=_ACCENT,
                     fontsize=10, fontweight='bold', pad=4)
        ax.tick_params(colors=_TEXT_DIM, labelsize=9)
        ax.set_xlabel('Deaths', color=_TEXT_DIM, fontsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(_SPINE)

        try:
            fig.tight_layout()
        except Exception:
            pass
        self._deaths_canvas.draw()

    def _render_vision(self, stats_list: list[dict]):
        fig = self._vision_canvas.figure
        fig.clear()
        fig.patch.set_facecolor(_CHART_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(_AXES_BG)

        xs = list(range(1, len(stats_list) + 1))
        ax.plot(xs, [s['vision_score'] for s in stats_list],
                color=_ACCENT, label='Vision Score',
                linewidth=1.5, marker='o', markersize=4)
        ax.plot(xs, [s['wards_placed'] for s in stats_list],
                color='#e8d5a3', label='Wards Placed',
                linewidth=1.5, marker='s', markersize=4)
        ax.plot(xs, [s['control_wards'] for s in stats_list],
                color='#ffaa00', label='Control Wards',
                linewidth=1.5, marker='^', markersize=4)
        ax.axhline(25, color=_ACCENT, linestyle='--', alpha=0.4, linewidth=1)
        ax.axhline(2, color='#ffaa00', linestyle='--', alpha=0.4, linewidth=1)
        ax.set_title('Vision Control', color=_ACCENT,
                     fontsize=10, fontweight='bold', pad=4)
        ax.tick_params(colors=_TEXT_DIM, labelsize=8)
        ax.set_xlabel('Match', color=_TEXT_DIM, fontsize=8)
        ax.legend(fontsize=8, labelcolor=_TEXT_DIM,
                  facecolor=_AXES_BG, edgecolor=_SPINE)
        for spine in ax.spines.values():
            spine.set_edgecolor(_SPINE)

        try:
            fig.tight_layout()
        except Exception:
            pass
        self._vision_canvas.draw()

    # ── Insight generators ─────────────────────────────────────────────────────

    def _generate_laning_insight(self, early_stats_list: list[dict]) -> str:
        avg_cs10 = round(
            sum(s['cs_at_10'] for s in early_stats_list) / len(early_stats_list))
        avg_gd15 = round(
            sum(s['gold_diff_at_15'] for s in early_stats_list) / len(early_stats_list))
        if avg_gd15 < -300:
            return (f'You average {avg_gd15:+} gold at 15 min — '
                    f'focus on surviving and farming safely.')
        if avg_cs10 < 60:
            return (f'You average {avg_cs10} CS at 10 min — '
                    f'most strong ADC players hit 70+.')
        if avg_cs10 >= 70:
            return f'Your 10-min CS average of {avg_cs10} is solid.'
        return (f'You average {avg_cs10} CS at 10 min — '
                f'room to improve towards 70+.')

    def _generate_death_insight(self, all_deaths: list[dict]) -> str:
        buckets = {'0–10 min': 0, '10–20 min': 0,
                   '20–30 min': 0, '30+ min': 0}
        messages = {
            '0–10 min':  'Most deaths happen early — consider playing safer in the laning phase.',
            '10–20 min': 'Most deaths occur mid-game — watch your positioning when roaming.',
            '20–30 min': 'Most deaths happen 20–30 min — a common sign of overextending after winning lane.',
            '30+ min':   'Late-game deaths dominate — focus on positioning in teamfights and objectives.',
        }
        for d in all_deaths:
            t = d['t']
            if t < 10:
                buckets['0–10 min'] += 1
            elif t < 20:
                buckets['10–20 min'] += 1
            elif t < 30:
                buckets['20–30 min'] += 1
            else:
                buckets['30+ min'] += 1
        worst = max(buckets, key=buckets.get)
        return messages[worst]

    def _generate_vision_insight(self, stats_list: list[dict]) -> str:
        avg_cw = round(
            sum(s['control_wards'] for s in stats_list) / len(stats_list), 1)
        avg_vs = round(
            sum(s['vision_score'] for s in stats_list) / len(stats_list))
        if avg_cw < 1.5:
            return (f'You average {avg_cw} control wards per game — '
                    f'aim for 2+ as ADC.')
        if avg_vs < 20:
            return (f'Your vision score averages {avg_vs} — '
                    f'try placing wards more actively.')
        return (f'Vision control is consistent — {avg_vs} avg vision score '
                f'and {avg_cw} control wards per game.')
```

- [ ] **Step 2: Verify the file imports cleanly**

```
python -c "from src.ui.views.performance import PerformanceView; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/ui/views/performance.py
git commit -m "feat: add PerformanceView with trends and weakness panels"
```

---

## Task 4: Wire PerformanceView into app.py

**Files:**
- Modify: `src/ui/app.py`

- [ ] **Step 1: Add the import**

In `src/ui/app.py`, add to the existing import block:

```python
from src.ui.views.performance import PerformanceView
```

- [ ] **Step 2: Add the sidebar item and stacked widget**

In `_build_ui()`, the sidebar items list currently reads:
```python
for item in ['Dashboard', 'Match History', 'Builds & Runes']:
```

Change it to:
```python
for item in ['Dashboard', 'Match History', 'Builds & Runes', 'Performance']:
```

After the line `self.builds_panel_view = BuildsPanelView(self)`, add:
```python
self.performance_view = PerformanceView(self)
```

After `self.stack.addWidget(self.builds_panel_view)  # index 2`, add:
```python
self.stack.addWidget(self.performance_view)           # index 3
```

- [ ] **Step 3: Trigger refresh when Performance tab is selected**

Replace the existing `_on_nav_changed` method with:

```python
def _on_nav_changed(self, index: int):
    self.stack.setCurrentIndex(index)
    if index == 3:
        self.performance_view.refresh()
```

- [ ] **Step 4: Verify the app launches without errors**

```
python -c "
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.app import MainWindow
app = QApplication(sys.argv)
w = MainWindow()
print('OK')
app.quit()
"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add src/ui/app.py
git commit -m "feat: wire PerformanceView into sidebar as 4th tab"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Rolling window selector (Last 10/20/50) — Task 3 `_set_window` + `_update_btn_styles`
- ✅ Trends: Win Rate, KDA, CS/min, Damage Share, Vision Score — Task 3 `_render_trends` with GridSpec
- ✅ Reference lines — `axhline` calls in `_render_trends`
- ✅ Laning Phase chart + insight — Task 3 `_render_laning` + `_generate_laning_insight`
- ✅ `extract_early_stats()` — Task 2
- ✅ Death Patterns histogram + insight — Task 3 `_render_deaths` + `_generate_death_insight`
- ✅ Vision Control chart + insight — Task 3 `_render_vision` + `_generate_vision_insight`
- ✅ `wards_placed` / `control_wards` in stats — Task 1
- ✅ Empty/no-summoner state — `_no_data_label` visibility toggle in `refresh()`
- ✅ Partial window (fewer matches than N) — subtitle shows actual count
- ✅ Missing timeline data skipped gracefully — try/except in `refresh()`

**Type consistency check:**
- `extract_early_stats` returns `cs_at_10`, `cs_at_15`, `gold_diff_at_10`, `gold_diff_at_15` — matches usage in `_render_laning` and `_generate_laning_insight` ✅
- `extract_match_stats` returns `wards_placed`, `control_wards` — matches usage in `_render_vision` and `_generate_vision_insight` ✅
- `extract_position_events` returns `{'kills': [...], 'deaths': [...], 'assists': [...]}` — only `deaths` used, each element has `'t'` key ✅
