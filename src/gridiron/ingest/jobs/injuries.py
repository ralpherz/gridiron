"""Load the weekly injury report."""
from __future__ import annotations

import pandas as pd
import psycopg

from gridiron.ingest.nflverse import fetch_injuries

COLUMNS = [
    "player_id", "season", "week", "team", "position",
    "report_primary_injury", "report_secondary_injury", "report_status",
    "practice_primary_injury", "practice_secondary_injury", "practice_status",
]

MERGE = """
INSERT INTO injuries (player_id, season, week, team, position,
                      report_primary_injury, report_secondary_injury,
                      report_status, practice_primary_injury,
                      practice_secondary_injury, practice_status)
SELECT player_id, season, week, team, position,
       report_primary_injury, report_secondary_injury,
       report_status, practice_primary_injury,
       practice_secondary_injury, practice_status
FROM   injuries_staging
ON CONFLICT (player_id, season, week) DO UPDATE SET
    team                      = EXCLUDED.team,
    position                  = EXCLUDED.position,
    report_primary_injury     = EXCLUDED.report_primary_injury,
    report_secondary_injury   = EXCLUDED.report_secondary_injury,
    report_status             = EXCLUDED.report_status,
    practice_primary_injury   = EXCLUDED.practice_primary_injury,
    practice_secondary_injury = EXCLUDED.practice_secondary_injury,
    practice_status           = EXCLUDED.practice_status,
    loaded_at                 = now();
"""

def load_injuries(conn: psycopg.Connection, season: int) -> int:
    df = fetch_injuries(season)
    sub = df.rename(columns={"gsis_id": "player_id"})

    with conn.cursor() as cur:
        cur.execute("SELECT player_id FROM players")
        known = {r[0] for r in cur.fetchall()}

    total = len(sub)
    sub = sub.dropna(subset=["player_id", "season", "week"])
    sub = sub[sub["player_id"].isin(known)]
    dropped = total - len(sub)
    if dropped:
        print(f"  skipped {dropped} rows with no matching player")

    sub = sub.drop_duplicates(subset=["player_id", "season", "week"])
    sub = sub[COLUMNS].astype(object)
    sub = sub.where(pd.notna(sub), None)
    rows = list(sub.itertuples(index=False, name=None))

    with conn.cursor() as cur:
        cur.execute(
            "CREATE TEMP TABLE injuries_staging "
            "(LIKE injuries INCLUDING DEFAULTS) ON COMMIT DROP"
        )
        cols = ", ".join(COLUMNS)
        with cur.copy(f"COPY injuries_staging ({cols}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)
        cur.execute(MERGE)

    return len(rows)
