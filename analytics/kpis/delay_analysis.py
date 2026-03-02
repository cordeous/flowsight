"""
Supplier Delay Distribution Analysis.
Computes: mean, median, P75, P90, P99 delay days per supplier.
Also flags suppliers whose avg delay exceeds the fleet-wide P75.
"""
import sqlite3

import numpy as np
import pandas as pd

from config.settings import DB_PATH


def compute_delay_distribution(db_path=DB_PATH) -> pd.DataFrame:
    """Full delay distribution stats per supplier."""
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT
            sup.SupplierID,
            sup.SupplierName,
            sup.Country,
            sh.DelayDays
        FROM Suppliers sup
        JOIN Orders    o  ON sup.SupplierID = o.SupplierID
        JOIN Shipments sh ON o.OrderID      = sh.OrderID
    """
    raw = pd.read_sql_query(sql, conn)
    conn.close()

    def percentile(n):
        def fn(x):
            return np.percentile(x, n)
        fn.__name__ = f"P{n}"
        return fn

    agg = raw.groupby(["SupplierID", "SupplierName", "Country"])["DelayDays"].agg(
        Count="count",
        Mean="mean",
        Median="median",
        P75=percentile(75),
        P90=percentile(90),
        P99=percentile(99),
        Max="max",
    ).round(1).reset_index()

    # Flag suppliers with mean delay above fleet-wide P75
    fleet_p75 = float(np.percentile(raw["DelayDays"], 75))
    agg["AboveFleetP75"] = (agg["Mean"] > fleet_p75).astype(int)

    print(f"[kpi:delay_analysis] Fleet-wide P75 delay: {fleet_p75:.1f} days")
    print(f"  Suppliers above fleet P75: {agg['AboveFleetP75'].sum()} / {len(agg)}")
    return agg


if __name__ == "__main__":
    df = compute_delay_distribution()
    print(df.to_string())
