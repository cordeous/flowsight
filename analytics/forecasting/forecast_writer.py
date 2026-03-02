"""
Writes forecast and evaluation DataFrames to SQLite.
Clears existing data before writing (idempotent re-runs).
"""
import sqlite3

import pandas as pd

from config.settings import DB_PATH
from analytics.forecasting.arima_forecast import run_arima_forecast
from analytics.forecasting.holtwinters_forecast import run_holtwinters_forecast
from analytics.forecasting.forecast_evaluator import run_evaluation


def write_forecasts(db_path=DB_PATH) -> None:
    """Generate, combine, and persist all forecasts + evaluation results."""
    print("[forecast_writer] Running ARIMA forecast...")
    arima_df = run_arima_forecast(db_path)

    print("[forecast_writer] Running Holt-Winters forecast...")
    hw_df = run_holtwinters_forecast(db_path)

    print("[forecast_writer] Running evaluation (walk-forward backtest)...")
    eval_df = run_evaluation(db_path)

    conn = sqlite3.connect(db_path)

    # Clear existing rows
    conn.execute("DELETE FROM Forecasts")
    conn.execute("DELETE FROM ForecastEvaluation")
    conn.commit()

    # Write forecasts
    all_forecasts = pd.concat([arima_df, hw_df], ignore_index=True)
    all_forecasts.to_sql("Forecasts", conn, if_exists="append", index=False)
    print(f"[forecast_writer] Wrote {len(all_forecasts):,} rows to Forecasts")

    # Write evaluation
    if not eval_df.empty:
        eval_df.to_sql("ForecastEvaluation", conn, if_exists="append", index=False)
        print(f"[forecast_writer] Wrote {len(eval_df):,} rows to ForecastEvaluation")

    conn.commit()
    conn.close()
    print("[forecast_writer] Done.")


def verify_phase2(db_path=DB_PATH) -> None:
    """Phase 2 gate checks."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    count = cur.execute("SELECT COUNT(*) FROM Forecasts").fetchone()[0]
    assert count > 0, "Forecasts table is empty"
    print(f"  [ok] Forecasts rows: {count:,}")

    models = {r[0] for r in cur.execute("SELECT DISTINCT ModelName FROM Forecasts").fetchall()}
    assert "ARIMA" in models, "ARIMA forecasts missing"
    assert "HoltWinters" in models, "HoltWinters forecasts missing"
    print(f"  [ok] Models: {models}")

    horizons = {r[0] for r in cur.execute("SELECT DISTINCT HorizonDays FROM Forecasts").fetchall()}
    assert {30, 60, 90} <= horizons, f"Missing horizons: {horizons}"
    print(f"  [ok] Horizons: {horizons}")

    null_qty = cur.execute("SELECT COUNT(*) FROM Forecasts WHERE ForecastQty IS NULL").fetchone()[0]
    assert null_qty == 0, f"Null ForecastQty: {null_qty}"
    print(f"  [ok] No null ForecastQty")

    mape_rows = cur.execute(
        "SELECT ModelName, AVG(MAPE) FROM ForecastEvaluation GROUP BY ModelName"
    ).fetchall()
    for model, avg_mape in mape_rows:
        flag = "WARNING" if avg_mape and avg_mape > 0.35 else "ok"
        print(f"  [{flag}] {model} avg MAPE: {avg_mape:.4f}" if avg_mape else f"  [ok] {model} MAPE: N/A")

    conn.close()
    print("\n[forecast_writer] Phase 2: ALL CHECKS PASSED")


if __name__ == "__main__":
    write_forecasts()
    verify_phase2()
