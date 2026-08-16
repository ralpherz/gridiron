"""Recompute per-player, per-game stats from raw plays.

This reads only from plays and writes only to player_game_stats, so it can be
re-run any time the aggregation logic changes without re-downloading anything.
That separation is why plays holds source data and nothing derived.
"""
from __future__ import annotations

import psycopg

RECOMPUTE = """
WITH receiving AS (
    SELECT p.receiver_id AS player_id,
           p.game_id,
           count(*)                                AS targets,
           count(*) FILTER (WHERE p.complete_pass)  AS receptions,
           coalesce(sum(p.receiving_yards), 0)      AS rec_yards,
           count(*) FILTER (WHERE p.pass_touchdown) AS rec_tds
    FROM   plays p
    JOIN   games g ON g.game_id = p.game_id
    WHERE  p.receiver_id IS NOT NULL AND g.season = %(season)s
    GROUP  BY 1, 2
),
rushing AS (
    SELECT p.rusher_id AS player_id,
           p.game_id,
           coalesce(sum(p.rushing_yards), 0)        AS rush_yards,
           count(*) FILTER (WHERE p.rush_touchdown) AS rush_tds
    FROM   plays p
    JOIN   games g ON g.game_id = p.game_id
    WHERE  p.rusher_id IS NOT NULL AND g.season = %(season)s
    GROUP  BY 1, 2
),
combined AS (
    SELECT coalesce(rc.player_id, ru.player_id) AS player_id,
           coalesce(rc.game_id,   ru.game_id)   AS game_id,
           coalesce(rc.targets,    0) AS targets,
           coalesce(rc.receptions, 0) AS receptions,
           coalesce(rc.rec_yards,  0) AS rec_yards,
           coalesce(rc.rec_tds,    0) AS rec_tds,
           coalesce(ru.rush_yards, 0) AS rush_yards,
           coalesce(ru.rush_tds,   0) AS rush_tds
    FROM   receiving rc
    FULL OUTER JOIN rushing ru
      ON  rc.player_id = ru.player_id AND rc.game_id = ru.game_id
)
INSERT INTO player_game_stats
    (player_id, game_id, season, week, targets, receptions,
     rec_yards, rec_tds, rush_yards, rush_tds, computed_at)
SELECT c.player_id, c.game_id, g.season, g.week, c.targets, c.receptions,
       c.rec_yards, c.rec_tds, c.rush_yards, c.rush_tds, now()
FROM   combined c
JOIN   games   g  ON g.game_id   = c.game_id
JOIN   players pl ON pl.player_id = c.player_id
ON CONFLICT (player_id, game_id) DO UPDATE SET
    targets     = EXCLUDED.targets,
    receptions  = EXCLUDED.receptions,
    rec_yards   = EXCLUDED.rec_yards,
    rec_tds     = EXCLUDED.rec_tds,
    rush_yards  = EXCLUDED.rush_yards,
    rush_tds    = EXCLUDED.rush_tds,
    computed_at = now();
"""

def recompute_stats(conn: psycopg.Connection, season: int) -> int:
    """Rebuild player_game_stats for one season. Returns rows written."""
    with conn.cursor() as cur:
        cur.execute(RECOMPUTE, {"season": season})
        return cur.rowcount
