"""Database connection and idempotent upsert helpers."""
from __future__ import annotations

import psycopg

from config import CONNINFO


def connect() -> psycopg.Connection:
    return psycopg.connect(CONNINFO, autocommit=False)


UPSERT_TEAM = """
INSERT INTO teams (team_abbr, team_name, conference, division)
VALUES (%(team_abbr)s, %(team_name)s, %(conference)s, %(division)s)
ON CONFLICT (team_abbr) DO UPDATE SET
    team_name  = EXCLUDED.team_name,
    conference = EXCLUDED.conference,
    division   = EXCLUDED.division;
"""
UPSERT_PLAYER = """
INSERT INTO players (player_id, full_name, position, team_abbr, updated_at)
VALUES (%(player_id)s, %(full_name)s, %(position)s, %(team_abbr)s, now())
ON CONFLICT (player_id) DO UPDATE SET
    full_name  = EXCLUDED.full_name,
    position   = EXCLUDED.position,
    team_abbr  = EXCLUDED.team_abbr,
    updated_at = now();
"""


def upsert_many(conn: psycopg.Connection, sql: str, rows: list[dict]) -> int:
    """Run an upsert for every row. Returns the number of rows sent."""
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)
