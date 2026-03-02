"""
Bulk-loads validated DataFrames into flowsight.db.
Uses pandas .to_sql() with a raw sqlite3 connection (DBAPI2),
which is reliably supported across pandas 2.x without SQLAlchemy version concerns.
"""
import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd

from config.settings import DB_PATH

# Insertion order must respect FK dependencies
TABLE_ORDER = [
    "Products",
    "Suppliers",
    "Inventory",
    "Orders",
    "OrderItems",
    "Sales",
    "Shipments",
]


def clear_tables(db_path: Path = DB_PATH) -> None:
    """Truncate all core tables in reverse FK order before re-loading."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in reversed(TABLE_ORDER):
        conn.execute(f"DELETE FROM {table}")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()


def load_all(dataframes: Dict[str, pd.DataFrame], db_path: Path = DB_PATH) -> None:
    """Insert all DataFrames into SQLite in FK-safe order."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")

    for table in TABLE_ORDER:
        df = dataframes.get(table)
        if df is None:
            raise KeyError(f"Missing DataFrame for table '{table}'")
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"[db_loader] Loaded {len(df):,} rows -> {table}")

    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    print("[db_loader] All tables loaded successfully.")


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    tables = [
        r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    ]
    conn.close()
    print(f"[db_loader] Tables in DB: {tables}")
