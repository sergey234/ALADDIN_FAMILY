from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import api_clients_repo, orders_repo, users_repo
from partner_api.main import create_app


@pytest.fixture
def payment_client(tmp_path, monkeypatch):
    db = tmp_path / "payhook.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:pay-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "pay_test_pepper_minimum_32_chars_______")
    secret = "payment_webhook_secret_for_tests_only____"
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET", secret)

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=777001, username="payu", first_name="P")
        cid, _ = await api_clients_repo.create_api_client(
            conn, owner_user_id=777001, pepper=os.environ["API_KEY_PEPPER"], label="pay", revoke_previous=False
        )
        idem = str(uuid.uuid4())
        oid, _ = await orders_repo.create_order_partner_api(
            conn,
            owner_user_id=777001,
            api_client_id=cid,
            idempotency_key=idem,
            external_ref="ext-1",
            product_id="stars_100",
            product_title="Stars 100",
            payment_method="fiat",
            usd_base=1.0,
            rub_before=100.0,
            rub_after=100.0,
            referral_discount_rub=0.0,
            wholesale_discount_rub=0.0,
            referrer_id=None,
            user_note="@buyer",
        )
        await conn.close()
        return oid

    order_id = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, secret, order_id, db


def test_payment_webhook_marks_paid(payment_client) -> None:
    client, secret, order_id, db_path = payment_client
    idem = str(uuid.uuid4())
    body = {"idempotency_key": idem, "order_id": order_id, "action": "mark_paid"}
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    r = client.post(
        "/v1/payments/provider-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Payment-Signature": f"sha256={sig}"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["status"] == "paid"

    async def check() -> str:
        conn = await connect(Path(db_path))
        row = await orders_repo.get_order(conn, order_id)
        await conn.close()
        return str(row["status"])

    assert asyncio.run(check()) == "paid"

    r2 = client.post(
        "/v1/payments/provider-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Payment-Signature": f"sha256={sig}"},
    )
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True


def test_payment_webhook_bad_signature(payment_client) -> None:
    client, _secret, order_id, _db = payment_client
    body = {"idempotency_key": str(uuid.uuid4()), "order_id": order_id, "action": "mark_paid"}
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    r = client.post(
        "/v1/payments/provider-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Payment-Signature": "deadbeef"},
    )
    assert r.status_code == 401


def test_payment_webhook_409_for_processing_state(payment_client) -> None:
    client, secret, order_id, db_path = payment_client

    async def set_processing() -> None:
        conn = await connect(Path(db_path))
        await orders_repo.update_status(conn, order_id, "processing")
        await conn.close()

    asyncio.run(set_processing())
    idem = str(uuid.uuid4())
    body = {"idempotency_key": idem, "order_id": order_id, "action": "mark_paid"}
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    r = client.post(
        "/v1/payments/provider-webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Payment-Signature": f"sha256={sig}"},
    )
    assert r.status_code == 409
