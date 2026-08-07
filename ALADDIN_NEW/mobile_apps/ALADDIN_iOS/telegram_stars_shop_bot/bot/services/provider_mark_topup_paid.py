from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import aiosqlite

from bot.services import balance_repo

Outcome = Literal["duplicate", "already_terminal", "not_found", "conflict", "ok"]


@dataclass(frozen=True)
class MarkTopupPaidResult:
    outcome: Outcome
    topup_id: int
    user_id: int | None = None
    amount_rub: float | None = None
    previous_status: str | None = None


async def claim_topup_provider_event(conn: aiosqlite.Connection, *, idempotency_key: str, topup_id: int) -> None:
    await conn.execute(
        """
        INSERT INTO topup_payment_events (idempotency_key, topup_id)
        VALUES (?, ?)
        """,
        (idempotency_key, topup_id),
    )


async def mark_topup_paid_idempotent(
    conn: aiosqlite.Connection,
    *,
    topup_id: int,
    idempotency_key: str,
) -> MarkTopupPaidResult:
    """pending → completed + balance_rub. Вызывать внутри BEGIN IMMEDIATE."""
    cur = await conn.execute(
        "SELECT topup_id FROM topup_payment_events WHERE idempotency_key = ?",
        (idempotency_key,),
    )
    dup = await cur.fetchone()
    if dup is not None:
        row = await balance_repo.get_topup(conn, topup_id)
        uid = int(row["user_id"]) if row else None
        amt = float(row["amount_rub"]) if row else None
        return MarkTopupPaidResult("duplicate", topup_id, uid, amt, "completed")

    row = await balance_repo.get_topup(conn, topup_id)
    if row is None:
        return MarkTopupPaidResult("not_found", topup_id)
    st = str(row["status"] or "")
    uid = int(row["user_id"])
    amt = float(row["amount_rub"])
    if st == "completed":
        return MarkTopupPaidResult("already_terminal", topup_id, uid, amt, st)
    if st == "cancelled":
        return MarkTopupPaidResult("conflict", topup_id, uid, amt, st)
    if st != "pending":
        return MarkTopupPaidResult("conflict", topup_id, uid, amt, st)

    try:
        await claim_topup_provider_event(conn, idempotency_key=idempotency_key, topup_id=topup_id)
    except aiosqlite.IntegrityError:
        return MarkTopupPaidResult("duplicate", topup_id, uid, amt, st)

    ok = await balance_repo.approve_topup_no_commit(conn, topup_id)
    if not ok:
        return MarkTopupPaidResult("conflict", topup_id, uid, amt, st)
    await conn.execute(
        """
        UPDATE topup_requests
        SET payment_idempotency_key = ?, paid_at = datetime('now')
        WHERE id = ?
        """,
        (idempotency_key, topup_id),
    )
    return MarkTopupPaidResult("ok", topup_id, uid, amt, "pending")
