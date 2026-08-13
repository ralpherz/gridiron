-- 001_initial.sql
-- Core domain tables. Raw source data (plays) is kept separate from derived
-- values (player_game_stats) so aggregation bugs can be fixed by recomputing
-- rather than re-downloading.
BEGIN;

CREATE TABLE teams (
    team_abbr   TEXT PRIMARY KEY,
    team_name   TEXT NOT NULL,
    conference  TEXT,
    division    TEXT
);
CREATE TABLE players (
    player_id   TEXT PRIMARY KEY,
    full_name   TEXT NOT NULL,
    position    TEXT,
    team_abbr   TEXT REFERENCES teams(team_abbr),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_players_team ON players (team_abbr);

CREATE TABLE games (
    game_id     TEXT PRIMARY KEY,
    season      INT  NOT NULL,
    week        INT  NOT NULL,
    game_date   DATE,
    home_team   TEXT REFERENCES teams(team_abbr),
    away_team   TEXT REFERENCES teams(team_abbr),
    home_score  INT,
    away_score  INT
);
CREATE INDEX idx_games_season_week ON games (season, week);
-- One row per play. Natural key (game_id, play_id) makes ingestion idempotent.
CREATE TABLE plays (
    game_id      TEXT NOT NULL REFERENCES games(game_id),
    play_id      INT  NOT NULL,
    posteam      TEXT,
    play_type    TEXT,
    yards_gained INT,
    touchdown    BOOLEAN,
    passer_id    TEXT,
    receiver_id  TEXT,
    rusher_id    TEXT,
    epa          NUMERIC(8,4),
    PRIMARY KEY (game_id, play_id)
);
CREATE INDEX idx_plays_receiver ON plays (receiver_id) WHERE receiver_id IS NOT NULL;
CREATE INDEX idx_plays_rusher   ON plays (rusher_id)   WHERE rusher_id   IS NOT NULL;
-- Derived from plays. season/week denormalized so season-long aggregates
-- do not need to join through games.
CREATE TABLE player_game_stats (
    player_id   TEXT NOT NULL REFERENCES players(player_id),
    game_id     TEXT NOT NULL REFERENCES games(game_id),
    season      INT  NOT NULL,
    week        INT  NOT NULL,
    targets     INT DEFAULT 0,
    receptions  INT DEFAULT 0,
    rec_yards   INT DEFAULT 0,
    rec_tds     INT DEFAULT 0,
    rush_yards  INT DEFAULT 0,
    rush_tds    INT DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (player_id, game_id)
);
CREATE INDEX idx_pgs_season ON player_game_stats (season, week);

CREATE TABLE injuries (
    player_id       TEXT NOT NULL REFERENCES players(player_id),
    season          INT  NOT NULL,
    week            INT  NOT NULL,
    report_status   TEXT,
    practice_status TEXT,
    PRIMARY KEY (player_id, season, week)
);

COMMIT;
