"""
Guards against a bug that has now happened three times: a query constant
gets dropped from queries.py during an edit, main.py still references it,
and nothing notices until a user hits that endpoint in production and gets
a 500.

main.py is parsed rather than imported, because importing it would build a
database connection pool at module load.
"""
import ast
from pathlib import Path

import queries

ROOT = Path(__file__).resolve().parent.parent
API_MAIN = ROOT / "api" / "main.py"


def referenced_constants() -> set[str]:
    """Every `q.SOMETHING` referenced anywhere in api/main.py."""
    tree = ast.parse(API_MAIN.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "q"
        ):
            found.add(node.attr)
    return found


def test_main_references_at_least_one_query():
    """If this fails the parser is broken, not the code under test."""
    assert referenced_constants(), "no q.* references found in api/main.py"


def test_every_referenced_query_exists():
    missing = sorted(
        name for name in referenced_constants() if not hasattr(queries, name)
    )
    assert not missing, f"queries.py is missing: {', '.join(missing)}"


def test_no_query_is_empty():
    for name in dir(queries):
        if name.isupper():
            value = getattr(queries, name)
            assert isinstance(value, str), f"{name} is not a string"
            assert value.strip(), f"{name} is empty"
