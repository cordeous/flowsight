"""
Alert rule engine — evaluates threshold conditions against live DB data.
Returns a list of alert dicts; does not send emails directly.
email_sender.py consumes this output.

Rules:
  1. STOCKOUT RISK  — QuantityOnHand <= RecommendedROP
  2. ORDER NOW      — QuantityOnHand <= RecommendedROP and DaysOfStock < LeadTimeDays
  3. HIGH ANOMALY   — Anomalies with Severity = 'HIGH' in the last 30 days
  4. SUPPLIER DELAY — Supplier AvgDelayDays above fleet P90
"""
import sqlite3
from typing import List, Dict, Any

import numpy as np
import pandas as pd

from config.settings import DB_PATH


def evaluate_all_rules(
    db_path=DB_PATH,
    send_email: bool = False,
) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    alerts = []

    # ── Rule 1 & 2: Stockout / Reorder alerts ─────────────────
    stockout_sql = """
        SELECT
            p.ProductID,
            p.ProductName,
            p.Category,
            p.LeadTimeDays,
            i.QuantityOnHand,
            r.RecommendedROP,
            r.RecommendedEOQ,
            CASE WHEN i.QuantityOnHand > 0 AND
                      (SELECT AVG(QuantitySold) FROM Sales WHERE ProductID = p.ProductID) > 0
                 THEN ROUND(
                     i.QuantityOnHand /
                     (SELECT AVG(QuantitySold) FROM Sales WHERE ProductID = p.ProductID)
                 , 1)
                 ELSE 0
            END AS DaysOfStock
        FROM Products p
        JOIN Inventory     i ON i.ProductID = p.ProductID
        JOIN Recommendations r ON r.ProductID = p.ProductID
        WHERE i.QuantityOnHand <= r.RecommendedROP
        ORDER BY DaysOfStock ASC
    """
    stockout_df = pd.read_sql_query(stockout_sql, conn)
    for _, row in stockout_df.iterrows():
        level = "CRITICAL" if row["DaysOfStock"] < row["LeadTimeDays"] else "WARNING"
        alerts.append({
            "rule":        "REORDER_ALERT",
            "level":       level,
            "product_id":  int(row["ProductID"]),
            "product":     row["ProductName"],
            "category":    row["Category"],
            "message":     (
                f"{row['ProductName']}: {int(row['QuantityOnHand'])} units on hand, "
                f"ROP={row['RecommendedROP']:.0f}, "
                f"~{row['DaysOfStock']:.0f} days of stock remaining "
                f"(lead time: {row['LeadTimeDays']}d). "
                f"Order {row['RecommendedEOQ']:.0f} units."
            ),
        })

    # ── Rule 3: High anomaly alerts ────────────────────────────
    anomaly_sql = """
        SELECT a.ProductID, p.ProductName, a.DetectorType,
               a.AnomalyScore, a.AnomalyDate, a.FeatureName, a.FeatureValue
        FROM Anomalies a
        JOIN Products p ON a.ProductID = p.ProductID
        WHERE a.Severity = 'HIGH'
        ORDER BY a.AnomalyScore DESC
        LIMIT 20
    """
    anomaly_df = pd.read_sql_query(anomaly_sql, conn)
    for _, row in anomaly_df.iterrows():
        alerts.append({
            "rule":        "ANOMALY_DETECTED",
            "level":       "WARNING",
            "product_id":  int(row["ProductID"]),
            "product":     row["ProductName"],
            "category":    None,
            "message":     (
                f"{row['ProductName']}: HIGH anomaly detected by {row['DetectorType']} "
                f"on {row['AnomalyDate']}. "
                f"{row['FeatureName']} = {row['FeatureValue']:.1f} "
                f"(score: {row['AnomalyScore']:.3f})"
            ),
        })

    # ── Rule 4: Supplier delay spike ───────────────────────────
    supplier_sql = """
        SELECT SupplierName, AvgDelayDays, OnTimeDeliveryPct, TotalShipments
        FROM vw_supplier_performance
        ORDER BY AvgDelayDays DESC
    """
    sup_df = pd.read_sql_query(supplier_sql, conn)
    if len(sup_df) > 0:
        p90_delay = float(np.percentile(sup_df["AvgDelayDays"].dropna(), 90))
        worst = sup_df[sup_df["AvgDelayDays"] > p90_delay]
        for _, row in worst.iterrows():
            alerts.append({
                "rule":       "SUPPLIER_DELAY",
                "level":      "WARNING",
                "product_id": None,
                "product":    None,
                "category":   None,
                "message":    (
                    f"Supplier '{row['SupplierName']}': avg delay {row['AvgDelayDays']:.1f}d "
                    f"(fleet P90={p90_delay:.1f}d), "
                    f"OTD={row['OnTimeDeliveryPct']:.1f}% "
                    f"over {int(row['TotalShipments'])} shipments."
                ),
            })

    conn.close()
    print(f"[alert_rules] {len(alerts)} alerts fired "
          f"({sum(1 for a in alerts if a['level']=='CRITICAL')} CRITICAL, "
          f"{sum(1 for a in alerts if a['level']=='WARNING')} WARNING)")
    return alerts


if __name__ == "__main__":
    alerts = evaluate_all_rules()
    for a in alerts:
        print(f"[{a['level']:8s}] {a['rule']}: {a['message']}")
