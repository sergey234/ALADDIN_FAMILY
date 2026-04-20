from __future__ import annotations

import asyncio
import os

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import api_clients_repo, users_repo
from partner_api.main import create_app


@pytest.fixture
def wh_client(tmp_path, monkeypatch):
    db = tmp_path / "wh_sub.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:wh-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "wh_test_pepper_value_minimum_32_chars__")

    async def seed() -> str:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=888001, username="whu", first_name="W")
        _, raw = await api_clients_repo.create_api_client(
            conn, owner_user_id=888001, pepper=os.environ["API_KEY_PEPPER"], label="wh", revoke_previous=False
        )
        await conn.close()
        return raw

    key = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, key


def test_webhook_subscription_roundtrip(wh_client) -> None:
    client, key = wh_client
    r0 = client.get("/v1/webhooks/subscription", headers={"X-API-KEY": key})
    assert r0.status_code == 200
    assert r0.json()["has_signing_secret"] is False

    r1 = client.put(
        "/v1/webhooks/subscription",
        headers={"X-API-KEY": key},
        json={"webhook_url": "https://example.com/partner-hook", "rotate_secret": False},
    )
    assert r1.status_code == 200, r1.text
    j1 = r1.json()
    assert j1["webhook_url"] == "https://example.com/partner-hook"
    assert j1["has_signing_secret"] is True
    assert j1.get("signing_secret", "").startswith("whsec_")

    r2 = client.get("/v1/webhooks/subscription", headers={"X-API-KEY": key})
    assert r2.json()["has_signing_secret"] is True

    r3 = client.put(
        "/v1/webhooks/subscription",
        headers={"X-API-KEY": key},
        json={"rotate_secret": True},
    )
    assert r3.status_code == 200
    assert r3.json().get("signing_secret", "").startswith("whsec_")
    assert r3.json()["webhook_url"] == "https://example.com/partner-hook"
