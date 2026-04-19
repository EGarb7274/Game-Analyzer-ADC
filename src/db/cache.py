import json
import sqlite3
from typing import Optional


def upsert_summoner(conn: sqlite3.Connection, puuid: str,
                    game_name: str, tag_line: str) -> None:
    conn.execute("""
        INSERT INTO summoners (puuid, game_name, tag_line)
        VALUES (?, ?, ?)
        ON CONFLICT(puuid) DO UPDATE SET
            game_name=excluded.game_name,
            tag_line=excluded.tag_line,
            last_updated=strftime('%s', 'now')
    """, (puuid, game_name, tag_line))
    conn.commit()


def get_summoner_by_name(conn: sqlite3.Connection,
                         game_name: str, tag_line: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM summoners WHERE game_name=? AND tag_line=?",
        (game_name, tag_line)
    ).fetchone()
    return dict(row) if row else None


def save_match_ids(conn: sqlite3.Connection, puuid: str,
                   match_ids: list[str]) -> None:
    conn.executemany(
        "INSERT OR IGNORE INTO match_ids (puuid, match_id) VALUES (?, ?)",
        [(puuid, mid) for mid in match_ids]
    )
    conn.commit()


def get_cached_match_ids(conn: sqlite3.Connection, puuid: str) -> list[str]:
    rows = conn.execute(
        "SELECT match_id FROM match_ids WHERE puuid=?", (puuid,)
    ).fetchall()
    return [row['match_id'] for row in rows]


def get_uncached_match_ids(conn: sqlite3.Connection, puuid: str) -> list[str]:
    rows = conn.execute("""
        SELECT mi.match_id FROM match_ids mi
        LEFT JOIN matches m ON mi.match_id = m.match_id
        WHERE mi.puuid=? AND m.match_id IS NULL
    """, (puuid,)).fetchall()
    return [row['match_id'] for row in rows]


def save_match(conn: sqlite3.Connection, match_id: str, data: dict) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO matches (match_id, data_json) VALUES (?, ?)",
        (match_id, json.dumps(data))
    )
    conn.commit()


def get_match(conn: sqlite3.Connection, match_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT data_json FROM matches WHERE match_id=?", (match_id,)
    ).fetchone()
    return json.loads(row['data_json']) if row else None


def save_timeline(conn: sqlite3.Connection, match_id: str, data: dict) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO match_timelines (match_id, data_json) VALUES (?, ?)",
        (match_id, json.dumps(data))
    )
    conn.commit()


def get_timeline(conn: sqlite3.Connection, match_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT data_json FROM match_timelines WHERE match_id=?", (match_id,)
    ).fetchone()
    return json.loads(row['data_json']) if row else None
