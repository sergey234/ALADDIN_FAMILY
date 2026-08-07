from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import uuid

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import balance_repo, users_repo
from bot.services.payment_reference import parse_lava_payment_reference
from bot.services.provider_mark_topup_paid import mark_topup_paid_idempotent
from bot.services.topup_crypto_payload import (
    decode_topup_crypto_payload,
    encode_topup_crypto_payload,
    is_topup_crypto_payload,
)
from partner_api.main import create_app


def test_parse_lava_payment_reference_topup() -> None:
    assert parse_lava_payment_reference("TOPUP12") == ("topup", 12)
    assert parse_lava_payment_reference("TOPUP12-r2") == ("topup", 12)
    assert parse_lava_payment_reference("59") == ("order", 59)
    assert parse_lava_payment_reference("59-r2") == ("order", 59)
    assert parse_lava_payment_reference("") is None


def test_topup_crypto_payload_roundtrip() -> None:
    raw = encode_topup_crypto_payload(topup_id=5, due_rub=100.0)
    assert raw == "SB1T|5|10000"
    assert is_topup_crypto_payload(raw)
    decoded = decode_topup_crypto_payload(raw)
    assert decoded.topup_id == 5
    assert decoded.due_rub == 100.0


@pytest.mark.asyncio
async def test_mark_topup_paid_idempotent(conn, monkeypatch) -> None:
    monkeypatch.setenv("TOPUP_MIN_RUB", "50")
    from bot.config import load_settings

    settings = load_settings()
    await users_repo.upsert_user(conn, user_id=92001, username="t", first_name="T")
    tid = await balance_repo.create_topup_request(conn, user_id=92001, amount_rub=100.0, settings=settings)
    await conn.execute("BEGIN IMMEDIATE")
    r1 = await mark_topup_paid_idempotent(conn, topup_id=tid, idempotency_key="test:topup:1")
    assert r1.outcome == "ok"
    await conn.commit()
    bal = await balance_repo.get_balance(conn, 92001)
    assert bal == pytest.approx(100.0)
    await conn.execute("BEGIN IMMEDIATE")
    r2 = await mark_topup_paid_idempotent(conn, topup_id=tid, idempotency_key="test:topup:1")
    assert r2.outcome == "duplicate"
    await conn.rollback()


@pytest.fixture
def lava_topup_client(tmp_path, monkeypatch):
    db = tmp_path / "lava_topup_hook.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:lava-topup-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "lava_topup_test_pepper_minimum_32_chars____")
    add = "lava_topup_additional_webhook_secret_test_only"
    monkeypatch.setenv("LAVA_WEBHOOK_ADDITIONAL_SECRET", add)
    monkeypatch.setenv("TOPUP_MIN_RUB", "50")

    async def seed() -> int:
        from bot.config import load_settings

        settings = load_settings()
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=888002, username="top", first_name="T")
        tid = await balance_repo.create_topup_request(
            conn, user_id=888002, amount_rub=100.0, settings=settings
        )
        await conn.close()
        return tid

    topup_id = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, add, topup_id, db


def _sign_body(secret: str, raw: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def test_lava_webhook_marks_topup_paid(lava_topup_client) -> None:
    client, secret, topup_id, db_path = lava_topup_client
    inv = str(uuid.uuid4())
    body_obj = {
        "invoice_id": inv,
        "status": "success",
        "pay_time": "2022-09-09 15:15:35",
        "amount": 100,
        "order_id": f"TOPUP{topup_id}",
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
    data = r.json()
    assert data.get("topup_id") == topup_id
    assert data.get("status") == "completed"

    async def check() -> float:
        conn = await connect(db_path)
        try:
            return await balance_repo.get_balance(conn, 888002)
        finally:
            await conn.close()

    assert asyncio.run(check()) == pytest.approx(100.0)
