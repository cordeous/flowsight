"""
Adds derived columns to DataFrames before loading into the database.
All transformations are pure-pandas operations (no DB reads required).
"""
import pandas as pd


def add_delay_days(shipments_df: pd.DataFrame) -> pd.DataFrame:
    """
    Confirms/recalculates DelayDays = ActualDeliveryDate - ExpectedDeliveryDate.
    Generators compute this already; this step makes it authoritative.
    """
    df = shipments_df.copy()
    df["ActualDeliveryDate"] = pd.to_datetime(df["ActualDeliveryDate"])
    df["ExpectedDeliveryDate"] = pd.to_datetime(df["ExpectedDeliveryDate"])
    df["DelayDays"] = (
        df["ActualDeliveryDate"] - df["ExpectedDeliveryDate"]
    ).dt.days
    # Restore to ISO string for SQLite DATE columns
    df["ActualDeliveryDate"] = df["ActualDeliveryDate"].dt.date.astype(str)
    df["ExpectedDeliveryDate"] = df["ExpectedDeliveryDate"].dt.date.astype(str)
    return df


def add_gross_margin(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds GrossMarginPct = (UnitPrice - UnitCost) / UnitPrice.
    Informational column; not in schema (not loaded to DB directly).
    """
    df = products_df.copy()
    df["GrossMarginPct"] = (
        (df["UnitPrice"] - df["UnitCost"]) / df["UnitPrice"]
    ).round(4)
    return df


def transform_all(dataframes: dict) -> dict:
    """
    Applies all transformations in one pass.
    Returns a new dict with transformed DataFrames.
    """
    out = dict(dataframes)   # shallow copy of dict, DataFrames still shared
    out["Shipments"] = add_delay_days(dataframes["Shipments"])
    return out
