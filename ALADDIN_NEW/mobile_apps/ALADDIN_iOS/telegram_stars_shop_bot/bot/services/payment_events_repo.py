from __future__ import annotations

import aiosqlite


async def claim_provider_event(conn: aiosqlite.Connection, *, idempotency_key: str, order_id: int) -> None:
    """Вставка в уже открытой транзакции; IntegrityError = дубликат idempotency_key."""
    await conn.execute(
        """
        INSERT INTO payment_provider_events (idempotency_key, order_id)
        VALUES (?, ?)
        """,
        (idempotency_key, order_id),
    )
