"""
Generates Orders and OrderItems tables — 2 years of purchase orders.
Depends on Suppliers (SupplierID FK) and Products (ProductID FK).
Returns a tuple of (orders_df, order_items_df).
"""
from typing import Tuple

import numpy as np
import pandas as pd

from config.settings import END_DATE, RANDOM_SEED, START_DATE

_ITEMS_PER_ORDER_RANGE = (2, 8)       # line items per PO
_ORDERS_PER_MONTH = (8, 20)           # POs created per month
_ORDER_QTY_RANGE = (10, 500)          # units per line item
_STATUSES = ["Delivered", "Delivered", "Delivered", "In Transit", "Pending", "Cancelled"]
# Delivered is weighted 3x to reflect a realistic historical dataset


def generate_orders(
    suppliers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    supplier_ids = suppliers_df["SupplierID"].tolist()
    product_ids = products_df["ProductID"].tolist()
    unit_costs = dict(zip(products_df["ProductID"], products_df["UnitCost"]))

    date_range = pd.date_range(START_DATE, END_DATE, freq="MS")  # monthly starts

    order_records = []
    item_records = []
    order_id = 1
    item_id = 1

    for month_start in date_range:
        # Number of orders this month
        n_orders = int(rng.integers(*_ORDERS_PER_MONTH))

        # Spread orders across the month
        days_in_month = (
            (month_start + pd.offsets.MonthEnd(0)) - month_start
        ).days + 1
        order_days = rng.integers(0, days_in_month, size=n_orders)

        for day_offset in sorted(order_days):
            order_date = month_start + pd.Timedelta(days=int(day_offset))
            if order_date > pd.Timestamp(END_DATE):
                continue

            supplier_id = int(rng.choice(supplier_ids))
            status = str(rng.choice(_STATUSES))
            n_items = int(rng.integers(*_ITEMS_PER_ORDER_RANGE))

            # Pick n_items distinct products for this PO
            selected_products = rng.choice(product_ids, size=n_items, replace=False).tolist()

            total_cost = 0.0
            for prod_id in selected_products:
                qty = int(rng.integers(*_ORDER_QTY_RANGE))
                unit_cost = round(float(unit_costs[prod_id] * rng.uniform(0.90, 1.05)), 2)
                line_total = qty * unit_cost
                total_cost += line_total

                item_records.append({
                    "OrderItemID":    item_id,
                    "OrderID":        order_id,
                    "ProductID":      prod_id,
                    "QuantityOrdered": qty,
                    "UnitCost":       unit_cost,
                })
                item_id += 1

            order_records.append({
                "OrderID":   order_id,
                "OrderDate": order_date.date().isoformat(),
                "SupplierID": supplier_id,
                "Status":    status,
                "TotalCost": round(total_cost, 2),
            })
            order_id += 1

    orders_df = pd.DataFrame(order_records)
    items_df = pd.DataFrame(item_records)
    print(f"[gen_orders] Generated {len(orders_df):,} orders, {len(items_df):,} order items")
    return orders_df, items_df


if __name__ == "__main__":
    from data.generators.gen_products import generate_products
    from data.generators.gen_suppliers import generate_suppliers
    products = generate_products()
    suppliers = generate_suppliers()
    orders, items = generate_orders(suppliers, products)
    print(orders.head())
    print(items.head())
