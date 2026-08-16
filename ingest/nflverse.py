"""Fetches data straight from nflverse public releases.

We read the published CSV/parquet assets directly rather than going through a
wrapper library. Fewer dependencies, no version pinning conflicts, and the
release URLs are stable.
"""
from __future__ import annotations

import io

import pandas as pd
import requests

NFLDATA = "https://raw.githubusercontent.com/nflverse/nfldata/master/data"
RELEASES = "https://github.com/nflverse/nflverse-data/releases/download"

TIMEOUT = 60


class DataNotAvailable(Exception):
    """The source file does not exist yet. Not an error - just too early."""


def _get(url: str) -> bytes:
    resp = requests.get(url, timeout=TIMEOUT)
    if resp.status_code == 404:
        raise DataNotAvailable(url)
    resp.raise_for_status()
    return resp.content

def fetch_teams(season: int) -> pd.DataFrame:
    """Team abbreviations and names for a given season."""
    df = pd.read_csv(io.BytesIO(_get(f"{NFLDATA}/teams.csv")))
    return df[df["season"] == season].copy()


def fetch_roster(season: int) -> pd.DataFrame:
    """Season roster: one row per player per team."""
    url = f"{RELEASES}/rosters/roster_{season}.parquet"
    return pd.read_parquet(io.BytesIO(_get(url)))


def fetch_games(season: int) -> pd.DataFrame:
    """Schedule and results."""
    df = pd.read_csv(io.BytesIO(_get(f"{NFLDATA}/games.csv")))
    return df[df["season"] == season].copy()


def fetch_pbp(season: int) -> pd.DataFrame:
    """Play-by-play for a season. Roughly 20MB and 50,000 rows."""
    url = f"{RELEASES}/pbp/play_by_play_{season}.parquet"
    return pd.read_parquet(io.BytesIO(_get(url)))
