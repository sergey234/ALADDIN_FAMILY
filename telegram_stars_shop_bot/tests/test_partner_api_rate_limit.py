from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bot.db.database import connect
from bot.services import users_repo
from partner_api.main import create_app


@pytest.fixture
def rate_limit_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db = tmp_path / "rl.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:rate-limit")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "rate_limit_test_pepper_minimum_32_chars")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE", "2")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_API_PER_MINUTE", "200")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE", "200")

    async def seed() -> None:
        c = await connect(db)
        await users_repo.upsert_user(c, user_id=1, username="u", first_name="U")
        await c.close()

    asyncio.run(seed())

    with TestClient(create_app()) as client:
        yield client


def test_partner_api_rate_limit_health_after_two_ok(rate_limit_client: TestClient) -> None:
    assert rate_limit_client.get("/health").status_code == 200
    assert rate_limit_client.get("/health").status_code == 200
    r = rate_limit_client.get("/health")
    assert r.status_code == 429
    assert r.json().get("code") == "rate_limited"


@pytest.fixture
def webhook_rl_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db = tmp_path / "rlw.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:rate-limit-w")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "rate_limit_w_test_pepper_minimum_32_chars__")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE", "9999")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_API_PER_MINUTE", "9999")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE", "1")

    async def seed() -> None:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
        await conn.close()

    asyncio.run(seed())

    with TestClient(create_app()) as client:
        yield client


def test_partner_api_webhook_rate_limit_per_ip(webhook_rl_client: TestClient) -> None:
    # POST без валидного тела всё равно проходит rate-limit до хендлера — второй вызов 429.
    r1 = webhook_rl_client.post("/v1/payments/lava-webhook", content=b"{}", headers={"content-type": "application/json"})
    assert r1.status_code in (400, 401, 403, 422, 503), r1.text
    r2 = webhook_rl_client.post("/v1/payments/lava-webhook", content=b"{}", headers={"content-type": "application/json"})
    assert r2.status_code == 429


@pytest.fixture
def redis_backend_fallback_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db = tmp_path / "rl_redis_fallback.db"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    monkeypatch.setenv("BOT_TOKEN", "9:rate-limit-r")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "rate_limit_r_test_pepper_minimum_32_chars__")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:6399/15")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE", "2")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_API_PER_MINUTE", "9999")
    monkeypatch.setenv("PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE", "9999")

    async def seed() -> None:
        conn = await connect(db)
        await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
        await conn.close()

    asyncio.run(seed())

    with TestClient(create_app()) as client:
        yield client


def test_partner_api_rate_limit_redis_backend_falls_back_to_memory(
    redis_backend_fallback_client: TestClient,
) -> None:
    assert redis_backend_fallback_client.get("/health").status_code == 200
    assert redis_backend_fallback_client.get("/health").status_code == 200
    r = redis_backend_fallback_client.get("/health")
    assert r.status_code == 429
