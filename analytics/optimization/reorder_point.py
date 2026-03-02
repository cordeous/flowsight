"""
Reorder Point (ROP) calculator — per product.

ROP = (AvgDailyDemand * LeadTimeDays) + SafetyStock

Where SafetyStock uses a service-level Z-factor:
  SafetyStock = Z * StdDailyDemand * sqrt(LeadTimeDays)
  Z = 1.65 for 95% service level (configurable)

Also computes DaysOfStockRemaining = QuantityOnHand / AvgDailyDemand
"""
import sqlite3
from math import sqrt

import numpy as np
import pandas as pd

from config.settings import DB_PATH

Z_95 = 1.645   # 95% service level


def compute_reorder_points(db_path=DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    # Daily demand stats per product (last 365 days)
    sql = """
        SELECT
            p.ProductID,
            p.ProductName,
            p.Category,
            p.UnitCost,
            p.LeadTimeDays,
            p.SafetyStockLevel,
            i.QuantityOnHand,
            s.SaleDate,
            s.DailyQty
        FROM Products p
        JOIN Inventory i ON i.ProductID = p.ProductID
        JOIN (
            SELECT ProductID,
                   SaleDate,
                   SUM(QuantitySold) AS DailyQty
            FROM Sales
            WHERE SaleDate >= date((SELECT MAX(SaleDate) FROM Sales), '-365 days')
            GROUP BY ProductID, SaleDate
        ) s ON s.ProductID = p.ProductID
        ORDER BY p.ProductID, s.SaleDate
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    records = []
    for prod_id, grp in df.groupby("ProductID"):
        row0 = grp.iloc[0]
        daily_qty = grp["DailyQty"].values.astype(float)

        avg_daily = float(np.mean(daily_qty))
        std_daily = float(np.std(daily_qty))
        lead_time = int(row0["LeadTimeDays"])
        qty_on_hand = int(row0["QuantityOnHand"])

        # Safety stock with Z-factor
        safety_stock = Z_95 * std_daily * sqrt(lead_time)
        # Reorder point
        rop = avg_daily * lead_time + safety_stock
        # Days of stock remaining (avoid div by zero)
        days_remaining = qty_on_hand / avg_daily if avg_daily > 0 else float("inf")

        records.append({
            "ProductID":        int(prod_id),
            "ProductName":      row0["ProductName"],
            "Category":         row0["Category"],
            "UnitCost":         float(row0["UnitCost"]),
            "LeadTimeDays":     lead_time,
            "AvgDailyDemand":   round(avg_daily, 2),
            "StdDailyDemand":   round(std_daily, 2),
            "SafetyStockQty":   round(safety_stock, 1),
            "ReorderPoint":     round(rop, 1),
            "QuantityOnHand":   qty_on_hand,
            "DaysOfStock":      round(min(days_remaining, 9999), 1),
            "ProvidedSafetyStock": int(row0["SafetyStockLevel"]),
        })

    result = pd.DataFrame(records)
    urgent = (result["QuantityOnHand"] <= result["ReorderPoint"]).sum()
    print(f"[rop] Reorder points computed for {len(result)} products. "
          f"Below ROP right now: {urgent}/{len(result)}")
    return result


if __name__ == "__main__":
    df = compute_reorder_points()
    cols = ["ProductName", "AvgDailyDemand", "ReorderPoint", "QuantityOnHand", "DaysOfStock"]
    print(df[cols].sort_values("DaysOfStock").to_string())
