from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import orders_repo, users_repo
from bot.services.cardlink_api import cardlink_payment_signature
from partner_api.main import create_app


@pytest.fixture
def cardlink_client(tmp_path, monkeypatch):
    db = tmp_path / "cardlink_hook.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:cardlink-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "cardlink_test_pepper_minimum_32_chars____")
    token = "test_api_token_cardlink_only"
    monkeypatch.setenv("CARDLINK_ENABLED", "true")
    monkeypatch.setenv("CARDLINK_SHOP_ID", "shop_test_01")
    monkeypatch.setenv("CARDLINK_API_TOKEN", token)

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=888002, username="clk", first_name="C")
        oid = await orders_repo.create_order(
            conn,
            user_id=888002,
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
        yield client, token, order_id, db


def _payment_form(token: str, *, order_id: int, amount: str = "100", trs_id: str = "bill_abc") -> dict[str, str]:
    inv = str(order_id)
    sig = cardlink_payment_signature(token, amount, inv)
    return {
        "InvId": inv,
        "OutSum": amount,
        "Commission": "3.00",
        "TrsId": trs_id,
        "Status": "SUCCESS",
        "CurrencyIn": "RUB",
        "SignatureValue": sig,
    }


def test_cardlink_webhook_marks_paid(cardlink_client) -> None:
    client, token, order_id, db_path = cardlink_client
    r = client.post("/v1/payments/cardlink-webhook", data=_payment_form(token, order_id=order_id))
    assert r.status_code == 200, r.text
    assert r.text == "OK"

    async def check() -> str:
        conn = await connect(Path(db_path))
        row = await orders_repo.get_order(conn, order_id)
        await conn.close()
        return str(row["status"])

    assert asyncio.run(check()) == "paid"


def test_cardlink_webhook_duplicate(cardlink_client) -> None:
    client, token, order_id, _db = cardlink_client
    form = _payment_form(token, order_id=order_id, trs_id="bill_dup_1")
    assert client.post("/v1/payments/cardlink-webhook", data=form).status_code == 200
    r2 = client.post("/v1/payments/cardlink-webhook", data=form)
    assert r2.status_code == 200


def test_cardlink_webhook_bad_signature(cardlink_client) -> None:
    client, token, order_id, _db = cardlink_client
    form = _payment_form(token, order_id=order_id)
    form["SignatureValue"] = "DEADBEEF"
    r = client.post("/v1/payments/cardlink-webhook", data=form)
    assert r.status_code == 401


def test_cardlink_payment_success_page(cardlink_client) -> None:
    client, token, order_id, _db = cardlink_client
    form = _payment_form(token, order_id=order_id)
    r = client.post("/v1/payment/success", data=form)
    assert r.status_code == 200
    assert "Оплата прошла успешно" in r.text
    assert "AiMonkeyStars_bot" in r.text


def test_cardlink_payment_fail_page(cardlink_client) -> None:
    client, _token, order_id, _db = cardlink_client
    r = client.get(f"/v1/payment/fail?InvId={order_id}")
    assert r.status_code == 200
    assert "Оплата не завершена" in r.text
