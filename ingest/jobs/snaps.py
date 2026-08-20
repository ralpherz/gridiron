"""Load snap counts.

The only job that crosses ID systems. Snap counts key on Pro Football
Reference ids; everything else here uses gsis ids. The roster file carries
both, so players.pfr_id is the bridge. Coverage is partial and the job
reports what it dropped rather than failing or silently discarding.
"""
from __future__ import annotations

import pandas as pd
import psycopg

from nflverse import fetch_snap_counts

COLUMNS = [
    "player_id", "game_id", "season", "week", "team", "opponent",
    "position", "offense_snaps", "offense_pct", "defense_snaps",
    "defense_pct", "st_snaps", "st_pct",
]

INT_COLUMNS = ["offense_snaps", "defense_snaps", "st_snaps"]
PCT_COLUMNS = ["offense_pct", "defense_pct", "st_pct"]

MERGE = """
INSERT INTO snap_counts (player_id, game_id, season, week, team, opponent,
                         position, offense_snaps, offense_pct, defense_snaps,
                         defense_pct, st_snaps, st_pct)
SELECT player_id, game_id, season, week, team, opponent,
       position, offense_snaps, offense_pct, defense_snaps,
       defense_pct, st_snaps, st_pct
FROM   snaps_staging
ON CONFLICT (player_id, game_id) DO UPDATE SET
    team          = EXCLUDED.team,
    opponent      = EXCLUDED.opponent,
    position      = EXCLUDED.position,
    offense_snaps = EXCLUDED.offense_snaps,
    offense_pct   = EXCLUDED.offense_pct,
    defense_snaps = EXCLUDED.defense_snaps,
    defense_pct   = EXCLUDED.defense_pct,
    st_snaps      = EXCLUDED.st_snaps,
    st_pct        = EXCLUDED.st_pct;
"""

def _prepare(df: pd.DataFrame, crosswalk: dict[str, str],
             known_games: set[str]) -> list[tuple]:
    sub = df.copy()
    sub["player_id"] = sub["pfr_player_id"].map(crosswalk)

    total = len(sub)
    sub = sub.dropna(subset=["player_id", "game_id"])
    unmatched = total - len(sub)

    before = len(sub)
    sub = sub[sub["game_id"].isin(known_games)]
    no_game = before - len(sub)

    sub = sub.drop_duplicates(subset=["player_id", "game_id"])
    sub = sub[COLUMNS]

    for col in INT_COLUMNS:
        sub[col] = sub[col].astype("Int64")
    for col in PCT_COLUMNS:
        sub[col] = sub[col].round(3)

    sub = sub.astype(object)
    sub = sub.where(pd.notna(sub), None)

    print(f"  {len(sub)} snap rows "
          f"(dropped {unmatched} with no pfr_id match, {no_game} with no game)")
    return list(sub.itertuples(index=False, name=None))

def load_snap_counts(conn: psycopg.Connection, season: int) -> int:
    df = fetch_snap_counts(season)

    with conn.cursor() as cur:
        cur.execute("SELECT pfr_id, player_id FROM players WHERE pfr_id IS NOT NULL")
        crosswalk = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute("SELECT game_id FROM games WHERE season = %s", (season,))
        known_games = {r[0] for r in cur.fetchall()}

    if not crosswalk:
        raise RuntimeError(
            "No pfr_id values on players - run the player_detail job first"
        )

    rows = _prepare(df, crosswalk, known_games)

    with conn.cursor() as cur:
        cur.execute(
            "CREATE TEMP TABLE snaps_staging "
            "(LIKE snap_counts INCLUDING DEFAULTS) ON COMMIT DROP"
        )
        cols = ", ".join(COLUMNS)
        with cur.copy(f"COPY snaps_staging ({cols}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)
        cur.execute(MERGE)

    return len(rows)
