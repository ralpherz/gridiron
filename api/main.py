"""Gridiron read API."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

import queries as q
from config import DEFAULT_SEASON, MAX_PAGE_SIZE
from db import fetch_all, fetch_one, pool
from models import (BoxScore, Game, GameLine, Health, InjuryLine, Player, RosterPlayer, ScheduleGame, SeasonTotal, SnapLine, StatLine, Team, TeamDetail)

# Whitelisted so the sort parameter can never reach SQL as raw input.
SORTABLE = {
    "rec_yards": "rec_yards",
    "rec_tds": "rec_tds",
    "receptions": "receptions",
    "targets": "targets",
    "rush_yards": "rush_yards",
    "rush_tds": "rush_tds",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()


app = FastAPI(
    title="Gridiron API",
    description="Read access to NFL play-by-play, rosters, and derived stats.",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health", response_model=Health, tags=["meta"])
def health():
    try:
        fetch_one(q.HEALTH_DB)
    except Exception:
        raise HTTPException(status_code=503, detail="database unreachable")
    row = fetch_one(q.HEALTH_LAST_RUN)
    return Health(
        status="ok",
        database="ok",
        last_successful_run=row["last_run"] if row else None,
    )


@app.get("/teams", response_model=list[Team], tags=["reference"])
def list_teams():
    return fetch_all(q.TEAMS)

@app.get("/players", response_model=list[Player], tags=["players"])
def list_players(
    team: str | None = Query(None, min_length=2, max_length=3),
    position: str | None = Query(None, max_length=4),
    search: str | None = Query(None, min_length=2, max_length=50),
    limit: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
):
    return fetch_all(
        q.PLAYERS,
        {
            "team": team.upper() if team else None,
            "position": position.upper() if position else None,
            "search": search,
            "limit": limit,
            "offset": offset,
        },
    )


@app.get("/players/{player_id}", response_model=Player, tags=["players"])
def get_player(player_id: str):
    row = fetch_one(q.PLAYER_BY_ID, {"player_id": player_id})
    if row is None:
        raise HTTPException(status_code=404, detail="player not found")
    return row


@app.get("/players/{player_id}/games", response_model=list[GameLine], tags=["players"])
def player_game_log(player_id: str, season: int | None = Query(None, ge=1999)):
    if fetch_one(q.PLAYER_BY_ID, {"player_id": player_id}) is None:
        raise HTTPException(status_code=404, detail="player not found")
    return fetch_all(q.PLAYER_GAME_LOG, {"player_id": player_id, "season": season})

@app.get("/games", response_model=list[Game], tags=["games"])
def list_games(
    season: int = Query(DEFAULT_SEASON, ge=1999),
    week: int | None = Query(None, ge=1, le=22),
    limit: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
):
    return fetch_all(
        q.GAMES,
        {"season": season, "week": week, "limit": limit, "offset": offset},
    )


@app.get("/leaders", response_model=list[SeasonTotal], tags=["stats"])
def leaders(
    season: int = Query(DEFAULT_SEASON, ge=1999),
    sort: str = Query("rec_yards"),
    position: str | None = Query(None, max_length=4),
    limit: int = Query(25, ge=1, le=MAX_PAGE_SIZE),
):
    if sort not in SORTABLE:
        raise HTTPException(
            status_code=400,
            detail=f"sort must be one of: {', '.join(sorted(SORTABLE))}",
        )
    sql = q.LEADERS.format(sort_column=SORTABLE[sort])
    return fetch_all(
        sql,
        {
            "season": season,
            "position": position.upper() if position else None,
            "limit": limit,
        },
    )

@app.get("/teams/{team_abbr}", response_model=TeamDetail, tags=["teams"])
def team_detail(team_abbr: str, season: int = Query(DEFAULT_SEASON, ge=1999)):
    row = fetch_one(q.TEAM_DETAIL, {"team": team_abbr.upper(), "season": season})
    if row is None:
        raise HTTPException(status_code=404, detail="team not found")
    return row


@app.get("/teams/{team_abbr}/schedule", response_model=list[ScheduleGame], tags=["teams"])
def team_schedule(team_abbr: str, season: int = Query(DEFAULT_SEASON, ge=1999)):
    return fetch_all(q.TEAM_SCHEDULE, {"team": team_abbr.upper(), "season": season})


@app.get("/teams/{team_abbr}/roster", response_model=list[RosterPlayer], tags=["teams"])
def team_roster(team_abbr: str):
    return fetch_all(q.TEAM_ROSTER, {"team": team_abbr.upper()})

@app.get("/players/{player_id}/stats", response_model=list[StatLine], tags=["players"])
def player_stats(player_id: str, season: int | None = Query(None, ge=1999)):
    if fetch_one(q.PLAYER_BY_ID, {"player_id": player_id}) is None:
        raise HTTPException(status_code=404, detail="player not found")
    return fetch_all(q.PLAYER_STATS, {"player_id": player_id, "season": season})


@app.get("/players/{player_id}/snaps", response_model=list[SnapLine], tags=["players"])
def player_snaps(player_id: str, season: int | None = Query(None, ge=1999)):
    if fetch_one(q.PLAYER_BY_ID, {"player_id": player_id}) is None:
        raise HTTPException(status_code=404, detail="player not found")
    return fetch_all(q.PLAYER_SNAPS, {"player_id": player_id, "season": season})


@app.get("/players/{player_id}/injuries", response_model=list[InjuryLine], tags=["players"])
def player_injuries(player_id: str, season: int | None = Query(None, ge=1999)):
    if fetch_one(q.PLAYER_BY_ID, {"player_id": player_id}) is None:
        raise HTTPException(status_code=404, detail="player not found")
    return fetch_all(q.PLAYER_INJURIES, {"player_id": player_id, "season": season})

@app.get("/games/{game_id}", response_model=BoxScore, tags=["games"])
def game_box_score(game_id: str):
    game = fetch_one(q.GAME_DETAIL, {"game_id": game_id})
    if game is None:
        raise HTTPException(status_code=404, detail="game not found")
    game["players"] = fetch_all(q.GAME_BOX, {"game_id": game_id})
    return game
