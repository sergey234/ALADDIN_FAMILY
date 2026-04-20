from __future__ import annotations

import aiosqlite

from bot.config import Settings
from bot.services import orders_repo
from bot.services.pricing import commission_for_first_order


async def apply_completed_side_effects(conn: aiosqlite.Connection, order_id: int, settings: Settings) -> None:
    """
    Вызывать после перевода заказа в status=completed.
    Первый завершённый заказ пользователя: фиксируем first_order_completed и начисляем комиссию рефереру
    (15% от суммы этого заказа в ₽ — см. Settings).
    """
    order = await orders_repo.get_order(conn, order_id)
    if order is None or order["status"] != "completed":
        return

    user_id = int(order["user_id"])
    cur = await conn.execute(
        """
        SELECT COUNT(*) AS c FROM orders
        WHERE user_id = ? AND status = 'completed' AND id <> ?
        """,
        (user_id, order_id),
    )
    row = await cur.fetchone()
    had_completed_before = int(row["c"] if row else 0) > 0
    if had_completed_before:
        return

    await conn.execute(
        "UPDATE users SET first_order_completed = 1 WHERE user_id = ?",
        (user_id,),
    )

    referrer_id = order["referrer_id"]
    commission_paid = int(order["commission_paid"] or 0)
    rub = float(order["rub_after_discounts"] or 0)
    commission = commission_for_first_order(rub, settings) if referrer_id else 0.0

    if referrer_id and commission > 0 and commission_paid == 0:
        await conn.execute(
            "UPDATE users SET ref_balance_rub = ref_balance_rub + ? WHERE user_id = ?",
            (commission, int(referrer_id)),
        )
        await conn.execute(
            "UPDATE orders SET commission_rub = ?, commission_paid = 1 WHERE id = ?",
            (commission, order_id),
        )
    await conn.commit()
