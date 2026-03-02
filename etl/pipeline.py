"""
Phase 1 ETL Pipeline — top-level orchestrator.
Run this file directly to go from an empty directory to a fully populated DB:

    python -m etl.pipeline
    # or from project root:
    python etl/pipeline.py
"""
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path when run as a script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config.settings import DB_PATH
from data.generate_data import generate_all
from db.db_init import init_db
from db.db_loader import clear_tables, load_all
from etl.transformers import transform_all
from etl.validators import validate_all


def run_pipeline(seed=None) -> None:
    t0 = time.time()
    kwargs = {"seed": seed} if seed is not None else {}

    print("=" * 60)
    print("FlowSight ETL Pipeline — Phase 1")
    print("=" * 60)

    # Step 1: Initialise database (idempotent)
    print("\n[1/5] Initialising database...")
    init_db(DB_PATH)

    # Step 2: Generate synthetic data
    print("\n[2/5] Generating synthetic data...")
    dataframes = generate_all(**kwargs)

    # Step 3: Transform (add derived columns)
    print("\n[3/5] Applying transformations...")
    dataframes = transform_all(dataframes)

    # Step 4: Validate
    print("\n[4/5] Validating data...")
    validate_all(dataframes)

    # Step 5: Load into DB
    print("\n[5/5] Loading into SQLite...")
    clear_tables(DB_PATH)
    load_all(dataframes, DB_PATH)

    elapsed = time.time() - t0
    print(f"\n[pipeline] Done in {elapsed:.1f}s. DB: {DB_PATH}")
    print("=" * 60)


def verify_phase1() -> None:
    """Quick Phase 1 gate check — run after pipeline."""
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = {
        r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    required_tables = {
        "Products", "Suppliers", "Inventory", "Orders",
        "OrderItems", "Sales", "Shipments",
    }
    missing = required_tables - tables
    assert not missing, f"Missing tables: {missing}"

    checks = {
        "Products":  ("SELECT COUNT(*) FROM Products",  lambda n: n == 50),
        "Suppliers": ("SELECT COUNT(*) FROM Suppliers", lambda n: n == 15),
        "Sales":     ("SELECT COUNT(*) FROM Sales",     lambda n: n > 20_000),
        "No null DelayDays": (
            "SELECT COUNT(*) FROM Shipments WHERE DelayDays IS NULL",
            lambda n: n == 0,
        ),
    }
    for label, (sql, predicate) in checks.items():
        n = cur.execute(sql).fetchone()[0]
        assert predicate(n), f"Failed check '{label}': got {n}"
        print(f"  [ok] {label}: {n}")

    views = [
        r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='view'"
        ).fetchall()
    ]
    assert len(views) == 8, f"Expected 8 views, found {len(views)}: {views}"
    print(f"  [ok] Views ({len(views)}): {', '.join(sorted(views))}")

    conn.close()
    print("\n[pipeline] Phase 1: ALL CHECKS PASSED")


if __name__ == "__main__":
    run_pipeline()
    verify_phase1()
