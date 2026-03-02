"""
Tests: KPI modules return correct shapes and plausible values.
"""
import pytest
from config.settings import DB_PATH
from analytics.kpis.inventory_turnover import compute_inventory_turnover
from analytics.kpis.stockout_rate import compute_stockout_snapshot, compute_stockout_rate_by_category
from analytics.kpis.supplier_otd import compute_supplier_otd, compute_otd_monthly_trend
from analytics.kpis.delay_analysis import compute_delay_distribution


@pytest.fixture(scope="module")
def turnover_df():
    return compute_inventory_turnover()


@pytest.fixture(scope="module")
def stockout_df():
    return compute_stockout_snapshot()


@pytest.fixture(scope="module")
def otd_df():
    return compute_supplier_otd()


@pytest.fixture(scope="module")
def delay_df():
    return compute_delay_distribution()


def test_inventory_turnover_not_empty(turnover_df):
    assert len(turnover_df) > 0


def test_inventory_turnover_has_required_columns(turnover_df):
    for col in ["ProductID", "YearMonth", "COGS", "InventoryTurnoverRatio"]:
        assert col in turnover_df.columns


def test_inventory_turnover_positive_cogs(turnover_df):
    assert (turnover_df["COGS"] > 0).all()


def test_stockout_covers_all_products(stockout_df):
    assert len(stockout_df) == 50


def test_stockout_binary_flags(stockout_df):
    assert stockout_df["IsStockout"].isin([0, 1]).all()
    assert stockout_df["BelowReorderPoint"].isin([0, 1]).all()


def test_stockout_by_category_five_rows():
    cat_df = compute_stockout_rate_by_category()
    assert len(cat_df) == 5


def test_supplier_otd_covers_all_suppliers(otd_df):
    assert len(otd_df) == 15


def test_supplier_otd_pct_in_range(otd_df):
    assert otd_df["OnTimeDeliveryPct"].between(0, 100).all()


def test_otd_monthly_trend_not_empty():
    trend = compute_otd_monthly_trend()
    assert len(trend) > 0


def test_delay_distribution_covers_all_suppliers(delay_df):
    assert len(delay_df) == 15


def test_delay_distribution_has_percentiles(delay_df):
    for col in ["Mean", "Median", "P75", "P90", "P99"]:
        assert col in delay_df.columns
