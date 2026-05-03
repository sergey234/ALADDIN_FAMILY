from __future__ import annotations

import aiosqlite

from bot.config import Settings
from bot.services import orders_repo
from bot.services.pricing import commission_for_first_order


def _fulfillment_applied_at(order: aiosqlite.Row) -> str | None:
    try:
        v = order["fulfillment_applied_at"]
    except (KeyError, IndexError):
        return None
    return str(v) if v is not None else None


async def apply_completed_side_effects(conn: aiosqlite.Connection, order_id: int, settings: Settings) -> None:
    """
    Вызывать после перевода заказа в status=completed.
    Идемпотентно (один раз на заказ): колонка fulfillment_applied_at + атомарный UPDATE commission_paid.

    Первый завершённый (выданный) заказ пользователя: first_order_completed и комиссия рефереру
    (процент от суммы заказа в ₽ после скидок - см. Settings), если есть referrer и комиссия ещё не проведена.
    Скидка покупателю по рефкоду (`quote_product` / is_first_order) тоже действует до первого completed.
    """
    await conn.execute("BEGIN IMMEDIATE")
    try:
        order = await orders_repo.get_order(conn, order_id)
        if order is None or str(order["status"]) != "completed":
            await conn.rollback()
            return
        if _fulfillment_applied_at(order):
            await conn.rollback()
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
            await conn.execute(
                """
                UPDATE orders SET fulfillment_applied_at = datetime('now')
                WHERE id = ? AND fulfillment_applied_at IS NULL
                """,
                (order_id,),
            )
            await orders_repo.write_profit_snapshot(conn, order_id, settings)
            await conn.commit()
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
            ucur = await conn.execute(
                """
                UPDATE orders
                SET commission_rub = ?, commission_paid = 1,
                    fulfillment_applied_at = datetime('now')
                WHERE id = ? AND commission_paid = 0 AND fulfillment_applied_at IS NULL
                """,
                (commission, order_id),
            )
            if ucur.rowcount != 1:
                await conn.rollback()
                return
            await conn.execute(
                "UPDATE users SET ref_balance_rub = round(ref_balance_rub + ?, 2) WHERE user_id = ?",
                (commission, int(referrer_id)),
            )
        else:
            await conn.execute(
                """
                UPDATE orders SET fulfillment_applied_at = datetime('now')
                WHERE id = ? AND fulfillment_applied_at IS NULL
                """,
                (order_id,),
            )
        await orders_repo.write_profit_snapshot(conn, order_id, settings)
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
