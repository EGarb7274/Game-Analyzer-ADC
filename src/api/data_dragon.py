import json
import requests
from pathlib import Path
from typing import Optional

DDRAGON_BASE = 'https://ddragon.leagueoflegends.com'
CACHE_DIR = Path.home() / '.lol_adc_analyzer' / 'ddragon'


def _get_latest_version() -> str:
    resp = requests.get(f'{DDRAGON_BASE}/api/versions.json', timeout=10)
    resp.raise_for_status()
    return resp.json()[0]


def _fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


class DataDragon:
    def __init__(self, version: Optional[str] = None):
        self._version = version
        self._items: Optional[dict] = None
        self._champions: Optional[dict] = None
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def version(self) -> str:
        if self._version is None:
            self._version = _get_latest_version()
        return self._version

    def get_items(self) -> dict:
        """Returns {item_id_str: {name, description, ...}}"""
        if self._items is None:
            cache_file = CACHE_DIR / f'items_{self.version}.json'
            if cache_file.exists():
                self._items = json.loads(cache_file.read_text())
            else:
                data = _fetch_json(
                    f'{DDRAGON_BASE}/cdn/{self.version}/data/en_US/item.json'
                )
                self._items = data['data']
                cache_file.write_text(json.dumps(self._items))
        return self._items

    def get_item_name(self, item_id: int) -> str:
        items = self.get_items()
        entry = items.get(str(item_id))
        return entry['name'] if entry else f'Item {item_id}'

    def get_champions(self) -> dict:
        """Returns {champion_name: {id, title, ...}}"""
        if self._champions is None:
            cache_file = CACHE_DIR / f'champions_{self.version}.json'
            if cache_file.exists():
                self._champions = json.loads(cache_file.read_text())
            else:
                data = _fetch_json(
                    f'{DDRAGON_BASE}/cdn/{self.version}/data/en_US/champion.json'
                )
                self._champions = data['data']
                cache_file.write_text(json.dumps(self._champions))
        return self._champions

    def get_minimap_path(self) -> Path:
        """Downloads and caches the Summoner's Rift map image."""
        minimap_file = CACHE_DIR / 'minimap.png'
        if not minimap_file.exists():
            resp = requests.get(
                'https://raw.communitydragon.org/latest/plugins/'
                'rcp-fe-lol-match-history/global/default/map11.png',
                timeout=15
            )
            resp.raise_for_status()
            minimap_file.write_bytes(resp.content)
        return minimap_file
