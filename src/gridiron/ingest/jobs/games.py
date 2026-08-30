"""Load the season schedule and results."""
from __future__ import annotations

import pandas as pd
import psycopg

from db import UPSERT_GAME, upsert_many
from nflverse import fetch_games


def _text(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _int(value):
    if value is None or pd.isna(value):
        return None
    return int(value)

def load_games(conn: psycopg.Connection, season: int) -> int:
    df = fetch_games(season)

    with conn.cursor() as cur:
        cur.execute("SELECT team_abbr FROM teams")
        known = {r[0] for r in cur.fetchall()}

    rows, skipped = [], 0
    for rec in df.to_dict("records"):
        home, away = _text(rec.get("home_team")), _text(rec.get("away_team"))
        if home not in known or away not in known:
            skipped += 1
            continue
        rows.append(
            {
                "game_id": _text(rec.get("game_id")),
                "season": _int(rec.get("season")),
                "week": _int(rec.get("week")),
                "game_date": _text(rec.get("gameday")),
                "home_team": home,
                "away_team": away,
                "home_score": _int(rec.get("home_score")),
                "away_score": _int(rec.get("away_score")),
            }
        )

    if skipped:
        print(f"  skipped {skipped} games with unrecognized teams")
    return upsert_many(conn, UPSERT_GAME, rows)
