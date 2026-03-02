"""
FlowSight — Master Runner
Runs all phases in sequence with a summary report at the end.

Usage:
  python scripts/run_all.py              # all phases
  python scripts/run_all.py --phase 1   # Phase 1 only (ETL)
  python scripts/run_all.py --phase 2   # Phase 1 + 2 (ETL + forecasting)
  python scripts/run_all.py --phase 3   # Phase 1 + 2 + 3 (full analytics)
"""
import argparse
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _banner(title: str) -> None:
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def run_phase1() -> float:
    _banner("PHASE 1 -- ETL Pipeline")
    t = time.time()
    from etl.pipeline import run_pipeline, verify_phase1
    run_pipeline()
    verify_phase1()
    return time.time() - t


def run_phase2() -> float:
    _banner("PHASE 2 -- KPIs + Forecasting")
    t = time.time()
    from analytics.forecasting.forecast_writer import write_forecasts, verify_phase2
    write_forecasts()
    verify_phase2()
    return time.time() - t


def export_csvs() -> None:
    """Export all 8 Power BI views to powerbi/data_export/ for CSV import method."""
    import sqlite3
    import pandas as pd
    from config.settings import DB_PATH

    export_dir = _ROOT / "powerbi" / "data_export"
    export_dir.mkdir(parents=True, exist_ok=True)

    views = [
        "vw_sales_trend", "vw_kpi_inventory_turnover", "vw_kpi_stockout",
        "vw_supplier_performance", "vw_demand_forecast", "vw_reorder_alerts",
        "vw_eoq_recommendations", "vw_anomaly_summary",
    ]
    conn = sqlite3.connect(DB_PATH)
    for v in views:
        df = pd.read_sql_query(f"SELECT * FROM {v}", conn)
        df.to_csv(export_dir / f"{v}.csv", index=False)
    conn.close()
    print(f"[csv_export] Exported {len(views)} views -> powerbi/data_export/")


def run_phase3() -> float:
    _banner("PHASE 3 -- Optimization + Anomaly Detection + Alerts")
    t = time.time()

    from analytics.optimization.optimization_writer import (
        write_recommendations, verify_optimization,
    )
    write_recommendations()
    verify_optimization()

    from analytics.anomaly.anomaly_writer import write_anomalies, verify_anomalies
    write_anomalies()
    verify_anomalies()

    from alerts.alert_rules import evaluate_all_rules
    alerts = evaluate_all_rules()
    print(f"\n  Active alerts: {len(alerts)}")
    for a in alerts[:5]:
        print(f"  [{a['level']:8s}] {a['message'][:80]}...")

    return time.time() - t


def main() -> None:
    parser = argparse.ArgumentParser(description="FlowSight master runner")
    parser.add_argument(
        "--phase", type=int, choices=[1, 2, 3], default=3,
        help="Run up to this phase (default: 3 = all)"
    )
    args = parser.parse_args()

    total_start = time.time()
    timings = {}

    timings["Phase 1 (ETL)"] = run_phase1()

    if args.phase >= 2:
        timings["Phase 2 (Forecasting)"] = run_phase2()

    if args.phase >= 3:
        timings["Phase 3 (Optimization + Anomaly)"] = run_phase3()

    # Always export CSVs so Power BI files stay current
    export_csvs()

    # Regenerate interactive HTML dashboard
    t_dash = time.time()
    try:
        import importlib.util, types
        spec = importlib.util.spec_from_file_location(
            "generate_dashboard",
            _ROOT / "powerbi" / "generate_dashboard.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_dashboard(open_browser=False)
        timings["Dashboard (HTML)"] = time.time() - t_dash
    except Exception as exc:
        print(f"  [dashboard] WARNING: could not regenerate dashboard: {exc}")

    _banner("COMPLETE -- Timing Summary")
    for label, elapsed in timings.items():
        print(f"  {label:<35} {elapsed:5.1f}s")
    print(f"  {'Total':<35} {time.time() - total_start:5.1f}s")
    print()
    print("  Database:    db/flowsight.db")
    print("  CSV export:  powerbi/data_export/  (8 files, ready to import)")
    print("  Dashboard:   powerbi/FlowSight_Dashboard.html")
    print("  Power BI:    see powerbi/odbc_setup_guide.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
