from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from bot.db.database import connect
from bot.services import contest_repo


@pytest.mark.asyncio
async def test_contest_create_and_active(tmp_path, monkeypatch) -> None:
    db = tmp_path / "contest.db"
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("DATABASE_PATH", str(db))
    conn = await connect(db)
    oid = await contest_repo.create_contest(
        conn,
        title="Тест",
        prize_text="Приз",
        starts_at="2026-01-01 00:00:00",
        ends_at="2026-12-31 23:59:59",
        activate=True,
    )
    assert oid > 0
    row = await contest_repo.get_active_contest(conn)
    assert row is not None
    assert int(row["id"]) == oid
    await conn.close()
