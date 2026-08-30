"""Load pre-aggregated weekly player stats.

nflverse publishes 150 columns per player per week covering passing, rushing,
receiving, defense, kicking, punting, and returns. We keep 60 of them.

Deriving these from play-by-play would mean parsing scattered tackler columns
(solo_tackle_1_player_id, assist_tackle_2_player_id, and so on) and would get
subtly wrong answers. plays stays for analytical work; counting stats come
from the source that already computed them.
"""
from __future__ import annotations

import pandas as pd
import psycopg

from gridiron.ingest.nflverse import fetch_player_week_stats

KEY_COLUMNS = [
    "player_id", "game_id", "season", "week", "season_type",
    "team", "opponent_team", "position",
]

INT_COLUMNS = [
    "completions", "attempts", "passing_yards", "passing_tds",
    "passing_interceptions", "sacks_suffered", "sack_yards_lost",
    "passing_air_yards", "passing_yards_after_catch", "passing_first_downs",
    "carries", "rushing_yards", "rushing_tds", "rushing_fumbles",
    "rushing_fumbles_lost", "rushing_first_downs",
    "receptions", "targets", "receiving_yards", "receiving_tds",
    "receiving_fumbles", "receiving_air_yards", "receiving_yards_after_catch",
    "receiving_first_downs",
    "def_tackles_solo", "def_tackle_assists", "def_tackles_for_loss",
    "def_qb_hits", "def_interceptions", "def_interception_yards",
    "def_pass_defended", "def_tds", "def_fumbles_forced", "def_safeties",
    "fg_made", "fg_att", "fg_long", "pat_made", "pat_att",
    "gwfg_made", "gwfg_att",
    "pt_att", "pt_yards", "pt_net_yards", "pt_inside_20", "pt_long",
    "punt_returns", "punt_return_yards", "kickoff_returns",
    "kickoff_return_yards", "special_teams_tds",
]

NUMERIC_COLUMNS = [
    "passing_epa", "rushing_epa", "receiving_epa", "target_share",
    "def_sacks", "def_sack_yards", "fg_pct",
    "fantasy_points", "fantasy_points_ppr",
]

ALL_COLUMNS = KEY_COLUMNS + INT_COLUMNS + NUMERIC_COLUMNS

def _merge_sql() -> str:
    cols = ", ".join(ALL_COLUMNS)
    updates = ",\n    ".join(
        f"{c} = EXCLUDED.{c}"
        for c in ALL_COLUMNS
        if c not in ("player_id", "game_id")
    )
    return f"""
INSERT INTO player_week_stats ({cols})
SELECT {cols}
FROM   pws_staging
ON CONFLICT (player_id, game_id) DO UPDATE SET
    {updates},
    loaded_at = now();
"""

def _prepare(df: pd.DataFrame, known_players: set[str],
             known_games: set[str]) -> list[tuple]:
    sub = df[ALL_COLUMNS].copy()
    sub = sub.dropna(subset=["player_id", "game_id"])
    sub = sub.drop_duplicates(subset=["player_id", "game_id"])

    before = len(sub)
    sub = sub[sub["player_id"].isin(known_players)]
    sub = sub[sub["game_id"].isin(known_games)]
    dropped = before - len(sub)
    if dropped:
        print(f"  skipped {dropped} rows with no matching player or game")

    for col in INT_COLUMNS:
        sub[col] = sub[col].astype("Int64")
    for col in NUMERIC_COLUMNS:
        sub[col] = sub[col].round(4)

    sub = sub.astype(object)
    sub = sub.where(pd.notna(sub), None)

    return list(sub.itertuples(index=False, name=None))

def load_player_stats(conn: psycopg.Connection, season: int) -> int:
    df = fetch_player_week_stats(season)

    with conn.cursor() as cur:
        cur.execute("SELECT player_id FROM players")
        known_players = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT game_id FROM games WHERE season = %s", (season,))
        known_games = {r[0] for r in cur.fetchall()}

    rows = _prepare(df, known_players, known_games)

    with conn.cursor() as cur:
        cur.execute(
            "CREATE TEMP TABLE pws_staging "
            "(LIKE player_week_stats INCLUDING DEFAULTS) ON COMMIT DROP"
        )
        cols = ", ".join(ALL_COLUMNS)
        with cur.copy(f"COPY pws_staging ({cols}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)
        cur.execute(_merge_sql())

    return len(rows)
