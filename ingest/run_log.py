"""Records every ingestion attempt in data_runs."""
from __future__ import annotations

import contextlib
import traceback

import psycopg


@contextlib.contextmanager
def track(conn: psycopg.Connection, job_name: str, season=None, week=None):
    """Open a data_runs row, yield a counter, close the row on exit.

    On success the row is marked 'success' with the row count. On exception
    the row is marked 'failed' with the traceback, and the exception is
    re-raised so the container exits non-zero.
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO data_runs (job_name, season, week) "
            "VALUES (%s, %s, %s) RETURNING id",
            (job_name, season, week),
        )
        run_id = cur.fetchone()[0]
    conn.commit()
    counter = {"rows": 0}
    try:
        yield counter
    except Exception as exc:
        conn.rollback()
        detail = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"[:4000]
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE data_runs SET status='failed', finished_at=now(), "
                "error_message=%s WHERE id=%s",
                (detail, run_id),
            )
        conn.commit()
        raise
    else:
        conn.commit()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE data_runs SET status='success', finished_at=now(), "
                "rows_written=%s WHERE id=%s",
                (counter["rows"], run_id),
            )
        conn.commit()
