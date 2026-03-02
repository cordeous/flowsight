"""
Supplier On-Time Delivery (OTD) — per supplier.
On-time = DelayDays <= 0 (arrived on or before expected date).

Returns two DataFrames:
  1. Per-supplier summary (OTD%, avg delay, shipment count)
  2. Monthly trend of OTD% across all suppliers combined
"""
import sqlite3

import pandas as pd

from config.settings import DB_PATH


def compute_supplier_otd(db_path=DB_PATH) -> pd.DataFrame:
    """Per-supplier OTD performance."""
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT
            sup.SupplierID,
            sup.SupplierName,
            sup.Country,
            sup.Rating,
            COUNT(sh.ShipmentID)                                          AS TotalShipments,
            SUM(CASE WHEN sh.DelayDays <= 0 THEN 1 ELSE 0 END)           AS OnTimeShipments,
            ROUND(
                100.0 * SUM(CASE WHEN sh.DelayDays <= 0 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(sh.ShipmentID), 0)
            , 1)                                                          AS OnTimeDeliveryPct,
            ROUND(AVG(sh.DelayDays), 1)                                   AS AvgDelayDays,
            MAX(sh.DelayDays)                                             AS MaxDelayDays,
            MIN(sh.DelayDays)                                             AS MinDelayDays
        FROM Suppliers sup
        JOIN Orders    o  ON sup.SupplierID = o.SupplierID
        JOIN Shipments sh ON o.OrderID      = sh.OrderID
        GROUP BY sup.SupplierID
        ORDER BY OnTimeDeliveryPct DESC
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    overall_otd = df["OnTimeDeliveryPct"].mean()
    print(f"[kpi:supplier_otd] Suppliers: {len(df)} | "
          f"Avg OTD: {overall_otd:.1f}% | "
          f"Best: {df['OnTimeDeliveryPct'].max():.1f}% | "
          f"Worst: {df['OnTimeDeliveryPct'].min():.1f}%")
    return df


def compute_otd_monthly_trend(db_path=DB_PATH) -> pd.DataFrame:
    """Monthly OTD% across all suppliers — for trend chart."""
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT
            strftime('%Y-%m', o.OrderDate)                                AS YearMonth,
            COUNT(sh.ShipmentID)                                          AS TotalShipments,
            SUM(CASE WHEN sh.DelayDays <= 0 THEN 1 ELSE 0 END)           AS OnTimeShipments,
            ROUND(
                100.0 * SUM(CASE WHEN sh.DelayDays <= 0 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(sh.ShipmentID), 0)
            , 1)                                                          AS OnTimeDeliveryPct
        FROM Orders o
        JOIN Shipments sh ON o.OrderID = sh.OrderID
        GROUP BY strftime('%Y-%m', o.OrderDate)
        ORDER BY YearMonth
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


if __name__ == "__main__":
    df = compute_supplier_otd()
    print(df.to_string())
    print()
    trend = compute_otd_monthly_trend()
    print(trend.to_string())
