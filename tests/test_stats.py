import pytest
from src.analysis.stats import (
    get_participant, calc_kda, calc_cs_per_min,
    calc_damage_share, calc_kill_participation, extract_match_stats
)

SAMPLE_MATCH = {
    'info': {
        'gameDuration': 1800,
        'participants': [
            {
                'puuid': 'player1',
                'participantId': 1,
                'teamId': 100,
                'championName': 'Jinx',
                'win': True,
                'kills': 10,
                'deaths': 2,
                'assists': 5,
                'totalMinionsKilled': 200,
                'neutralMinionsKilled': 10,
                'totalDamageDealtToChampions': 30000,
                'goldEarned': 15000,
                'visionScore': 25,
                'wardsPlaced': 8,
                'visionWardsBoughtInGame': 2,
                'item0': 3031, 'item1': 3046, 'item2': 3094,
                'item3': 3036, 'item4': 3072, 'item5': 0, 'item6': 0,
                'perks': {'styles': []},
            },
            {
                'puuid': 'player2',
                'participantId': 2,
                'teamId': 100,
                'championName': 'Lulu',
                'win': True,
                'kills': 1,
                'deaths': 3,
                'assists': 12,
                'totalMinionsKilled': 30,
                'neutralMinionsKilled': 0,
                'totalDamageDealtToChampions': 10000,
                'goldEarned': 8000,
                'visionScore': 60,
                'wardsPlaced': 12,
                'visionWardsBoughtInGame': 3,
                'item0': 0, 'item1': 0, 'item2': 0,
                'item3': 0, 'item4': 0, 'item5': 0, 'item6': 0,
                'perks': {'styles': []},
            },
        ]
    }
}


def test_get_participant_returns_correct_player():
    p = get_participant(SAMPLE_MATCH, 'player1')
    assert p['championName'] == 'Jinx'


def test_get_participant_raises_for_unknown_puuid():
    with pytest.raises(ValueError):
        get_participant(SAMPLE_MATCH, 'unknown')


def test_calc_kda():
    p = get_participant(SAMPLE_MATCH, 'player1')
    assert calc_kda(p) == (10, 2, 5)


def test_calc_cs_per_min():
    p = get_participant(SAMPLE_MATCH, 'player1')
    result = calc_cs_per_min(p, game_duration_seconds=1800)
    assert result == 7.0   # 210 cs / 30 min


def test_calc_damage_share():
    p = get_participant(SAMPLE_MATCH, 'player1')
    result = calc_damage_share(p, SAMPLE_MATCH)
    assert result == 75.0  # 30000 / 40000


def test_calc_kill_participation():
    p = get_participant(SAMPLE_MATCH, 'player1')
    result = calc_kill_participation(p, SAMPLE_MATCH)
    # team kills = 10+1 = 11, kills+assists = 15, kp = round(15/11*100, 1) = 136.4
    assert result == 136.4


def test_extract_match_stats_returns_full_dict():
    stats = extract_match_stats(SAMPLE_MATCH, 'player1')
    assert stats['champion'] == 'Jinx'
    assert stats['win'] is True
    assert stats['kills'] == 10
    assert stats['cs_per_min'] == 7.0
    assert stats['damage_share'] == 75.0
    assert stats['items'] == [3031, 3046, 3094, 3036, 3072, 0, 0]


def test_extract_match_stats_includes_wards():
    stats = extract_match_stats(SAMPLE_MATCH, 'player1')
    assert stats['wards_placed'] == 8
    assert stats['control_wards'] == 2
