from __future__ import annotations

from bot.services.auto_fulfill_runner import stars_quantity_for_fulfillment
from bot.services.catalog import Product


def _stars_product() -> Product:
    return Product(
        id="stars_100",
        kind="stars",
        title="100 Stars",
        emoji="⭐",
        price_usd=1.8,
        stars=100,
    )


def _custom_product() -> Product:
    return Product(
        id="stars_custom",
        kind="stars",
        title="Своё количество",
        emoji="✏️",
        price_usd=0.0,
        stars=0,
    )


def test_stars_qty_from_order_for_custom() -> None:
    p = _custom_product()
    assert stars_quantity_for_fulfillment({"stars_qty": 150}, p) == 150


def test_stars_qty_from_catalog_when_no_order_field() -> None:
    p = _stars_product()
    assert stars_quantity_for_fulfillment({}, p) == 100


def test_custom_product_zero_falls_back_to_order_only() -> None:
    p = _custom_product()
    assert stars_quantity_for_fulfillment({}, p) is None
