def get_participant(match_data: dict, puuid: str) -> dict:
    for p in match_data['info']['participants']:
        if p['puuid'] == puuid:
            return p
    raise ValueError(f'PUUID {puuid} not found in match')


def calc_kda(participant: dict) -> tuple[int, int, int]:
    return participant['kills'], participant['deaths'], participant['assists']


def calc_cs_per_min(participant: dict, game_duration_seconds: int) -> float:
    cs = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
    minutes = game_duration_seconds / 60
    return round(cs / minutes, 1) if minutes > 0 else 0.0


def calc_damage_share(participant: dict, match_data: dict) -> float:
    team_id = participant['teamId']
    team_damage = sum(
        p['totalDamageDealtToChampions']
        for p in match_data['info']['participants']
        if p['teamId'] == team_id
    )
    if team_damage == 0:
        return 0.0
    return round(participant['totalDamageDealtToChampions'] / team_damage * 100, 1)


def calc_kill_participation(participant: dict, match_data: dict) -> float:
    team_id = participant['teamId']
    team_kills = sum(
        p['kills']
        for p in match_data['info']['participants']
        if p['teamId'] == team_id
    )
    if team_kills == 0:
        return 0.0
    return round((participant['kills'] + participant['assists']) / team_kills * 100, 1)


def extract_match_stats(match_data: dict, puuid: str) -> dict:
    participant = get_participant(match_data, puuid)
    duration = match_data['info']['gameDuration']
    return {
        'champion': participant['championName'],
        'win': participant['win'],
        'kills': participant['kills'],
        'deaths': participant['deaths'],
        'assists': participant['assists'],
        'cs_per_min': calc_cs_per_min(participant, duration),
        'damage_dealt': participant['totalDamageDealtToChampions'],
        'damage_share': calc_damage_share(participant, match_data),
        'gold_earned': participant['goldEarned'],
        'vision_score': participant['visionScore'],
        'kill_participation': calc_kill_participation(participant, match_data),
        'game_duration': duration,
        'items': [participant[f'item{i}'] for i in range(7)],
        'perks': participant.get('perks', {}),
        'wards_placed': participant.get('wardsPlaced', 0),
        'control_wards': participant.get('visionWardsBoughtInGame', 0),
    }
