-- ============================================================
-- FlowSight – SQLite Schema (Source of Truth)
-- All column names used in generators, ETL, and analytics
-- derive from this file. Do not rename columns here without
-- updating every downstream module.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────
-- CORE PRD TABLES (7)
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Products (
    ProductID        INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName      TEXT    NOT NULL,
    Category         TEXT    NOT NULL,
    UnitCost         REAL    NOT NULL CHECK (UnitCost > 0),
    UnitPrice        REAL    NOT NULL CHECK (UnitPrice > UnitCost),
    SafetyStockLevel INTEGER NOT NULL CHECK (SafetyStockLevel >= 0),
    LeadTimeDays     INTEGER NOT NULL CHECK (LeadTimeDays > 0)
);

CREATE TABLE IF NOT EXISTS Suppliers (
    SupplierID      INTEGER PRIMARY KEY AUTOINCREMENT,
    SupplierName    TEXT    NOT NULL,
    Country         TEXT    NOT NULL,
    AverageLeadTime INTEGER NOT NULL CHECK (AverageLeadTime > 0),
    Rating          REAL    NOT NULL CHECK (Rating BETWEEN 1.0 AND 5.0)
);

CREATE TABLE IF NOT EXISTS Inventory (
    InventoryID       INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductID         INTEGER NOT NULL REFERENCES Products(ProductID),
    WarehouseLocation TEXT    NOT NULL,
    QuantityOnHand    INTEGER NOT NULL CHECK (QuantityOnHand >= 0),
    ReorderPoint      INTEGER NOT NULL CHECK (ReorderPoint >= 0),
    LastUpdated       DATE    NOT NULL
);

CREATE TABLE IF NOT EXISTS Orders (
    OrderID     INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderDate   DATE    NOT NULL,
    SupplierID  INTEGER NOT NULL REFERENCES Suppliers(SupplierID),
    Status      TEXT    NOT NULL CHECK (Status IN ('Pending','In Transit','Delivered','Cancelled')),
    TotalCost   REAL    NOT NULL CHECK (TotalCost >= 0)
);

CREATE TABLE IF NOT EXISTS OrderItems (
    OrderItemID     INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID         INTEGER NOT NULL REFERENCES Orders(OrderID),
    ProductID       INTEGER NOT NULL REFERENCES Products(ProductID),
    QuantityOrdered INTEGER NOT NULL CHECK (QuantityOrdered > 0),
    UnitCost        REAL    NOT NULL CHECK (UnitCost > 0)
);

CREATE TABLE IF NOT EXISTS Sales (
    SaleID       INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductID    INTEGER NOT NULL REFERENCES Products(ProductID),
    SaleDate     DATE    NOT NULL,
    QuantitySold INTEGER NOT NULL CHECK (QuantitySold > 0),
    Revenue      REAL    NOT NULL CHECK (Revenue > 0)
);

CREATE TABLE IF NOT EXISTS Shipments (
    ShipmentID           INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID              INTEGER NOT NULL REFERENCES Orders(OrderID),
    ActualDeliveryDate   DATE    NOT NULL,
    ExpectedDeliveryDate DATE    NOT NULL,
    DelayDays            INTEGER NOT NULL   -- negative = early, positive = late
);

-- ─────────────────────────────────────────────
-- ANALYTICS OUTPUT TABLES (4)
-- Written by Python analytics modules
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Forecasts (
    ForecastID   INTEGER  PRIMARY KEY AUTOINCREMENT,
    ProductID    INTEGER  NOT NULL REFERENCES Products(ProductID),
    ModelName    TEXT     NOT NULL,          -- 'ARIMA' or 'Prophet'
    ForecastDate DATE     NOT NULL,
    ForecastQty  REAL     NOT NULL,
    LowerBound   REAL,
    UpperBound   REAL,
    HorizonDays  INTEGER  NOT NULL,          -- 30, 60, or 90
    GeneratedAt  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Recommendations (
    RecID           INTEGER  PRIMARY KEY AUTOINCREMENT,
    ProductID       INTEGER  NOT NULL REFERENCES Products(ProductID),
    AnnualDemand    REAL     NOT NULL,
    OrderingCost    REAL     NOT NULL,
    HoldingCostPct  REAL     NOT NULL,
    RecommendedEOQ  REAL     NOT NULL,
    RecommendedROP  REAL     NOT NULL,
    SafetyStockQty  REAL     NOT NULL,
    GeneratedAt     DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Anomalies (
    AnomalyID    INTEGER  PRIMARY KEY AUTOINCREMENT,
    ProductID    INTEGER  NOT NULL REFERENCES Products(ProductID),
    DetectorType TEXT     NOT NULL,          -- 'zscore' or 'isolation_forest'
    AnomalyScore REAL     NOT NULL,
    AnomalyDate  DATE     NOT NULL,
    FeatureName  TEXT     NOT NULL,
    FeatureValue REAL     NOT NULL,
    Severity     TEXT     NOT NULL,          -- 'LOW', 'MEDIUM', 'HIGH'
    DetectedAt   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ForecastEvaluation (
    EvalID       INTEGER  PRIMARY KEY AUTOINCREMENT,
    ProductID    INTEGER  NOT NULL REFERENCES Products(ProductID),
    ModelName    TEXT     NOT NULL,
    HorizonDays  INTEGER  NOT NULL,
    MAE          REAL,
    RMSE         REAL,
    MAPE         REAL,
    EvaluatedAt  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
-- INDEXES (performance for analytics queries)
-- ─────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_sales_product   ON Sales(ProductID);
CREATE INDEX IF NOT EXISTS idx_sales_date      ON Sales(SaleDate);
CREATE INDEX IF NOT EXISTS idx_inventory_prod  ON Inventory(ProductID);
CREATE INDEX IF NOT EXISTS idx_shipments_order ON Shipments(OrderID);
CREATE INDEX IF NOT EXISTS idx_orderitems_prod ON OrderItems(ProductID);
CREATE INDEX IF NOT EXISTS idx_forecasts_prod  ON Forecasts(ProductID);
CREATE INDEX IF NOT EXISTS idx_anomalies_prod  ON Anomalies(ProductID);
