import json
from pathlib import Path
from typing import Optional

BUILDS_FILE = Path(__file__).parent.parent.parent / 'data' / 'builds.json'


def load_builds() -> dict:
    with open(BUILDS_FILE) as f:
        return json.load(f)


def get_champion_build(champion_name: str) -> Optional[dict]:
    return load_builds().get(champion_name)


def list_champions() -> list[str]:
    return sorted(load_builds().keys())
