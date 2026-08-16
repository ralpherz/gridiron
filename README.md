# gridiron

A live NFL analytics platform. Scheduled ingestion of play-by-play, roster,
and injury data into Postgres, served through an API and web frontend, with
the pipeline monitoring itself.

Status: in development. Week 1 - database and ingestion.

## Why this exists

Most portfolio projects are built once and never run again. This one is meant
to be operated: data arrives on a schedule, jobs record whether they
succeeded, and the system reports its own health.

## Architecture (planned)

- Postgres - raw play-by-play kept separate from derived per-player stats
- Ingestion worker - scheduled jobs, idempotent upserts, run logging
- API - read endpoints over players, games, and computed stats
- Frontend - React/TypeScript, per-player views and watchlists
- Observability - Prometheus metrics scraped into Grafana

## Running locally

    docker compose up -d

Postgres listens on host port 5433 and applies db/migrations on first boot.

## Roadmap

- [x] Week 1 - schema, ingestion jobs, run logging
- [ ] Week 2 - API layer
- [ ] Week 3 - frontend
- [ ] Week 4 - auth and caching
- [ ] Week 5 - CI, metrics, health checks
- [ ] Week 6 - deploy

## Database

Seven tables. Raw source data is kept separate from derived values: plays is
what nflverse provided, keyed on (game_id, play_id) so re-ingesting updates
rather than duplicates. player_game_stats is computed from plays and can be
recomputed at any time without re-downloading anything.

data_runs records every ingestion attempt with status, row count, and a stack
trace on failure. A failed job leaves evidence instead of vanishing.

Migrations in db/migrations are applied by Postgres on first boot of an empty
volume. To reapply after schema changes: docker compose down -v && docker
compose up -d

## Ingestion

Jobs run as a separate container against the database:

    docker compose run --rm ingest all 2025

Teams must load before rosters - players carry a foreign key to teams, and a
player on an unrecognized team gets a null team rather than failing the run.

Data comes from nflverse release assets (CSV and parquet) fetched directly
over HTTPS. An earlier version used nfl_data_py, which pins pandas below 2.0
and therefore cannot install on Python 3.12.

Every job is wrapped in a run tracker that writes to data_runs. When the teams
job failed on a signature mismatch, the traceback was in the database rather
than lost in container output:

    SELECT id, job_name, status, rows_written, error_message FROM data_runs;

Re-running is safe. Every insert uses ON CONFLICT DO UPDATE against a natural
key, so a second run updates existing rows instead of duplicating them.

## Play-by-play

Around 49,000 rows per season. Two things make this job different from the
smaller ones.

Loading uses COPY into a temporary staging table followed by a single merge
statement, rather than row-by-row inserts. 48,771 rows load in about 2.3
seconds; the same volume through executemany would round-trip per row.

The source frame has 372 columns and we want 10. Narrowing the DataFrame
before converting to Python objects took the transform from roughly 18
seconds to under a second - the cost was in materializing 372 columns per
row, not in the row count.

Re-running is safe. The natural key (game_id, play_id) drives an ON CONFLICT
merge, so a second run updates rows in place. Verified: two consecutive runs,
48,771 rows both times.

## Derived stats

player_game_stats is recomputed from plays in a single SQL statement. Nothing
is aggregated in Python, and the job reads only from plays and writes only to
player_game_stats - so when the aggregation logic changes, it re-runs without
re-downloading anything. That is the reason raw and derived data live in
separate tables.

The recompute joins players before inserting. A player who appears in play
data but is not on any roster we have loaded would otherwise violate the
foreign key; joining drops them instead of failing the whole run.

### The imprecision, resolved

The first version derived receiving touchdowns from the play-level touchdown
column, which is true for any score on the play including fumble returns.
Migration 003 added complete_pass, pass_touchdown, rush_touchdown,
receiving_yards, and rushing_yards, and the plays job now ingests them.

The difference is small and real. Across the 2025 season the play-level flag
credited Puka Nacua with 13 receiving touchdowns and Ja Marr Chase with 9;
the correct figures are 12 and 8.

## Missing upstream data

Play-by-play for a season that has not started yet returns 404. That is a
normal condition every offseason, not a failure, so the fetch layer raises a
distinct exception and the run tracker records the attempt as skipped:

    job_name | season | status
    ---------+--------+---------
    plays    |   2026 | skipped

A skipped run exits zero. A genuine failure still records a traceback and
exits non-zero.
