"""
Tests: database schema integrity — all tables and key columns exist.
"""
import sqlite3
import pytest
from config.settings import DB_PATH

REQUIRED_TABLES = {
    "Products", "Suppliers", "Inventory", "Orders",
    "OrderItems", "Sales", "Shipments",
    "Forecasts", "Recommendations", "Anomalies", "ForecastEvaluation",
}
REQUIRED_VIEWS = {
    "vw_kpi_inventory_turnover", "vw_kpi_stockout",
    "vw_supplier_performance", "vw_demand_forecast",
    "vw_reorder_alerts", "vw_eoq_recommendations",
    "vw_anomaly_summary", "vw_sales_trend",
}
REQUIRED_COLUMNS = {
    "Products":  ["ProductID", "ProductName", "Category", "UnitCost", "UnitPrice",
                  "SafetyStockLevel", "LeadTimeDays"],
    "Sales":     ["SaleID", "ProductID", "SaleDate", "QuantitySold", "Revenue"],
    "Shipments": ["ShipmentID", "OrderID", "ActualDeliveryDate",
                  "ExpectedDeliveryDate", "DelayDays"],
}


@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()


def _tables(conn):
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}


def _views(conn):
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view'"
    ).fetchall()}


def _columns(conn, table):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_all_tables_exist(conn):
    missing = REQUIRED_TABLES - _tables(conn)
    assert not missing, f"Missing tables: {missing}"


def test_all_views_exist(conn):
    missing = REQUIRED_VIEWS - _views(conn)
    assert not missing, f"Missing views: {missing}"


def test_column_names(conn):
    for table, cols in REQUIRED_COLUMNS.items():
        actual = _columns(conn, table)
        for col in cols:
            assert col in actual, f"{table}.{col} column missing"


def test_foreign_key_integrity(conn):
    # Inventory -> Products
    orphans = conn.execute("""
        SELECT COUNT(*) FROM Inventory i
        LEFT JOIN Products p ON i.ProductID = p.ProductID
        WHERE p.ProductID IS NULL
    """).fetchone()[0]
    assert orphans == 0, f"Inventory has {orphans} orphan ProductID references"

    # Sales -> Products
    orphans = conn.execute("""
        SELECT COUNT(*) FROM Sales s
        LEFT JOIN Products p ON s.ProductID = p.ProductID
        WHERE p.ProductID IS NULL
    """).fetchone()[0]
    assert orphans == 0, f"Sales has {orphans} orphan ProductID references"

    # Shipments -> Orders
    orphans = conn.execute("""
        SELECT COUNT(*) FROM Shipments sh
        LEFT JOIN Orders o ON sh.OrderID = o.OrderID
        WHERE o.OrderID IS NULL
    """).fetchone()[0]
    assert orphans == 0, f"Shipments has {orphans} orphan OrderID references"
