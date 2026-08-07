from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo, users_repo
from bot.services.lava_payment_reconcile import reconcile_lava_pending_orders_once


@pytest.mark.asyncio
async def test_lava_reconcile_marks_paid_when_api_success(tmp_path, monkeypatch) -> None:
    db = tmp_path / "lava_rec.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:rec")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("LAVA_SHOP_ID", "a81738ce-8116-4b99-bdd7-5338fab2162d")
    monkeypatch.setenv("LAVA_SECRET_KEY", "sec" * 8)
    monkeypatch.setenv("LAVA_HOOK_URL", "https://ex.example/v1/payments/lava-webhook")
    monkeypatch.setenv("LAVA_RECONCILE_INTERVAL_SECONDS", "120")
    settings = Settings()

    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    await orders_repo.set_invoice_provider_metadata(
        conn, order_id=oid, provider="lava", external_id="inv-uuid-1"
    )
    await conn.close()

    fake = {"status": "success", "amount": 100.0, "id": "inv-uuid-1", "order_id": str(oid)}
    with patch(
        "bot.services.lava_payment_reconcile.fetch_invoice_status",
        new=AsyncMock(return_value=fake),
    ):
        n = await reconcile_lava_pending_orders_once(settings)
    assert n == 1

    conn2 = await connect(db)
    row = await orders_repo.get_order(conn2, oid)
    await conn2.close()
    assert row is not None
    assert str(row["status"]) == "paid"
