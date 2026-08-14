"""CLI entry point for ingestion jobs.

    python main.py teams [season]
    python main.py rosters [season]
    python main.py all [season]
"""
from __future__ import annotations

import sys

from config import CURRENT_SEASON
from db import connect
from jobs.rosters import load_players
from jobs.teams import load_teams
from run_log import track


def run_teams(conn, season: int) -> None:
    print(f"job: teams (season {season})")
    with track(conn, "teams", season=season) as run:
        run["rows"] = load_teams(conn, season)
    print(f"  wrote {run['rows']} teams")


def run_rosters(conn, season: int) -> None:
    print(f"job: rosters (season {season})")
    with track(conn, "rosters", season=season) as run:
        run["rows"] = load_players(conn, season)
    print(f"  wrote {run['rows']} players")

def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    job = args[0]
    season = int(args[1]) if len(args) > 1 else CURRENT_SEASON

    with connect() as conn:
        if job == "teams":
            run_teams(conn, season)
        elif job == "rosters":
            run_rosters(conn, season)
        elif job == "all":
            run_teams(conn, season)
            run_rosters(conn, season)
        else:
            print(f"Unknown job: {job}")
            return 1

    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
