"""Configuration loaded from environment variables.

Local development uses the individual POSTGRES_* variables. Hosted
environments hand out a single connection URL, so that wins when present.
"""
import os

DB_HOST = os.environ.get("POSTGRES_HOST", "db")
DB_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
DB_NAME = os.environ.get("POSTGRES_DB", "gridiron")
DB_USER = os.environ.get("POSTGRES_USER", "gridiron")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "devpassword")

CONNINFO = os.environ.get("DATABASE_URL") or (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)

DEFAULT_SEASON = int(os.environ.get("NFL_SEASON", "2025"))
MAX_PAGE_SIZE = 200

# Origins allowed to call this API from a browser.
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]
