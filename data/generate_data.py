"""
Master data generator entry point.
Calls all generators in FK-safe order and returns a dict of DataFrames
keyed by table name, ready for ETL validation and loading.
"""
from typing import Dict

import pandas as pd

from config.settings import RANDOM_SEED
from data.generators.gen_inventory import generate_inventory
from data.generators.gen_orders import generate_orders
from data.generators.gen_products import generate_products
from data.generators.gen_sales import generate_sales
from data.generators.gen_shipments import generate_shipments
from data.generators.gen_suppliers import generate_suppliers


def generate_all(seed: int = RANDOM_SEED) -> Dict[str, pd.DataFrame]:
    """
    Returns:
        Dict mapping table name → DataFrame (7 tables, FK-safe).
    """
    print("[generate_data] Generating Products...")
    products = generate_products(seed=seed)

    print("[generate_data] Generating Suppliers...")
    suppliers = generate_suppliers(seed=seed)

    print("[generate_data] Generating Inventory...")
    inventory = generate_inventory(products_df=products, seed=seed)

    print("[generate_data] Generating Orders + OrderItems...")
    orders, order_items = generate_orders(
        suppliers_df=suppliers, products_df=products, seed=seed
    )

    print("[generate_data] Generating Sales...")
    sales = generate_sales(products_df=products, seed=seed)

    print("[generate_data] Generating Shipments...")
    shipments = generate_shipments(orders_df=orders, suppliers_df=suppliers, seed=seed)

    dataframes = {
        "Products":   products,
        "Suppliers":  suppliers,
        "Inventory":  inventory,
        "Orders":     orders,
        "OrderItems": order_items,
        "Sales":      sales,
        "Shipments":  shipments,
    }

    print("\n[generate_data] Summary:")
    for name, df in dataframes.items():
        print(f"  {name:<15} {len(df):>7,} rows")

    return dataframes


if __name__ == "__main__":
    generate_all()
