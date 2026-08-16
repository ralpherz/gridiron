"""Response models. These define the API's contract."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class Team(BaseModel):
    team_abbr: str
    team_name: str
    conference: str | None = None
    division: str | None = None


class Player(BaseModel):
    player_id: str
    full_name: str
    position: str | None = None
    team_abbr: str | None = None


class Game(BaseModel):
    game_id: str
    season: int
    week: int
    game_date: date | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: int | None = None
    away_score: int | None = None

class GameLine(BaseModel):
    """One player's line in one game."""
    game_id: str
    season: int
    week: int
    targets: int
    receptions: int
    rec_yards: int
    rec_tds: int
    rush_yards: int
    rush_tds: int


class SeasonTotal(BaseModel):
    player_id: str
    full_name: str
    position: str | None = None
    team_abbr: str | None = None
    games: int
    targets: int
    receptions: int
    rec_yards: int
    rec_tds: int
    rush_yards: int
    rush_tds: int


class Health(BaseModel):
    status: str
    database: str
    last_successful_run: str | None = None
