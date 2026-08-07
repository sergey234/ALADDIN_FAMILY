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


def _sign_crypto_raw(token: str, raw: bytes) -> str:
    secret = hashlib.sha256(token.encode("utf-8")).digest()
    return hmac.new(secret, raw, hashlib.sha256).hexdigest()


def _crypto_update_body(
    *,
    invoice_id: int,
    order_id: int,
    due_rub: float,
    update_type: str = "invoice_paid",
) -> bytes:
    payload_str = encode_crypto_invoice_payload(order_id=order_id, due_rub=due_rub)
    inv = {
        "invoice_id": invoice_id,
        "status": "paid",
        "hash": "testhash",
        "asset": "USDT",
        "amount": "1",
        "payload": payload_str,
    }
    update = {
        "update_id": 1,
        "update_type": update_type,
        "request_date": "2020-01-01T00:00:00+00:00",
        "payload": inv,
    }
    return json.dumps(update, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


@pytest.fixture
def crypto_hook_client(tmp_path, monkeypatch):
    db = tmp_path / "crypto_hook.db"
    tok = "crypto_pay_webhook_test_token__________"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:crypto-hook-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "crypto_hook_pepper_minimum_32_chars_______")
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "true")
    monkeypatch.setenv("CRYPTO_PAY_API_TOKEN", tok)

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=777001, username="cru", first_name="C")
        oid = await orders_repo.create_order(
            conn,
            user_id=777001,
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
        yield client, tok, order_id, db


def test_crypto_pay_webhook_marks_paid(crypto_hook_client) -> None:
    client, token, order_id, db_path = crypto_hook_client
    raw = _crypto_update_body(invoice_id=555001, order_id=order_id, due_rub=100.0)
    sig = _sign_crypto_raw(token, raw)
    r = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": sig},
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


def test_crypto_pay_webhook_duplicate(crypto_hook_client) -> None:
    client, token, order_id, _db = crypto_hook_client
    raw = _crypto_update_body(invoice_id=555002, order_id=order_id, due_rub=100.0)
    sig = _sign_crypto_raw(token, raw)
    r1 = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": sig},
    )
    assert r1.status_code == 200
    r2 = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": sig},
    )
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True


def test_crypto_pay_webhook_bad_signature(crypto_hook_client) -> None:
    client, _token, order_id, _db = crypto_hook_client
    raw = _crypto_update_body(invoice_id=555003, order_id=order_id, due_rub=100.0)
    r = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": "deadbeef"},
    )
    assert r.status_code == 401


def test_crypto_pay_webhook_payload_mismatch(crypto_hook_client) -> None:
    client, token, order_id, _db = crypto_hook_client
    raw = _crypto_update_body(invoice_id=555004, order_id=order_id, due_rub=99.0)
    sig = _sign_crypto_raw(token, raw)
    r = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": sig},
    )
    assert r.status_code == 422
    assert r.json().get("detail", {}).get("code") == "payload_mismatch"


def test_crypto_pay_webhook_ignored_update_type(crypto_hook_client) -> None:
    client, token, order_id, _db = crypto_hook_client
    raw = _crypto_update_body(invoice_id=555005, order_id=order_id, due_rub=100.0, update_type="noop")
    sig = _sign_crypto_raw(token, raw)
    r = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": sig},
    )
    assert r.status_code == 200
    assert r.json().get("ignored") is True


def test_crypto_pay_webhook_misconfigured(monkeypatch, tmp_path) -> None:
    db = tmp_path / "crypto_bad.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "crypto_hook_pepper_minimum_32_chars_______")
    monkeypatch.setenv("CRYPTO_PAY_API_TOKEN", "")
    with TestClient(create_app()) as client:
        r = client.post("/v1/payments/crypto-pay-webhook", content=b"{}", headers={"Content-Type": "application/json"})
    assert r.status_code == 503


@pytest.fixture
def crypto_hook_mix_client(tmp_path, monkeypatch):
    db = tmp_path / "crypto_hook_mix.db"
    tok = "crypto_pay_mix_webhook_test_token_____"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:crypto-mix-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "crypto_hook_pepper_minimum_32_chars_______")
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "true")
    monkeypatch.setenv("CRYPTO_PAY_API_TOKEN", tok)

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=777002, username="cmix", first_name="M")
        oid = await orders_repo.create_order(
            conn,
            user_id=777002,
            product_id="stars_100",
            product_title="Stars 100",
            payment_method="mix_crypto",
            usd_base=1.0,
            rub_before=100.0,
            rub_after=100.0,
            referral_discount_rub=0.0,
            wholesale_discount_rub=0.0,
            referrer_id=None,
            commission_rub=0.0,
            user_note="@u",
            status="pending_payment",
            balance_applied_rub=30.0,
        )
        await conn.close()
        return oid

    order_id = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, tok, order_id


def test_crypto_pay_webhook_mix_crypto_due(crypto_hook_mix_client) -> None:
    client, token, order_id = crypto_hook_mix_client
    raw = _crypto_update_body(invoice_id=555006, order_id=order_id, due_rub=70.0)
    sig = _sign_crypto_raw(token, raw)
    r = client.post(
        "/v1/payments/crypto-pay-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "crypto-pay-api-signature": sig},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("ok") is True
