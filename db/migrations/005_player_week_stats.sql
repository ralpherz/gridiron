-- 005_player_week_stats.sql
-- nflverse publishes per-player weekly stats already aggregated across every
-- category. Deriving tackles and kicking from raw play-by-play would mean
-- parsing a dozen scattered tackler columns and getting it subtly wrong.
-- We keep plays for analytical work and take counting stats from the source.
BEGIN;

CREATE TABLE player_week_stats (
    player_id       TEXT NOT NULL REFERENCES players(player_id),
    game_id         TEXT NOT NULL REFERENCES games(game_id),
    season          INT  NOT NULL,
    week            INT  NOT NULL,
    season_type     TEXT,
    team            TEXT,
    opponent_team   TEXT,
    position        TEXT,
    completions                 INT,
    attempts                    INT,
    passing_yards               INT,
    passing_tds                 INT,
    passing_interceptions       INT,
    sacks_suffered              INT,
    sack_yards_lost             INT,
    passing_air_yards           INT,
    passing_yards_after_catch   INT,
    passing_first_downs         INT,
    passing_epa                 NUMERIC(8,3),
    carries                     INT,
    rushing_yards               INT,
    rushing_tds                 INT,
    rushing_fumbles             INT,
    rushing_fumbles_lost        INT,
    rushing_first_downs         INT,
    rushing_epa                 NUMERIC(8,3),
    receptions                  INT,
    targets                     INT,
    receiving_yards             INT,
    receiving_tds               INT,
    receiving_fumbles           INT,
    receiving_air_yards         INT,
    receiving_yards_after_catch INT,
    receiving_first_downs       INT,
    receiving_epa               NUMERIC(8,3),
    target_share                NUMERIC(6,4),
    def_tackles_solo            INT,
    def_tackle_assists          INT,
    def_tackles_for_loss        INT,
    def_sacks                   NUMERIC(4,1),
    def_sack_yards              NUMERIC(6,1),
    def_qb_hits                 INT,
    def_interceptions           INT,
    def_interception_yards      INT,
    def_pass_defended           INT,
    def_tds                     INT,
    def_fumbles_forced          INT,
    def_safeties                INT,
    fg_made                     INT,
    fg_att                      INT,
    fg_long                     INT,
    fg_pct                      NUMERIC(5,3),
    pat_made                    INT,
    pat_att                     INT,
    gwfg_made                   INT,
    gwfg_att                    INT,
    pt_att                      INT,
    pt_yards                    INT,
    pt_net_yards                INT,
    pt_inside_20                INT,
    pt_long                     INT,
    punt_returns                INT,
    punt_return_yards           INT,
    kickoff_returns             INT,
    kickoff_return_yards        INT,
    special_teams_tds           INT,
    fantasy_points              NUMERIC(7,2),
    fantasy_points_ppr          NUMERIC(7,2),
    loaded_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (player_id, game_id)
);
CREATE INDEX idx_pws_season_week ON player_week_stats (season, week);
CREATE INDEX idx_pws_team        ON player_week_stats (team, season);
CREATE INDEX idx_pws_game        ON player_week_stats (game_id);

-- Player photo, and the Pro Football Reference id that snap counts key on.
ALTER TABLE players ADD COLUMN headshot_url TEXT;
ALTER TABLE players ADD COLUMN pfr_id TEXT;

-- Team branding for the frontend.
ALTER TABLE teams ADD COLUMN team_color  TEXT;
ALTER TABLE teams ADD COLUMN team_color2 TEXT;
ALTER TABLE teams ADD COLUMN logo_url    TEXT;

COMMIT;
