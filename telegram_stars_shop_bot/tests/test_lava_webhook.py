from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import orders_repo, users_repo
from partner_api.main import create_app


@pytest.fixture
def lava_client(tmp_path, monkeypatch):
    db = tmp_path / "lava_hook.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:lava-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "lava_test_pepper_minimum_32_chars__________")
    add = "lava_additional_webhook_secret_test_only___"
    monkeypatch.setenv("LAVA_WEBHOOK_ADDITIONAL_SECRET", add)

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=888001, username="lavu", first_name="L")
        oid = await orders_repo.create_order(
            conn,
            user_id=888001,
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
        yield client, add, order_id, db


def _sign_body(secret: str, raw: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def test_lava_webhook_marks_paid(lava_client) -> None:
    client, secret, order_id, db_path = lava_client
    inv = str(uuid.uuid4())
    body_obj = {
        "invoice_id": inv,
        "status": "success",
        "pay_time": "2022-09-09 15:15:35",
        "amount": 100,
        "order_id": str(order_id),
        "pay_service": "sbp",
        "payer_details": "7999***",
        "custom_fields": None,
        "credited": 97.0,
    }
    raw = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = _sign_body(secret, raw)
    r = client.post(
        "/v1/payments/lava-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "Authorization": sig},
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


def test_lava_webhook_duplicate(lava_client) -> None:
    client, secret, order_id, _db = lava_client
    inv = str(uuid.uuid4())
    body_obj = {
        "invoice_id": inv,
        "status": "success",
        "pay_time": "2022-09-09 15:15:35",
        "amount": 100,
        "order_id": str(order_id),
        "pay_service": "sbp",
        "custom_fields": None,
        "credited": 97.0,
    }
    raw = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = _sign_body(secret, raw)
    r1 = client.post(
        "/v1/payments/lava-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "Authorization": sig},
    )
    assert r1.status_code == 200
    r2 = client.post(
        "/v1/payments/lava-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "Authorization": sig},
    )
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True


def test_lava_webhook_bad_auth(lava_client) -> None:
    client, _secret, order_id, _db = lava_client
    body_obj = {
        "invoice_id": str(uuid.uuid4()),
        "status": "success",
        "pay_time": "2022-09-09 15:15:35",
        "amount": 100,
        "order_id": str(order_id),
    }
    raw = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    r = client.post(
        "/v1/payments/lava-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "Authorization": "deadbeef"},
    )
    assert r.status_code == 401


def test_lava_webhook_misconfigured(monkeypatch, tmp_path) -> None:
    db = tmp_path / "lava_bad.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "lava_test_pepper_minimum_32_chars__________")
    monkeypatch.setenv("LAVA_WEBHOOK_ADDITIONAL_SECRET", "")
    with TestClient(create_app()) as client:
        r = client.post("/v1/payments/lava-webhook", content=b"{}", headers={"Content-Type": "application/json"})
    assert r.status_code == 503
