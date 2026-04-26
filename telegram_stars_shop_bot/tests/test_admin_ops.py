from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services import admin_audit_repo


def test_all_admins_super_when_super_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:adm-test")
    monkeypatch.setenv("ADMIN_IDS", "1,2")
    monkeypatch.setenv("SUPER_ADMIN_IDS", "")
    s = Settings()
    assert not s.admin_roles_restricted()
    assert s.is_super_admin(1) and s.is_super_admin(2)


def test_operator_when_super_subset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:adm-test")
    monkeypatch.setenv("ADMIN_IDS", "10,20")
    monkeypatch.setenv("SUPER_ADMIN_IDS", "10")
    s = Settings()
    assert s.admin_roles_restricted()
    assert s.is_super_admin(10)
    assert not s.is_super_admin(20)


def test_super_disjoint_admin_falls_back_all_super(monkeypatch: pytest.MonkeyPatch) -> None:
    """Неверный SUPER без пересечения с ADMIN — не блокируем магазин."""
    monkeypatch.setenv("BOT_TOKEN", "9:adm-test")
    monkeypatch.setenv("ADMIN_IDS", "5")
    monkeypatch.setenv("SUPER_ADMIN_IDS", "999")
    s = Settings()
    assert s.is_super_admin(5)


@pytest.mark.asyncio
async def test_admin_audit_log_append(conn) -> None:
    await admin_audit_repo.append_admin_action(
        conn,
        admin_user_id=70001,
        action="adm:proc",
        payload_json='{"order_id":3}',
    )
    cur = await conn.execute("SELECT action, payload_json FROM admin_audit_log ORDER BY id DESC LIMIT 1")
    row = await cur.fetchone()
    assert row["action"] == "adm:proc"
    assert "order_id" in str(row["payload_json"])
