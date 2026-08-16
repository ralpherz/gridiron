"""Connection pool. Opened at startup, closed at shutdown.

The ingestion jobs open a single connection and exit. An API serves
concurrent requests, so it holds a pool rather than reconnecting per request.
"""
from __future__ import annotations

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from config import CONNINFO

pool = ConnectionPool(CONNINFO, min_size=1, max_size=10, open=False)


def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
    with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, params or {})
        return cur.fetchall()


def fetch_one(sql: str, params: dict | None = None) -> dict | None:
    with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, params or {})
        return cur.fetchone()
