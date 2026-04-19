import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS summoners (
            puuid       TEXT PRIMARY KEY,
            game_name   TEXT NOT NULL,
            tag_line    TEXT NOT NULL,
            last_updated INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
        );

        CREATE TABLE IF NOT EXISTS match_ids (
            puuid       TEXT NOT NULL,
            match_id    TEXT NOT NULL,
            PRIMARY KEY (puuid, match_id),
            FOREIGN KEY (puuid) REFERENCES summoners(puuid)
        );

        CREATE TABLE IF NOT EXISTS matches (
            match_id    TEXT PRIMARY KEY,
            data_json   TEXT NOT NULL,
            fetched_at  INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
        );

        CREATE TABLE IF NOT EXISTS match_timelines (
            match_id    TEXT PRIMARY KEY,
            data_json   TEXT NOT NULL,
            fetched_at  INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """)
    conn.commit()


def open_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn
