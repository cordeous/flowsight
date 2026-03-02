"""
Generates the Shipments table — one shipment per 'Delivered' or 'In Transit' order.
Delays follow a Gamma distribution (realistic: mostly on-time, occasional large delays).
DelayDays is computed here and passed through; transformers.py confirms it.
Depends on Orders (OrderID FK) and Suppliers (AverageLeadTime).
"""
import numpy as np
import pandas as pd

from config.settings import RANDOM_SEED

# Gamma params for delay offset around expected: shape=2, scale=1 → mean=2 days late
_DELAY_GAMMA_SHAPE = 2.0
_DELAY_GAMMA_SCALE = 1.5
_EARLY_PROB = 0.30   # 30% of shipments arrive early (negative delay)
_EARLY_MAX = -5      # earliest possible: 5 days before expected


def generate_shipments(
    orders_df: pd.DataFrame,
    suppliers_df: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Args:
        orders_df:    Output of gen_orders.generate_orders() [0].
        suppliers_df: Output of gen_suppliers.generate_suppliers().
    Returns:
        DataFrame matching the Shipments schema.
    """
    rng = np.random.default_rng(seed)
    lead_times = dict(zip(suppliers_df["SupplierID"], suppliers_df["AverageLeadTime"]))

    # Only create shipments for non-Cancelled, non-Pending orders
    eligible = orders_df[orders_df["Status"].isin(["Delivered", "In Transit"])].copy()

    records = []
    for shipment_id, (_, order) in enumerate(eligible.iterrows(), start=1):
        order_id = int(order["OrderID"])
        supplier_id = int(order["SupplierID"])
        order_date = pd.Timestamp(order["OrderDate"])

        avg_lead = lead_times.get(supplier_id, 14)

        # Expected delivery = order date + supplier average lead time
        expected_delivery = order_date + pd.Timedelta(days=avg_lead)

        # Actual delay: Gamma-distributed positive delay, sometimes early
        if rng.random() < _EARLY_PROB:
            delay_days = int(rng.integers(_EARLY_MAX, 0))
        else:
            delay_days = int(np.ceil(rng.gamma(_DELAY_GAMMA_SHAPE, _DELAY_GAMMA_SCALE)))

        actual_delivery = expected_delivery + pd.Timedelta(days=delay_days)

        records.append({
            "ShipmentID":           shipment_id,
            "OrderID":              order_id,
            "ActualDeliveryDate":   actual_delivery.date().isoformat(),
            "ExpectedDeliveryDate": expected_delivery.date().isoformat(),
            "DelayDays":            delay_days,
        })

    df = pd.DataFrame(records)
    print(f"[gen_shipments] Generated {len(df):,} shipments "
          f"(avg delay: {df['DelayDays'].mean():.1f} days)")
    return df


if __name__ == "__main__":
    from data.generators.gen_orders import generate_orders
    from data.generators.gen_products import generate_products
    from data.generators.gen_suppliers import generate_suppliers
    products = generate_products()
    suppliers = generate_suppliers()
    orders, _ = generate_orders(suppliers, products)
    shipments = generate_shipments(orders, suppliers)
    print(shipments.head())
    print(shipments["DelayDays"].describe())
