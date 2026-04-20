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


# ── extract_early_stats fixtures ──────────────────────────────────────────────

SAMPLE_MATCH_WITH_TEAMS = {
    'info': {
        'participants': [
            {'puuid': 'player1', 'participantId': 1, 'teamId': 100},
            {'puuid': 'player2', 'participantId': 2, 'teamId': 200},
        ]
    }
}

SAMPLE_TIMELINE_EARLY = {
    'info': {
        'frames': [
            {
                'timestamp': 0,
                'participantFrames': {
                    '1': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
                    '2': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
                },
                'events': [],
            },
            {
                'timestamp': 600000,  # 10 min
                'participantFrames': {
                    '1': {'minionsKilled': 60, 'jungleMinionsKilled': 3, 'totalGold': 3500},
                    '2': {'minionsKilled': 40, 'jungleMinionsKilled': 0, 'totalGold': 3000},
                },
                'events': [],
            },
            {
                'timestamp': 900000,  # 15 min
                'participantFrames': {
                    '1': {'minionsKilled': 95, 'jungleMinionsKilled': 5, 'totalGold': 5200},
                    '2': {'minionsKilled': 70, 'jungleMinionsKilled': 0, 'totalGold': 4800},
                },
                'events': [],
            },
        ]
    }
}


from src.analysis.timeline import extract_early_stats


def test_extract_early_stats_cs():
    stats = extract_early_stats(SAMPLE_TIMELINE_EARLY, participant_id=1,
                                match_data=SAMPLE_MATCH_WITH_TEAMS)
    assert stats['cs_at_10'] == 63   # 60 + 3
    assert stats['cs_at_15'] == 100  # 95 + 5


def test_extract_early_stats_gold_diff():
    stats = extract_early_stats(SAMPLE_TIMELINE_EARLY, participant_id=1,
                                match_data=SAMPLE_MATCH_WITH_TEAMS)
    assert stats['gold_diff_at_10'] == 500   # 3500 - 3000
    assert stats['gold_diff_at_15'] == 400   # 5200 - 4800


def test_extract_early_stats_missing_frame_returns_zeros():
    short_timeline = {'info': {'frames': [
        {'timestamp': 0,
         'participantFrames': {
             '1': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
             '2': {'minionsKilled': 0, 'jungleMinionsKilled': 0, 'totalGold': 500},
         },
         'events': []}
    ]}}
    stats = extract_early_stats(short_timeline, participant_id=1,
                                match_data=SAMPLE_MATCH_WITH_TEAMS)
    assert stats['cs_at_15'] == 0
    assert stats['gold_diff_at_15'] == 0
