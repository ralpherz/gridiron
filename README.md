# gridiron

A live NFL analytics platform. Scheduled ingestion of play-by-play, rosters,
and per-player statistics into Postgres, served through a REST API, with the
pipeline recording its own health.

Status: in development. Database, ingestion, and API are working; frontend
is next.

## Why this exists

Most portfolio projects are built once and never run again. This one is meant
to be operated: data arrives on a schedule, jobs record whether they
succeeded, and the system reports when it last updated.

## Architecture

- Postgres - raw play-by-play kept separate from per-player aggregates
- Ingestion worker - seven jobs, idempotent upserts, run logging
- API - FastAPI read layer over players, teams, games, and stats
- Frontend - planned: team browser, player pages, search
- Observability - planned: Prometheus metrics scraped into Grafana

## Running locally

    docker compose up -d
    docker compose run --rm ingest all 2025

Postgres listens on host port 5433 and applies db/migrations on first boot of
an empty volume. The API comes up on port 8000 with interactive docs at /docs.

## Roadmap

- [x] Week 1 - schema, ingestion jobs, run logging
- [x] Week 2 - API layer
- [ ] Week 3 - frontend
- [ ] Week 4 - auth and caching
- [ ] Week 5 - CI, metrics, health checks
- [ ] Week 6 - deploy

## Database

Six tables.

**teams** - 32 rows with conference, division, brand colors, and logo URL.

**players** - roster identity, plus a headshot URL and the Pro Football
Reference id that snap counts key on.

**games** - schedule and results. Loaded for a future season before any game
is played, so scores fill in as they happen.

**plays** - one row per play, keyed on (game_id, play_id). Roughly 49,000 rows
per season. This is source data, not derived from anything.

**player_week_stats** - one row per player per game, 60 stat columns covering
passing, rushing, receiving, defense, kicking, punting, and returns.

**data_runs** - every ingestion attempt with status, row count, duration, and
a stack trace on failure. A failed job leaves evidence instead of vanishing.

## Ingestion

Jobs run as a separate container against the database:

    docker compose run --rm ingest all 2025

Order matters and is enforced by the job registry: teams before rosters
(players carry a foreign key to teams), games before plays and stats. A
player on an unrecognized team gets a null team rather than failing the run.

Data comes from nflverse release assets - CSV and parquet - fetched directly
over HTTPS. An earlier version used nfl_data_py, which pins pandas below 2.0
and therefore cannot install on Python 3.12.

Re-running is safe. Every insert uses ON CONFLICT DO UPDATE against a natural
key, so a second run updates existing rows instead of duplicating them.

### Run tracking

Every job is wrapped in a tracker that writes to data_runs. When the teams job
once failed on a function signature mismatch, the traceback was in the
database rather than lost in container output:

    SELECT id, job_name, status, rows_written, error_message FROM data_runs;

### Missing upstream data is not a failure

Play-by-play for a season that has not started yet returns 404. That is a
normal offseason condition, so the fetch layer raises a distinct exception and
the tracker records the attempt as skipped:

    job_name | season | status
    ---------+--------+---------
    plays    |   2026 | skipped

A skipped run exits zero. A genuine failure still records a traceback and
exits non-zero.

## Play-by-play

Around 49,000 rows per season. Two things make this job different from the
smaller ones.

Loading uses COPY into a temporary staging table followed by a single merge
statement rather than row-by-row inserts. 48,771 rows load in about 2.3
seconds; the same volume through executemany would round-trip per row.

The source frame has 372 columns and we want 15. Narrowing the DataFrame
before converting to Python objects took the transform from roughly 18 seconds
to under a second - the cost was materializing 372 columns per row, not the
row count itself.

Verified idempotent: two consecutive runs, 48,771 rows both times.

## Player statistics

player_week_stats is loaded from nflverse's own weekly aggregation rather than
derived from plays. That was a deliberate reversal.

The first version computed six columns from play-by-play: targets, receptions,
receiving yards and touchdowns, rushing yards and touchdowns. It worked, and
it covered receivers and running backs. It could not cover anyone else without
substantially more work - tackles are spread across a dozen scattered columns
(solo_tackle_1_player_id, assist_tackle_2_player_id, and so on), and getting
that subtly wrong is easy.

nflverse publishes 150 columns per player per week, already correct. Taking 60
of them gives quarterbacks, defenders, kickers, and punters real numbers
instead of blank rows. Migration 006 dropped the derived table.

plays stays, because it answers questions the aggregates cannot: expected
points added, situational splits, anything computed per snap.

### An earlier accuracy fix, kept for the record

While the derived table still existed, receiving touchdowns came from the
play-level touchdown column, which is true for any score on the play including
fumble returns. Migration 003 added the specific flags. Across 2025 the
play-level column credited Puka Nacua with 13 receiving touchdowns and
Ja'Marr Chase with 9; the correct figures are 12 and 8.

## API

A FastAPI service reading from the same database, running as a third compose
service on port 8000. Interactive docs at /docs are generated from the type
hints - no separate spec to maintain.

    GET /health
    GET /teams
    GET /players?search=nacua&team=LA&position=WR
    GET /players/{player_id}
    GET /players/{player_id}/games?season=2025
    GET /games?season=2026&week=1
    GET /leaders?season=2025&sort=rec_yards&position=WR

Endpoints read pre-aggregated rows rather than scanning plays per request. A
season leaders query touches a few thousand rows instead of 48,771.

The connection pool opens at startup and closes at shutdown. Ingestion jobs
open one connection and exit; an API serves concurrent requests and cannot
reconnect per request.

/health checks the database and reports the timestamp of the last successful
ingestion run, so a stale pipeline is visible without opening psql.

## Notes

**Sort whitelisting.** The sort parameter on /leaders maps through a
dictionary before reaching SQL. A user-supplied column name never becomes part
of a query string.

**Typed null parameters.** Optional filters written as
`%(param)s IS NULL OR col = %(param)s` fail with "could not determine data
type of parameter" when the value is NULL - Postgres has nothing to infer from.
Explicit ::text and ::int casts resolve it.

**Rebuilding from scratch.** Migrations only run on an empty volume:

    docker compose down -v && docker compose up -d
