import json
import pytest
from pathlib import Path
from unittest.mock import patch
from src.analysis import builds


def test_load_builds_returns_dict(tmp_path):
    builds_file = tmp_path / 'builds.json'
    builds_file.write_text(json.dumps({'Jinx': {'build': [3031], 'runes': {}, 'skill_order': 'Q'}}))
    with patch.object(builds, 'BUILDS_FILE', builds_file):
        result = builds.load_builds()
    assert 'Jinx' in result
    assert result['Jinx']['build'] == [3031]


def test_get_champion_build_returns_data(tmp_path):
    builds_file = tmp_path / 'builds.json'
    builds_file.write_text(json.dumps({'Jinx': {'build': [3031, 3046], 'runes': {'keystone': 'LT'}, 'skill_order': 'Q>E'}}))
    with patch.object(builds, 'BUILDS_FILE', builds_file):
        result = builds.get_champion_build('Jinx')
    assert result['skill_order'] == 'Q>E'
    assert result['runes']['keystone'] == 'LT'


def test_get_champion_build_returns_none_for_unknown(tmp_path):
    builds_file = tmp_path / 'builds.json'
    builds_file.write_text(json.dumps({}))
    with patch.object(builds, 'BUILDS_FILE', builds_file):
        result = builds.get_champion_build('Unknown')
    assert result is None


def test_list_champions_returns_sorted_list(tmp_path):
    builds_file = tmp_path / 'builds.json'
    builds_file.write_text(json.dumps({'Jinx': {}, 'Caitlyn': {}, 'Jhin': {}}))
    with patch.object(builds, 'BUILDS_FILE', builds_file):
        result = builds.list_champions()
    assert result == ['Caitlyn', 'Jhin', 'Jinx']
