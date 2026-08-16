"""Configuration loaded from environment variables."""
import os

DB_HOST = os.environ.get("POSTGRES_HOST", "db")
DB_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
DB_NAME = os.environ.get("POSTGRES_DB", "gridiron")
DB_USER = os.environ.get("POSTGRES_USER", "gridiron")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "devpassword")

CONNINFO = (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)

DEFAULT_SEASON = int(os.environ.get("NFL_SEASON", "2025"))
MAX_PAGE_SIZE = 200
