"""Load the 32 NFL teams.

Conference and division are hardcoded: nflverse does not publish them in
teams.csv, and realignment happens roughly once a decade.
"""
from __future__ import annotations

import psycopg

from db import UPSERT_TEAM, upsert_many
from nflverse import fetch_teams

ALIGNMENT = {
    "BUF": ("AFC", "East"),  "MIA": ("AFC", "East"),  "NE": ("AFC", "East"),
    "NYJ": ("AFC", "East"),  "BAL": ("AFC", "North"), "CIN": ("AFC", "North"),
    "CLE": ("AFC", "North"), "PIT": ("AFC", "North"), "HOU": ("AFC", "South"),
    "IND": ("AFC", "South"), "JAX": ("AFC", "South"), "TEN": ("AFC", "South"),
    "DEN": ("AFC", "West"),  "KC": ("AFC", "West"),   "LV": ("AFC", "West"),
    "LAC": ("AFC", "West"),  "DAL": ("NFC", "East"),  "NYG": ("NFC", "East"),
    "PHI": ("NFC", "East"),  "WAS": ("NFC", "East"),  "CHI": ("NFC", "North"),
    "DET": ("NFC", "North"), "GB": ("NFC", "North"),  "MIN": ("NFC", "North"),
    "ATL": ("NFC", "South"), "CAR": ("NFC", "South"), "NO": ("NFC", "South"),
    "TB": ("NFC", "South"),  "ARI": ("NFC", "West"),  "LA": ("NFC", "West"),
    "SF": ("NFC", "West"),   "SEA": ("NFC", "West"),
}

def load_teams(conn: psycopg.Connection, season: int) -> int:
    df = fetch_teams(season)

    rows = []
    for abbr, name in zip(df["team"], df["full"]):
        conf, div = ALIGNMENT.get(abbr, (None, None))
        rows.append(
            {
                "team_abbr": abbr,
                "team_name": name,
                "conference": conf,
                "division": div,
            }
        )

    return upsert_many(conn, UPSERT_TEAM, rows)
