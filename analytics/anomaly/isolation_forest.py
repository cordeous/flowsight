"""
Isolation Forest anomaly detection on a multi-feature matrix.

Features per product (monthly aggregates):
  - TotalUnitsSold       (sales volume)
  - AvgDailyRevenue      (revenue rate)
  - SupplierAvgDelay     (supply-side stress)
  - InventoryTurnover    (stock velocity)

Flags the top ISOLATION_FOREST_CONTAMINATION fraction as anomalies.
Severity: score > 0.6 = HIGH, 0.5-0.6 = MEDIUM, <0.5 = LOW
"""
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from config.settings import DB_PATH, ISOLATION_FOREST_CONTAMINATION


def detect_isolation_forest_anomalies(db_path=DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    # Build monthly feature matrix
    sales_sql = """
        SELECT
            p.ProductID,
            strftime('%Y-%m', s.SaleDate) AS YearMonth,
            SUM(s.QuantitySold)           AS TotalUnitsSold,
            SUM(s.Revenue) / 30.0         AS AvgDailyRevenue
        FROM Sales s
        JOIN Products p ON s.ProductID = p.ProductID
        GROUP BY p.ProductID, strftime('%Y-%m', s.SaleDate)
    """
    sales_df = pd.read_sql_query(sales_sql, conn)

    # Per-supplier monthly avg delay (joined via orders/shipments)
    delay_sql = """
        SELECT
            oi.ProductID,
            strftime('%Y-%m', o.OrderDate) AS YearMonth,
            AVG(sh.DelayDays)              AS SupplierAvgDelay
        FROM OrderItems oi
        JOIN Orders    o  ON oi.OrderID  = o.OrderID
        JOIN Shipments sh ON o.OrderID   = sh.OrderID
        GROUP BY oi.ProductID, strftime('%Y-%m', o.OrderDate)
    """
    delay_df = pd.read_sql_query(delay_sql, conn)

    # Inventory turnover from the view
    turnover_sql = """
        SELECT ProductID, YearMonth, InventoryTurnoverRatio AS InventoryTurnover
        FROM vw_kpi_inventory_turnover
    """
    turnover_df = pd.read_sql_query(turnover_sql, conn)
    conn.close()

    # Merge all features
    feat = sales_df.merge(delay_df,    on=["ProductID", "YearMonth"], how="left")
    feat = feat.merge(turnover_df,     on=["ProductID", "YearMonth"], how="left")
    feat = feat.fillna(0)

    feature_cols = ["TotalUnitsSold", "AvgDailyRevenue",
                    "SupplierAvgDelay", "InventoryTurnover"]
    X = feat[feature_cols].values.astype(float)

    if len(X) < 10:
        print("[isoforest] Not enough data to run Isolation Forest")
        return pd.DataFrame(
            columns=["ProductID", "DetectorType", "AnomalyScore",
                     "AnomalyDate", "FeatureName", "FeatureValue", "Severity"]
        )

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = IsolationForest(
        contamination=ISOLATION_FOREST_CONTAMINATION,
        random_state=42,
        n_estimators=100,
    )
    clf.fit(X_scaled)

    # score_samples returns negative values; convert to [0,1] anomaly score
    raw_scores = clf.score_samples(X_scaled)
    # Normalise: most anomalous = 1.0
    min_s, max_s = raw_scores.min(), raw_scores.max()
    if max_s == min_s:
        norm_scores = np.zeros_like(raw_scores)
    else:
        norm_scores = (max_s - raw_scores) / (max_s - min_s)

    feat = feat.copy()
    feat["AnomalyScore"] = norm_scores
    feat["IsAnomaly"]    = clf.predict(X_scaled) == -1  # -1 = anomaly

    flagged = feat[feat["IsAnomaly"]].copy()

    def severity(score):
        if score > 0.6:
            return "HIGH"
        elif score > 0.5:
            return "MEDIUM"
        return "LOW"

    records = []
    for _, row in flagged.iterrows():
        # Pick the feature with the highest absolute scaled value as the "driver"
        row_idx = feat.index.get_loc(row.name)
        scaled_row = X_scaled[row_idx]
        driver_idx = int(np.argmax(np.abs(scaled_row)))
        driver_col = feature_cols[driver_idx]
        driver_val = float(row[driver_col])

        records.append({
            "ProductID":    int(row["ProductID"]),
            "DetectorType": "isolation_forest",
            "AnomalyScore": round(float(row["AnomalyScore"]), 4),
            "AnomalyDate":  f"{row['YearMonth']}-01",
            "FeatureName":  driver_col,
            "FeatureValue": round(driver_val, 2),
            "Severity":     severity(row["AnomalyScore"]),
        })

    result = pd.DataFrame(records) if records else pd.DataFrame(
        columns=["ProductID", "DetectorType", "AnomalyScore", "AnomalyDate",
                 "FeatureName", "FeatureValue", "Severity"]
    )
    print(f"[isoforest] Flagged {len(result)} anomalies across "
          f"{result['ProductID'].nunique() if len(result) else 0} products "
          f"(contamination: {ISOLATION_FOREST_CONTAMINATION:.0%})")
    return result


if __name__ == "__main__":
    df = detect_isolation_forest_anomalies()
    print(df.sort_values("AnomalyScore", ascending=False).head(20).to_string())
