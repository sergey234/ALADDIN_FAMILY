#!/usr/bin/env python3
"""Contabo admin smoke T1–T8 for AiMonkey Assistant (no secrets printed)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path


def _load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


async def main() -> None:
    _load_env(Path("/opt/aladdin-telegram-shop-bot/shared/.env"))

    from bot.config import load_settings
    from bot.db.database import connect
    from bot.assistant.access import assistant_feature_allowed
    from bot.assistant.kb import build_kb, retrieve_kb
    from bot.assistant.llm_client import chat_complete, llm_configured
    from bot.assistant.orchestrator import escalate_user_button, handle_user_message
    from bot.assistant.tools import ALLOWED_TOOLS, get_my_orders
    from bot.assistant.policy import detect_immediate_escalate, validate_assistant_reply
    from bot.assistant.redact import mask_sub_urls
    from bot.assistant.html_sanitize import sanitize_telegram_html

    s = load_settings()
    assert s.assistant_enabled and s.assistant_admin_only
    assert llm_configured(s), "LLM not configured"
    admin = sorted(s.parsed_admin_ids())[0]
    assert assistant_feature_allowed(admin, s)
    assert not assistant_feature_allowed(999999001, s)
    print("T8/flag OK admin_only")

    conn = await connect(s.database_path)
    n = await build_kb(conn, s)
    hits = await retrieve_kb(conn, "Happ Android", topic_hint_ids=["kb.happ.android"])
    assert hits and hits[0]["id"] == "kb.happ.android"
    print("KB OK rebuild", n, "hit", hits[0]["id"])

    r = validate_assistant_reply(
        "Да можно Stars с бонуса",
        user_text="stars с бонуса?",
        kb_chunk_ids=["kb.ref"],
    )
    assert "VPN" in r.text
    print("T2 OK")

    assert detect_immediate_escalate("верните деньги") == "esc.refund"
    print("T6 trigger OK")

    assert "Secret" not in mask_sub_urls("https://x/sub/SecretToken999")
    assert "<script" not in sanitize_telegram_html("<b>a</b><script>x</script>").lower()
    assert "revoke" not in " ".join(ALLOWED_TOOLS)
    print("R4/R7/R17 OK")

    llm = await chat_complete(
        s,
        [
            {"role": "system", "content": "Ответь одним словом: ок"},
            {"role": "user", "content": "ping"},
        ],
    )
    print("LLM", llm.ok, (llm.error or "")[:60], (llm.text or "")[:60].replace("\n", " "))
    assert llm.ok, llm.error

    res = await handle_user_message(
        conn,
        s,
        user_id=admin,
        text="Как подключить Happ на Android?",
        username="smoke_admin",
    )
    assert res.html
    print("T1 OK kb", res.kb_ids, "llm_down", res.llm_down, "len", len(res.html))
    if res.llm_down:
        print("T1 WARN llm_down fallback used (credits?)")
    else:
        print("T1 LLM live OK")

    res6 = await handle_user_message(
        conn,
        s,
        user_id=admin,
        text="Верните деньги за заказ",
        username="smoke_admin",
    )
    assert res6.escalate_ticket_id, res6.html[:200]
    print("T6 OK ticket", res6.escalate_ticket_id)

    cur = await conn.execute("SELECT id,user_id FROM orders ORDER BY id DESC LIMIT 1")
    row = await cur.fetchone()
    if row:
        oid = int(row["id"])
        own = int(row["user_id"])
        ok = await get_my_orders(conn, own, order_id=oid)
        bad = await get_my_orders(conn, own + 777000, order_id=oid)
        assert ok["orders"] and not bad["orders"]
        print("T3/T4 OK order", oid)
    else:
        print("T3/T4 SKIP no orders")

    res7 = await escalate_user_button(
        conn, s, user_id=admin, username="smoke_admin", bot=None
    )
    assert res7.escalate_ticket_id or res7.support_url or "лимит" in res7.html.lower()
    print("T7 OK", res7.escalate_ticket_id)

    for t in (
        "assistant_sessions",
        "assistant_turns",
        "assistant_tickets",
        "assistant_kb_chunks",
    ):
        cur = await conn.execute(f"SELECT COUNT(*) AS c FROM {t}")
        print(t, int((await cur.fetchone())["c"]))

    await conn.close()
    print("SMOKE_ADMIN_OK")


if __name__ == "__main__":
    asyncio.run(main())
