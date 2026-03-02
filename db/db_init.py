"""
Creates flowsight.db and applies schema.sql + views.sql.
Safe to re-run: uses CREATE TABLE IF NOT EXISTS and DROP VIEW IF EXISTS.
"""
import sqlite3
from pathlib import Path

from config.settings import DB_PATH

_DB_DIR = Path(__file__).parent
_SCHEMA_FILE = _DB_DIR / "schema.sql"
_VIEWS_FILE = _DB_DIR / "views.sql"


def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    schema_sql = _SCHEMA_FILE.read_text(encoding="utf-8")
    views_sql = _VIEWS_FILE.read_text(encoding="utf-8")

    conn.executescript(schema_sql)
    conn.executescript(views_sql)
    conn.commit()
    conn.close()
    print(f"[db_init] Database ready: {db_path}")


if __name__ == "__main__":
    init_db()
