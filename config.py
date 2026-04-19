import json
from pathlib import Path

CONFIG_DIR = Path.home() / '.lol_adc_analyzer'
CONFIG_FILE = CONFIG_DIR / 'config.json'

DEFAULT_CONFIG = {
    'api_key': '',
    'region': 'na1',
    'match_region': 'americas',
    'match_count': 20,
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE) as f:
        data = json.load(f)
    return {**DEFAULT_CONFIG, **data}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)
