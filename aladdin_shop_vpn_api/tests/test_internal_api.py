from __future__ import annotations

import asyncio
import json
import time
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from aladdin_shop_vpn_api import hmac_auth
from aladdin_shop_vpn_api.main import create_app
from aladdin_shop_vpn_api.settings import load_settings
from aladdin_shop_vpn_api.worker import process_one_job


def _headers(secret: str, *, method: str, path: str, body: bytes, nonce: str) -> dict[str, str]:
    ts = str(int(time.time()))
    sig = hmac_auth.compute_signature(secret, method=method, path=path, timestamp=ts, nonce=nonce, body=body)
    return {
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": sig,
        "Content-Type": "application/json",
    }


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_metrics_prometheus_exposition(client: TestClient) -> None:
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.content.decode("utf-8", errors="replace")
    assert "aladdin_shop_vpn_http_request_duration_seconds" in body
    assert "aladdin_shop_vpn_http_requests_total" in body
    assert "aladdin_shop_vpn_jobs_pending" in body
    assert "aladdin_shop_vpn_accounts_vpn_active" in body


def test_provision_enqueue_and_worker(client: TestClient) -> None:
    secret = "test-hmac-secret-for-pytest"
    body_dict = {
        "telegram_user_id": 424242,
        "order_id": 9001,
        "paid_until": "2099-06-01T00:00:00+00:00",
    }
    body = json.dumps(body_dict).encode()
    path = "/internal/v1/provision"
    h = _headers(secret, method="POST", path=path, body=body, nonce="nonce-a-1")
    r = client.post(
        path,
        content=body,
        headers={**h, "Idempotency-Key": "payevt-1"},
    )
    assert r.status_code == 202
    data = r.json()
    assert "job_id" in data and "account_id" in data

    h2 = _headers(secret, method="POST", path=path, body=body, nonce="nonce-a-2")
    r2 = client.post(
        path,
        content=body,
        headers={**h2, "Idempotency-Key": "payevt-1"},
    )
    assert r2.status_code == 202
    assert r2.json() == data

    assert asyncio.run(process_one_job()) is True

    async def _check() -> Optional[str]:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            cur = await conn.execute(
                "SELECT status FROM vpn_accounts WHERE telegram_user_id = ?",
                (424242,),
            )
            row = await cur.fetchone()
            return str(row[0]) if row else None
        finally:
            await conn.close()

    assert asyncio.run(_check()) == "vpn_active"


def test_add_subscription_days_new_account(client: TestClient) -> None:
    secret = "test-hmac-secret-for-pytest"
    tid = 777001
    body_dict = {"telegram_user_id": tid, "order_id": 91001, "days": 5, "reason": "referral_friend"}
    body = json.dumps(body_dict).encode()
    path = "/internal/v1/add-subscription-days"
    h = _headers(secret, method="POST", path=path, body=body, nonce="nonce-add-1")
    r = client.post(path, content=body, headers={**h, "Idempotency-Key": "refgrant-f-91001"})
    assert r.status_code == 202
    data = r.json()
    assert data["status"] == "enqueued"
    assert "paid_until" in data
    assert data["telegram_user_id"] == tid

    assert asyncio.run(process_one_job()) is True

    async def _paid_until() -> tuple[str | None, str | None]:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            cur = await conn.execute(
                "SELECT paid_until, status FROM vpn_accounts WHERE telegram_user_id = ?",
                (tid,),
            )
            row = await cur.fetchone()
            if not row:
                return None, None
            return str(row[0]) if row[0] is not None else None, str(row[1]) if row[1] is not None else None
        finally:
            await conn.close()

    pu, st = asyncio.run(_paid_until())
    assert st == "vpn_active"
    assert pu and len(pu) >= 10


def test_worker_expires_accounts_when_paid_until_passed() -> None:
    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = 900002")
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
                ) VALUES (900002, 'vpn_active', '2020-01-01T00:00:00+00:00', 'opaque-exp-900002', datetime('now'), datetime('now'))
                """
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())
    assert asyncio.run(process_one_job()) is True

    async def _status() -> str:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            cur = await conn.execute(
                "SELECT status FROM vpn_accounts WHERE telegram_user_id = ?",
                (900002,),
            )
            row = await cur.fetchone()
            return str(row[0]) if row else ""
        finally:
            await conn.close()

    assert asyncio.run(_status()) == "vpn_expired"

    old_tok = "opaque-exp-900002"
    r_old = TestClient(create_app()).get(f"/sub/{old_tok}")
    assert r_old.status_code == 404

    async def _new_token() -> str:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            cur = await conn.execute(
                "SELECT opaque_token FROM vpn_accounts WHERE telegram_user_id = ?",
                (900002,),
            )
            row = await cur.fetchone()
            return str(row[0]) if row else ""
        finally:
            await conn.close()

    new_tok = asyncio.run(_new_token())
    assert new_tok and new_tok != old_tok


def test_worker_expires_provisioning_when_paid_until_passed() -> None:
    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = 900003")
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
                ) VALUES (900003, 'vpn_provisioning', '2019-06-01T00:00:00+00:00', 'opaque-prv-900003', datetime('now'), datetime('now'))
                """
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())
    assert asyncio.run(process_one_job()) is True

    async def _status() -> str:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            cur = await conn.execute(
                "SELECT status FROM vpn_accounts WHERE telegram_user_id = ?",
                (900003,),
            )
            row = await cur.fetchone()
            return str(row[0]) if row else ""
        finally:
            await conn.close()

    assert asyncio.run(_status()) == "vpn_expired"


def test_revoke_job_paid_until_elapsed_sets_vpn_expired(client: TestClient) -> None:
    secret = "test-hmac-secret-for-pytest"
    tid = 900004

    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
                ) VALUES (?, 'vpn_active', '2099-01-01T00:00:00+00:00', 'opaque-900004', datetime('now'), datetime('now'))
                """,
                (tid,),
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())

    body_dict = {"telegram_user_id": tid, "reason": "paid_until_elapsed"}
    body = json.dumps(body_dict).encode()
    path = "/internal/v1/revoke"
    h = _headers(secret, method="POST", path=path, body=body, nonce="nonce-rev-1")
    r = client.post(path, content=body, headers={**h, "Idempotency-Key": "revoke-expire-900004"})
    assert r.status_code == 202
    assert asyncio.run(process_one_job()) is True

    async def _status() -> str:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            cur = await conn.execute("SELECT status FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
            row = await cur.fetchone()
            return str(row[0]) if row else ""
        finally:
            await conn.close()

    assert asyncio.run(_status()) == "vpn_expired"


def test_wg_conf_for_active_account(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-hmac-secret-for-pytest"
    keys = tmp_path / "wgk"
    keys.mkdir(parents=True, exist_ok=True)
    (keys / "555001.key").write_text("CLIENTPRIVKEYLINE\n", encoding="utf-8")
    pubf = tmp_path / "srv.pub"
    pubf.write_text("SERVERPUBKEYLINE\n", encoding="utf-8")
    monkeypatch.setenv("WG_KEYS_DIR", str(keys))
    monkeypatch.setenv("VPN_WG_SERVER_PUBLIC_KEY_PATH", str(pubf))
    monkeypatch.setenv("VPN_WG_ENDPOINT_HOST", "ep.example.test")
    monkeypatch.setenv("VPN_WG_LISTEN_PORT", "51899")

    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = 555001")
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token, wg_client_tunnel_ip, created_at, updated_at
                ) VALUES (555001, 'vpn_active', '2099-01-01T00:00:00+00:00', 'opaque-wg-555001', '10.8.0.55', datetime('now'), datetime('now'))
                """
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())

    body_dict = {"telegram_user_id": 555001}
    body = json.dumps(body_dict).encode()
    path = "/internal/v1/wg/conf"
    h = _headers(secret, method="POST", path=path, body=body, nonce="nonce-wg-conf-1")
    r = client.post(path, content=body, headers=h)
    assert r.status_code == 200
    assert "PrivateKey = CLIENTPRIVKEYLINE" in r.text
    assert "SERVERPUBKEYLINE" in r.text
    assert "10.8.0.55/32" in r.text
    assert "ep.example.test:51899" in r.text
    assert "MTU = 1280" in r.text


def test_locations_catalog_hmac(client: TestClient) -> None:
    secret = "test-hmac-secret-for-pytest"
    path = "/internal/v1/locations/catalog"
    body = b""
    h = _headers(secret, method="GET", path=path, body=body, nonce="nonce-loc-catalog-1")
    r = client.get(path, headers=h)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("lines"), list)
    assert data.get("preview_n", 0) >= 1
    assert len(data["lines"]) >= 3
