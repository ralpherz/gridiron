"""Load players from the season roster."""
from __future__ import annotations

import pandas as pd
import psycopg

from gridiron.ingest.db import UPSERT_PLAYER, upsert_many
from gridiron.ingest.nflverse import fetch_roster


def _clean(value):
    """nflverse uses both NaN and empty string for missing values."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None

def load_players(conn: psycopg.Connection, season: int) -> int:
    df = fetch_roster(season)

    # A player whose team is not in our teams table would violate the FK.
    with conn.cursor() as cur:
        cur.execute("SELECT team_abbr FROM teams")
        known_teams = {r[0] for r in cur.fetchall()}

    rows, seen = [], set()
    no_id = unknown_team = 0
    for rec in df.to_dict("records"):
        pid = _clean(rec.get("gsis_id"))
        if pid is None:
            no_id += 1
            continue
        if pid in seen:
            continue

        team = _clean(rec.get("team"))
        if team not in known_teams:
            unknown_team += 1
            team = None

        seen.add(pid)
        rows.append(
            {
                "player_id": pid,
                "full_name": _clean(rec.get("full_name")) or "Unknown",
                "position": _clean(rec.get("position")),
                "team_abbr": team,
            }
        )

    print(f"  {len(rows)} players (skipped {no_id} without an id, "
          f"{unknown_team} on unrecognized teams)")
    return upsert_many(conn, UPSERT_PLAYER, rows)

def load_player_detail(conn, season: int) -> int:
    """Backfill headshot and Pro Football Reference id from the roster file."""
    from db import UPSERT_PLAYER_DETAIL, upsert_many

    df = fetch_roster(season)
    rows = []
    seen = set()
    for rec in df.to_dict("records"):
        pid = _clean(rec.get("gsis_id"))
        if pid is None or pid in seen:
            continue
        seen.add(pid)
        rows.append({
            "player_id": pid,
            "headshot_url": _clean(rec.get("headshot_url")),
            "pfr_id": _clean(rec.get("pfr_id")),
        })
    return upsert_many(conn, UPSERT_PLAYER_DETAIL, rows)
