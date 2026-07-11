from __future__ import annotations
import sqlite3
from pathlib import Path
from backend.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_DB_PATH = Path("database/evidence_review.db")


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _apply_schema(conn)
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()