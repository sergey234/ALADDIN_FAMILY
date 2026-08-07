from __future__ import annotations

from pathlib import Path

from bot.config import Settings
from bot.services.catalog import load_products
from bot.services.pricing import quote_custom_stars, quote_product

_PRODUCTS = load_products(Path(__file__).resolve().parents[1] / "bot" / "products.yaml")


def _settings(**kwargs: object) -> Settings:
    base: dict[str, object] = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        USD_RUB_RATE=100.0,
        STARS_WHOLESALE_THRESHOLD=500,
        STARS_WHOLESALE_DISCOUNT_PERCENT=5.0,
        REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT=10.0,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_custom_stars_unit_from_pack_100() -> None:
    settings = _settings()
    custom = quote_custom_stars(500, _PRODUCTS, settings, is_first_order=False)
    unit = next(p for p in _PRODUCTS if p.id == "stars_100")
    expected_list = round(unit.price_usd * settings.usd_rub_rate * 5, 2)
    assert custom.rub_list == expected_list
    assert custom.rub_final == expected_list
    assert custom.rub_wholesale_discount == 0.0
    assert custom.rub_referral_discount == 0.0


def test_custom_stars_no_wholesale_or_referral() -> None:
    settings = _settings()
    q = quote_custom_stars(1000, _PRODUCTS, settings, is_first_order=False)
    assert q.rub_wholesale_discount == 0.0
    assert q.rub_referral_discount == 0.0
    assert q.rub_final == q.rub_list


def test_custom_stars_first_order_still_full_price() -> None:
    settings = _settings()
    q = quote_custom_stars(100, _PRODUCTS, settings, is_first_order=True)
    assert q.rub_referral_discount == 0.0
    assert q.rub_final == q.rub_list


def test_premium_no_referral_discount() -> None:
    settings = _settings()
    premium = next(p for p in _PRODUCTS if p.kind == "premium")
    q = quote_product(premium, settings, is_first_order=True)
    assert q.rub_referral_discount == 0.0
    assert q.rub_final == q.rub_list
