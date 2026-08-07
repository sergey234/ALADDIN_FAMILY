from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import aiosqlite

from bot.services import orders_repo
from bot.services.payment_events_repo import claim_provider_event

Outcome = Literal["duplicate", "already_terminal", "not_found", "conflict", "ok"]


@dataclass(frozen=True)
class MarkOrderPaidResult:
    outcome: Outcome
    order_id: int
    previous_status: str | None
    new_status: str | None


async def mark_order_paid_idempotent(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    idempotency_key: str,
) -> MarkOrderPaidResult:
    """
    Перевод заказа pending_payment → paid с записью idempotency_key.
    Вызывать внутри уже открытой транзакции BEGIN IMMEDIATE.
    """
    cur = await conn.execute(
        "SELECT order_id FROM payment_provider_events WHERE idempotency_key = ?",
        (idempotency_key,),
    )
    dup = await cur.fetchone()
    if dup is not None:
        return MarkOrderPaidResult("duplicate", int(dup["order_id"]), None, None)

    order = await orders_repo.get_order(conn, order_id)
    if order is None:
        return MarkOrderPaidResult("not_found", order_id, None, None)
    st = str(order["status"])
    if st in ("paid", "completed", "refunded"):
        return MarkOrderPaidResult("already_terminal", order_id, st, st)
    # expired: late Lava success после ORDER_PENDING_PAYMENT_EXPIRE_MINUTES
    if st not in ("pending_payment", "expired"):
        return MarkOrderPaidResult("conflict", order_id, st, None)

    try:
        await claim_provider_event(conn, idempotency_key=idempotency_key, order_id=order_id)
    except aiosqlite.IntegrityError:
        cur2 = await conn.execute(
            "SELECT order_id FROM payment_provider_events WHERE idempotency_key = ?",
            (idempotency_key,),
        )
        row2 = await cur2.fetchone()
        oid = int(row2["order_id"]) if row2 else order_id
        return MarkOrderPaidResult("duplicate", oid, None, None)

    prev = st
    from bot.services.order_status import require_transition

    require_transition(prev, "paid")
    await orders_repo.update_status_no_commit(conn, order_id, "paid")
    try:
        from bot.services import promo_repo

        uid = int(order["user_id"])
        await promo_repo.redeem_activation_for_order(conn, order_id=order_id, user_id=uid)
    except Exception:
        pass
    return MarkOrderPaidResult("ok", order_id, prev, "paid")
