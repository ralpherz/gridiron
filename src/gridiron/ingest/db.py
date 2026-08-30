"""Database connection and idempotent upsert helpers."""
from __future__ import annotations

import psycopg

from gridiron.ingest.config import CONNINFO


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

UPSERT_GAME = """
INSERT INTO games (game_id, season, week, game_date,
                   home_team, away_team, home_score, away_score)
VALUES (%(game_id)s, %(season)s, %(week)s, %(game_date)s,
        %(home_team)s, %(away_team)s, %(home_score)s, %(away_score)s)
ON CONFLICT (game_id) DO UPDATE SET
    game_date  = EXCLUDED.game_date,
    home_score = EXCLUDED.home_score,
    away_score = EXCLUDED.away_score;
"""

UPSERT_PLAYER_DETAIL = """
UPDATE players SET
    headshot_url = %(headshot_url)s,
    pfr_id       = %(pfr_id)s
WHERE player_id = %(player_id)s;
"""

UPSERT_TEAM_BRANDING = """
UPDATE teams SET
    conference  = %(conference)s,
    division    = %(division)s,
    team_color  = %(team_color)s,
    team_color2 = %(team_color2)s,
    logo_url    = %(logo_url)s
WHERE team_abbr = %(team_abbr)s;
"""
