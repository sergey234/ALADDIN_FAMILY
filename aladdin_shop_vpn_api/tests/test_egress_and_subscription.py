from __future__ import annotations

import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from aladdin_shop_vpn_api import egress_nodes_util, hmac_auth, subscription_util
from aladdin_shop_vpn_api.main import create_app
from aladdin_shop_vpn_api.settings import load_settings


def test_egress_nodes_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    nodes_json = json.dumps(
        [
            {
                "id": "primary",
                "wg_host": "149.154.65.180",
                "wg_port": 51820,
                "active": True,
            },
            {"id": "secondary", "wg_host": "", "active": False},
        ]
    )
    monkeypatch.setenv("VPN_EGRESS_NODES_JSON", nodes_json)
    settings = load_settings()
    nodes = egress_nodes_util.egress_nodes_from_settings(settings)
    assert len(nodes) == 2
    assert egress_nodes_util.primary_egress_node(settings) is not None
    assert egress_nodes_util.active_egress_nodes(settings)[0].wg_host == "149.154.65.180"


def test_subscription_vless_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "VPN_SUBSCRIBE_VLESS_TEMPLATE",
        "vless://{xray_uuid}@{host}:{port}#vpn-{opaque_token}",
    )
    monkeypatch.setenv("VPN_XRAY_PUBLIC_HOST", "ep.test")
    monkeypatch.setenv("VPN_XRAY_PORT", "8443")
    settings = load_settings()
    body = subscription_util.build_subscription_body(
        settings=settings,
        opaque_token="tok-abc",
        xray_client_uuid="uuid-1111-2222",
    )
    assert body is not None
    assert "vless://uuid-1111-2222@ep.test:8443#vpn-tok-abc" in body


def test_sub_endpoint_uses_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "VPN_SUBSCRIBE_VLESS_TEMPLATE",
        "line={opaque_token} uuid={xray_uuid}\n",
    )
    tid = 880022
    token = "opaque-sub-template-880022"

    async def _seed() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id = ?", (tid,))
            await conn.execute(
                """
                INSERT INTO vpn_accounts (
                    telegram_user_id, status, paid_until, opaque_token,
                    xray_client_uuid, created_at, updated_at
                ) VALUES (?, 'vpn_active', '2099-01-01T00:00:00+00:00', ?, ?, datetime('now'), datetime('now'))
                """,
                (tid, token, "bed682e6-1726-419b-b45b-e8e891de7b7b"),
            )
            await conn.commit()
        finally:
            await conn.close()

    asyncio.run(_seed())
    r = TestClient(create_app()).get(f"/sub/{token}")
    assert r.status_code == 200
    assert f"line={token}" in r.text
    assert "bed682e6-1726-419b-b45b-e8e891de7b7b" in r.text


def test_egress_catalog_hmac(monkeypatch: pytest.MonkeyPatch) -> None:
    from tests.test_internal_api import _headers

    monkeypatch.setenv(
        "VPN_EGRESS_NODES_JSON",
        json.dumps([{"id": "primary", "wg_host": "1.2.3.4", "active": True}]),
    )
    secret = "test-hmac-secret-for-pytest"
    path = "/internal/v1/egress/catalog"
    body = b""
    h = _headers(secret, method="GET", path=path, body=body, nonce="nonce-egress-1")
    r = TestClient(create_app()).get(path, headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["active_count"] == 1
