"""Tool scope + ticket limit + KB build (T3/T4/T14)."""

from __future__ import annotations

import pytest

from bot.assistant.kb import build_kb, retrieve_kb
from bot.assistant.tools import get_my_orders, open_human_ticket, run_tool
from bot.config import load_settings


async def _seed_order(conn, *, owner_id: int = 10) -> int:
    await conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, 'a')",
        (owner_id,),
    )
    await conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (20, 'b')",
    )
    cur = await conn.execute(
        """
        INSERT INTO orders (
          user_id, product_id, product_title, product_kind, status,
          payment_method, usd_base, rub_before_discounts, rub_after_discounts
        ) VALUES (?, 'stars_50', 'Stars 50', 'stars', 'completed', 'lava', 1, 100, 100)
        """,
        (owner_id,),
    )
    await conn.commit()
    return int(cur.lastrowid)


@pytest.mark.asyncio
async def test_orders_scope_own_vs_foreign(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    oid = await _seed_order(conn, owner_id=10)
    own = await get_my_orders(conn, 10, order_id=oid)
    assert len(own["orders"]) == 1
    assert own["orders"][0]["id"] == oid

    foreign = await get_my_orders(conn, 20, order_id=oid)
    assert foreign["orders"] == []
    assert foreign.get("note") == "order_not_found_or_no_access"


@pytest.mark.asyncio
async def test_write_tool_rejected(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    s = load_settings()
    res = await run_tool("revoke_vpn", conn, s, 10)
    assert res.get("error") == "tool_not_allowed"


@pytest.mark.asyncio
async def test_kb_build_and_retrieve(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    s = load_settings()
    n = await build_kb(conn, s)
    assert n >= 9
    hits = await retrieve_kb(conn, "Happ Android установка", topic_hint_ids=["kb.happ.android"])
    assert hits
    assert hits[0]["id"] == "kb.happ.android"


@pytest.mark.asyncio
async def test_ticket_daily_limit(conn, monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("ASSISTANT_TICKET_DAILY_LIMIT", "2")
    s = load_settings()
    await conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (7)")
    await conn.commit()
    r1 = await open_human_ticket(
        conn, s, telegram_user_id=7, session_id=None, reason="esc.user", summary="a"
    )
    r2 = await open_human_ticket(
        conn, s, telegram_user_id=7, session_id=None, reason="esc.user", summary="b"
    )
    r3 = await open_human_ticket(
        conn, s, telegram_user_id=7, session_id=None, reason="esc.user", summary="c"
    )
    assert r1["ok"] and r2["ok"]
    assert r3["ok"] is False
    assert r3["error"] == "ticket_daily_limit"
