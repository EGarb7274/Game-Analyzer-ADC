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
