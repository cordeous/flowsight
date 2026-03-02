"""
Holt-Winters (Triple Exponential Smoothing) demand forecasting — per ProductID.

Holt-Winters captures level + trend + seasonality, making it a strong
complement to ARIMA for supply chain data with weekly/annual patterns.
Uses statsmodels ExponentialSmoothing with additive trend + additive seasonality.

Same interface as arima_forecast.py — returns a list of forecast record dicts.
"""
import warnings
from datetime import date, timedelta
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import sqlite3
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from config.settings import DB_PATH, END_DATE, FORECAST_HORIZONS

warnings.filterwarnings("ignore")

MODEL_NAME = "HoltWinters"
_SEASONAL_PERIODS = 52   # annual seasonality in weekly data
_MIN_OBSERVATIONS = 52   # need at least 1 full seasonal cycle


def _load_sales_weekly(product_id: int, conn: sqlite3.Connection) -> pd.Series:
    """Aggregate daily sales -> weekly totals for one product (same as ARIMA module)."""
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
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
    daily = df.reindex(full_idx, fill_value=0)["QuantitySold"]
    weekly = daily.resample("W").sum()
    # Replace zeros with small positive value to help HW fitting
    weekly = weekly.clip(lower=0.1)
    return weekly


def _forecast_one(
    product_id: int,
    conn: sqlite3.Connection,
    forecast_start: date,
) -> List[Dict[str, Any]]:
    """Fit Holt-Winters on one product and return forecast records."""
    series = _load_sales_weekly(product_id, conn)

    if len(series) < 20:
        return []
    # Need 2 full seasonal cycles for seasonal HW; use trend-only if shorter
    if len(series) >= 2 * _SEASONAL_PERIODS:
        seasonal = "add"
        seasonal_periods = _SEASONAL_PERIODS
    else:
        seasonal = None
        seasonal_periods = None

    try:
        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal=seasonal,
            seasonal_periods=seasonal_periods,
            initialization_method="estimated",
        )
        fit = model.fit(optimized=True, remove_bias=True)
    except Exception:
        return []

    records = []
    for horizon in FORECAST_HORIZONS:
        n_weeks = max(1, round(horizon / 7))
        try:
            mean_weekly = fit.forecast(n_weeks).values
        except Exception:
            continue

        # HW doesn't have built-in CI — approximate with ±1.5 * residual std
        resid_std = float(np.std(fit.resid)) if len(fit.resid) > 0 else 0.0
        ci_half = 1.5 * resid_std / 7.0   # per-day

        days_per_week = 7.0
        for week_i in range(n_weeks):
            week_start = forecast_start + timedelta(weeks=week_i)
            for day_offset in range(7):
                forecast_date = week_start + timedelta(days=day_offset)
                if (forecast_date - forecast_start).days >= horizon:
                    break
                daily_qty = max(0.0, float(mean_weekly[week_i]) / days_per_week)
                records.append({
                    "ProductID":    product_id,
                    "ModelName":    MODEL_NAME,
                    "ForecastDate": forecast_date.isoformat(),
                    "ForecastQty":  round(daily_qty, 2),
                    "LowerBound":   round(max(0.0, daily_qty - ci_half), 2),
                    "UpperBound":   round(daily_qty + ci_half, 2),
                    "HorizonDays":  horizon,
                })

    return records


def run_holtwinters_forecast(db_path=DB_PATH) -> pd.DataFrame:
    """
    Runs Holt-Winters forecast for all products.
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
    print(f"[holtwinters] Forecasted {len(product_ids) - skipped}/{len(product_ids)} products "
          f"-> {len(df):,} records (start: {forecast_start})")
    return df


if __name__ == "__main__":
    df = run_holtwinters_forecast()
    print(df.head(10).to_string())
