from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import orders_repo, users_repo
from bot.services.crypto_pay_payload import encode_crypto_invoice_payload
from partner_api.main import create_app


def _sign_xrocket_body(api_key: str, body_str: str) -> str:
    secret = hashlib.sha256(api_key.encode("utf-8")).digest()
    return hmac.new(secret, body_str.encode("utf-8"), hashlib.sha256).hexdigest()


def _xrocket_invoice_pay_body(
    *,
    invoice_db_id: int,
    order_id: int,
    due_rub: float,
    webhook_type: str = "invoicePay",
) -> str:
    payload_str = encode_crypto_invoice_payload(order_id=order_id, due_rub=due_rub)
    data = {
        "id": invoice_db_id,
        "amount": 1.0,
        "minPayment": 1.0,
        "totalActivations": 1,
        "activationsLeft": 0,
        "description": "test",
        "hiddenMessage": "",
        "payload": payload_str,
        "callbackUrl": "https://t.me/test",
        "commentsEnabled": False,
        "currency": "USDT",
        "created": "2020-01-01T00:00:00.000Z",
        "paid": "2020-01-01T00:01:00.000Z",
        "status": "paid",
        "expiredIn": 3600,
        "link": "https://t.me/xRocket?start=test",
        "payment": {
            "id": "pay-1",
            "userId": 123456,
            "paymentNum": 1,
            "paymentAmount": 1.0,
            "paymentAmountReceived": 0.99,
            "comment": "",
            "paid": "2020-01-01T00:01:00.000Z",
        },
    }
    root = {"type": webhook_type, "timestamp": "2020-01-01T00:01:00.000Z", "data": data}
    return json.dumps(root, separators=(",", ":"), ensure_ascii=False)


@pytest.fixture
def xrocket_hook_client(tmp_path, monkeypatch):
    db = tmp_path / "xrocket_hook.db"
    key = "xrocket_webhook_test_api_key____________"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:xrocket-hook-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "xrocket_hook_pepper_minimum_32_chars____")
    monkeypatch.setenv("XROCKET_PAY_ENABLED", "true")
    monkeypatch.setenv("XROCKET_PAY_API_KEY", key)

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=666001, username="xr", first_name="X")
        oid = await orders_repo.create_order(
            conn,
            user_id=666001,
            product_id="stars_100",
            product_title="Stars 100",
            payment_method="crypto",
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
        yield client, key, order_id, db


def test_xrocket_webhook_marks_paid(xrocket_hook_client) -> None:
    client, key, order_id, db_path = xrocket_hook_client
    body = _xrocket_invoice_pay_body(invoice_db_id=9001, order_id=order_id, due_rub=100.0)
    sig = _sign_xrocket_body(key, body)
    r = client.post(
        "/v1/payments/xrocket-webhook",
        content=body.encode("utf-8"),
        headers={"Content-Type": "application/json", "rocket-pay-signature": sig},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("ok") is True
    assert r.json().get("status") == "paid"

    async def check() -> str:
        conn = await connect(Path(db_path))
        row = await orders_repo.get_order(conn, order_id)
        await conn.close()
        return str(row["status"])

    assert asyncio.run(check()) == "paid"


def test_xrocket_webhook_duplicate(xrocket_hook_client) -> None:
    client, key, order_id, _db = xrocket_hook_client
    body = _xrocket_invoice_pay_body(invoice_db_id=9002, order_id=order_id, due_rub=100.0)
    sig = _sign_xrocket_body(key, body)
    r1 = client.post(
        "/v1/payments/xrocket-webhook",
        content=body.encode("utf-8"),
        headers={"Content-Type": "application/json", "rocket-pay-signature": sig},
    )
    assert r1.status_code == 200
    r2 = client.post(
        "/v1/payments/xrocket-webhook",
        content=body.encode("utf-8"),
        headers={"Content-Type": "application/json", "rocket-pay-signature": sig},
    )
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True


def test_xrocket_webhook_bad_signature(xrocket_hook_client) -> None:
    client, _key, order_id, _db = xrocket_hook_client
    body = _xrocket_invoice_pay_body(invoice_db_id=9003, order_id=order_id, due_rub=100.0)
    r = client.post(
        "/v1/payments/xrocket-webhook",
        content=body.encode("utf-8"),
        headers={"Content-Type": "application/json", "rocket-pay-signature": "deadbeef"},
    )
    assert r.status_code == 401


def test_xrocket_webhook_ignored_type(xrocket_hook_client) -> None:
    client, key, order_id, _db = xrocket_hook_client
    body = _xrocket_invoice_pay_body(
        invoice_db_id=9004, order_id=order_id, due_rub=100.0, webhook_type="subscriptionPay"
    )
    sig = _sign_xrocket_body(key, body)
    r = client.post(
        "/v1/payments/xrocket-webhook",
        content=body.encode("utf-8"),
        headers={"Content-Type": "application/json", "rocket-pay-signature": sig},
    )
    assert r.status_code == 200
    assert r.json().get("ignored") is True


def test_xrocket_webhook_misconfigured(monkeypatch, tmp_path) -> None:
    db = tmp_path / "xrocket_bad.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "xrocket_hook_pepper_minimum_32_chars____")
    monkeypatch.setenv("XROCKET_PAY_API_KEY", "")
    with TestClient(create_app()) as client:
        r = client.post("/v1/payments/xrocket-webhook", content=b"{}", headers={"Content-Type": "application/json"})
    assert r.status_code == 503
