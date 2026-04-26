from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import orders_repo, users_repo
from bot.services.hmac_util import hmac_sha256_hex
from partner_api.main import create_app


def _completed_payload(*, ext_order_id: str) -> dict:
    return {
        "event_type": "order.completed",
        "occurred_at": "2025-04-01T12:34:58Z",
        "order": {
            "id": ext_order_id,
            "status": "completed",
            "order_type": "star",
            "amount": 55.5,
            "created_at": "2025-04-01T12:34:56Z",
            "updated_at": "2025-04-01T12:34:58Z",
            "payload": {"username": "john", "quantity": 100},
        },
    }


@pytest.fixture
def istar_hook_client(tmp_path, monkeypatch):
    db = tmp_path / "istar_hook.db"
    wh_secret = "istar_webhook_secret_test_value________"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:istar-hook-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "istar_hook_pepper_minimum_32_chars____")
    monkeypatch.setenv("ISTAR_WEBHOOK_SECRET", wh_secret)

    ext_id = "550e8400-e29b-41d4-a716-446655440099"

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=777001, username="t", first_name="T")
        oid = await orders_repo.create_order(
            conn,
            user_id=777001,
            product_id="stars_100",
            product_title="Stars 100",
            payment_method="test",
            usd_base=1.0,
            rub_before=100.0,
            rub_after=100.0,
            referral_discount_rub=0.0,
            wholesale_discount_rub=0.0,
            referrer_id=None,
            commission_rub=0.0,
            user_note="@john",
            status="processing",
        )
        await conn.execute(
            "UPDATE orders SET fulfillment_provider_ref = ? WHERE id = ?",
            (ext_id, oid),
        )
        await conn.commit()
        await conn.close()
        return oid

    oid = asyncio.run(seed())
    return {"db": db, "secret": wh_secret, "order_id": oid, "ext_id": ext_id}


def test_istar_webhook_completed_marks_completed(istar_hook_client, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(istar_hook_client["db"]))
    app = create_app()
    body = _completed_payload(ext_order_id=istar_hook_client["ext_id"])
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = hmac_sha256_hex(istar_hook_client["secret"], raw)
    with TestClient(app) as client:
        r = client.post(
            "/v1/payments/istar-webhook",
            content=raw,
            headers={"Content-Type": "application/json", "X-iStar-Signature": sig},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["order_id"] == istar_hook_client["order_id"]

    async def check() -> str:
        conn = await connect(Path(istar_hook_client["db"]))
        row = await orders_repo.get_order(conn, istar_hook_client["order_id"])
        await conn.close()
        assert row is not None
        return str(row["status"])

    st = asyncio.run(check())
    assert st == "completed"


def test_istar_webhook_invalid_signature(istar_hook_client, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(istar_hook_client["db"]))
    app = create_app()
    body = _completed_payload(ext_order_id=istar_hook_client["ext_id"])
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    with TestClient(app) as client:
        r = client.post(
            "/v1/payments/istar-webhook",
            content=raw,
            headers={"Content-Type": "application/json", "X-iStar-Signature": "deadbeef"},
        )
    assert r.status_code == 401
