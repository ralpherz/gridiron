"""Load play-by-play.

Two things make this different from the smaller jobs:

1. Volume. Roughly 50,000 rows per season is too many for row-by-row inserts,
   so we COPY into a temporary staging table and merge in one statement.
2. Width. The source has 372 columns and we want 15. Narrowing the frame
   before converting to Python objects takes the transform from ~18s to ~0.2s.
"""
from __future__ import annotations

import pandas as pd
import psycopg

from nflverse import fetch_pbp

SOURCE_COLUMNS = [
    "game_id", "play_id", "posteam", "play_type", "yards_gained",
    "touchdown", "passer_player_id", "receiver_player_id",
    "rusher_player_id", "epa", "complete_pass", "pass_touchdown",
    "rush_touchdown", "receiving_yards", "rushing_yards",
]

TARGET_COLUMNS = [
    "game_id", "play_id", "posteam", "play_type", "yards_gained",
    "touchdown", "passer_id", "receiver_id", "rusher_id", "epa",
    "complete_pass", "pass_touchdown", "rush_touchdown",
    "receiving_yards", "rushing_yards",
]

INT_COLUMNS = ["yards_gained", "receiving_yards", "rushing_yards"]
BOOL_COLUMNS = ["touchdown", "complete_pass", "pass_touchdown", "rush_touchdown"]
MERGE = """
INSERT INTO plays (game_id, play_id, posteam, play_type, yards_gained,
                   touchdown, passer_id, receiver_id, rusher_id, epa,
                   complete_pass, pass_touchdown, rush_touchdown,
                   receiving_yards, rushing_yards)
SELECT game_id, play_id, posteam, play_type, yards_gained,
       touchdown, passer_id, receiver_id, rusher_id, epa,
       complete_pass, pass_touchdown, rush_touchdown,
       receiving_yards, rushing_yards
FROM   plays_staging
ON CONFLICT (game_id, play_id) DO UPDATE SET
    posteam         = EXCLUDED.posteam,
    play_type       = EXCLUDED.play_type,
    yards_gained    = EXCLUDED.yards_gained,
    touchdown       = EXCLUDED.touchdown,
    passer_id       = EXCLUDED.passer_id,
    receiver_id     = EXCLUDED.receiver_id,
    rusher_id       = EXCLUDED.rusher_id,
    epa             = EXCLUDED.epa,
    complete_pass   = EXCLUDED.complete_pass,
    pass_touchdown  = EXCLUDED.pass_touchdown,
    rush_touchdown  = EXCLUDED.rush_touchdown,
    receiving_yards = EXCLUDED.receiving_yards,
    rushing_yards   = EXCLUDED.rushing_yards;
"""

def _prepare(df: pd.DataFrame, known_games: set[str]) -> list[tuple]:
    sub = df[SOURCE_COLUMNS].copy()
    sub = sub.dropna(subset=["game_id", "play_id"])
    sub = sub.drop_duplicates(subset=["game_id", "play_id"])

    before = len(sub)
    sub = sub[sub["game_id"].isin(known_games)]
    orphaned = before - len(sub)
    if orphaned:
        print(f"  skipped {orphaned} plays with no matching game")

    sub["play_id"] = sub["play_id"].astype("int64")
    for col in INT_COLUMNS:
        sub[col] = sub[col].astype("Int64")
    for col in BOOL_COLUMNS:
        sub[col] = sub[col].astype("boolean")
    sub["epa"] = sub["epa"].round(4)

    # Postgres wants None, pandas gives NaN and pd.NA.
    sub = sub.astype(object)
    sub = sub.where(pd.notna(sub), None)

    return list(sub.itertuples(index=False, name=None))

def load_plays(conn: psycopg.Connection, season: int) -> int:
    df = fetch_pbp(season)

    with conn.cursor() as cur:
        cur.execute("SELECT game_id FROM games WHERE season = %s", (season,))
        known_games = {r[0] for r in cur.fetchall()}

    rows = _prepare(df, known_games)

    with conn.cursor() as cur:
        cur.execute(
            "CREATE TEMP TABLE plays_staging "
            "(LIKE plays INCLUDING DEFAULTS) ON COMMIT DROP"
        )
        cols = ", ".join(TARGET_COLUMNS)
        with cur.copy(f"COPY plays_staging ({cols}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)
        cur.execute(MERGE)

    return len(rows)
