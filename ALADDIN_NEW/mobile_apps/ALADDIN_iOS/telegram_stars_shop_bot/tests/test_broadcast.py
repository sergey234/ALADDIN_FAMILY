"""Тесты маркетинговой рассылки (opt-in не влияет на VPN-reminders)."""

from __future__ import annotations

import pytest

from bot.services import broadcast_repo


@pytest.mark.asyncio
async def test_marketing_opt_in_default_and_toggle(tmp_path) -> None:
    from bot.db.database import connect, migrate_legacy

    db = tmp_path / "t.db"
    conn = await connect(db)
    await migrate_legacy(conn)
    await conn.execute(
        "INSERT INTO users (user_id, username, first_name) VALUES (7, 'u', 'U')"
    )
    await conn.commit()
    assert await broadcast_repo.is_marketing_opt_in(conn, 7) is True
    await broadcast_repo.set_marketing_opt_in(conn, 7, False)
    assert await broadcast_repo.is_marketing_opt_in(conn, 7) is False
    assert await broadcast_repo.count_unsubscribed(conn) == 1
    ids = await broadcast_repo.list_recipient_ids(
        conn, mode="all", admin_ids={1}, actor_id=1
    )
    assert 7 not in ids
    await conn.close()


@pytest.mark.asyncio
async def test_list_recipients_modes(tmp_path) -> None:
    from bot.db.database import connect, migrate_legacy

    db = tmp_path / "t2.db"
    conn = await connect(db)
    await migrate_legacy(conn)
    for uid in (10, 11, 12):
        await conn.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (?, 'u', 'U')",
            (uid,),
        )
    await conn.commit()
    dry = await broadcast_repo.list_recipient_ids(
        conn, mode="dry", admin_ids={10, 99}, actor_id=10
    )
    assert dry == [10]
    adm = await broadcast_repo.list_recipient_ids(
        conn, mode="admins", admin_ids={10, 99}, actor_id=10
    )
    assert adm == [10, 99]
    cohort = await broadcast_repo.list_recipient_ids(
        conn, mode="cohort:2", admin_ids=set(), actor_id=10
    )
    assert len(cohort) == 2
    await conn.close()
