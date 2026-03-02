"""
Z-score anomaly detection on daily sales volume per product.

Method:
  1. For each product, compute a rolling 30-day mean and std of QuantitySold
  2. Flag days where |z-score| > ZSCORE_THRESHOLD (default 3.0)
  3. Classify severity: |z| 3-4 = MEDIUM, >4 = HIGH

Returns a DataFrame of flagged anomaly records.
"""
import sqlite3

import numpy as np
import pandas as pd

from config.settings import DB_PATH, ZSCORE_THRESHOLD

_ROLLING_WINDOW = 30   # days


def detect_zscore_anomalies(db_path=DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT ProductID, SaleDate, SUM(QuantitySold) AS QuantitySold
        FROM Sales
        GROUP BY ProductID, SaleDate
        ORDER BY ProductID, SaleDate
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    df["SaleDate"] = pd.to_datetime(df["SaleDate"])
    anomaly_records = []

    for prod_id, grp in df.groupby("ProductID"):
        grp = grp.sort_values("SaleDate").set_index("SaleDate")
        series = grp["QuantitySold"].astype(float)

        # Fill date gaps with 0 before rolling (so window is truly 30 calendar days)
        full_idx = pd.date_range(series.index.min(), series.index.max(), freq="D")
        series = series.reindex(full_idx, fill_value=0.0)

        roll_mean = series.rolling(_ROLLING_WINDOW, min_periods=7).mean()
        roll_std  = series.rolling(_ROLLING_WINDOW, min_periods=7).std()

        # Avoid division by zero on flat series
        roll_std = roll_std.replace(0, np.nan)
        z_scores = (series - roll_mean) / roll_std

        flagged = z_scores[z_scores.abs() > ZSCORE_THRESHOLD].dropna()

        for sale_date, z in flagged.items():
            severity = "HIGH" if abs(z) > 4.0 else "MEDIUM"
            anomaly_records.append({
                "ProductID":    int(prod_id),
                "DetectorType": "zscore",
                "AnomalyScore": round(float(abs(z)), 4),
                "AnomalyDate":  sale_date.date().isoformat(),
                "FeatureName":  "QuantitySold",
                "FeatureValue": round(float(series[sale_date]), 2),
                "Severity":     severity,
            })

    result = pd.DataFrame(anomaly_records) if anomaly_records else pd.DataFrame(
        columns=["ProductID", "DetectorType", "AnomalyScore", "AnomalyDate",
                 "FeatureName", "FeatureValue", "Severity"]
    )
    print(f"[zscore] Flagged {len(result)} anomalies across "
          f"{result['ProductID'].nunique() if len(result) else 0} products "
          f"(threshold: |z| > {ZSCORE_THRESHOLD})")
    return result


if __name__ == "__main__":
    df = detect_zscore_anomalies()
    print(df.sort_values("AnomalyScore", ascending=False).head(20).to_string())
