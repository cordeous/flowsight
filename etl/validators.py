"""
Validates DataFrames before DB insertion.
Raises ValueError with a descriptive message on any failure.
All checks are in-memory (no DB connection needed).
"""
from typing import Dict

import pandas as pd


def _check_no_nulls(df: pd.DataFrame, table: str, columns: list) -> None:
    for col in columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            raise ValueError(
                f"[validator] {table}.{col} has {null_count} null values"
            )


def _check_positive(df: pd.DataFrame, table: str, columns: list) -> None:
    for col in columns:
        bad = (df[col] <= 0).sum()
        if bad > 0:
            raise ValueError(
                f"[validator] {table}.{col} has {bad} non-positive values"
            )


def _check_fk(
    child_df: pd.DataFrame,
    child_col: str,
    parent_df: pd.DataFrame,
    parent_col: str,
    child_table: str,
    parent_table: str,
) -> None:
    orphans = ~child_df[child_col].isin(parent_df[parent_col])
    count = orphans.sum()
    if count > 0:
        raise ValueError(
            f"[validator] {child_table}.{child_col} has {count} orphan FK "
            f"references not found in {parent_table}.{parent_col}"
        )


def validate_all(dataframes: Dict[str, pd.DataFrame]) -> None:
    """
    Runs all validation checks. Raises ValueError on first failure.
    """
    products  = dataframes["Products"]
    suppliers = dataframes["Suppliers"]
    inventory = dataframes["Inventory"]
    orders    = dataframes["Orders"]
    items     = dataframes["OrderItems"]
    sales     = dataframes["Sales"]
    shipments = dataframes["Shipments"]

    # ── Products ──────────────────────────────────────────────
    _check_no_nulls(products, "Products",
        ["ProductID", "ProductName", "Category", "UnitCost", "UnitPrice"])
    _check_positive(products, "Products", ["UnitCost", "UnitPrice", "LeadTimeDays"])
    price_below_cost = (products["UnitPrice"] <= products["UnitCost"]).sum()
    if price_below_cost > 0:
        raise ValueError(
            f"[validator] Products: {price_below_cost} rows have UnitPrice <= UnitCost"
        )

    # ── Suppliers ─────────────────────────────────────────────
    _check_no_nulls(suppliers, "Suppliers",
        ["SupplierID", "SupplierName", "Country", "AverageLeadTime", "Rating"])
    bad_rating = ((suppliers["Rating"] < 1.0) | (suppliers["Rating"] > 5.0)).sum()
    if bad_rating > 0:
        raise ValueError(f"[validator] Suppliers: {bad_rating} Rating values out of [1,5]")

    # ── Inventory ─────────────────────────────────────────────
    _check_no_nulls(inventory, "Inventory",
        ["InventoryID", "ProductID", "QuantityOnHand", "ReorderPoint"])
    _check_fk(inventory, "ProductID", products, "ProductID", "Inventory", "Products")
    negative_qty = (inventory["QuantityOnHand"] < 0).sum()
    if negative_qty > 0:
        raise ValueError(f"[validator] Inventory: {negative_qty} negative QuantityOnHand values")

    # ── Orders ────────────────────────────────────────────────
    _check_no_nulls(orders, "Orders", ["OrderID", "OrderDate", "SupplierID", "Status"])
    _check_fk(orders, "SupplierID", suppliers, "SupplierID", "Orders", "Suppliers")
    valid_statuses = {"Pending", "In Transit", "Delivered", "Cancelled"}
    bad_status = (~orders["Status"].isin(valid_statuses)).sum()
    if bad_status > 0:
        raise ValueError(f"[validator] Orders: {bad_status} invalid Status values")

    # ── OrderItems ────────────────────────────────────────────
    _check_no_nulls(items, "OrderItems",
        ["OrderItemID", "OrderID", "ProductID", "QuantityOrdered", "UnitCost"])
    _check_fk(items, "OrderID",   orders,   "OrderID",   "OrderItems", "Orders")
    _check_fk(items, "ProductID", products, "ProductID", "OrderItems", "Products")
    _check_positive(items, "OrderItems", ["QuantityOrdered", "UnitCost"])

    # ── Sales ─────────────────────────────────────────────────
    _check_no_nulls(sales, "Sales",
        ["SaleID", "ProductID", "SaleDate", "QuantitySold", "Revenue"])
    _check_fk(sales, "ProductID", products, "ProductID", "Sales", "Products")
    _check_positive(sales, "Sales", ["QuantitySold", "Revenue"])

    # ── Shipments ─────────────────────────────────────────────
    _check_no_nulls(shipments, "Shipments",
        ["ShipmentID", "OrderID", "ActualDeliveryDate", "ExpectedDeliveryDate", "DelayDays"])
    _check_fk(shipments, "OrderID", orders, "OrderID", "Shipments", "Orders")

    print("[validator] All checks passed.")
