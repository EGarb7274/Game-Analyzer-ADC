def get_participant_id(match_data: dict, puuid: str) -> int:
    """Get the 1-based participantId used in timeline events."""
    for p in match_data['info']['participants']:
        if p['puuid'] == puuid:
            return p['participantId']
    raise ValueError(f'PUUID {puuid} not found in match')


def extract_item_timings(timeline_data: dict, participant_id: int) -> list[dict]:
    """Returns [{item_id, timestamp_min}, ...] for ITEM_PURCHASED events."""
    timings = []
    for frame in timeline_data['info']['frames']:
        for event in frame['events']:
            if (event['type'] == 'ITEM_PURCHASED' and
                    event['participantId'] == participant_id):
                timings.append({
                    'item_id': event['itemId'],
                    'timestamp_min': round(event['timestamp'] / 60000, 1),
                })
    return timings


def extract_position_events(timeline_data: dict,
                            participant_id: int) -> dict:
    """Returns {kills: [{x,y,t}], deaths: [{x,y,t}], assists: [{x,y,t}]}"""
    kills, deaths, assists = [], [], []
    for frame in timeline_data['info']['frames']:
        for event in frame['events']:
            if event['type'] != 'CHAMPION_KILL':
                continue
            pos = event.get('position')
            if not pos:
                continue
            t = round(event['timestamp'] / 60000, 1)
            point = {'x': pos['x'], 'y': pos['y'], 't': t}
            if event.get('killerId') == participant_id:
                kills.append(point)
            elif event.get('victimId') == participant_id:
                deaths.append(point)
            elif participant_id in event.get('assistingParticipantIds', []):
                assists.append(point)
    return {'kills': kills, 'deaths': deaths, 'assists': assists}


def extract_early_stats(timeline_data: dict, participant_id: int,
                        match_data: dict) -> dict:
    """Returns CS and gold differential at 10 and 15 minutes.

    Gold diff = player total gold - average enemy team gold at that timestamp.
    Returns zeros for any timestamp not reached in the timeline.
    """
    pid_str = str(participant_id)

    player_team_id = next(
        p['teamId'] for p in match_data['info']['participants']
        if p['participantId'] == participant_id
    )
    enemy_ids = [
        str(p['participantId'])
        for p in match_data['info']['participants']
        if p['teamId'] != player_team_id
    ]

    def last_frame_at(target_ms: int):
        best = None
        for frame in timeline_data['info']['frames']:
            if frame['timestamp'] <= target_ms:
                best = frame
            else:
                break
        return best

    def cs(frame) -> int:
        if frame is None:
            return 0
        pf = frame['participantFrames'].get(pid_str, {})
        return pf.get('minionsKilled', 0) + pf.get('jungleMinionsKilled', 0)

    def gold_diff(frame) -> int:
        if frame is None or not enemy_ids:
            return 0
        pf = frame['participantFrames'].get(pid_str, {})
        player_gold = pf.get('totalGold', 0)
        enemy_gold = [
            frame['participantFrames'].get(eid, {}).get('totalGold', 0)
            for eid in enemy_ids
        ]
        avg_enemy = sum(enemy_gold) / len(enemy_gold)
        return round(player_gold - avg_enemy)

    f10 = last_frame_at(10 * 60 * 1000)
    f15 = last_frame_at(15 * 60 * 1000)

    return {
        'cs_at_10': cs(f10),
        'cs_at_15': cs(f15),
        'gold_diff_at_10': gold_diff(f10),
        'gold_diff_at_15': gold_diff(f15),
    }
