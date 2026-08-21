"""Response models. These define the API's contract."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

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

class TeamDetail(BaseModel):
    team_abbr: str
    team_name: str
    conference: str | None = None
    division: str | None = None
    team_color: str | None = None
    logo_url: str | None = None
    season: int
    wins: int
    losses: int
    ties: int
    points_for: int
    points_against: int


class ScheduleGame(BaseModel):
    game_id: str
    season: int
    week: int
    game_date: date | None = None
    opponent: str | None = None
    is_home: bool
    points_for: int | None = None
    points_against: int | None = None


class RosterPlayer(BaseModel):
    player_id: str
    full_name: str
    position: str | None = None
    team_abbr: str | None = None
    headshot_url: str | None = None

class StatLine(BaseModel):
    """One player's full stat line for one game. Most fields are null for any
    given player - a quarterback has no punting numbers."""
    game_id: str
    season: int
    week: int
    season_type: str | None = None
    team: str | None = None
    opponent_team: str | None = None
    position: str | None = None
    completions: int | None = None
    attempts: int | None = None
    passing_yards: int | None = None
    passing_tds: int | None = None
    passing_interceptions: int | None = None
    sacks_suffered: int | None = None
    passing_epa: Decimal | None = None
    carries: int | None = None
    rushing_yards: int | None = None
    rushing_tds: int | None = None
    rushing_fumbles_lost: int | None = None
    rushing_epa: Decimal | None = None
    receptions: int | None = None
    targets: int | None = None
    receiving_yards: int | None = None
    receiving_tds: int | None = None
    receiving_air_yards: int | None = None
    target_share: Decimal | None = None
    receiving_epa: Decimal | None = None
    def_tackles_solo: int | None = None
    def_tackle_assists: int | None = None
    def_tackles_for_loss: int | None = None
    def_sacks: Decimal | None = None
    def_qb_hits: int | None = None
    def_interceptions: int | None = None
    def_pass_defended: int | None = None
    def_tds: int | None = None
    def_fumbles_forced: int | None = None
    fg_made: int | None = None
    fg_att: int | None = None
    fg_long: int | None = None
    pat_made: int | None = None
    pat_att: int | None = None
    pt_att: int | None = None
    pt_yards: int | None = None
    pt_net_yards: int | None = None
    pt_inside_20: int | None = None
    punt_returns: int | None = None
    punt_return_yards: int | None = None
    kickoff_returns: int | None = None
    kickoff_return_yards: int | None = None
    special_teams_tds: int | None = None
    fantasy_points: Decimal | None = None
    fantasy_points_ppr: Decimal | None = None


class SnapLine(BaseModel):
    game_id: str
    season: int
    week: int
    team: str | None = None
    opponent: str | None = None
    position: str | None = None
    offense_snaps: int | None = None
    offense_pct: Decimal | None = None
    defense_snaps: int | None = None
    defense_pct: Decimal | None = None
    st_snaps: int | None = None
    st_pct: Decimal | None = None


class InjuryLine(BaseModel):
    season: int
    week: int
    team: str | None = None
    position: str | None = None
    report_primary_injury: str | None = None
    report_secondary_injury: str | None = None
    report_status: str | None = None
    practice_primary_injury: str | None = None
    practice_secondary_injury: str | None = None
    practice_status: str | None = None

class BoxLine(BaseModel):
    """A trimmed stat line for box score display."""
    player_id: str
    full_name: str
    team: str | None = None
    position: str | None = None
    completions: int | None = None
    attempts: int | None = None
    passing_yards: int | None = None
    passing_tds: int | None = None
    passing_interceptions: int | None = None
    carries: int | None = None
    rushing_yards: int | None = None
    rushing_tds: int | None = None
    receptions: int | None = None
    targets: int | None = None
    receiving_yards: int | None = None
    receiving_tds: int | None = None
    def_tackles_solo: int | None = None
    def_sacks: Decimal | None = None
    def_interceptions: int | None = None
    fg_made: int | None = None
    fg_att: int | None = None
    fantasy_points_ppr: Decimal | None = None


class BoxScore(BaseModel):
    game_id: str
    season: int
    week: int
    game_date: date | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    players: list[BoxLine]
