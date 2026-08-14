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

- [ ] Week 1 - schema, ingestion jobs, run logging
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
