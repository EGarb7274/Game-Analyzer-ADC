import json
import sqlite3
import pytest
from src.db import schema, cache


@pytest.fixture
def db(tmp_path):
    conn = sqlite3.connect(str(tmp_path / 'test.db'))
    schema.init_db(conn)
    yield conn
    conn.close()


def test_init_db_creates_tables(db):
    tables = {row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    assert {'summoners', 'match_ids', 'matches', 'match_timelines'}.issubset(tables)


def test_upsert_and_get_summoner(db):
    cache.upsert_summoner(db, puuid='abc', game_name='Player', tag_line='NA1')
    result = cache.get_summoner_by_name(db, game_name='Player', tag_line='NA1')
    assert result['puuid'] == 'abc'
    assert result['game_name'] == 'Player'


def test_get_summoner_returns_none_when_missing(db):
    assert cache.get_summoner_by_name(db, game_name='X', tag_line='Y') is None


def test_save_and_get_match(db):
    data = {'info': {'gameDuration': 1800}}
    cache.save_match(db, match_id='NA1_123', data=data)
    result = cache.get_match(db, match_id='NA1_123')
    assert result['info']['gameDuration'] == 1800


def test_get_match_returns_none_when_missing(db):
    assert cache.get_match(db, match_id='NOPE') is None


def test_save_and_get_timeline(db):
    data = {'info': {'frames': []}}
    cache.save_timeline(db, match_id='NA1_123', data=data)
    result = cache.get_timeline(db, match_id='NA1_123')
    assert result['info']['frames'] == []


def test_save_match_ids_and_get_cached(db):
    cache.upsert_summoner(db, puuid='p1', game_name='A', tag_line='B')
    cache.save_match_ids(db, puuid='p1', match_ids=['M1', 'M2', 'M3'])
    ids = cache.get_cached_match_ids(db, puuid='p1')
    assert set(ids) == {'M1', 'M2', 'M3'}


def test_get_uncached_match_ids(db):
    cache.upsert_summoner(db, puuid='p1', game_name='A', tag_line='B')
    cache.save_match_ids(db, puuid='p1', match_ids=['M1', 'M2'])
    cache.save_match(db, match_id='M1', data={})
    uncached = cache.get_uncached_match_ids(db, puuid='p1')
    assert uncached == ['M2']
