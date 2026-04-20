from __future__ import annotations

import json

import pytest

from bot.services import partner_outbound


@pytest.mark.asyncio
async def test_partner_outbound_retry_then_deliver(conn, monkeypatch) -> None:
    await conn.execute(
        """
        INSERT INTO api_clients (owner_user_id, key_hash, key_prefix, webhook_url, webhook_secret)
        VALUES (?, ?, ?, ?, ?)
        """,
        (1, "hash_test_only", "ak_live_test…", "https://example.com/webhook", "whsec_test"),
    )
    await conn.commit()
    await conn.execute(
        """
        INSERT INTO outbound_webhook_events (
            api_client_id, order_id, event_type, target_url, payload_json, status, attempts, max_attempts, next_attempt_at
        ) VALUES (?, ?, ?, ?, ?, 'pending', 0, 3, datetime('now'))
        """,
        (1, 101, "order.status_changed", "https://example.com/webhook", json.dumps({"ok": 1})),
    )
    await conn.commit()

    state = {"calls": 0}

    class _Resp:
        def __init__(self, code: int) -> None:
            self.status_code = code

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, content: bytes, headers: dict[str, str]):
            _ = (url, content, headers)
            state["calls"] += 1
            if state["calls"] == 1:
                return _Resp(500)
            return _Resp(200)

    monkeypatch.setattr(partner_outbound.httpx, "AsyncClient", lambda timeout: _Client())

    first = await partner_outbound.process_webhook_queue_once(conn, limit=10)
    assert first == 0
    cur = await conn.execute("SELECT status, attempts FROM outbound_webhook_events WHERE id = 1")
    row = await cur.fetchone()
    assert str(row["status"]) == "pending"
    assert int(row["attempts"]) == 1

    await conn.execute("UPDATE outbound_webhook_events SET next_attempt_at = datetime('now') WHERE id = 1")
    await conn.commit()
    second = await partner_outbound.process_webhook_queue_once(conn, limit=10)
    assert second == 1
    cur2 = await conn.execute("SELECT status, attempts FROM outbound_webhook_events WHERE id = 1")
    row2 = await cur2.fetchone()
    assert str(row2["status"]) == "delivered"
    assert int(row2["attempts"]) == 2
