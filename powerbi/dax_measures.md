# FlowSight — DAX Measures Reference

All measures below should be created in a dedicated **Measures** table in Power BI.
To create the table: **Modeling > New Table > `Measures = {}`**, then add each measure.

---

## Executive KPIs

```dax
Total Revenue =
SUM(vw_sales_trend[TotalRevenue])

Total Units Sold =
SUM(vw_sales_trend[TotalUnitsSold])

Avg Daily Sales =
AVERAGE(vw_sales_trend[AvgDailySales])

Revenue MoM Change % =
VAR CurrentMonth = MAX(vw_sales_trend[YearMonth])
VAR PrevMonthRev =
    CALCULATE(
        SUM(vw_sales_trend[TotalRevenue]),
        vw_sales_trend[YearMonth] = FORMAT(DATEADD(DATE(LEFT(CurrentMonth,4), RIGHT(CurrentMonth,2), 1), -1, MONTH), "YYYY-MM")
    )
VAR CurrentRev = CALCULATE(SUM(vw_sales_trend[TotalRevenue]), vw_sales_trend[YearMonth] = CurrentMonth)
RETURN
    DIVIDE(CurrentRev - PrevMonthRev, PrevMonthRev) * 100
```

---

## Inventory KPIs

```dax
Stockout Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(vw_kpi_stockout), vw_kpi_stockout[IsStockout] = 1),
    COUNTROWS(vw_kpi_stockout)
) * 100

Below Reorder Point Count =
CALCULATE(
    COUNTROWS(vw_kpi_stockout),
    vw_kpi_stockout[BelowReorderPoint] = 1
)

Avg Inventory Turnover =
AVERAGEX(
    vw_kpi_inventory_turnover,
    vw_kpi_inventory_turnover[InventoryTurnoverRatio]
)

Total Inventory Value =
SUMX(
    vw_kpi_inventory_turnover,
    vw_kpi_inventory_turnover[CurrentInventoryValue]
)

Critical Reorders =
CALCULATE(
    COUNTROWS(vw_reorder_alerts),
    vw_reorder_alerts[AlertStatus] = "ORDER NOW"
)

Order Soon Count =
CALCULATE(
    COUNTROWS(vw_reorder_alerts),
    vw_reorder_alerts[AlertStatus] = "ORDER SOON"
)
```

---

## Supplier KPIs

```dax
Fleet OTD % =
AVERAGE(vw_supplier_performance[OnTimeDeliveryPct])

Fleet Avg Delay Days =
AVERAGE(vw_supplier_performance[AvgDelayDays])

Worst Supplier OTD =
MIN(vw_supplier_performance[OnTimeDeliveryPct])

Best Supplier OTD =
MAX(vw_supplier_performance[OnTimeDeliveryPct])

Suppliers Below 50% OTD =
CALCULATE(
    COUNTROWS(vw_supplier_performance),
    vw_supplier_performance[OnTimeDeliveryPct] < 50
)

Avg Supplier Rating =
AVERAGE(vw_supplier_performance[Rating])
```

---

## Forecasting KPIs

```dax
-- ARIMA 30-day total forecast (use as forward-looking demand signal)
ARIMA Forecast 30d =
CALCULATE(
    SUM(vw_demand_forecast[ForecastQty]),
    vw_demand_forecast[ModelName] = "ARIMA",
    vw_demand_forecast[HorizonDays] = 30
)

-- HoltWinters 30-day forecast
HW Forecast 30d =
CALCULATE(
    SUM(vw_demand_forecast[ForecastQty]),
    vw_demand_forecast[ModelName] = "HoltWinters",
    vw_demand_forecast[HorizonDays] = 30
)

-- Forecast confidence band width (proxy for uncertainty)
Forecast Uncertainty =
AVERAGE(vw_demand_forecast[UpperBound]) - AVERAGE(vw_demand_forecast[LowerBound])

-- Products with forecast data
Forecasted Products =
DISTINCTCOUNT(vw_demand_forecast[ProductID])
```

---

## Anomaly KPIs

```dax
Total Anomalies =
COUNTROWS(vw_anomaly_summary)

High Anomalies =
CALCULATE(
    COUNTROWS(vw_anomaly_summary),
    vw_anomaly_summary[Severity] = "HIGH"
)

Medium Anomalies =
CALCULATE(
    COUNTROWS(vw_anomaly_summary),
    vw_anomaly_summary[Severity] = "MEDIUM"
)

Anomaly Rate % =
DIVIDE([Total Anomalies], DISTINCTCOUNT(vw_anomaly_summary[ProductID])) * 100

Avg Anomaly Score =
AVERAGE(vw_anomaly_summary[AnomalyScore])

ZScore Anomalies =
CALCULATE(
    COUNTROWS(vw_anomaly_summary),
    vw_anomaly_summary[DetectorType] = "zscore"
)

IsoForest Anomalies =
CALCULATE(
    COUNTROWS(vw_anomaly_summary),
    vw_anomaly_summary[DetectorType] = "isolation_forest"
)
```

---

## Optimization KPIs

```dax
Total Recommended EOQ =
SUM(vw_eoq_recommendations[RecommendedEOQ])

Avg EOQ =
AVERAGE(vw_eoq_recommendations[RecommendedEOQ])

Total Annual Demand =
SUM(vw_eoq_recommendations[AnnualDemand])

Avg Safety Stock =
AVERAGE(vw_eoq_recommendations[SafetyStockQty])
```

---

## Conditional Formatting Rules

Apply these in **Format > Conditional formatting** on table visuals:

### Reorder Alert Status (Background Color)
```
Rules:
  AlertStatus = "ORDER NOW"  → #dc3545 (red),   white text
  AlertStatus = "ORDER SOON" → #fd7e14 (orange), white text
  AlertStatus = "OK"         → #198754 (green),  white text
```

### Anomaly Severity (Font Color)
```
Rules:
  Severity = "HIGH"   → #dc3545 (red)
  Severity = "MEDIUM" → #fd7e14 (orange)
  Severity = "LOW"    → #6c757d (grey)
```

### Inventory Turnover (Background Color — diverging)
```
Field: InventoryTurnoverRatio
  Low value  → #dc3545 (red)    — slow-moving inventory
  Mid value  → #ffffff (white)
  High value → #198754 (green)  — fast-moving inventory
```

### OTD % (Background Color)
```
Field: OnTimeDeliveryPct
  < 25%  → #dc3545 (red)
  25-50% → #fd7e14 (orange)
  > 50%  → #198754 (green)
```

---

## Slicer Recommendations

| Page | Slicers |
|------|---------|
| Executive Summary | Category, YearMonth |
| Inventory Health | Category, AlertStatus |
| Demand Forecast | ProductName, HorizonDays (30/60/90), ModelName |
| Anomalies & Suppliers | DetectorType, Severity, Category |

---

## Data Types to Set in Power Query

Open **Transform Data** and set these types explicitly:

| Table | Column | Type |
|-------|--------|------|
| vw_kpi_stockout | IsStockout, BelowReorderPoint | Whole Number |
| vw_demand_forecast | ForecastDate | Date |
| vw_anomaly_summary | AnomalyDate | Date |
| vw_sales_trend | YearMonth | Text (keep as YYYY-MM string) |
| vw_supplier_performance | OnTimeDeliveryPct, AvgDelayDays | Decimal Number |
| vw_eoq_recommendations | RecommendedEOQ, RecommendedROP | Decimal Number |
