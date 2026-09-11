"""Put the service directories on sys.path so tests can import them."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for service in ("api", "ingest"):
    path = str(ROOT / service)
    if path not in sys.path:
        sys.path.insert(0, path)
