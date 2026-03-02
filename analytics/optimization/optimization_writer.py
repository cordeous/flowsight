"""
Orchestrates EOQ + ROP computation and writes results to the
Recommendations table in SQLite.
"""
import sqlite3

import pandas as pd

from config.settings import DB_PATH
from analytics.optimization.eoq_calculator import compute_eoq
from analytics.optimization.reorder_point import compute_reorder_points


def write_recommendations(db_path=DB_PATH) -> None:
    print("[opt_writer] Computing EOQ...")
    eoq_df = compute_eoq(db_path)

    print("[opt_writer] Computing Reorder Points...")
    rop_df = compute_reorder_points(db_path)

    # Merge on ProductID
    merged = eoq_df[["ProductID", "AnnualDemand", "OrderingCost", "HoldingCostPct", "EOQ"]].merge(
        rop_df[["ProductID", "ReorderPoint", "SafetyStockQty"]],
        on="ProductID",
        how="left",
    )

    recs = merged.rename(columns={
        "EOQ":            "RecommendedEOQ",
        "ReorderPoint":   "RecommendedROP",
    })

    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM Recommendations")
    conn.commit()
    recs[["ProductID", "AnnualDemand", "OrderingCost", "HoldingCostPct",
          "RecommendedEOQ", "RecommendedROP", "SafetyStockQty"]].to_sql(
        "Recommendations", conn, if_exists="append", index=False
    )
    conn.commit()
    conn.close()
    print(f"[opt_writer] Wrote {len(recs)} rows to Recommendations.")


def verify_optimization(db_path=DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    count = cur.execute("SELECT COUNT(*) FROM Recommendations").fetchone()[0]
    assert count == 50, f"Expected 50 recommendations, got {count}"
    print(f"  [ok] Recommendations rows: {count}")

    bad_eoq = cur.execute(
        "SELECT COUNT(*) FROM Recommendations WHERE RecommendedEOQ <= 0"
    ).fetchone()[0]
    assert bad_eoq == 0, f"{bad_eoq} non-positive EOQ values"
    print("  [ok] All EOQ values positive")

    bad_rop = cur.execute(
        "SELECT COUNT(*) FROM Recommendations WHERE RecommendedROP < 0"
    ).fetchone()[0]
    assert bad_rop == 0, f"{bad_rop} negative ROP values"
    print("  [ok] All ROP values non-negative")

    conn.close()


if __name__ == "__main__":
    write_recommendations()
    verify_optimization()
