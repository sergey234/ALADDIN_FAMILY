from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aladdin_shop_vpn_api import hmac_auth
from aladdin_shop_vpn_api.main import create_app
from aladdin_shop_vpn_api.settings import load_settings


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_legal_vpn_terms_ok(client: TestClient) -> None:
    r = client.get("/v1/legal/vpn-terms")
    assert r.status_code == 200
    ct = r.headers.get("content-type") or ""
    assert "markdown" in ct
    assert "Пользовательское соглашение" in r.text
    assert "AiMonkeyVPN" in r.text
    assert "AiMonkeyStars_bot" in r.text
    assert "ShukaVPN" not in r.text
    assert "Safe Journey" not in r.text
    assert "ИП «AiMonkeyStars»" in r.text
    assert "07 мая 2026" in r.text


def test_legal_vpn_privacy_ok(client: TestClient) -> None:
    r = client.get("/v1/legal/vpn-data")
    assert r.status_code == 200
    assert "Политика конфиденциальности" in r.text
    assert "no-logs" in r.text.lower() or "не собираем" in r.text.lower()
    assert "152-ФЗ" in r.text
    assert "AiMonkeyStars_bot" in r.text
    assert "ShukaVPN" not in r.text
    assert "ofvoltage" not in r.text
    assert "07 мая 2026" in r.text


def test_legal_vpn_instructions_ok(client: TestClient) -> None:
    r = client.get("/v1/legal/vpn-instructions")
    assert r.status_code == 200
    assert "markdown" in (r.headers.get("content-type") or "")
    assert "VPN" in r.text


def test_legal_unknown_404(client: TestClient) -> None:
    assert client.get("/v1/legal/no-such-doc").status_code == 404


def test_sub_uses_body_file_when_configured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body_path = tmp_path / "sub.txt"
    body_path.write_text("token={opaque_token}\n", encoding="utf-8")
    monkeypatch.setenv("VPN_SUBSCRIBE_BODY_FILE", str(body_path))

    tid = 880011
    token = "opaque-sub-test-880011"

    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token, created_at, updated_at
                ) VALUES (?, 'vpn_active', '2099-01-01T00:00:00+00:00', ?, datetime('now'), datetime('now'))
                """,
                (tid, token),
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())

    tc = TestClient(create_app())
    r = tc.get(f"/sub/{token}")
    assert r.status_code == 200
    assert f"token={token}" in r.text

    monkeypatch.delenv("VPN_SUBSCRIBE_BODY_FILE", raising=False)
    tc2 = TestClient(create_app())
    r2 = tc2.get(f"/sub/{token}")
    assert r2.status_code == 501
