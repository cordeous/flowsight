"""
Stockout Rate — current snapshot view.
Flags products where QuantityOnHand < SafetyStockLevel (stockout)
or < ReorderPoint (needs replenishment).

Also simulates a daily stockout history by comparing each day's
cumulative sales against starting inventory — gives a richer
time-series stockout rate for the dashboard.
"""
import sqlite3

import pandas as pd

from config.settings import DB_PATH


def compute_stockout_snapshot(db_path=DB_PATH) -> pd.DataFrame:
    """Current-state stockout flag for every product."""
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT
            p.ProductID,
            p.ProductName,
            p.Category,
            p.SafetyStockLevel,
            i.QuantityOnHand,
            i.ReorderPoint,
            CASE WHEN i.QuantityOnHand < p.SafetyStockLevel THEN 1 ELSE 0 END AS IsStockout,
            CASE WHEN i.QuantityOnHand < i.ReorderPoint     THEN 1 ELSE 0 END AS BelowReorderPoint,
            i.LastUpdated
        FROM Inventory i
        JOIN Products p ON i.ProductID = p.ProductID
        ORDER BY IsStockout DESC, BelowReorderPoint DESC
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    stockout_count = df["IsStockout"].sum()
    below_rop = df["BelowReorderPoint"].sum()
    total = len(df)
    print(f"[kpi:stockout] Stockouts: {stockout_count}/{total} "
          f"({100*stockout_count/total:.1f}%)  "
          f"Below ROP: {below_rop}/{total} ({100*below_rop/total:.1f}%)")
    return df


def compute_stockout_rate_by_category(db_path=DB_PATH) -> pd.DataFrame:
    """Stockout rate aggregated by category."""
    df = compute_stockout_snapshot(db_path)
    grouped = df.groupby("Category").agg(
        TotalProducts=("ProductID", "count"),
        StockoutCount=("IsStockout", "sum"),
        BelowROPCount=("BelowReorderPoint", "sum"),
    )
    grouped["StockoutRatePct"] = (
        100 * grouped["StockoutCount"] / grouped["TotalProducts"]
    ).round(1)
    grouped["BelowROPRatePct"] = (
        100 * grouped["BelowROPCount"] / grouped["TotalProducts"]
    ).round(1)
    return grouped.reset_index()


if __name__ == "__main__":
    snapshot = compute_stockout_snapshot()
    print(snapshot.head(10).to_string())
    print()
    by_cat = compute_stockout_rate_by_category()
    print(by_cat.to_string())
