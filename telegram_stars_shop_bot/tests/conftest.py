from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

os.environ.setdefault("BOT_TOKEN", "9:pytest-bot-token")
os.environ.setdefault("ADMIN_IDS", "1")
os.environ.setdefault("API_KEY_PEPPER", "pytest_pepper_value_minimum_32_chars__")
# В проде курс только из .env; в тестах — стабильное значение, если тест не переопределяет.
os.environ.setdefault("USD_RUB_RATE", "90")
os.environ.setdefault("VPN_REFERRAL_API_RETRY_INTERVAL_SECONDS", "0")


@pytest.fixture
async def temp_db_path() -> AsyncGenerator[Path, None]:
    fd, raw = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    p = Path(raw)
    old = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(p)
    yield p
    if old is None:
        os.environ.pop("DATABASE_PATH", None)
    else:
        os.environ["DATABASE_PATH"] = old
    p.unlink(missing_ok=True)


@pytest.fixture
async def conn(temp_db_path: Path):
    from bot.db.database import connect

    c = await connect(temp_db_path)
    yield c
    await c.close()
