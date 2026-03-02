"""
Tests: data generators produce correct shapes, types, and FK-safe data.
"""
import pytest
import pandas as pd

from data.generators.gen_products import generate_products
from data.generators.gen_suppliers import generate_suppliers
from data.generators.gen_inventory import generate_inventory
from data.generators.gen_orders import generate_orders
from data.generators.gen_sales import generate_sales
from data.generators.gen_shipments import generate_shipments
from config.settings import NUM_PRODUCTS, NUM_SUPPLIERS


@pytest.fixture(scope="module")
def products():
    return generate_products()


@pytest.fixture(scope="module")
def suppliers():
    return generate_suppliers()


@pytest.fixture(scope="module")
def orders_and_items(suppliers, products):
    return generate_orders(suppliers, products)


@pytest.fixture(scope="module")
def orders(orders_and_items):
    return orders_and_items[0]


@pytest.fixture(scope="module")
def order_items(orders_and_items):
    return orders_and_items[1]


def test_products_row_count(products):
    assert len(products) == NUM_PRODUCTS


def test_products_no_pk_nulls(products):
    assert products["ProductID"].isna().sum() == 0


def test_products_price_above_cost(products):
    assert (products["UnitPrice"] > products["UnitCost"]).all()


def test_suppliers_row_count(suppliers):
    assert len(suppliers) == NUM_SUPPLIERS


def test_suppliers_rating_range(suppliers):
    assert suppliers["Rating"].between(1.0, 5.0).all()


def test_inventory_one_row_per_product(products):
    inv = generate_inventory(products)
    assert len(inv) == len(products)


def test_inventory_no_negative_stock(products):
    inv = generate_inventory(products)
    assert (inv["QuantityOnHand"] >= 0).all()


def test_orders_have_items(orders, order_items):
    assert len(orders) > 0
    assert len(order_items) >= len(orders)  # at least 1 item per order


def test_order_items_fk_valid(orders, order_items, products):
    valid_order_ids = set(orders["OrderID"])
    valid_product_ids = set(products["ProductID"])
    assert set(order_items["OrderID"]).issubset(valid_order_ids)
    assert set(order_items["ProductID"]).issubset(valid_product_ids)


def test_sales_positive_quantities(products):
    sales = generate_sales(products)
    assert (sales["QuantitySold"] > 0).all()
    assert (sales["Revenue"] > 0).all()


def test_sales_fk_valid(products):
    sales = generate_sales(products)
    valid_ids = set(products["ProductID"])
    assert set(sales["ProductID"]).issubset(valid_ids)


def test_shipments_delay_computed(orders, suppliers):
    ships = generate_shipments(orders, suppliers)
    assert ships["DelayDays"].isna().sum() == 0


def test_shipments_fk_valid(orders, suppliers):
    ships = generate_shipments(orders, suppliers)
    eligible_order_ids = set(
        orders[orders["Status"].isin(["Delivered", "In Transit"])]["OrderID"]
    )
    assert set(ships["OrderID"]).issubset(eligible_order_ids)
