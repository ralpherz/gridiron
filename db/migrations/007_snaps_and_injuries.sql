-- 007_snaps_and_injuries.sql
-- Snap counts key on Pro Football Reference ids, not the gsis ids everything
-- else uses. The roster file carries both, so players.pfr_id (added in 005)
-- bridges them. Coverage is partial - roughly 80% of snap rows resolve to a
-- known player, the rest being linemen and practice-squad players without a
-- pfr_id on file.
BEGIN;

CREATE TABLE snap_counts (
    player_id      TEXT NOT NULL REFERENCES players(player_id),
    game_id        TEXT NOT NULL REFERENCES games(game_id),
    season         INT  NOT NULL,
    week           INT  NOT NULL,
    team           TEXT,
    opponent       TEXT,
    position       TEXT,
    offense_snaps  INT,
    offense_pct    NUMERIC(5,3),
    defense_snaps  INT,
    defense_pct    NUMERIC(5,3),
    st_snaps       INT,
    st_pct         NUMERIC(5,3),
    PRIMARY KEY (player_id, game_id)
);

CREATE INDEX idx_snaps_season_week ON snap_counts (season, week);
CREATE INDEX idx_snaps_game        ON snap_counts (game_id);
-- The injuries table was created in 001 and never populated. Widen it to
-- match what nflverse actually publishes.
ALTER TABLE injuries
    ADD COLUMN team                      TEXT,
    ADD COLUMN position                  TEXT,
    ADD COLUMN report_primary_injury     TEXT,
    ADD COLUMN report_secondary_injury   TEXT,
    ADD COLUMN practice_primary_injury   TEXT,
    ADD COLUMN practice_secondary_injury TEXT,
    ADD COLUMN loaded_at                 TIMESTAMPTZ NOT NULL DEFAULT now();

CREATE INDEX idx_injuries_season_week ON injuries (season, week);

COMMIT;
