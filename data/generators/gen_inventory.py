"""
Generates the Inventory table — one row per product.
Depends on Products (ProductID FK).
"""
import numpy as np
import pandas as pd

from config.settings import (
    DEFAULT_SAFETY_STOCK_DAYS,
    END_DATE,
    NUM_WAREHOUSES,
    RANDOM_SEED,
    WAREHOUSE_LOCATIONS,
)


def generate_inventory(
    products_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Args:
        products_df: Output of gen_products.generate_products().
    Returns:
        DataFrame matching the Inventory schema.
    """
    rng = np.random.default_rng(seed)
    records = []

    for idx, row in products_df.iterrows():
        product_id = row["ProductID"]
        safety_stock = row["SafetyStockLevel"]

        # QuantityOnHand: some products are well-stocked, some near reorder
        # Mix of healthy, marginal, and low-stock states for dashboard richness
        stock_multiplier = float(rng.choice(
            [0.3, 0.5, 0.8, 1.2, 2.0, 3.0],
            p=[0.05, 0.10, 0.20, 0.35, 0.20, 0.10],
        ))
        qty_on_hand = max(0, int(safety_stock * stock_multiplier))

        # ReorderPoint = safety_stock + (avg daily demand proxy * lead_time)
        # We approximate avg daily demand as safety_stock / DEFAULT_SAFETY_STOCK_DAYS
        avg_daily = safety_stock / max(DEFAULT_SAFETY_STOCK_DAYS, 1)
        lead_time = int(row["LeadTimeDays"])
        reorder_point = int(safety_stock + avg_daily * lead_time)

        warehouse = WAREHOUSE_LOCATIONS[int(rng.integers(0, NUM_WAREHOUSES))]

        records.append({
            "InventoryID":       idx + 1,
            "ProductID":         product_id,
            "WarehouseLocation": warehouse,
            "QuantityOnHand":    qty_on_hand,
            "ReorderPoint":      reorder_point,
            "LastUpdated":       END_DATE,
        })

    df = pd.DataFrame(records)
    assert len(df) == len(products_df), "Inventory row count must equal product count"
    return df


if __name__ == "__main__":
    from data.generators.gen_products import generate_products
    products = generate_products()
    inv = generate_inventory(products)
    print(inv.to_string())
