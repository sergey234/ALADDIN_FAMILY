from __future__ import annotations

import asyncio
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import orders_repo, users_repo
from bot.services.ckassa_api import (
    CKASSA_DEMO_SECRET,
    CKASSA_DEMO_SHOP,
    ckassa_callback_signature,
)
from partner_api.main import create_app


@pytest.fixture
def ckassa_hook_client(tmp_path, monkeypatch):
    db = tmp_path / "ckassa_hook.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:ckassa-hook")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "ckassa_test_pepper_minimum_32_chars_______")
    monkeypatch.setenv("CKASSA_ENABLED", "true")
    monkeypatch.setenv("CKASSA_TEST_MODE", "true")

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=777001, username="cku", first_name="C")
        oid = await orders_repo.create_order(
            conn,
            user_id=777001,
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
            user_note="@u",
            status="pending_payment",
        )
        await conn.close()
        return oid

    order_id = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, order_id, db


def test_ckassa_webhook_get_marks_paid(ckassa_hook_client) -> None:
    client, order_id, db_path = ckassa_hook_client
    amount_k = 10000
    reg = "REG-UNIT-1"
    sig = ckassa_callback_signature(
        CKASSA_DEMO_SECRET,
        CKASSA_DEMO_SHOP,
        order_id=int(order_id),
        reg_pay_num=reg,
        amount_kopecks=amount_k,
        result="success",
    )
    qs = urlencode(
        {
            "regPayNum": reg,
            "result": "success",
            "orderId": str(order_id),
            "amount": str(amount_k),
            "shop": CKASSA_DEMO_SHOP,
            "signature": sig,
            "errorMsg": "",
        }
    )
    r = client.get(f"/v1/payments/ckassa-webhook?{qs}")
    assert r.status_code == 200
    assert r.text.strip() == "success"

    async def read_status() -> str:
        conn = await connect(db_path)
        row = await orders_repo.get_order(conn, int(order_id))
        await conn.close()
        return str(row["status"]) if row else ""

    assert asyncio.run(read_status()) == "paid"


def test_ckassa_webhook_bad_signature_fail(ckassa_hook_client) -> None:
    client, order_id, _ = ckassa_hook_client
    qs = urlencode(
        {
            "regPayNum": "x",
            "result": "success",
            "orderId": str(order_id),
            "amount": "10000",
            "shop": CKASSA_DEMO_SHOP,
            "signature": "WRONG",
            "errorMsg": "",
        }
    )
    r = client.get(f"/v1/payments/ckassa-webhook?{qs}")
    assert r.status_code == 200
    assert r.text.strip() == "fail"
