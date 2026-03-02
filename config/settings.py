"""
Central configuration for FlowSight.
Every other module imports from here — nothing is hardcoded elsewhere.
"""
import os
from pathlib import Path

# ── Project root (two levels up from this file: config/ → project root)
ROOT_DIR = Path(__file__).resolve().parent.parent

# ── Database
DB_PATH = ROOT_DIR / "db" / "flowsight.db"
DB_URL = "sqlite:///" + str(DB_PATH)

# ── Synthetic data parameters
RANDOM_SEED = 42
START_DATE = "2022-01-01"   # Inclusive
END_DATE = "2023-12-31"     # Inclusive

# ── Data volumes
NUM_PRODUCTS = 50
NUM_SUPPLIERS = 15
NUM_WAREHOUSES = 5

PRODUCT_CATEGORIES = [
    "Electronics",
    "Industrial Parts",
    "Packaging",
    "Raw Materials",
    "Office Supplies",
]

WAREHOUSE_LOCATIONS = [
    "Chicago, IL",
    "Dallas, TX",
    "Los Angeles, CA",
    "Newark, NJ",
    "Atlanta, GA",
]

# ── Inventory thresholds
DEFAULT_SAFETY_STOCK_DAYS = 7   # days of avg demand
REORDER_BUFFER_FACTOR = 1.2     # ROP alert fires at ROP * 1.2 as "ORDER SOON"

# ── Forecasting
FORECAST_HORIZONS = [30, 60, 90]   # days
MAPE_ALERT_THRESHOLD = 0.35        # alert if MAPE > 35%

# ── Anomaly detection
ZSCORE_THRESHOLD = 3.0
ISOLATION_FOREST_CONTAMINATION = 0.05   # top 5% flagged

# ── EOQ / optimization defaults
EOQ_ORDERING_COST = 50.0       # $ per order (flat assumption)
EOQ_HOLDING_COST_PCT = 0.20    # 20% of unit cost per year

# ── Alerts
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "alerts@flowsight.local")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "ops@flowsight.local")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
