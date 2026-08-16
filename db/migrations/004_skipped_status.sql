-- 004_skipped_status.sql
-- Data that does not exist yet is not a failure. Play-by-play for an upcoming
-- season returns 404 until the first games are played; that should be recorded
-- as a skip, not an error.
BEGIN;

ALTER TABLE data_runs DROP CONSTRAINT data_runs_status_chk;

ALTER TABLE data_runs ADD CONSTRAINT data_runs_status_chk
    CHECK (status IN ('running','success','failed','skipped'));

COMMIT;
