from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# ── Color palette ──────────────────────────────────────────────────────────────
BG_DARK      = '#0f0f1a'
BG_SURFACE   = '#1a1a2e'
BG_CARD      = '#16213e'
BG_CARD_ALT  = '#1e2d4a'
ACCENT       = '#c89b3c'
ACCENT_DARK  = '#a07828'
ACCENT_LIGHT = '#d4a94a'
TEXT_PRI     = '#e8d5a3'
TEXT_SEC     = '#a8a8b8'
TEXT_MUTED   = '#555566'
BORDER       = '#2a2a3e'
SUCCESS      = '#00cc44'
ERROR        = '#cc3300'
WARNING      = '#ffaa00'

# ── Type scale (px) ─────────────────────────────────────────────────────────────
TYPE_TITLE   = 20
TYPE_SECTION = 13
TYPE_BODY    = 13
TYPE_VALUE   = 16
TYPE_SMALL   = 11

# ── Reusable card stylesheet ─────────────────────────────────────────────────────
_CARD_STYLE = f"""
    QFrame {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    QLabel {{
        background-color: transparent;
        border: none;
        border-radius: 0px;
    }}
"""

# ── App-wide stylesheet ──────────────────────────────────────────────────────────
APP_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {BG_DARK};
}}
QWidget {{
    font-family: 'Segoe UI';
    font-size: {TYPE_BODY}px;
    color: {TEXT_PRI};
}}

/* Sidebar nav */
QListWidget {{
    background-color: {BG_SURFACE};
    border: none;
    border-right: 1px solid {BORDER};
    outline: none;
    padding: 8px 0;
}}
QListWidget::item {{
    color: {TEXT_SEC};
    padding: 12px 16px;
    min-height: 20px;
}}
QListWidget::item:selected {{
    background-color: {BG_CARD};
    color: {ACCENT};
    font-weight: bold;
}}
QListWidget::item:hover:!selected {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
}}

/* Champion list (distinct from sidebar) */
QListWidget#champ_list {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px;
}}
QListWidget#champ_list::item {{
    padding: 8px 12px;
    border-radius: 4px;
    color: {TEXT_PRI};
}}
QListWidget#champ_list::item:selected {{
    background-color: {ACCENT};
    color: {BG_DARK};
    font-weight: bold;
}}
QListWidget#champ_list::item:hover:!selected {{
    background-color: {BG_CARD_ALT};
}}

/* Buttons — secondary (default) */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    min-height: 34px;
    font-size: {TYPE_BODY}px;
}}
QPushButton:hover {{
    background-color: {BG_CARD_ALT};
    border-color: {ACCENT};
    color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT_DARK};
    border-color: {ACCENT_DARK};
    color: {BG_DARK};
}}
QPushButton:disabled {{
    background-color: {BG_SURFACE};
    color: {TEXT_MUTED};
    border-color: {BORDER};
}}

/* CTA / primary button — set objectName="cta_btn" */
QPushButton#cta_btn {{
    background-color: {ACCENT};
    color: {BG_DARK};
    border: none;
    font-weight: bold;
}}
QPushButton#cta_btn:hover {{
    background-color: {ACCENT_LIGHT};
}}
QPushButton#cta_btn:pressed {{
    background-color: {ACCENT_DARK};
}}
QPushButton#cta_btn:disabled {{
    background-color: {TEXT_MUTED};
    color: {BG_SURFACE};
}}

/* Text inputs */
QLineEdit {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 34px;
    selection-background-color: {ACCENT};
    selection-color: {BG_DARK};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}
QLineEdit:disabled {{
    color: {TEXT_MUTED};
    background-color: {BG_SURFACE};
}}

/* Combo box */
QComboBox {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 34px;
}}
QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
    selection-background-color: {ACCENT};
    selection-color: {BG_DARK};
    border: 1px solid {BORDER};
    outline: none;
}}

/* Spin box */
QSpinBox {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 34px;
}}
QSpinBox:focus {{
    border-color: {ACCENT};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BG_CARD_ALT};
    border: none;
    border-radius: 3px;
    width: 16px;
}}

/* Tables */
QTableWidget {{
    background-color: {BG_SURFACE};
    alternate-background-color: {BG_CARD};
    color: {TEXT_PRI};
    gridline-color: transparent;
    border: none;
    outline: none;
}}
QTableWidget::item {{
    padding: 8px 10px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: {BG_CARD_ALT};
    color: {TEXT_PRI};
}}
QHeaderView::section {{
    background-color: {BG_DARK};
    color: {ACCENT};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: bold;
    font-size: 12px;
}}
QHeaderView {{
    background-color: {BG_DARK};
    border: none;
}}

/* Scroll bars */
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollBar:vertical {{
    background: {BG_SURFACE};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_SURFACE};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* Status bar */
QStatusBar {{
    background-color: {BG_SURFACE};
    color: {TEXT_SEC};
    border-top: 1px solid {BORDER};
    font-size: 12px;
}}

/* Transparent label default */
QLabel {{
    background-color: transparent;
}}

/* Message box */
QMessageBox {{
    background-color: {BG_DARK};
}}
QMessageBox QLabel {{
    color: {TEXT_PRI};
}}
"""


class StatCard(QFrame):
    """Reusable stat display card: title above, large bold value below."""
    def __init__(self, title: str, value: str):
        super().__init__()
        self.setStyleSheet(_CARD_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet(f'color: {TEXT_SEC}; font-size: {TYPE_SMALL}px;')

        lbl_value = QLabel(value)
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_value.setStyleSheet(
            f'color: {TEXT_PRI}; font-size: {TYPE_VALUE}px; font-weight: bold;')
        lbl_value.setWordWrap(True)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)


def section_label(text: str) -> QLabel:
    """Returns a styled gold section header QLabel."""
    lbl = QLabel(text)
    lbl.setFont(QFont('Segoe UI', TYPE_SECTION, QFont.Weight.Bold))
    lbl.setStyleSheet(
        f'color: {ACCENT}; '
        f'background-color: transparent; '
        f'padding-top: 8px; padding-bottom: 2px;'
    )
    return lbl
