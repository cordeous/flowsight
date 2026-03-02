"""
Economic Order Quantity (EOQ) calculator — per product.

EOQ = sqrt(2 * AnnualDemand * OrderingCost / HoldingCostPerUnit)

Where:
  AnnualDemand     = total units sold in the most recent 365 days from Sales
  OrderingCost     = fixed cost per purchase order (from settings)
  HoldingCostPerUnit = UnitCost * HoldingCostPct (from settings)

Returns a DataFrame with one row per product.
"""
import sqlite3
from math import sqrt

import pandas as pd

from config.settings import DB_PATH, EOQ_HOLDING_COST_PCT, EOQ_ORDERING_COST


def compute_eoq(db_path=DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    # Annual demand = sum of QuantitySold over last 365 days in dataset
    sql = """
        SELECT
            p.ProductID,
            p.ProductName,
            p.Category,
            p.UnitCost,
            p.UnitPrice,
            p.LeadTimeDays,
            p.SafetyStockLevel,
            COALESCE(SUM(s.QuantitySold), 0)  AS AnnualDemand
        FROM Products p
        LEFT JOIN Sales s
            ON  s.ProductID = p.ProductID
            AND s.SaleDate >= date((SELECT MAX(SaleDate) FROM Sales), '-365 days')
        GROUP BY p.ProductID
        ORDER BY p.ProductID
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    ordering_cost = EOQ_ORDERING_COST
    holding_pct   = EOQ_HOLDING_COST_PCT

    records = []
    for _, row in df.iterrows():
        demand      = float(row["AnnualDemand"])
        unit_cost   = float(row["UnitCost"])
        holding_per_unit = unit_cost * holding_pct

        if demand <= 0 or holding_per_unit <= 0:
            eoq = 0.0
        else:
            eoq = sqrt(2 * demand * ordering_cost / holding_per_unit)

        records.append({
            "ProductID":      int(row["ProductID"]),
            "ProductName":    row["ProductName"],
            "Category":       row["Category"],
            "UnitCost":       unit_cost,
            "AnnualDemand":   round(demand, 0),
            "OrderingCost":   ordering_cost,
            "HoldingCostPct": holding_pct,
            "EOQ":            round(eoq, 1),
        })

    result = pd.DataFrame(records)
    print(f"[eoq] Computed EOQ for {len(result)} products. "
          f"Median EOQ: {result['EOQ'].median():.0f} units")
    return result


if __name__ == "__main__":
    df = compute_eoq()
    print(df[["ProductName", "AnnualDemand", "EOQ"]].to_string())
