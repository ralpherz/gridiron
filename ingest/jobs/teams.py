"""Load the 32 NFL teams."""
from __future__ import annotations

import nfl_data_py as nfl
import psycopg

from db import UPSERT_TEAM, upsert_many


def _pick(row, *names):
    """Return the first present, non-null column from a row."""
    for n in names:
        if n in row and row[n] is not None:
            return row[n]
    return None

def load_teams(conn: psycopg.Connection) -> int:
    df = nfl.import_team_desc()

    rows = []
    seen = set()
    for _, r in df.iterrows():
        abbr = _pick(r, "team_abbr")
        if not abbr or abbr in seen:
            continue
        seen.add(abbr)
        rows.append(
            {
                "team_abbr": abbr,
                "team_name": _pick(r, "team_name", "team_nick") or abbr,
                "conference": _pick(r, "team_conf"),
                "division": _pick(r, "team_division"),
            }
        )

    return upsert_many(conn, UPSERT_TEAM, rows)
