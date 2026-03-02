"""
Walk-forward backtesting — compares ARIMA vs Holt-Winters per product.

Strategy: hold out the last 90 days of historical sales as the test set.
Train on everything before, forecast 90 days, compute MAE / RMSE / MAPE.
Writes results to ForecastEvaluation table and returns a summary DataFrame.
"""
import sqlite3
import warnings
from datetime import date, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from config.settings import DB_PATH, END_DATE

warnings.filterwarnings("ignore")

HOLDOUT_DAYS = 90
_ARIMA_ORDER = (1, 1, 1)
_SEASONAL_PERIODS = 52


def _mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    mask = actual > 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])))


def _rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def _mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - predicted)))


def _load_daily_series(product_id: int, conn: sqlite3.Connection) -> pd.Series:
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
    full_idx = pd.date_range(df["SaleDate"].min(), df["SaleDate"].max(), freq="D")
    series = df.set_index("SaleDate")["QuantitySold"].reindex(full_idx, fill_value=0)
    return series


def _evaluate_product(product_id: int, conn: sqlite3.Connection) -> List[Dict]:
    daily = _load_daily_series(product_id, conn)
    if len(daily) < HOLDOUT_DAYS + 30:
        return []

    # Split
    train_daily = daily.iloc[:-HOLDOUT_DAYS]
    test_daily = daily.iloc[-HOLDOUT_DAYS:]

    # Weekly aggregation for models
    train_weekly = train_daily.resample("W").sum().clip(lower=0.1)
    test_weekly = test_daily.resample("W").sum()
    n_test_weeks = len(test_weekly)

    results = []

    # ── ARIMA ──────────────────────────────────────────────────
    try:
        arima_fit = ARIMA(train_weekly, order=_ARIMA_ORDER).fit()
        arima_pred_weekly = arima_fit.forecast(steps=n_test_weeks).values
        # Align lengths
        min_len = min(len(test_weekly), len(arima_pred_weekly))
        actual_w = test_weekly.values[:min_len]
        pred_w = np.maximum(0, arima_pred_weekly[:min_len])
        results.append({
            "ProductID":   product_id,
            "ModelName":   "ARIMA",
            "HorizonDays": HOLDOUT_DAYS,
            "MAE":         round(_mae(actual_w, pred_w), 3),
            "RMSE":        round(_rmse(actual_w, pred_w), 3),
            "MAPE":        round(_mape(actual_w, pred_w), 4),
        })
    except Exception:
        pass

    # ── Holt-Winters ───────────────────────────────────────────
    # Need 2 full seasonal cycles (104 weeks) for seasonal HW;
    # fall back to trend-only (Holt's double exponential) if shorter.
    try:
        if len(train_weekly) >= 2 * _SEASONAL_PERIODS:
            seasonal = "add"
            sp = _SEASONAL_PERIODS
        else:
            seasonal = None
            sp = None
        hw_fit = ExponentialSmoothing(
            train_weekly,
            trend="add",
            seasonal=seasonal,
            seasonal_periods=sp,
            initialization_method="estimated",
        ).fit(optimized=True, remove_bias=True)
        hw_pred_weekly = hw_fit.forecast(n_test_weeks).values
        min_len = min(len(test_weekly), len(hw_pred_weekly))
        actual_w = test_weekly.values[:min_len]
        pred_w = np.maximum(0, hw_pred_weekly[:min_len])
        results.append({
            "ProductID":   product_id,
            "ModelName":   "HoltWinters",
            "HorizonDays": HOLDOUT_DAYS,
            "MAE":         round(_mae(actual_w, pred_w), 3),
            "RMSE":        round(_rmse(actual_w, pred_w), 3),
            "MAPE":        round(_mape(actual_w, pred_w), 4),
        })
    except Exception:
        pass

    return results


def run_evaluation(db_path=DB_PATH) -> pd.DataFrame:
    """
    Runs walk-forward backtest for all products.
    Returns DataFrame ready to be written to ForecastEvaluation table.
    """
    conn = sqlite3.connect(db_path)
    product_ids = [
        r[0] for r in conn.execute("SELECT ProductID FROM Products ORDER BY ProductID").fetchall()
    ]

    all_results = []
    for pid in product_ids:
        all_results.extend(_evaluate_product(pid, conn))

    conn.close()

    if not all_results:
        return pd.DataFrame()

    df = pd.DataFrame(all_results)
    # Summary
    summary = df.groupby("ModelName")[["MAE", "RMSE", "MAPE"]].mean().round(4)
    print(f"[evaluator] Evaluated {len(product_ids)} products, {len(df)} results")
    print(summary.to_string())
    return df


if __name__ == "__main__":
    df = run_evaluation()
    print(df.sort_values("MAPE").head(20).to_string())
