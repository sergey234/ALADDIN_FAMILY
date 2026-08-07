#!/usr/bin/env python3
"""Снять baseline метрик помощника с Contabo shop.db (без секретов)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path


def _load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


async def main() -> None:
    _load_env(Path("/opt/aladdin-telegram-shop-bot/shared/.env"))
    from bot.config import load_settings
    from bot.db.database import connect

    s = load_settings()
    conn = await connect(s.database_path)
    print("=== assistant baseline ===")
    for label, sql in [
        (
            "csat_up_7d",
            """
            SELECT COUNT(*) AS c FROM analytics_events
            WHERE event_type='assistant_csat' AND meta_json LIKE '%up%'
              AND created_at >= datetime('now','-7 days')
            """,
        ),
        (
            "csat_down_7d",
            """
            SELECT COUNT(*) AS c FROM analytics_events
            WHERE event_type='assistant_csat' AND meta_json LIKE '%down%'
              AND created_at >= datetime('now','-7 days')
            """,
        ),
        (
            "msgs_7d",
            """
            SELECT COUNT(*) AS c FROM assistant_turns
            WHERE role='user' AND created_at >= datetime('now','-7 days')
            """,
        ),
        (
            "tickets_7d",
            """
            SELECT COUNT(*) AS c FROM assistant_tickets
            WHERE created_at >= datetime('now','-7 days')
            """,
        ),
        (
            "top_topics_7d",
            """
            SELECT COALESCE(topic_guess,'(none)') AS t, COUNT(*) AS c
            FROM assistant_turns
            WHERE role='user' AND created_at >= datetime('now','-7 days')
            GROUP BY 1 ORDER BY c DESC LIMIT 10
            """,
        ),
    ]:
        cur = await conn.execute(sql)
        rows = await cur.fetchall()
        if label.startswith("top_"):
            print(label + ":")
            for r in rows:
                print(f"  {r['t']}: {r['c']}")
        else:
            print(label, int(rows[0]["c"] if rows else 0))
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
