"""
ARIMA demand forecasting — per ProductID.

Uses statsmodels ARIMA with a fixed (1,1,1) order as the baseline.
For each product we:
  1. Aggregate daily sales to weekly totals (reduces noise, speeds fitting)
  2. Fit ARIMA(1,1,1) on the weekly series
  3. Forecast 30 / 60 / 90 calendar-day horizons
  4. Convert weekly forecast back to daily average quantities

Returns a list of forecast record dicts ready for forecast_writer.py.
"""
import warnings
from datetime import date, timedelta
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import sqlite3
from statsmodels.tsa.arima.model import ARIMA

from config.settings import DB_PATH, END_DATE, FORECAST_HORIZONS

warnings.filterwarnings("ignore")  # suppress ARIMA convergence warnings

MODEL_NAME = "ARIMA"
_ARIMA_ORDER = (1, 1, 1)
_MIN_OBSERVATIONS = 20   # skip products with too little history


def _load_sales_weekly(product_id: int, conn: sqlite3.Connection) -> pd.Series:
    """Aggregate daily sales -> weekly totals for one product."""
    sql = """
        SELECT SaleDate, SUM(QuantitySold) AS QuantitySold
        FROM Sales
        WHERE ProductID = ?
        GROUP BY SaleDate
        ORDER BY SaleDate
    """
    df = pd.read_sql_query(sql, conn, params=(product_id,))
    if df.empty:
        return pd.Series(dtype=float)

    df["SaleDate"] = pd.to_datetime(df["SaleDate"])
    df = df.set_index("SaleDate").sort_index()

    # Fill missing days with 0, then resample to weekly
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
    daily = df.reindex(full_idx, fill_value=0)["QuantitySold"]
    weekly = daily.resample("W").sum()
    return weekly


def _forecast_one(
    product_id: int,
    conn: sqlite3.Connection,
    forecast_start: date,
) -> List[Dict[str, Any]]:
    """Fit ARIMA on one product's weekly series and return forecast records."""
    series = _load_sales_weekly(product_id, conn)

    if len(series) < _MIN_OBSERVATIONS:
        return []

    try:
        model = ARIMA(series, order=_ARIMA_ORDER)
        fit = model.fit()
    except Exception:
        return []

    records = []
    for horizon in FORECAST_HORIZONS:
        n_weeks = max(1, round(horizon / 7))
        try:
            forecast_result = fit.get_forecast(steps=n_weeks)
            mean_weekly = forecast_result.predicted_mean.values
            ci = forecast_result.conf_int(alpha=0.20)  # 80% CI
            lower_weekly = ci.iloc[:, 0].values
            upper_weekly = ci.iloc[:, 1].values
        except Exception:
            continue

        # Convert weekly forecast to daily average and emit one record per day
        days_per_week = 7.0
        for week_i in range(n_weeks):
            week_start = forecast_start + timedelta(weeks=week_i)
            for day_offset in range(7):
                forecast_date = week_start + timedelta(days=day_offset)
                # Only emit within horizon window
                if (forecast_date - forecast_start).days >= horizon:
                    break
                daily_qty = max(0.0, float(mean_weekly[week_i]) / days_per_week)
                daily_lower = max(0.0, float(lower_weekly[week_i]) / days_per_week)
                daily_upper = max(0.0, float(upper_weekly[week_i]) / days_per_week)

                records.append({
                    "ProductID":    product_id,
                    "ModelName":    MODEL_NAME,
                    "ForecastDate": forecast_date.isoformat(),
                    "ForecastQty":  round(daily_qty, 2),
                    "LowerBound":   round(daily_lower, 2),
                    "UpperBound":   round(daily_upper, 2),
                    "HorizonDays":  horizon,
                })

    return records


def run_arima_forecast(db_path=DB_PATH) -> pd.DataFrame:
    """
    Runs ARIMA forecast for all products.
    Returns DataFrame of all forecast records.
    """
    conn = sqlite3.connect(db_path)
    product_ids = [
        r[0] for r in conn.execute("SELECT ProductID FROM Products ORDER BY ProductID").fetchall()
    ]

    forecast_start = date.fromisoformat(END_DATE) + timedelta(days=1)
    all_records = []
    skipped = 0

    for pid in product_ids:
        records = _forecast_one(pid, conn, forecast_start)
        if records:
            all_records.extend(records)
        else:
            skipped += 1

    conn.close()

    df = pd.DataFrame(all_records)
    print(f"[arima] Forecasted {len(product_ids) - skipped}/{len(product_ids)} products "
          f"-> {len(df):,} records (start: {forecast_start})")
    return df


if __name__ == "__main__":
    df = run_arima_forecast()
    print(df.head(10).to_string())
