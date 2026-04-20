from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import api_clients_repo, users_repo
from partner_api.main import create_app


@pytest.fixture
def partner_client(tmp_path, monkeypatch):
    db = tmp_path / "http_test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:http-test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "http_test_pepper_minimum_32_chars___")

    async def seed() -> str:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=424242, username="apiu", first_name="A")
        _, raw = await api_clients_repo.create_api_client(
            conn, owner_user_id=424242, pepper=os.environ["API_KEY_PEPPER"], label="http", revoke_previous=False
        )
        await conn.close()
        return raw

    key = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, key


def test_partner_profile_and_order(partner_client) -> None:
    client, key = partner_client
    r = client.get("/v1/user/profile", headers={"X-API-KEY": key})
    assert r.status_code == 200
    idem = str(uuid.uuid4())
    r2 = client.post(
        "/v1/orders/create",
        headers={"X-API-KEY": key, "Idempotency-Key": idem},
        json={"product_id": "stars_100", "recipient": "@telegram", "payment_method": "fiat"},
    )
    assert r2.status_code == 201, r2.text
