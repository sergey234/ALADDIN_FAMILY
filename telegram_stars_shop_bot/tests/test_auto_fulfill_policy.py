from __future__ import annotations

from bot.config import Settings
from bot.services.auto_fulfill_policy import auto_fulfill_order_eligible, auto_fulfill_type_enabled


def _s(**kwargs: object) -> Settings:
    base: dict[str, object] = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_type_enabled_requires_master() -> None:
    s = _s(
        AUTO_FULFILL_ENABLED=False,
        AUTO_FULFILL_STARS_ENABLED=True,
        AUTO_FULFILL_PREMIUM_ENABLED=True,
    )
    assert auto_fulfill_type_enabled(s, product_kind="stars") is False
    s2 = _s(
        AUTO_FULFILL_ENABLED=True,
        AUTO_FULFILL_STARS_ENABLED=True,
        AUTO_FULFILL_PREMIUM_ENABLED=False,
    )
    assert auto_fulfill_type_enabled(s2, product_kind="stars") is True
    assert auto_fulfill_type_enabled(s2, product_kind="gift") is True
    assert auto_fulfill_type_enabled(s2, product_kind="premium") is False


def test_order_eligible_happy_path() -> None:
    s = _s(
        AUTO_FULFILL_ENABLED=True,
        AUTO_FULFILL_STARS_ENABLED=True,
        AUTO_FULFILL_PREMIUM_ENABLED=False,
    )
    order = {
        "status": "paid",
        "fulfillment_mode": "auto",
        "fulfillment_attempt_count": 0,
        "rub_after_discounts": 100.0,
    }
    ok, reason = auto_fulfill_order_eligible(order, s, product_kind="stars", stars=100)
    assert ok is True
    assert reason == "ok"


def test_order_not_paid() -> None:
    s = _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=True)
    ok, reason = auto_fulfill_order_eligible(
        {"status": "pending_payment", "fulfillment_attempt_count": 0},
        s,
        product_kind="stars",
        stars=100,
    )
    assert ok is False
    assert reason == "not_paid"


def test_manual_only_mode() -> None:
    s = _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=True)
    order = {"status": "paid", "fulfillment_mode": "manual_only", "fulfillment_attempt_count": 0}
    ok, reason = auto_fulfill_order_eligible(order, s, product_kind="stars", stars=100)
    assert ok is False
    assert reason == "manual_only"


def test_rub_cap() -> None:
    s = _s(
        AUTO_FULFILL_ENABLED=True,
        AUTO_FULFILL_STARS_ENABLED=True,
        AUTO_FULFILL_MAX_ORDER_RUB=50.0,
    )
    ok, _ = auto_fulfill_order_eligible(
        {"status": "paid", "fulfillment_mode": "auto", "rub_after_discounts": 49.0, "fulfillment_attempt_count": 0},
        s,
        product_kind="stars",
        stars=100,
    )
    assert ok is True
    ok2, reason2 = auto_fulfill_order_eligible(
        {"status": "paid", "fulfillment_mode": "auto", "rub_after_discounts": 50.01, "fulfillment_attempt_count": 0},
        s,
        product_kind="stars",
        stars=100,
    )
    assert ok2 is False
    assert reason2 == "over_rub_cap"


def test_max_attempts() -> None:
    s = _s(
        AUTO_FULFILL_ENABLED=True,
        AUTO_FULFILL_STARS_ENABLED=True,
        AUTO_FULFILL_MAX_ATTEMPTS=3,
    )
    ok, reason = auto_fulfill_order_eligible(
        {"status": "paid", "fulfillment_mode": "auto", "fulfillment_attempt_count": 3},
        s,
        product_kind="stars",
        stars=100,
    )
    assert ok is False
    assert reason == "max_attempts"


def test_stars_below_minimum() -> None:
    s = _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=True)
    order = {"status": "paid", "fulfillment_mode": "auto", "fulfillment_attempt_count": 0}
    ok, reason = auto_fulfill_order_eligible(order, s, product_kind="stars", stars=49)
    assert ok is False
    assert reason == "stars_quantity_below_minimum"


def test_gift_without_stars_rejected() -> None:
    s = _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=True)
    order = {"status": "paid", "fulfillment_mode": "auto", "fulfillment_attempt_count": 0}
    ok, reason = auto_fulfill_order_eligible(order, s, product_kind="gift", stars=None)
    assert ok is False
    assert reason == "gift_no_stars_quantity"


def test_premium_invalid_months() -> None:
    s = _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_PREMIUM_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=False)
    order = {"status": "paid", "fulfillment_mode": "auto", "fulfillment_attempt_count": 0}
    ok, reason = auto_fulfill_order_eligible(order, s, product_kind="premium", duration_months=1)
    assert ok is False
    assert reason == "premium_months_invalid"


def test_premium_eligible() -> None:
    s = _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_PREMIUM_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=False)
    order = {"status": "paid", "fulfillment_mode": "auto", "fulfillment_attempt_count": 0}
    ok, reason = auto_fulfill_order_eligible(order, s, product_kind="premium", duration_months=6)
    assert ok is True
    assert reason == "ok"


def test_db_migration_has_fulfillment_columns(tmp_path) -> None:
    """Новые колонки orders появляются после connect + migrate_legacy."""
    import asyncio

    from bot.db.database import connect

    db = tmp_path / "af.db"

    async def run() -> set[str]:
        conn = await connect(db)
        cur = await conn.execute("PRAGMA table_info(orders)")
        rows = await cur.fetchall()
        await conn.close()
        return {str(r[1]) for r in rows}

    names = asyncio.run(run())
    for col in (
        "fulfillment_mode",
        "fulfillment_attempt_count",
        "fulfillment_last_error",
        "fulfillment_last_attempt_at",
        "fulfillment_provider_ref",
    ):
        assert col in names
