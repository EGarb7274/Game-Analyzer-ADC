import time
from riotwatcher import LolWatcher, RiotWatcher, ApiError


class RiotClient:
    def __init__(self, api_key: str, region: str = 'na1',
                 match_region: str = 'americas'):
        self.watcher = LolWatcher(api_key)
        self.riot_watcher = RiotWatcher(api_key)
        self.region = region
        self.match_region = match_region

    def _call_with_retry(self, fn, *args, max_retries: int = 3, **kwargs):
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except ApiError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get('Retry-After', 1))
                    time.sleep(retry_after)
                    continue
                raise
        return fn(*args, **kwargs)

    def get_puuid(self, game_name: str, tag_line: str) -> dict:
        """Returns {puuid, gameName, tagLine}."""
        return self._call_with_retry(
            self.riot_watcher.account.by_riot_id,
            region=self.match_region,
            game_name=game_name,
            tag_line=tag_line,
        )

    def get_match_ids(self, puuid: str, count: int = 20,
                      queue: int = 420) -> list[str]:
        """Returns list of match IDs. queue=420 is Ranked Solo/Duo."""
        return self._call_with_retry(
            self.watcher.match.matchlist_by_puuid,
            region=self.match_region,
            puuid=puuid,
            queue=queue,
            count=count,
        )

    def get_match(self, match_id: str) -> dict:
        return self._call_with_retry(
            self.watcher.match.by_id,
            region=self.match_region,
            match_id=match_id,
        )

    def get_timeline(self, match_id: str) -> dict:
        return self._call_with_retry(
            self.watcher.match.timeline_by_match,
            region=self.match_region,
            match_id=match_id,
        )
