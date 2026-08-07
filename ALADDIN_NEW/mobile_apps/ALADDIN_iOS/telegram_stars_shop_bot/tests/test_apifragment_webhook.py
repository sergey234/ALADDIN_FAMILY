from __future__ import annotations

import asyncio
import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import orders_repo, users_repo
from partner_api.main import create_app
from partner_api.routers.apifragment_webhook import verify_apifragment_signature


def _sign(*, secret: str, timestamp: str, raw: bytes) -> str:
    message = f"{timestamp}.".encode("utf-8") + raw
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.fixture
def apifragment_hook_client(tmp_path, monkeypatch):
    db = tmp_path / "apifragment_hook.db"
    wh_secret = "whsec_test_apifragment_secret_value____"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:apifragment-hook-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "apifragment_hook_pepper_min_32_chars__")
    monkeypatch.setenv("APIFRAGMENT_WEBHOOK_SECRET", wh_secret)
    # Wrong legacy secret must not be used for ApiFragment.
    monkeypatch.setenv("ISTAR_WEBHOOK_SECRET", "legacy_istar_secret_should_not_match____")

    ext_id = "af-task-550e8400-e29b-41d4-a716"

    async def seed() -> int:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=777002, username="t2", first_name="T")
        oid = await orders_repo.create_order(
            conn,
            user_id=777002,
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


def test_verify_apifragment_signature_unit() -> None:
    secret = "whsec_abc"
    ts = "1710000000"
    raw = b'{"status":"completed","task_id":"1"}'
    sig = _sign(secret=secret, timestamp=ts, raw=raw)
    assert verify_apifragment_signature(secret=secret, raw_body=raw, signature=sig, timestamp=ts)
    assert not verify_apifragment_signature(
        secret=secret, raw_body=raw, signature=sig, timestamp="0"
    )
    assert not verify_apifragment_signature(
        secret=secret, raw_body=raw, signature=sig[7:], timestamp=None
    )


def test_apifragment_webhook_completed(apifragment_hook_client, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(apifragment_hook_client["db"]))
    monkeypatch.setenv("APIFRAGMENT_WEBHOOK_SECRET", apifragment_hook_client["secret"])
    app = create_app()
    body = {
        "status": "completed",
        "task_id": apifragment_hook_client["ext_id"],
        "event_type": "task.completed",
    }
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ts = "1711111111"
    sig = _sign(secret=apifragment_hook_client["secret"], timestamp=ts, raw=raw)
    with TestClient(app) as client:
        resp = client.post(
            "/v1/payments/apifragment-webhook",
            content=raw,
            headers={
                "Content-Type": "application/json",
                "X-ApiFragment-Timestamp": ts,
                "X-ApiFragment-Signature": sig,
            },
        )
    assert resp.status_code == 200, resp.text
    assert resp.json().get("status") == "completed"

    async def check() -> str:
        conn = await connect(apifragment_hook_client["db"])
        row = await orders_repo.get_order(conn, apifragment_hook_client["order_id"])
        await conn.close()
        assert row is not None
        return str(row["status"])

    assert asyncio.run(check()) == "completed"


def test_apifragment_webhook_rejects_body_only_hmac(apifragment_hook_client, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(apifragment_hook_client["db"]))
    monkeypatch.setenv("APIFRAGMENT_WEBHOOK_SECRET", apifragment_hook_client["secret"])
    app = create_app()
    body = {"status": "completed", "task_id": apifragment_hook_client["ext_id"]}
    raw = json.dumps(body).encode("utf-8")
    # Old incorrect scheme: HMAC(body) without timestamp.
    bad = hmac.new(
        apifragment_hook_client["secret"].encode("utf-8"), raw, hashlib.sha256
    ).hexdigest()
    with TestClient(app) as client:
        resp = client.post(
            "/v1/payments/apifragment-webhook",
            content=raw,
            headers={
                "Content-Type": "application/json",
                "X-ApiFragment-Timestamp": "1711111111",
                "X-ApiFragment-Signature": f"sha256={bad}",
            },
        )
    assert resp.status_code == 401
