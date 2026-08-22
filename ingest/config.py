"""Configuration loaded from environment variables.

Local development uses the individual POSTGRES_* variables. Hosted
environments hand out a single connection URL, so that wins when present.
"""
import os


def _env(key: str, default: str | None = None) -> str:
    val = os.environ.get(key, default)
    if val is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


DB_HOST = _env("POSTGRES_HOST", "db")
DB_PORT = int(_env("POSTGRES_PORT", "5432"))
DB_NAME = _env("POSTGRES_DB", "gridiron")
DB_USER = _env("POSTGRES_USER", "gridiron")
DB_PASSWORD = _env("POSTGRES_PASSWORD", "devpassword")

CONNINFO = os.environ.get("DATABASE_URL") or (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)

CURRENT_SEASON = int(_env("NFL_SEASON", "2025"))
