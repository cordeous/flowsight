"""
Tests: forecasting modules produce correct output shapes and valid values.
"""
import sqlite3
import pytest
from config.settings import DB_PATH, FORECAST_HORIZONS


@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()


def test_forecasts_table_populated(conn):
    count = conn.execute("SELECT COUNT(*) FROM Forecasts").fetchone()[0]
    assert count > 0, "Forecasts table is empty — run forecast_writer first"


def test_both_models_present(conn):
    models = {r[0] for r in conn.execute(
        "SELECT DISTINCT ModelName FROM Forecasts"
    ).fetchall()}
    assert "ARIMA" in models
    assert "HoltWinters" in models


def test_all_horizons_present(conn):
    horizons = {r[0] for r in conn.execute(
        "SELECT DISTINCT HorizonDays FROM Forecasts"
    ).fetchall()}
    assert set(FORECAST_HORIZONS) <= horizons


def test_no_null_forecast_qty(conn):
    nulls = conn.execute(
        "SELECT COUNT(*) FROM Forecasts WHERE ForecastQty IS NULL"
    ).fetchone()[0]
    assert nulls == 0


def test_no_negative_forecast_qty(conn):
    negatives = conn.execute(
        "SELECT COUNT(*) FROM Forecasts WHERE ForecastQty < 0"
    ).fetchone()[0]
    assert negatives == 0


def test_lower_bound_lte_upper_bound(conn):
    bad = conn.execute("""
        SELECT COUNT(*) FROM Forecasts
        WHERE LowerBound IS NOT NULL
          AND UpperBound IS NOT NULL
          AND LowerBound > UpperBound
    """).fetchone()[0]
    assert bad == 0, f"{bad} rows where LowerBound > UpperBound"


def test_evaluation_both_models(conn):
    models = {r[0] for r in conn.execute(
        "SELECT DISTINCT ModelName FROM ForecastEvaluation"
    ).fetchall()}
    assert "ARIMA" in models
    assert "HoltWinters" in models


def test_mape_not_extreme(conn):
    # MAPE should be <2.0 (200%) — anything higher indicates a bug
    rows = conn.execute(
        "SELECT ModelName, AVG(MAPE) FROM ForecastEvaluation GROUP BY ModelName"
    ).fetchall()
    for model, avg_mape in rows:
        if avg_mape is not None:
            assert avg_mape < 2.0, f"{model} avg MAPE={avg_mape:.2f} is unreasonably high"


def test_forecast_dates_in_future(conn):
    # All forecast dates should be after the training END_DATE (2023-12-31)
    bad = conn.execute(
        "SELECT COUNT(*) FROM Forecasts WHERE ForecastDate <= '2023-12-31'"
    ).fetchone()[0]
    assert bad == 0, f"{bad} forecasts have dates on or before training end date"
