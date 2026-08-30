-- 002_data_runs.sql
-- Every ingestion job records that it ran, how long it took, how many rows it
-- wrote, and what went wrong if it failed. A failed run leaves evidence
-- instead of disappearing silently. This is what the health dashboard reads.
BEGIN;
CREATE TABLE data_runs (
    id            BIGSERIAL PRIMARY KEY,
    job_name      TEXT        NOT NULL,
    season        INT,
    week          INT,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at   TIMESTAMPTZ,
    status        TEXT        NOT NULL DEFAULT 'running',
    rows_written  INT         DEFAULT 0,
    error_message TEXT,
    CONSTRAINT data_runs_status_chk CHECK (status IN ('running','success','failed'))
);
CREATE INDEX idx_data_runs_job_started ON data_runs (job_name, started_at DESC);

COMMIT;
