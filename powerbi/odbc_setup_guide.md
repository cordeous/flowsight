# FlowSight — Power BI Connection Guide

Two connection methods are available. **Method A (CSV)** works immediately
with no extra drivers. **Method B (ODBC)** gives live refresh from SQLite.

---

## Method A — CSV Import (Fastest, works right now)

All 8 views are pre-exported to CSV every time you run `python scripts/run_all.py`.
The files are in `powerbi/data_export/`.

### Steps

1. Open **Power BI Desktop**
2. **Home > Get Data > Text/CSV**
3. Import each of the 8 files below in sequence:

| File | Rows | Description |
|------|------|-------------|
| `vw_sales_trend.csv` | 1,200 | Monthly revenue + units by product/category |
| `vw_kpi_inventory_turnover.csv` | 1,200 | Inventory turnover ratio by product/month |
| `vw_kpi_stockout.csv` | 50 | Current stockout status per product |
| `vw_supplier_performance.csv` | 15 | OTD%, avg delay per supplier |
| `vw_demand_forecast.csv` | 17,800 | ARIMA + Holt-Winters forecasts (30/60/90d) |
| `vw_reorder_alerts.csv` | 50 | ORDER NOW / ORDER SOON / OK per product |
| `vw_eoq_recommendations.csv` | 50 | EOQ + ROP per product |
| `vw_anomaly_summary.csv` | 118 | Anomaly scores + severity |

4. For each file: click **Load** (no transformation needed — columns and types are clean)
5. The 8 tables will appear in the **Fields** pane on the right

### Refresh after re-running the pipeline

```bash
python scripts/run_all.py        # regenerates DB + CSVs
```

Then in Power BI: **Home > Refresh** (or Ctrl+Alt+F5) to reload the CSVs.

---

## Method B — Live ODBC Connection (Recommended for production)

This method connects Power BI directly to `flowsight.db` via ODBC.
After setup, refreshing Power BI automatically reads the latest data.

### Step 1 — Install SQLite ODBC Driver

1. Go to: http://www.ch-werner.de/sqliteodbc/
2. Download **sqliteodbc_w64.exe** (64-bit Windows installer)
3. Run the installer — accept all defaults
4. Verify in **Start > ODBC Data Sources (64-bit)** > Drivers tab:
   - You should see **SQLite3 ODBC Driver** in the list

### Step 2 — Create a System DSN

1. Open **Start > ODBC Data Sources (64-bit)** (search for "ODBC")
2. Click the **System DSN** tab
3. Click **Add...**
4. Select **SQLite3 ODBC Driver** > click **Finish**
5. Fill in the dialog:

```
Data Source Name:  FlowSight
Description:       FlowSight Supply Chain DB
Database Name:     C:\Users\antoj\OneDrive\Desktop\projects\sql\db\flowsight.db
```

6. Click **OK**

> **Note:** Use the exact path above. Do not use a relative path.

### Step 3 — Connect Power BI

1. Open **Power BI Desktop**
2. **Home > Get Data > More... > Other > ODBC**
3. In the dropdown select **FlowSight** DSN
4. Click **OK** (no username/password needed)
5. In the Navigator, expand the **FlowSight** node
6. You will see all tables and views. Select these 8 views:
   - `vw_anomaly_summary`
   - `vw_demand_forecast`
   - `vw_eoq_recommendations`
   - `vw_kpi_inventory_turnover`
   - `vw_kpi_stockout`
   - `vw_reorder_alerts`
   - `vw_sales_trend`
   - `vw_supplier_performance`
7. Click **Load**
8. Choose **Import** mode (NOT DirectQuery — SQLite DirectQuery is very slow)

---

## Relationships to Create

After importing, set these relationships in **Model view** (click the relationship icon):

| From Table | From Column | To Table | To Column | Cardinality |
|-----------|-------------|----------|-----------|-------------|
| vw_sales_trend | ProductID | vw_kpi_stockout | ProductID | Many:1 |
| vw_sales_trend | ProductID | vw_eoq_recommendations | ProductID | Many:1 |
| vw_demand_forecast | ProductID | vw_kpi_stockout | ProductID | Many:1 |
| vw_anomaly_summary | ProductID | vw_kpi_stockout | ProductID | Many:1 |
| vw_reorder_alerts | ProductID | vw_eoq_recommendations | ProductID | 1:1 |

> **Tip:** `vw_kpi_stockout` and `vw_eoq_recommendations` each have one row per
> product, making them natural dimension tables for product-level filtering.

---

## Dashboard Pages — Build Order

### Page 1: Executive Summary

**Visuals:**

| Visual | Type | Fields |
|--------|------|--------|
| Total Revenue | KPI Card | `vw_sales_trend[TotalRevenue]` SUM |
| Stockout Rate | KPI Card | `vw_kpi_stockout[IsStockout]` AVERAGE (= %) |
| Avg Supplier OTD | KPI Card | `vw_supplier_performance[OnTimeDeliveryPct]` AVERAGE |
| Revenue by Month | Line Chart | X: `YearMonth`, Y: `TotalRevenue` SUM |
| Revenue by Category | Donut | Legend: `Category`, Values: `TotalRevenue` SUM |
| Inventory Turnover | Bar Chart | Y: `ProductName`, X: `InventoryTurnoverRatio` AVERAGE |

**Slicers:** `Category`, `YearMonth`

---

### Page 2: Inventory Health

**Visuals:**

| Visual | Type | Fields |
|--------|------|--------|
| Reorder Alert Matrix | Table | `ProductName`, `QuantityOnHand`, `RecommendedROP`, `AlertStatus` |
| Alert Status | Bar Chart (stacked) | X: `AlertStatus`, Y: COUNT of ProductID |
| Stock vs ROP | Scatter | X: `RecommendedROP`, Y: `QuantityOnHand`, Details: `ProductName` |
| Stockout by Category | Bar | X: `Category`, Y: `IsStockout` SUM |
| EOQ Recommendations | Table | `ProductName`, `RecommendedEOQ`, `AnnualDemand`, `UnitCost` |

**Conditional formatting on Alert Matrix:**
- `AlertStatus = "ORDER NOW"` → Red background (#dc3545)
- `AlertStatus = "ORDER SOON"` → Orange background (#fd7e14)
- `AlertStatus = "OK"` → Green background (#198754)

**Slicers:** `Category`, `AlertStatus`

---

### Page 3: Demand Forecast

**Visuals:**

| Visual | Type | Fields |
|--------|------|--------|
| Forecast vs Horizon | Line Chart | X: `ForecastDate`, Y: `ForecastQty` SUM, Legend: `ModelName` |
| Confidence Band | Area Chart | X: `ForecastDate`, Y: `LowerBound`/`UpperBound` SUM |
| ARIMA vs HoltWinters MAPE | Bar | Use ForecastEvaluation table directly: `ModelName` vs `MAPE` AVG |
| Forecast by Category | Bar | X: `Category`, Y: `ForecastQty` SUM, filtered to HorizonDays=30 |

**Slicers:** `ProductName`, `HorizonDays` (30 / 60 / 90), `ModelName`

**DAX Measure for MAPE display:**
```
Avg MAPE % =
AVERAGE(vw_demand_forecast[ForecastQty]) -- placeholder
-- Connect ForecastEvaluation table via ODBC/CSV and use its MAPE column directly
```

---

### Page 4: Anomalies & Suppliers

**Visuals:**

| Visual | Type | Fields |
|--------|------|--------|
| Supplier OTD % | Bar Chart | Y: `SupplierName`, X: `OnTimeDeliveryPct` |
| Delay Heatmap | Matrix | Rows: `SupplierName`, Cols: Month (derive from Orders), Values: `AvgDelayDays` |
| Anomaly Timeline | Scatter | X: `AnomalyDate`, Y: `AnomalyScore`, Color: `Severity`, Size: `AnomalyScore` |
| Anomaly by Detector | Donut | Legend: `DetectorType`, Values: COUNT of AnomalyID |
| High-severity Table | Table | `ProductName`, `DetectorType`, `FeatureName`, `AnomalyScore`, `Severity` filtered to HIGH |
| Supplier Rating vs OTD | Scatter | X: `Rating`, Y: `OnTimeDeliveryPct`, Details: `SupplierName` |

**Conditional formatting on Anomaly Table:**
- `Severity = "HIGH"` → Red text (#dc3545)
- `Severity = "MEDIUM"` → Orange text (#fd7e14)

**Slicers:** `DetectorType`, `Severity`, `Category`

---

## Useful DAX Measures

Create these in a **Measures** table (New Table > empty, then add measures):

```dax
-- Overall stockout rate
Stockout Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(vw_kpi_stockout), vw_kpi_stockout[IsStockout] = 1),
    COUNTROWS(vw_kpi_stockout)
) * 100

-- Products needing immediate order
Critical Reorders =
CALCULATE(
    COUNTROWS(vw_reorder_alerts),
    vw_reorder_alerts[AlertStatus] = "ORDER NOW"
)

-- Average inventory turnover (current period)
Avg Turnover = AVERAGE(vw_kpi_inventory_turnover[InventoryTurnoverRatio])

-- Total forecasted demand (30-day)
Forecast 30d Total =
CALCULATE(
    SUM(vw_demand_forecast[ForecastQty]),
    vw_demand_forecast[HorizonDays] = 30,
    vw_demand_forecast[ModelName] = "ARIMA"
)

-- Supplier OTD fleet average
Fleet OTD % = AVERAGE(vw_supplier_performance[OnTimeDeliveryPct])

-- High anomaly count
High Anomalies =
CALCULATE(
    COUNTROWS(vw_anomaly_summary),
    vw_anomaly_summary[Severity] = "HIGH"
)
```

---

## Refreshing Data

Whenever you want updated data in Power BI:

```bash
# 1. Re-run the pipeline (from project root)
python scripts/run_all.py

# 2. If using CSV method: this also re-exports the CSVs automatically
#    Then click Refresh in Power BI Desktop

# 3. If using ODBC method: just click Refresh in Power BI Desktop
#    (it reads directly from the updated flowsight.db)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ODBC DSN not in Power BI list | Ensure you created a **System DSN** (not User DSN) and Power BI is 64-bit |
| `flowsight.db` not found | Check the full path in DSN matches `C:\Users\antoj\OneDrive\Desktop\projects\sql\db\flowsight.db` |
| Views show 0 rows | Re-run `python scripts/run_all.py` to populate the DB |
| `vw_reorder_alerts` empty | Recommendations table must be populated first (Phase 3) |
| Relationship error | Ensure `ProductID` columns are Integer type in Power BI — set in Transform Data |
| CSV refresh not updating | Delete and re-import CSVs, or use ODBC method for automatic refresh |
