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
