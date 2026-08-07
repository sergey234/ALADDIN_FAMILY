from __future__ import annotations

from pathlib import Path

import pytest

from bot.db.database import connect
from bot.services import orders_repo
from bot.services.invoice_checkout_cooldown import allow_checkout_invoice_attempt


@pytest.mark.asyncio
async def test_invoice_checkout_cooldown_allows_then_blocks() -> None:
    conn = await connect(Path(":memory:"))
    await conn.execute(
        """
        INSERT INTO users(user_id, username, first_name) VALUES (1, 'u', 'U')
        """
    )
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="Stars 100",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@buyer",
        status="pending_payment",
        balance_applied_rub=0.0,
    )
    ok1, _ = await allow_checkout_invoice_attempt(conn, oid, 60)
    assert ok1 is True
    ok2, wait = await allow_checkout_invoice_attempt(conn, oid, 60)
    assert ok2 is False
    assert wait > 0
    await conn.close()


@pytest.mark.asyncio
async def test_invoice_checkout_cooldown_zero_disabled() -> None:
    conn = await connect(Path(":memory:"))
    await conn.execute(
        """
        INSERT INTO users(user_id, username, first_name) VALUES (2, 'u2', 'U2')
        """
    )
    oid = await orders_repo.create_order(
        conn,
        user_id=2,
        product_id="stars_50",
        product_title="Stars 50",
        payment_method="crypto",
        usd_base=1.0,
        rub_before=50.0,
        rub_after=50.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@buyer2",
        status="pending_payment",
        balance_applied_rub=0.0,
    )
    ok1, _ = await allow_checkout_invoice_attempt(conn, oid, 0)
    assert ok1 is True
    ok2, _ = await allow_checkout_invoice_attempt(conn, oid, 0)
    assert ok2 is True
    await conn.close()


@pytest.mark.asyncio
async def test_invoice_checkout_cooldown_shared_db_two_connections(tmp_path: Path) -> None:
    db = tmp_path / "shop.db"
    c1 = await connect(db)
    c2 = await connect(db)
    await c1.execute("INSERT INTO users(user_id, username, first_name) VALUES (3, 'u3', 'U3')")
    oid = await orders_repo.create_order(
        c1,
        user_id=3,
        product_id="stars_10",
        product_title="Stars 10",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@buyer3",
        status="pending_payment",
        balance_applied_rub=0.0,
    )
    ok1, _ = await allow_checkout_invoice_attempt(c1, oid, 60)
    ok2, wait2 = await allow_checkout_invoice_attempt(c2, oid, 60)
    assert ok1 is True
    assert ok2 is False
    assert wait2 > 0
    await c1.close()
    await c2.close()
