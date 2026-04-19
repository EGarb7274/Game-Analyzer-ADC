import pytest
from src.analysis.timeline import (
    get_participant_id, extract_item_timings, extract_position_events
)

SAMPLE_MATCH = {
    'info': {
        'participants': [
            {'puuid': 'player1', 'participantId': 1},
            {'puuid': 'player2', 'participantId': 2},
        ]
    }
}

SAMPLE_TIMELINE = {
    'info': {
        'frames': [
            {
                'events': [
                    {
                        'type': 'ITEM_PURCHASED',
                        'participantId': 1,
                        'itemId': 3031,
                        'timestamp': 480000,   # 8 minutes
                    },
                    {
                        'type': 'ITEM_PURCHASED',
                        'participantId': 2,
                        'itemId': 3056,
                        'timestamp': 600000,
                    },
                    {
                        'type': 'CHAMPION_KILL',
                        'killerId': 1,
                        'victimId': 2,
                        'assistingParticipantIds': [],
                        'position': {'x': 5000, 'y': 3000},
                        'timestamp': 900000,   # 15 minutes
                    },
                    {
                        'type': 'CHAMPION_KILL',
                        'killerId': 2,
                        'victimId': 1,
                        'assistingParticipantIds': [],
                        'position': {'x': 7000, 'y': 4000},
                        'timestamp': 1200000,
                    },
                ]
            }
        ]
    }
}


def test_get_participant_id():
    assert get_participant_id(SAMPLE_MATCH, 'player1') == 1
    assert get_participant_id(SAMPLE_MATCH, 'player2') == 2


def test_get_participant_id_raises_for_unknown():
    with pytest.raises(ValueError):
        get_participant_id(SAMPLE_MATCH, 'unknown')


def test_extract_item_timings_returns_only_own_purchases():
    timings = extract_item_timings(SAMPLE_TIMELINE, participant_id=1)
    assert len(timings) == 1
    assert timings[0]['item_id'] == 3031
    assert timings[0]['timestamp_min'] == 8.0


def test_extract_item_timings_empty_for_other_participant():
    timings = extract_item_timings(SAMPLE_TIMELINE, participant_id=99)
    assert timings == []


def test_extract_position_events_kills():
    events = extract_position_events(SAMPLE_TIMELINE, participant_id=1)
    assert len(events['kills']) == 1
    assert events['kills'][0] == {'x': 5000, 'y': 3000, 't': 15.0}


def test_extract_position_events_deaths():
    events = extract_position_events(SAMPLE_TIMELINE, participant_id=1)
    assert len(events['deaths']) == 1
    assert events['deaths'][0] == {'x': 7000, 'y': 4000, 't': 20.0}


def test_extract_position_events_assists():
    timeline = {
        'info': {
            'frames': [{
                'events': [{
                    'type': 'CHAMPION_KILL',
                    'killerId': 2,
                    'victimId': 3,
                    'assistingParticipantIds': [1],
                    'position': {'x': 6000, 'y': 5000},
                    'timestamp': 600000,
                }]
            }]
        }
    }
    events = extract_position_events(timeline, participant_id=1)
    assert len(events['assists']) == 1
    assert events['assists'][0]['x'] == 6000
