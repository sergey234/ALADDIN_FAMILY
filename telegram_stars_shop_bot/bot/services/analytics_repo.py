from __future__ import annotations

import json
from typing import Any

import aiosqlite


async def log_event(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    event_type: str,
    meta: dict[str, Any] | None = None,
) -> None:
    """Событие воронки / поведения (не блокирует основной поток при ошибках вызывающей стороны)."""
    payload = json.dumps(meta, ensure_ascii=False) if meta else None
    await conn.execute(
        """
        INSERT INTO analytics_events (user_id, event_type, meta_json)
        VALUES (?, ?, ?)
        """,
        (int(user_id), (event_type or "").strip()[:64], payload),
    )
    await conn.commit()
