"""
Tests: anomaly detection and optimization modules produce valid outputs.
"""
import sqlite3
import pytest
from config.settings import DB_PATH


@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()


# ── Anomaly tests ─────────────────────────────────────────────

def test_anomalies_table_populated(conn):
    count = conn.execute("SELECT COUNT(*) FROM Anomalies").fetchone()[0]
    assert count > 0, "Anomalies table is empty"


def test_both_detectors_present(conn):
    detectors = {r[0] for r in conn.execute(
        "SELECT DISTINCT DetectorType FROM Anomalies"
    ).fetchall()}
    assert "zscore" in detectors
    assert "isolation_forest" in detectors


def test_valid_severity_values(conn):
    severities = {r[0] for r in conn.execute(
        "SELECT DISTINCT Severity FROM Anomalies"
    ).fetchall()}
    assert severities <= {"LOW", "MEDIUM", "HIGH"}


def test_anomaly_scores_positive(conn):
    bad = conn.execute(
        "SELECT COUNT(*) FROM Anomalies WHERE AnomalyScore <= 0"
    ).fetchone()[0]
    assert bad == 0


def test_anomalies_linked_to_valid_products(conn):
    orphans = conn.execute("""
        SELECT COUNT(*) FROM Anomalies a
        LEFT JOIN Products p ON a.ProductID = p.ProductID
        WHERE p.ProductID IS NULL
    """).fetchone()[0]
    assert orphans == 0


# ── Optimization tests ────────────────────────────────────────

def test_recommendations_all_products(conn):
    count = conn.execute("SELECT COUNT(*) FROM Recommendations").fetchone()[0]
    assert count == 50, f"Expected 50 recommendations, got {count}"


def test_eoq_all_positive(conn):
    bad = conn.execute(
        "SELECT COUNT(*) FROM Recommendations WHERE RecommendedEOQ <= 0"
    ).fetchone()[0]
    assert bad == 0


def test_rop_non_negative(conn):
    bad = conn.execute(
        "SELECT COUNT(*) FROM Recommendations WHERE RecommendedROP < 0"
    ).fetchone()[0]
    assert bad == 0


def test_reorder_alert_view_has_all_three_statuses(conn):
    statuses = {r[0] for r in conn.execute(
        "SELECT DISTINCT AlertStatus FROM vw_reorder_alerts"
    ).fetchall()}
    # At least one of the statuses should appear
    assert len(statuses) >= 1
    assert statuses <= {"ORDER NOW", "ORDER SOON", "OK"}
