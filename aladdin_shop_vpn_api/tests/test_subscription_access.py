from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from aladdin_shop_vpn_api import hmac_auth
from aladdin_shop_vpn_api.main import create_app
from aladdin_shop_vpn_api.settings import load_settings
from aladdin_shop_vpn_api.subscription_access import assert_subscription_active


def test_assert_active_rejects_expired_status() -> None:
    with pytest.raises(HTTPException) as exc:
        assert_subscription_active(status="vpn_expired", paid_until="2099-01-01T00:00:00+00:00")
    assert exc.value.status_code == 403


def test_assert_active_rejects_past_paid_until_while_active() -> None:
    past = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat()
    with pytest.raises(HTTPException) as exc:
        assert_subscription_active(status="vpn_active", paid_until=past)
    assert exc.value.status_code == 403


def test_sub_403_when_paid_until_elapsed_before_worker(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    body_path = tmp_path / "sub.txt"
    body_path.write_text("ok={opaque_token}\n", encoding="utf-8")
    monkeypatch.setenv("VPN_SUBSCRIBE_BODY_FILE", str(body_path))

    tid = 880099
    token = "opaque-sub-elapsed-880099"
    past = (datetime.now(timezone.utc) - timedelta(hours=2)).replace(microsecond=0).isoformat()

    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
                ) VALUES (?, 'vpn_active', ?, ?, datetime('now'), datetime('now'))
                """,
                (tid, past, token),
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())
    r = TestClient(create_app()).get(f"/sub/{token}")
    assert r.status_code == 403
    assert "subscription ended" in (r.json().get("detail") or r.text).lower()
