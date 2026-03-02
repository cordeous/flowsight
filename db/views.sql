-- ============================================================
-- FlowSight – Power BI Facing Views (8)
-- All views use DROP VIEW IF EXISTS for idempotent re-runs.
-- Run AFTER all tables are populated.
-- ============================================================

-- ─── View 1: Inventory Turnover by Product & Month ───────────
DROP VIEW IF EXISTS vw_kpi_inventory_turnover;
CREATE VIEW vw_kpi_inventory_turnover AS
SELECT
    p.ProductID,
    p.ProductName,
    p.Category,
    strftime('%Y-%m', s.SaleDate)                   AS YearMonth,
    SUM(s.QuantitySold * p.UnitCost)                AS COGS,
    i.QuantityOnHand * p.UnitCost                   AS CurrentInventoryValue,
    ROUND(
        SUM(s.QuantitySold * p.UnitCost)
        / NULLIF(i.QuantityOnHand * p.UnitCost, 0)
    , 2)                                             AS InventoryTurnoverRatio
FROM Sales s
JOIN Products  p ON s.ProductID = p.ProductID
JOIN Inventory i ON i.ProductID = p.ProductID
GROUP BY p.ProductID, strftime('%Y-%m', s.SaleDate);

-- ─── View 2: Stockout Status per Product ─────────────────────
DROP VIEW IF EXISTS vw_kpi_stockout;
CREATE VIEW vw_kpi_stockout AS
SELECT
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SafetyStockLevel,
    i.QuantityOnHand,
    i.ReorderPoint,
    CASE WHEN i.QuantityOnHand < p.SafetyStockLevel THEN 1 ELSE 0 END AS IsStockout,
    CASE WHEN i.QuantityOnHand < i.ReorderPoint     THEN 1 ELSE 0 END AS BelowReorderPoint,
    i.LastUpdated
FROM Inventory i
JOIN Products p ON i.ProductID = p.ProductID;

-- ─── View 3: Supplier Performance ────────────────────────────
DROP VIEW IF EXISTS vw_supplier_performance;
CREATE VIEW vw_supplier_performance AS
SELECT
    sup.SupplierID,
    sup.SupplierName,
    sup.Country,
    sup.Rating,
    COUNT(sh.ShipmentID)                                        AS TotalShipments,
    SUM(CASE WHEN sh.DelayDays <= 0 THEN 1 ELSE 0 END)         AS OnTimeShipments,
    ROUND(
        100.0 * SUM(CASE WHEN sh.DelayDays <= 0 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.ShipmentID), 0)
    , 1)                                                        AS OnTimeDeliveryPct,
    ROUND(AVG(sh.DelayDays), 1)                                 AS AvgDelayDays,
    MAX(sh.DelayDays)                                           AS MaxDelayDays,
    MIN(sh.DelayDays)                                           AS MinDelayDays
FROM Suppliers sup
JOIN Orders    o  ON sup.SupplierID = o.SupplierID
JOIN Shipments sh ON o.OrderID      = sh.OrderID
GROUP BY sup.SupplierID;

-- ─── View 4: Demand Forecast (joined to product info) ────────
DROP VIEW IF EXISTS vw_demand_forecast;
CREATE VIEW vw_demand_forecast AS
SELECT
    f.ForecastID,
    f.ProductID,
    p.ProductName,
    p.Category,
    f.ModelName,
    f.ForecastDate,
    f.ForecastQty,
    f.LowerBound,
    f.UpperBound,
    f.HorizonDays,
    f.GeneratedAt
FROM Forecasts f
JOIN Products p ON f.ProductID = p.ProductID;

-- ─── View 5: Reorder Alerts ───────────────────────────────────
DROP VIEW IF EXISTS vw_reorder_alerts;
CREATE VIEW vw_reorder_alerts AS
SELECT
    p.ProductID,
    p.ProductName,
    p.Category,
    i.QuantityOnHand,
    i.ReorderPoint                  AS CurrentROP,
    r.RecommendedROP,
    r.RecommendedEOQ,
    p.LeadTimeDays,
    CASE
        WHEN i.QuantityOnHand <= r.RecommendedROP       THEN 'ORDER NOW'
        WHEN i.QuantityOnHand <= r.RecommendedROP * 1.2 THEN 'ORDER SOON'
        ELSE 'OK'
    END                             AS AlertStatus
FROM Inventory i
JOIN Products       p ON i.ProductID = p.ProductID
JOIN Recommendations r ON r.ProductID = p.ProductID;

-- ─── View 6: EOQ Recommendations ─────────────────────────────
DROP VIEW IF EXISTS vw_eoq_recommendations;
CREATE VIEW vw_eoq_recommendations AS
SELECT
    r.RecID,
    r.ProductID,
    p.ProductName,
    p.Category,
    p.UnitCost,
    r.AnnualDemand,
    r.OrderingCost,
    r.HoldingCostPct,
    r.RecommendedEOQ,
    r.RecommendedROP,
    r.SafetyStockQty,
    r.GeneratedAt
FROM Recommendations r
JOIN Products p ON r.ProductID = p.ProductID;

-- ─── View 7: Anomaly Summary ──────────────────────────────────
DROP VIEW IF EXISTS vw_anomaly_summary;
CREATE VIEW vw_anomaly_summary AS
SELECT
    a.AnomalyID,
    a.ProductID,
    p.ProductName,
    p.Category,
    a.DetectorType,
    a.AnomalyScore,
    a.AnomalyDate,
    a.FeatureName,
    a.FeatureValue,
    a.Severity,
    a.DetectedAt
FROM Anomalies a
JOIN Products p ON a.ProductID = p.ProductID
ORDER BY a.AnomalyScore DESC;

-- ─── View 8: Sales Trend (Monthly & Weekly aggregates) ───────
DROP VIEW IF EXISTS vw_sales_trend;
CREATE VIEW vw_sales_trend AS
SELECT
    p.ProductID,
    p.ProductName,
    p.Category,
    strftime('%Y-%m', s.SaleDate)     AS YearMonth,
    strftime('%Y-W%W', s.SaleDate)    AS YearWeek,
    SUM(s.QuantitySold)               AS TotalUnitsSold,
    SUM(s.Revenue)                    AS TotalRevenue,
    ROUND(AVG(s.QuantitySold), 2)     AS AvgDailySales,
    COUNT(s.SaleID)                   AS SaleDays
FROM Sales s
JOIN Products p ON s.ProductID = p.ProductID
GROUP BY p.ProductID, strftime('%Y-%m', s.SaleDate);
