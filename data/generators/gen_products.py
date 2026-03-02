"""
Generates the Products table (50 SKUs across 5 categories).
No FK dependencies — build first.
"""
import numpy as np
import pandas as pd

from config.settings import (
    NUM_PRODUCTS,
    PRODUCT_CATEGORIES,
    RANDOM_SEED,
)

# Representative product name templates per category
_PRODUCT_TEMPLATES = {
    "Electronics": [
        "Microcontroller Unit {n}", "RFID Scanner {n}", "Barcode Reader {n}",
        "LED Display Module {n}", "Ethernet Switch {n}", "USB Hub Pro {n}",
        "Wireless Sensor {n}", "Power Supply Unit {n}", "Signal Converter {n}",
        "Touch Panel {n}",
    ],
    "Industrial Parts": [
        "Hydraulic Pump {n}", "Ball Bearing {n}", "Drive Shaft {n}",
        "Conveyor Belt {n}", "Gear Assembly {n}", "Valve Controller {n}",
        "Pneumatic Cylinder {n}", "Coupling Flange {n}", "Torque Sensor {n}",
        "Filter Housing {n}",
    ],
    "Packaging": [
        "Stretch Wrap Film {n}", "Cardboard Box {n}", "Bubble Wrap Roll {n}",
        "Shrink Sleeve {n}", "Pallet Wrap {n}", "Foam Insert {n}",
        "Corrugated Sheet {n}", "Tape Dispenser {n}", "Poly Bag {n}",
        "Label Stock {n}",
    ],
    "Raw Materials": [
        "Aluminum Sheet {n}", "Steel Rod {n}", "Copper Wire {n}",
        "PVC Pellets {n}", "Carbon Fiber Spool {n}", "Resin Block {n}",
        "Rubber Compound {n}", "Zinc Ingot {n}", "Titanium Powder {n}",
        "Silicone Sheet {n}",
    ],
    "Office Supplies": [
        "Thermal Paper Roll {n}", "Printer Cartridge {n}", "Staple Pack {n}",
        "File Folder {n}", "Desk Organizer {n}", "Whiteboard Marker {n}",
        "Binding Comb {n}", "Sticky Note Pad {n}", "Correction Tape {n}",
        "Index Card Pack {n}",
    ],
}

# Cost ranges per category (min, max) in USD
_COST_RANGES = {
    "Electronics":     (15.0,  350.0),
    "Industrial Parts": (5.0,  120.0),
    "Packaging":       (0.50,   12.0),
    "Raw Materials":   (2.0,    80.0),
    "Office Supplies": (0.30,    8.0),
}

# Margin range (markup over cost, e.g. 0.25 → price = cost * 1.25)
_MARGIN_RANGE = (0.20, 0.65)

# Safety stock in units (days × avg daily demand — set conservatively here)
_SAFETY_STOCK_RANGE = (10, 200)

# Lead time in days
_LEAD_TIME_RANGE = (3, 30)


def generate_products(seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    products_per_category = NUM_PRODUCTS // len(PRODUCT_CATEGORIES)
    records = []
    product_id = 1

    for category in PRODUCT_CATEGORIES:
        templates = _PRODUCT_TEMPLATES[category]
        cost_min, cost_max = _COST_RANGES[category]

        for i in range(products_per_category):
            template = templates[i % len(templates)]
            name = template.format(n=f"v{i + 1:02d}")

            unit_cost = round(float(rng.uniform(cost_min, cost_max)), 2)
            margin = float(rng.uniform(*_MARGIN_RANGE))
            unit_price = round(unit_cost * (1 + margin), 2)
            safety_stock = int(rng.integers(*_SAFETY_STOCK_RANGE))
            lead_time = int(rng.integers(*_LEAD_TIME_RANGE))

            records.append({
                "ProductID":        product_id,
                "ProductName":      name,
                "Category":         category,
                "UnitCost":         unit_cost,
                "UnitPrice":        unit_price,
                "SafetyStockLevel": safety_stock,
                "LeadTimeDays":     lead_time,
            })
            product_id += 1

    df = pd.DataFrame(records)
    assert len(df) == NUM_PRODUCTS, f"Expected {NUM_PRODUCTS} products, got {len(df)}"
    return df


if __name__ == "__main__":
    df = generate_products()
    print(df.to_string())
