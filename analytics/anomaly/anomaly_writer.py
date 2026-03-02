"""
Orchestrates both anomaly detectors and writes results to the Anomalies table.
"""
import sqlite3

import pandas as pd

from config.settings import DB_PATH
from analytics.anomaly.zscore_detector import detect_zscore_anomalies
from analytics.anomaly.isolation_forest import detect_isolation_forest_anomalies


def write_anomalies(db_path=DB_PATH) -> None:
    print("[anomaly_writer] Running Z-score detector...")
    zscore_df = detect_zscore_anomalies(db_path)

    print("[anomaly_writer] Running Isolation Forest detector...")
    isoforest_df = detect_isolation_forest_anomalies(db_path)

    all_anomalies = pd.concat([zscore_df, isoforest_df], ignore_index=True)

    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM Anomalies")
    conn.commit()

    if len(all_anomalies) > 0:
        all_anomalies.to_sql("Anomalies", conn, if_exists="append", index=False)
        print(f"[anomaly_writer] Wrote {len(all_anomalies):,} rows to Anomalies.")
    else:
        print("[anomaly_writer] No anomalies detected.")

    conn.commit()
    conn.close()


def verify_anomalies(db_path=DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) FROM Anomalies").fetchone()[0]
    assert total > 0, "No anomalies written to Anomalies table"
    print(f"  [ok] Anomalies rows: {total:,}")

    detectors = {r[0] for r in cur.execute(
        "SELECT DISTINCT DetectorType FROM Anomalies"
    ).fetchall()}
    assert "zscore" in detectors, "Z-score anomalies missing"
    assert "isolation_forest" in detectors, "Isolation Forest anomalies missing"
    print(f"  [ok] Detectors: {detectors}")

    severities = {r[0] for r in cur.execute(
        "SELECT DISTINCT Severity FROM Anomalies"
    ).fetchall()}
    print(f"  [ok] Severities: {severities}")

    conn.close()


if __name__ == "__main__":
    write_anomalies()
    verify_anomalies()
