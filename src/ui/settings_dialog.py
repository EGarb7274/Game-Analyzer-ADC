from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QLabel, QVBoxLayout, QSpinBox
)
import config


REGION_OPTIONS = [
    ('NA (na1 / americas)', 'na1', 'americas'),
    ('EUW (euw1 / europe)', 'euw1', 'europe'),
    ('EUNE (eun1 / europe)', 'eun1', 'europe'),
    ('KR (kr / asia)', 'kr', 'asia'),
    ('BR (br1 / americas)', 'br1', 'americas'),
    ('JP (jp1 / asia)', 'jp1', 'asia'),
]


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setMinimumWidth(420)
        self._cfg = config.load_config()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            'Get a free API key at <a href="https://developer.riotgames.com">'
            'developer.riotgames.com</a>'
        )
        info.setOpenExternalLinks(True)
        layout.addWidget(info)

        form = QFormLayout()

        self.api_key_input = QLineEdit(self._cfg.get('api_key', ''))
        self.api_key_input.setPlaceholderText('RGAPI-xxxxxxxx-xxxx-...')
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('API Key:', self.api_key_input)

        self.region_combo = QComboBox()
        for label, _, _ in REGION_OPTIONS:
            self.region_combo.addItem(label)
        current_region = self._cfg.get('region', 'na1')
        for i, (_, region, _) in enumerate(REGION_OPTIONS):
            if region == current_region:
                self.region_combo.setCurrentIndex(i)
                break
        form.addRow('Region:', self.region_combo)

        self.match_count_spin = QSpinBox()
        self.match_count_spin.setRange(5, 100)
        self.match_count_spin.setValue(self._cfg.get('match_count', 20))
        form.addRow('Matches to load:', self.match_count_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save_and_accept(self):
        idx = self.region_combo.currentIndex()
        _, region, match_region = REGION_OPTIONS[idx]
        self._cfg['api_key'] = self.api_key_input.text().strip()
        self._cfg['region'] = region
        self._cfg['match_region'] = match_region
        self._cfg['match_count'] = self.match_count_spin.value()
        config.save_config(self._cfg)
        self.accept()
