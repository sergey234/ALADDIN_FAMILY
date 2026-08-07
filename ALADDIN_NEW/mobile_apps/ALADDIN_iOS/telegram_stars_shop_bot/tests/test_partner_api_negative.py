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
def partner_client_neg(tmp_path, monkeypatch):
    db = tmp_path / "http_test_neg.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:http-test-neg")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "http_test_pepper_minimum_32_chars___")
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET", "payment_secret_for_neg_test")

    async def seed() -> str:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=425000, username="apiu2", first_name="B")
        _, raw = await api_clients_repo.create_api_client(
            conn, owner_user_id=425000, pepper=os.environ["API_KEY_PEPPER"], label="http", revoke_previous=False
        )
        await conn.close()
        return raw

    key = asyncio.run(seed())
    with TestClient(create_app()) as client:
        yield client, key


def test_unauthorized_without_key(partner_client_neg) -> None:
    client, _key = partner_client_neg
    r = client.get("/v1/user/profile")
    assert r.status_code == 422


def test_order_404_for_unknown_product(partner_client_neg) -> None:
    client, key = partner_client_neg
    r = client.post(
        "/v1/orders/create",
        headers={"X-API-KEY": key, "Idempotency-Key": str(uuid.uuid4())},
        json={"product_id": "not_exists", "recipient": "@telegram", "payment_method": "fiat"},
    )
    assert r.status_code == 404


def test_orders_422_for_invalid_limit(partner_client_neg) -> None:
    client, key = partner_client_neg
    r = client.get("/v1/orders?limit=1000", headers={"X-API-KEY": key})
    assert r.status_code == 422
