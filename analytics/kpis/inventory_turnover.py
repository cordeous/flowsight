"""
Inventory Turnover Ratio — by product and month.
Formula: COGS / Average Inventory Value
  COGS          = SUM(QuantitySold * UnitCost) for the month
  Avg Inv Value = QuantityOnHand * UnitCost (current snapshot)

Returns a DataFrame ready for Power BI or further analysis.
"""
import sqlite3

import pandas as pd

from config.settings import DB_PATH


def compute_inventory_turnover(db_path=DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    sql = """
        SELECT
            p.ProductID,
            p.ProductName,
            p.Category,
            strftime('%Y-%m', s.SaleDate)              AS YearMonth,
            SUM(s.QuantitySold * p.UnitCost)           AS COGS,
            i.QuantityOnHand * p.UnitCost              AS CurrentInventoryValue,
            ROUND(
                SUM(s.QuantitySold * p.UnitCost)
                / NULLIF(i.QuantityOnHand * p.UnitCost, 0)
            , 4)                                       AS InventoryTurnoverRatio
        FROM Sales s
        JOIN Products  p ON s.ProductID = p.ProductID
        JOIN Inventory i ON i.ProductID = p.ProductID
        GROUP BY p.ProductID, strftime('%Y-%m', s.SaleDate)
        ORDER BY p.ProductID, YearMonth
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    # Summary stats — useful for dashboard annotations
    summary = df.groupby("Category")["InventoryTurnoverRatio"].agg(
        mean="mean", median="median", max="max"
    ).round(2)

    print("[kpi:inventory_turnover] Rows:", len(df))
    print(summary.to_string())
    return df


if __name__ == "__main__":
    df = compute_inventory_turnover()
    print(df.head(10).to_string())
