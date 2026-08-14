"""Load players from seasonal rosters."""
from __future__ import annotations

import nfl_data_py as nfl
import psycopg

from db import UPSERT_PLAYER, upsert_many


def _pick(row, *names):
    for n in names:
        if n in row and row[n] is not None:
            return row[n]
    return None


def _fetch_rosters(season: int):
    """nfl_data_py has renamed this across versions; try the known names."""
    for fn_name in ("import_seasonal_rosters", "import_rosters", "import_weekly_rosters"):
        fn = getattr(nfl, fn_name, None)
        if fn is None:
            continue
        try:
            return fn([season])
        except Exception:
            continue
    raise RuntimeError("Could not fetch rosters: no compatible function found")

def load_players(conn: psycopg.Connection, season: int) -> int:
    df = _fetch_rosters(season)

    # Only insert players whose team exists, or the FK will reject them.
    with conn.cursor() as cur:
        cur.execute("SELECT team_abbr FROM teams")
        known_teams = {r[0] for r in cur.fetchall()}

    rows = []
    seen = set()
    skipped_no_id = 0
    skipped_team = 0
    for _, r in df.iterrows():
        pid = _pick(r, "player_id", "gsis_id")
        if not pid or pid in seen:
            if not pid:
                skipped_no_id += 1
            continue

        team = _pick(r, "team", "recent_team", "team_abbr")
        if team not in known_teams:
            skipped_team += 1
            team = None

        seen.add(pid)
        rows.append(
            {
                "player_id": str(pid),
                "full_name": _pick(r, "player_name", "full_name", "display_name") or "Unknown",
                "position": _pick(r, "position", "depth_chart_position"),
                "team_abbr": team,
            }
        )

    print(f"  parsed {len(rows)} players (skipped {skipped_no_id} no id, {skipped_team} unknown team)")
    return upsert_many(conn, UPSERT_PLAYER, rows)
