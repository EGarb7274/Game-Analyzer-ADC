import pytest
from unittest.mock import MagicMock, patch
from src.api.riot_client import RiotClient


@pytest.fixture
def mock_watcher():
    with patch('src.api.riot_client.LolWatcher') as MockLol, \
         patch('src.api.riot_client.RiotWatcher') as MockRiot:
        lol_instance = MockLol.return_value
        riot_instance = MockRiot.return_value
        yield lol_instance, riot_instance


@pytest.fixture
def client(mock_watcher):
    return RiotClient(api_key='test-key', region='na1', match_region='americas')


def test_get_puuid_calls_account_api(client, mock_watcher):
    _lol, riot = mock_watcher
    riot.account.by_riot_id.return_value = {
        'puuid': 'abc123', 'gameName': 'TestPlayer', 'tagLine': 'NA1'
    }
    result = client.get_puuid('TestPlayer', 'NA1')
    assert result['puuid'] == 'abc123'
    riot.account.by_riot_id.assert_called_once_with(
        region='americas', game_name='TestPlayer', tag_line='NA1'
    )


def test_get_match_ids_calls_matchlist(client, mock_watcher):
    lol, _riot = mock_watcher
    lol.match.matchlist_by_puuid.return_value = ['NA1_1', 'NA1_2']
    result = client.get_match_ids('abc123', count=20)
    assert result == ['NA1_1', 'NA1_2']
    lol.match.matchlist_by_puuid.assert_called_once_with(
        region='americas', puuid='abc123', queue=420, count=20
    )


def test_get_match_calls_match_by_id(client, mock_watcher):
    lol, _riot = mock_watcher
    lol.match.by_id.return_value = {'info': {'gameDuration': 1800}}
    result = client.get_match('NA1_1')
    assert result['info']['gameDuration'] == 1800
    lol.match.by_id.assert_called_once_with(
        region='americas', match_id='NA1_1'
    )


def test_get_timeline_calls_timeline_by_match(client, mock_watcher):
    lol, _riot = mock_watcher
    lol.match.timeline_by_match.return_value = {'info': {'frames': []}}
    result = client.get_timeline('NA1_1')
    assert result['info']['frames'] == []


def test_get_match_ids_retries_on_rate_limit(client, mock_watcher):
    from riotwatcher import ApiError
    lol, _riot = mock_watcher
    resp = MagicMock()
    resp.status_code = 429
    resp.headers = {'Retry-After': '0'}
    error = ApiError(response=resp)
    lol.match.matchlist_by_puuid.side_effect = [error, ['NA1_1']]
    result = client.get_match_ids('abc123', count=20)
    assert result == ['NA1_1']
    assert lol.match.matchlist_by_puuid.call_count == 2
