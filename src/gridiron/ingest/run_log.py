"""Records every ingestion attempt in data_runs."""
from __future__ import annotations

import contextlib
import traceback

import psycopg

from nflverse import DataNotAvailable


@contextlib.contextmanager
def track(conn: psycopg.Connection, job_name: str, season=None, week=None):
    """Open a data_runs row, yield a counter, close the row on exit.

    Success marks the row 'success' with a row count. A missing upstream file
    marks it 'skipped'. Anything else marks it 'failed' with the traceback and
    re-raises so the container exits non-zero.
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
    except DataNotAvailable as exc:
        conn.rollback()
        print(f"  no data published yet: {exc}")
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE data_runs SET status='skipped', finished_at=now(), "
                "error_message=%s WHERE id=%s",
                (f"Source not published yet: {exc}", run_id),
            )
        conn.commit()
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
