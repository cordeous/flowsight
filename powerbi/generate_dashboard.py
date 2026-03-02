"""
FlowSight — Interactive HTML Dashboard Generator
Produces a single self-contained HTML file with all 4 dashboard pages
using Plotly. Opens automatically in your default browser.

Usage:
    python powerbi/generate_dashboard.py

Output:
    powerbi/FlowSight_Dashboard.html   (self-contained, ~5MB)
"""
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
from config.settings import DB_PATH

# ── Colour palette ────────────────────────────────────────────
C_BLUE    = "#0d6efd"
C_GREEN   = "#198754"
C_RED     = "#dc3545"
C_ORANGE  = "#fd7e14"
C_GREY    = "#6c757d"
C_BG      = "#0f1117"      # dark background
C_SURFACE = "#1a1d27"      # card background
C_TEXT    = "#e8eaf6"
C_SUBTLE  = "#8892b0"
C_BORDER  = "#2a2d3e"

PLOTLY_TEMPLATE = "plotly_dark"


# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════

def load_all(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    data = {
        "sales":      pd.read_sql_query("SELECT * FROM vw_sales_trend", conn),
        "turnover":   pd.read_sql_query("SELECT * FROM vw_kpi_inventory_turnover", conn),
        "stockout":   pd.read_sql_query("SELECT * FROM vw_kpi_stockout", conn),
        "supplier":   pd.read_sql_query("SELECT * FROM vw_supplier_performance", conn),
        "forecast":   pd.read_sql_query("SELECT * FROM vw_demand_forecast", conn),
        "reorder":    pd.read_sql_query("SELECT * FROM vw_reorder_alerts", conn),
        "eoq":        pd.read_sql_query("SELECT * FROM vw_eoq_recommendations", conn),
        "anomaly":    pd.read_sql_query("SELECT * FROM vw_anomaly_summary", conn),
        "eval":       pd.read_sql_query("SELECT * FROM ForecastEvaluation", conn),
    }
    conn.close()
    return data


# ═══════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════

def _kpi_indicator(value, title, suffix="", prefix="", delta=None, ref=None):
    """Returns a Plotly indicator trace."""
    return go.Indicator(
        mode="number+delta" if delta is not None else "number",
        value=value,
        number={"prefix": prefix, "suffix": suffix,
                "font": {"size": 40, "color": C_TEXT}},
        delta={"reference": delta, "relative": False} if delta is not None else None,
        title={"text": f"<b>{title}</b>", "font": {"size": 13, "color": C_SUBTLE}},
    )


def _fig_base(title="", height=420):
    fig = go.Figure()
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=C_BG,
        plot_bgcolor=C_SURFACE,
        font={"color": C_TEXT, "family": "Inter, Segoe UI, sans-serif"},
        title={"text": title, "font": {"size": 15, "color": C_TEXT},
               "x": 0.01, "xanchor": "left"},
        height=height,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
    )
    return fig


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════

def build_executive(d):
    sales = d["sales"].copy()
    supplier = d["supplier"].copy()
    stockout = d["stockout"].copy()
    turnover = d["turnover"].copy()

    # ── KPI row ───────────────────────────────────────────────
    total_revenue = sales["TotalRevenue"].sum()
    stockout_rate = stockout["IsStockout"].mean() * 100
    fleet_otd = supplier["OnTimeDeliveryPct"].mean()
    avg_turnover = turnover["InventoryTurnoverRatio"].mean()

    fig_kpis = make_subplots(rows=1, cols=4, specs=[[{"type":"indicator"}]*4])
    fig_kpis.add_trace(_kpi_indicator(total_revenue, "Total Revenue (2yr)", prefix="$",
                                       suffix=""), row=1, col=1)
    fig_kpis.add_trace(_kpi_indicator(stockout_rate, "Stockout Rate", suffix="%"), row=1, col=2)
    fig_kpis.add_trace(_kpi_indicator(fleet_otd, "Fleet OTD %", suffix="%"), row=1, col=3)
    fig_kpis.add_trace(_kpi_indicator(avg_turnover, "Avg Inv. Turnover", suffix="x"), row=1, col=4)
    fig_kpis.update_layout(paper_bgcolor=C_BG, plot_bgcolor=C_BG,
                           height=150, margin={"l":10,"r":10,"t":10,"b":10},
                           font={"color": C_TEXT})

    # ── Revenue trend ─────────────────────────────────────────
    rev_monthly = sales.groupby("YearMonth", as_index=False)["TotalRevenue"].sum()
    rev_monthly = rev_monthly.sort_values("YearMonth")

    fig_rev = _fig_base("Monthly Revenue", height=350)
    fig_rev.add_trace(go.Scatter(
        x=rev_monthly["YearMonth"], y=rev_monthly["TotalRevenue"],
        mode="lines+markers", line={"color": C_BLUE, "width": 2},
        marker={"size": 5}, fill="tozeroy",
        fillcolor="rgba(13,110,253,0.12)", name="Revenue",
    ))
    fig_rev.update_layout(yaxis_tickprefix="$", showlegend=False,
                          xaxis_title="", yaxis_title="Revenue ($)")

    # ── Revenue by category ───────────────────────────────────
    cat_rev = sales.groupby("Category", as_index=False)["TotalRevenue"].sum()
    fig_cat = _fig_base("Revenue by Category", height=350)
    fig_cat.add_trace(go.Pie(
        labels=cat_rev["Category"], values=cat_rev["TotalRevenue"],
        hole=0.5,
        marker={"colors": [C_BLUE, C_GREEN, C_ORANGE, C_RED, C_SUBTLE]},
        textinfo="label+percent",
        textfont={"size": 11, "color": C_TEXT},
    ))
    fig_cat.update_layout(showlegend=False)

    # ── Inventory turnover by category ────────────────────────
    cat_turn = (turnover.groupby("Category", as_index=False)["InventoryTurnoverRatio"]
                .mean().sort_values("InventoryTurnoverRatio"))
    colors = [C_RED if v < 2 else C_ORANGE if v < 4 else C_GREEN
              for v in cat_turn["InventoryTurnoverRatio"]]
    fig_turn = _fig_base("Avg Inventory Turnover by Category", height=350)
    fig_turn.add_trace(go.Bar(
        x=cat_turn["InventoryTurnoverRatio"], y=cat_turn["Category"],
        orientation="h", marker={"color": colors},
        text=cat_turn["InventoryTurnoverRatio"].round(2).astype(str) + "x",
        textposition="outside",
    ))
    fig_turn.update_layout(showlegend=False, xaxis_title="Turnover Ratio")

    return fig_kpis, fig_rev, fig_cat, fig_turn


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — INVENTORY HEALTH
# ═══════════════════════════════════════════════════════════════

def build_inventory(d):
    stockout = d["stockout"].copy()
    reorder  = d["reorder"].copy()
    eoq      = d["eoq"].copy()

    # ── Alert status KPIs ─────────────────────────────────────
    order_now  = (reorder["AlertStatus"] == "ORDER NOW").sum()
    order_soon = (reorder["AlertStatus"] == "ORDER SOON").sum()
    ok_count   = (reorder["AlertStatus"] == "OK").sum()

    fig_kpis = make_subplots(rows=1, cols=3, specs=[[{"type":"indicator"}]*3])
    fig_kpis.add_trace(_kpi_indicator(order_now,  "ORDER NOW",  suffix=" products"), row=1, col=1)
    fig_kpis.add_trace(_kpi_indicator(order_soon, "ORDER SOON", suffix=" products"), row=1, col=2)
    fig_kpis.add_trace(_kpi_indicator(ok_count,   "Stock OK",   suffix=" products"), row=1, col=3)
    fig_kpis.update_layout(paper_bgcolor=C_BG, plot_bgcolor=C_BG,
                           height=140, margin={"l":10,"r":10,"t":10,"b":10},
                           font={"color": C_TEXT})

    # ── Reorder alert bar ─────────────────────────────────────
    alert_counts = reorder["AlertStatus"].value_counts().reset_index()
    alert_counts.columns = ["Status", "Count"]
    status_colors = {"ORDER NOW": C_RED, "ORDER SOON": C_ORANGE, "OK": C_GREEN}
    fig_alerts = _fig_base("Reorder Alert Status", height=280)
    fig_alerts.add_trace(go.Bar(
        x=alert_counts["Status"],
        y=alert_counts["Count"],
        marker={"color": [status_colors.get(s, C_GREY) for s in alert_counts["Status"]]},
        text=alert_counts["Count"], textposition="outside",
    ))
    fig_alerts.update_layout(showlegend=False, xaxis_title="", yaxis_title="Products")

    # ── Qty on hand vs ROP scatter ────────────────────────────
    merged = reorder.copy()
    merged["Alert_Color"] = merged["AlertStatus"].map(
        {"ORDER NOW": C_RED, "ORDER SOON": C_ORANGE, "OK": C_GREEN}
    )
    fig_scatter = _fig_base("Stock on Hand vs Reorder Point", height=400)
    for status, color in [("ORDER NOW", C_RED), ("ORDER SOON", C_ORANGE), ("OK", C_GREEN)]:
        sub = merged[merged["AlertStatus"] == status]
        fig_scatter.add_trace(go.Scatter(
            x=sub["RecommendedROP"], y=sub["QuantityOnHand"],
            mode="markers", name=status,
            marker={"color": color, "size": 10, "opacity": 0.85},
            hovertext=sub["ProductName"],
            hovertemplate="<b>%{hovertext}</b><br>ROP: %{x:.0f}<br>On Hand: %{y:.0f}<extra></extra>",
        ))
    # Diagonal reference line
    max_val = max(merged["RecommendedROP"].max(), merged["QuantityOnHand"].max())
    fig_scatter.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val], mode="lines",
        line={"dash": "dash", "color": C_SUBTLE, "width": 1},
        name="At ROP", showlegend=True,
    ))
    fig_scatter.update_layout(xaxis_title="Recommended ROP", yaxis_title="Qty On Hand",
                               legend={"x": 0.01, "y": 0.99})

    # ── Top 15 products by EOQ ────────────────────────────────
    top_eoq = eoq.nlargest(15, "RecommendedEOQ").sort_values("RecommendedEOQ")
    fig_eoq = _fig_base("Top 15 Products by Recommended EOQ", height=420)
    fig_eoq.add_trace(go.Bar(
        x=top_eoq["RecommendedEOQ"], y=top_eoq["ProductName"],
        orientation="h", marker={"color": C_BLUE},
        text=top_eoq["RecommendedEOQ"].round(0).astype(int).astype(str),
        textposition="outside",
    ))
    fig_eoq.update_layout(showlegend=False, xaxis_title="EOQ (units)")

    return fig_kpis, fig_alerts, fig_scatter, fig_eoq


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — DEMAND FORECAST
# ═══════════════════════════════════════════════════════════════

def build_forecast(d):
    forecast = d["forecast"].copy()
    evl      = d["eval"].copy()

    # ── Model accuracy KPIs ───────────────────────────────────
    arima_mape = evl[evl["ModelName"] == "ARIMA"]["MAPE"].mean()
    hw_mape    = evl[evl["ModelName"] == "HoltWinters"]["MAPE"].mean()

    fig_kpis = make_subplots(rows=1, cols=2, specs=[[{"type":"indicator"}]*2])
    fig_kpis.add_trace(_kpi_indicator(arima_mape * 100, "ARIMA MAPE", suffix="%"),
                        row=1, col=1)
    fig_kpis.add_trace(_kpi_indicator(hw_mape * 100, "Holt-Winters MAPE", suffix="%"),
                        row=1, col=2)
    fig_kpis.update_layout(paper_bgcolor=C_BG, plot_bgcolor=C_BG,
                           height=140, margin={"l":10,"r":10,"t":10,"b":10},
                           font={"color": C_TEXT})

    # ── Aggregate forecast: total demand by date, both models ─
    forecast["ForecastDate"] = pd.to_datetime(forecast["ForecastDate"])
    daily_agg = (forecast[forecast["HorizonDays"] == 30]
                 .groupby(["ForecastDate", "ModelName"], as_index=False)
                 ["ForecastQty"].sum())

    fig_timeline = _fig_base("Total Forecasted Demand — 30-Day Horizon (All Products)", height=380)
    model_colors = {"ARIMA": C_BLUE, "HoltWinters": C_ORANGE}
    for model in ["ARIMA", "HoltWinters"]:
        sub = daily_agg[daily_agg["ModelName"] == model].sort_values("ForecastDate")
        fig_timeline.add_trace(go.Scatter(
            x=sub["ForecastDate"], y=sub["ForecastQty"],
            mode="lines", name=model,
            line={"color": model_colors[model], "width": 2},
        ))
    fig_timeline.update_layout(xaxis_title="", yaxis_title="Total Units Forecasted",
                                legend={"x": 0.01, "y": 0.99})

    # ── Confidence band for ARIMA (top 5 products by demand) ─
    top5 = (forecast[forecast["ModelName"] == "ARIMA"]
            .groupby("ProductID")["ForecastQty"].sum()
            .nlargest(5).index.tolist())

    fig_band = _fig_base("ARIMA Forecast with Confidence Band — Top 5 Products (30d)", height=380)
    palette = [C_BLUE, C_GREEN, C_ORANGE, C_RED, "#a855f7"]
    for i, pid in enumerate(top5):
        sub = (forecast[(forecast["ProductID"] == pid) &
                        (forecast["ModelName"] == "ARIMA") &
                        (forecast["HorizonDays"] == 30)]
               .sort_values("ForecastDate"))
        name = sub["ProductName"].iloc[0] if len(sub) > 0 else f"P{pid}"
        color = palette[i]
        rgba_fill = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)"
        fig_band.add_trace(go.Scatter(
            x=pd.concat([sub["ForecastDate"], sub["ForecastDate"][::-1]]),
            y=pd.concat([sub["UpperBound"], sub["LowerBound"][::-1]]),
            fill="toself", fillcolor=rgba_fill,
            line={"color": "rgba(0,0,0,0)"}, showlegend=False, hoverinfo="skip",
        ))
        fig_band.add_trace(go.Scatter(
            x=sub["ForecastDate"], y=sub["ForecastQty"],
            mode="lines", name=name, line={"color": color, "width": 2},
        ))
    fig_band.update_layout(xaxis_title="", yaxis_title="Daily Units", legend={"x": 0.01, "y": 0.99})

    # ── Forecast by category (30d, ARIMA) ────────────────────
    cat_fc = (forecast[(forecast["HorizonDays"] == 30) & (forecast["ModelName"] == "ARIMA")]
              .groupby("Category", as_index=False)["ForecastQty"].sum()
              .sort_values("ForecastQty", ascending=True))
    fig_cat = _fig_base("30-Day Forecast Total by Category (ARIMA)", height=320)
    fig_cat.add_trace(go.Bar(
        x=cat_fc["ForecastQty"], y=cat_fc["Category"],
        orientation="h", marker={"color": C_GREEN},
        text=cat_fc["ForecastQty"].round(0).astype(int).astype(str),
        textposition="outside",
    ))
    fig_cat.update_layout(showlegend=False, xaxis_title="Forecasted Units (30d)")

    return fig_kpis, fig_timeline, fig_band, fig_cat


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — ANOMALIES & SUPPLIERS
# ═══════════════════════════════════════════════════════════════

def build_anomaly_supplier(d):
    anomaly  = d["anomaly"].copy()
    supplier = d["supplier"].copy()

    # ── KPIs ──────────────────────────────────────────────────
    total_anomalies = len(anomaly)
    high_anomalies  = (anomaly["Severity"] == "HIGH").sum()
    worst_otd       = supplier["OnTimeDeliveryPct"].min()
    worst_name      = supplier.loc[supplier["OnTimeDeliveryPct"].idxmin(), "SupplierName"]

    fig_kpis = make_subplots(rows=1, cols=3, specs=[[{"type":"indicator"}]*3])
    fig_kpis.add_trace(_kpi_indicator(total_anomalies, "Total Anomalies", suffix=""), row=1, col=1)
    fig_kpis.add_trace(_kpi_indicator(high_anomalies,  "HIGH Severity",   suffix=""), row=1, col=2)
    fig_kpis.add_trace(_kpi_indicator(worst_otd, f"Worst OTD\n({worst_name[:18]})", suffix="%"), row=1, col=3)
    fig_kpis.update_layout(paper_bgcolor=C_BG, plot_bgcolor=C_BG,
                           height=150, margin={"l":10,"r":10,"t":10,"b":10},
                           font={"color": C_TEXT})

    # ── Supplier OTD bar ──────────────────────────────────────
    sup_sorted = supplier.sort_values("OnTimeDeliveryPct")
    bar_colors = [C_RED if v < 25 else C_ORANGE if v < 40 else C_GREEN
                  for v in sup_sorted["OnTimeDeliveryPct"]]
    fig_otd = _fig_base("Supplier On-Time Delivery %", height=440)
    fig_otd.add_trace(go.Bar(
        x=sup_sorted["OnTimeDeliveryPct"],
        y=sup_sorted["SupplierName"],
        orientation="h",
        marker={"color": bar_colors},
        text=sup_sorted["OnTimeDeliveryPct"].astype(str) + "%",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>OTD: %{x:.1f}%<br>Avg Delay: "
                      + sup_sorted["AvgDelayDays"].astype(str) + "d<extra></extra>",
    ))
    fig_otd.update_layout(showlegend=False, xaxis_title="On-Time Delivery %",
                           xaxis_range=[0, 110])

    # ── Anomaly scatter timeline ──────────────────────────────
    anomaly["AnomalyDate"] = pd.to_datetime(anomaly["AnomalyDate"])
    sev_colors = {"HIGH": C_RED, "MEDIUM": C_ORANGE, "LOW": C_SUBTLE}
    fig_scatter = _fig_base("Anomaly Score Timeline", height=380)
    for sev in ["HIGH", "MEDIUM", "LOW"]:
        sub = anomaly[anomaly["Severity"] == sev]
        if len(sub) == 0:
            continue
        fig_scatter.add_trace(go.Scatter(
            x=sub["AnomalyDate"], y=sub["AnomalyScore"],
            mode="markers", name=sev,
            marker={
                "color": sev_colors[sev],
                "size": sub["AnomalyScore"] * 14 + 6,
                "opacity": 0.8,
                "line": {"color": "white", "width": 0.5},
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Date: %{x|%Y-%m-%d}<br>"
                "Score: %{y:.3f}<br>"
                "Feature: %{customdata[1]} = %{customdata[2]:.1f}"
                "<extra></extra>"
            ),
            customdata=sub[["ProductName", "FeatureName", "FeatureValue"]].values,
        ))
    fig_scatter.update_layout(yaxis_title="Anomaly Score", xaxis_title="",
                               legend={"x": 0.01, "y": 0.99})

    # ── Detector donut ────────────────────────────────────────
    det_counts = anomaly["DetectorType"].value_counts()
    fig_det = _fig_base("Anomalies by Detector", height=280)
    fig_det.add_trace(go.Pie(
        labels=det_counts.index, values=det_counts.values,
        hole=0.55,
        marker={"colors": [C_BLUE, C_ORANGE]},
        textinfo="label+percent",
        textfont={"size": 12},
    ))
    fig_det.update_layout(showlegend=False)

    # ── Supplier rating vs OTD scatter ────────────────────────
    fig_rating = _fig_base("Supplier Rating vs On-Time Delivery %", height=320)
    fig_rating.add_trace(go.Scatter(
        x=supplier["Rating"], y=supplier["OnTimeDeliveryPct"],
        mode="markers+text",
        marker={"color": C_BLUE, "size": 14, "opacity": 0.85,
                "line": {"color": "white", "width": 0.5}},
        text=supplier["SupplierName"].str.split().str[0],
        textposition="top center",
        textfont={"size": 9},
        hovertemplate="<b>%{text}</b><br>Rating: %{x}<br>OTD: %{y:.1f}%<extra></extra>",
        hovertext=supplier["SupplierName"],
    ))
    fig_rating.update_layout(xaxis_title="Supplier Rating (1-5)",
                              yaxis_title="On-Time Delivery %")

    return fig_kpis, fig_otd, fig_scatter, fig_det, fig_rating


# ═══════════════════════════════════════════════════════════════
# HTML ASSEMBLY
# ═══════════════════════════════════════════════════════════════

def to_html(fig):
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"displayModeBar": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
    )


def build_dashboard(output_path: Path = None, db_path=DB_PATH, open_browser: bool = True) -> None:
    if output_path is None:
        output_path = _ROOT / "powerbi" / "FlowSight_Dashboard.html"
    print("[dashboard] Loading data...")
    d = load_all(db_path)

    print("[dashboard] Building Page 1: Executive Summary...")
    ex_kpis, ex_rev, ex_cat, ex_turn = build_executive(d)

    print("[dashboard] Building Page 2: Inventory Health...")
    inv_kpis, inv_alerts, inv_scatter, inv_eoq = build_inventory(d)

    print("[dashboard] Building Page 3: Demand Forecast...")
    fc_kpis, fc_timeline, fc_band, fc_cat = build_forecast(d)

    print("[dashboard] Building Page 4: Anomalies & Suppliers...")
    an_kpis, an_otd, an_scatter, an_det, an_rating = build_anomaly_supplier(d)

    print("[dashboard] Assembling HTML...")

    # ── Live banner stats ──────────────────────────────────────
    reorder = d["reorder"]
    anomaly = d["anomaly"]
    stockout = d["stockout"]
    order_now_count  = int((reorder["AlertStatus"] == "ORDER NOW").sum())
    below_rop_count  = int(stockout["BelowReorderPoint"].sum()) if "BelowReorderPoint" in stockout.columns else 0
    total_products   = int(len(stockout))
    anomaly_count    = int(len(anomaly))
    import datetime as _dt
    generated_at = _dt.datetime.now().strftime("%b %d, %Y %H:%M")

    # Fetch Plotly CDN script tag
    plotly_cdn = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'

    def section(title, *figs, cols=2):
        items = ""
        width = f"{100 // cols}%"
        for f in figs:
            items += f'<div style="width:{width};min-width:320px;flex:1;">{to_html(f)}</div>'
        return f"""
        <div class="section-title">{title}</div>
        <div class="row">{items}</div>
        """

    def page(page_id, label, *sections):
        content = "".join(sections)
        return f'<div class="page" id="{page_id}" data-label="{label}">{content}</div>'

    p1 = page("page1", "Executive Summary",
        f'<div style="margin-bottom:8px;">{to_html(ex_kpis)}</div>',
        section("", ex_rev, ex_cat, cols=2),
        section("", ex_turn, cols=1),
    )
    p2 = page("page2", "Inventory Health",
        f'<div style="margin-bottom:8px;">{to_html(inv_kpis)}</div>',
        section("", inv_alerts, inv_scatter, cols=2),
        section("", inv_eoq, cols=1),
    )
    p3 = page("page3", "Demand Forecast",
        f'<div style="margin-bottom:8px;">{to_html(fc_kpis)}</div>',
        section("", fc_timeline, cols=1),
        section("", fc_band, fc_cat, cols=2),
    )
    p4 = page("page4", "Anomalies & Suppliers",
        f'<div style="margin-bottom:8px;">{to_html(an_kpis)}</div>',
        section("", an_otd, an_scatter, cols=2),
        section("", an_det, an_rating, cols=2),
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FlowSight — Supply Chain Intelligence Platform</title>
  {plotly_cdn}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {C_BG};
      color: {C_TEXT};
      font-family: Inter, "Segoe UI", system-ui, sans-serif;
      min-height: 100vh;
    }}
    /* ── Top nav ── */
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: {C_SURFACE};
      border-bottom: 1px solid {C_BORDER};
      padding: 0 28px;
      height: 52px;
      position: sticky; top: 0; z-index: 100;
    }}
    .logo {{
      font-size: 18px;
      font-weight: 700;
      color: {C_BLUE};
      letter-spacing: -0.5px;
    }}
    .logo span {{ color: {C_TEXT}; font-weight: 400; font-size: 13px; margin-left: 8px; }}
    nav {{ display: flex; gap: 4px; }}
    .nav-btn {{
      background: none; border: none;
      color: {C_SUBTLE};
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
    }}
    .nav-btn:hover {{ background: rgba(255,255,255,0.06); color: {C_TEXT}; }}
    .nav-btn.active {{ background: {C_BLUE}; color: #fff; font-weight: 600; }}
    .refresh-time {{ font-size: 11px; color: {C_SUBTLE}; }}
    /* ── Content ── */
    main {{ padding: 20px 24px; max-width: 1600px; margin: 0 auto; }}
    .page {{ display: none; }}
    .page.active {{ display: block; }}
    .section-title {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: {C_SUBTLE};
      margin: 16px 0 6px;
    }}
    .row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 4px;
    }}
    .row > div {{
      background: {C_SURFACE};
      border-radius: 10px;
      border: 1px solid {C_BORDER};
      padding: 4px;
      overflow: hidden;
    }}
    /* ── Alert badge ── */
    .alert-banner {{
      background: rgba(220,53,69,0.15);
      border: 1px solid {C_RED};
      border-radius: 8px;
      padding: 10px 16px;
      font-size: 13px;
      color: {C_RED};
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .alert-banner b {{ font-weight: 700; }}
  </style>
</head>
<body>
<header>
  <div class="logo">FlowSight <span>Supply Chain Intelligence Platform</span></div>
  <nav id="nav"></nav>
  <div class="refresh-time">Data as of {generated_at}</div>
</header>
<main>
  <div class="alert-banner">
    <b>{order_now_count} ORDER NOW</b> reorder alerts active &nbsp;|&nbsp;
    {below_rop_count}/{total_products} products below recommended reorder point &nbsp;|&nbsp;
    {anomaly_count} anomalies detected
  </div>
  {p1}{p2}{p3}{p4}
</main>
<script>
  const pages = document.querySelectorAll('.page');
  const nav   = document.getElementById('nav');

  pages.forEach((page, i) => {{
    const btn = document.createElement('button');
    btn.className = 'nav-btn' + (i === 0 ? ' active' : '');
    btn.textContent = page.dataset.label;
    btn.onclick = () => {{
      pages.forEach(p => p.classList.remove('active'));
      nav.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      page.classList.add('active');
      btn.classList.add('active');
    }};
    nav.appendChild(btn);
  }});

  pages[0].classList.add('active');
</script>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    print(f"[dashboard] Saved -> {output_path}")
    print(f"[dashboard] Size:  {output_path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    import webbrowser
    out = _ROOT / "powerbi" / "FlowSight_Dashboard.html"
    build_dashboard(out, open_browser=True)
    print("[dashboard] Opening in browser...")
    webbrowser.open(out.as_uri())
