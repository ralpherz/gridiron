-- 003_play_detail.sql
-- The initial plays table carried a play-level touchdown flag, which is true
-- for any score on the play including fumble returns. Receiving and rushing
-- stats need the specific flags and the specific yardage.
BEGIN;

ALTER TABLE plays
    ADD COLUMN complete_pass   BOOLEAN,
    ADD COLUMN pass_touchdown  BOOLEAN,
    ADD COLUMN rush_touchdown  BOOLEAN,
    ADD COLUMN receiving_yards INT,
    ADD COLUMN rushing_yards   INT;

COMMIT;
