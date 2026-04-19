import json
import pytest
from pathlib import Path
from unittest.mock import patch
import config


def test_load_config_returns_defaults_when_no_file(tmp_path):
    with patch.object(config, 'CONFIG_FILE', tmp_path / 'config.json'):
        result = config.load_config()
    assert result['api_key'] == ''
    assert result['region'] == 'na1'
    assert result['match_region'] == 'americas'
    assert result['match_count'] == 20


def test_save_and_load_config_roundtrip(tmp_path):
    with patch.object(config, 'CONFIG_FILE', tmp_path / 'config.json'), \
         patch.object(config, 'CONFIG_DIR', tmp_path):
        config.save_config({'api_key': 'test-key', 'region': 'euw1',
                            'match_region': 'europe', 'match_count': 30})
        result = config.load_config()
    assert result['api_key'] == 'test-key'
    assert result['region'] == 'euw1'
    assert result['match_count'] == 30


def test_load_config_merges_missing_keys(tmp_path):
    cfg_file = tmp_path / 'config.json'
    cfg_file.write_text(json.dumps({'api_key': 'abc'}))
    with patch.object(config, 'CONFIG_FILE', cfg_file):
        result = config.load_config()
    assert result['api_key'] == 'abc'
    assert result['region'] == 'na1'   # default filled in
