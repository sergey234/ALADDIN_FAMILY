from __future__ import annotations

import sqlite3

import aiosqlite


async def create_order(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    product_id: str,
    product_title: str,
    payment_method: str,
    usd_base: float,
    rub_before: float,
    rub_after: float,
    referral_discount_rub: float,
    wholesale_discount_rub: float,
    referrer_id: int | None,
    commission_rub: float,
    user_note: str | None,
    status: str = "pending_payment",
    balance_applied_rub: float = 0.0,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO orders (
            user_id, product_id, product_title, payment_method, status,
            usd_base, rub_before_discounts, rub_after_discounts,
            referral_discount_rub, wholesale_discount_rub,
            referrer_id, commission_rub, user_note, balance_applied_rub
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            product_id,
            product_title,
            payment_method,
            status,
            usd_base,
            rub_before,
            rub_after,
            referral_discount_rub,
            wholesale_discount_rub,
            referrer_id,
            commission_rub,
            user_note,
            balance_applied_rub,
        ),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def update_status(conn: aiosqlite.Connection, order_id: int, status: str) -> None:
    await update_status_no_commit(conn, order_id, status)
    await conn.commit()


async def update_status_no_commit(conn: aiosqlite.Connection, order_id: int, status: str) -> None:
    await conn.execute(
        """
        UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (status, order_id),
    )


async def list_recent_orders(conn: aiosqlite.Connection, limit: int = 15) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        "SELECT * FROM orders ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return await cur.fetchall()


async def list_user_orders(conn: aiosqlite.Connection, user_id: int, limit: int = 20) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    return await cur.fetchall()


async def list_user_orders_page(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    limit: int,
    offset: int,
) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM orders WHERE user_id = ?
        ORDER BY id DESC LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset),
    )
    return await cur.fetchall()


async def get_order(conn: aiosqlite.Connection, order_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    return await cur.fetchone()


async def count_user_orders(conn: aiosqlite.Connection, user_id: int) -> int:
    cur = await conn.execute("SELECT COUNT(*) AS c FROM orders WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    return int(row["c"] if row else 0)


async def count_user_completed_orders(conn: aiosqlite.Connection, user_id: int) -> int:
    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,),
    )
    row = await cur.fetchone()
    return int(row["c"] if row else 0)


def _balance_applied_from_row(order: aiosqlite.Row) -> float:
    try:
        return float(order["balance_applied_rub"] or 0)
    except (KeyError, IndexError, TypeError):
        return 0.0


async def create_paid_order_from_balance(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    product_id: str,
    product_title: str,
    usd_base: float,
    rub_before: float,
    rub_after: float,
    referral_discount_rub: float,
    wholesale_discount_rub: float,
    referrer_id: int | None,
    user_note: str | None,
) -> int:
    """Атомарно: списание баланса + заказ со статусом paid + запись в ledger."""
    from bot.services import balance_repo

    await conn.execute("BEGIN IMMEDIATE")
    try:
        bal = await balance_repo.get_balance(conn, user_id)
        if bal + 1e-6 < rub_after:
            await conn.rollback()
            raise ValueError("insufficient_balance")
        new_bal = round(bal - rub_after, 2)
        await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, user_id))
        cur = await conn.execute(
            """
            INSERT INTO orders (
                user_id, product_id, product_title, payment_method, status,
                usd_base, rub_before_discounts, rub_after_discounts,
                referral_discount_rub, wholesale_discount_rub,
                referrer_id, commission_rub, user_note, balance_applied_rub
            ) VALUES (?, ?, ?, 'balance', 'paid', ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                user_id,
                product_id,
                product_title,
                usd_base,
                rub_before,
                rub_after,
                referral_discount_rub,
                wholesale_discount_rub,
                referrer_id,
                user_note,
                rub_after,
            ),
        )
        oid = int(cur.lastrowid)
        await conn.execute(
            """
            INSERT INTO ledger (user_id, amount_rub, balance_after, kind, ref_type, ref_id)
            VALUES (?, ?, ?, 'order_pay', 'order', ?)
            """,
            (user_id, -rub_after, new_bal, oid),
        )
        await conn.commit()
        return oid
    except Exception:
        await conn.rollback()
        raise


async def create_order_with_balance_partial(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    product_id: str,
    product_title: str,
    payment_method: str,
    usd_base: float,
    rub_before: float,
    rub_invoice_total: float,
    referral_discount_rub: float,
    wholesale_discount_rub: float,
    referrer_id: int | None,
    user_note: str | None,
    balance_apply: float,
) -> int:
    """
    Списывает balance_apply с кошелька, создаёт заказ.
    Если доплата ~0 — сразу paid; иначе pending_payment и payment_method mix_fiat / mix_crypto.
    """
    from bot.services import balance_repo

    balance_apply = round(balance_apply, 2)
    if balance_apply <= 0:
        raise ValueError("invalid_balance_apply")
    remainder = round(rub_invoice_total - balance_apply, 2)
    if remainder < -1e-6:
        raise ValueError("balance_exceeds_total")

    await conn.execute("BEGIN IMMEDIATE")
    try:
        bal = await balance_repo.get_balance(conn, user_id)
        if bal + 1e-6 < balance_apply:
            await conn.rollback()
            raise ValueError("insufficient_balance")
        new_bal = round(bal - balance_apply, 2)
        await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, user_id))

        if remainder <= 0.01:
            status = "paid"
        else:
            status = "pending_payment"

        cur = await conn.execute(
            """
            INSERT INTO orders (
                user_id, product_id, product_title, payment_method, status,
                usd_base, rub_before_discounts, rub_after_discounts,
                referral_discount_rub, wholesale_discount_rub,
                referrer_id, commission_rub, user_note, balance_applied_rub
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                user_id,
                product_id,
                product_title,
                payment_method,
                status,
                usd_base,
                rub_before,
                rub_invoice_total,
                referral_discount_rub,
                wholesale_discount_rub,
                referrer_id,
                user_note,
                balance_apply,
            ),
        )
        oid = int(cur.lastrowid)
        await conn.execute(
            """
            INSERT INTO ledger (user_id, amount_rub, balance_after, kind, ref_type, ref_id)
            VALUES (?, ?, ?, 'order_pay', 'order', ?)
            """,
            (user_id, -balance_apply, new_bal, oid),
        )
        await conn.commit()
        return oid
    except Exception:
        await conn.rollback()
        raise


def amount_due_external(order: aiosqlite.Row) -> float:
    """Сколько ещё оплатить внешне (фиат/крипта)."""
    total = float(order["rub_after_discounts"] or 0)
    applied = _balance_applied_from_row(order)
    return max(0.0, round(total - applied, 2))


async def find_order_by_idempotency(
    conn: aiosqlite.Connection,
    *,
    api_client_id: int,
    idempotency_key: str,
) -> aiosqlite.Row | None:
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE api_client_id = ? AND idempotency_key = ?
        """,
        (api_client_id, idempotency_key),
    )
    return await cur.fetchone()


async def create_order_partner_api(
    conn: aiosqlite.Connection,
    *,
    owner_user_id: int,
    api_client_id: int,
    idempotency_key: str,
    external_ref: str | None,
    product_id: str,
    product_title: str,
    payment_method: str,
    usd_base: float,
    rub_before: float,
    rub_after: float,
    referral_discount_rub: float,
    wholesale_discount_rub: float,
    referrer_id: int | None,
    user_note: str,
) -> tuple[int, bool]:
    """
    Атомарно: идемпотентность + вставка заказа source=api.
    Возвращает (order_id, created_new).
    """
    await conn.execute("BEGIN IMMEDIATE")
    try:
        cur = await conn.execute(
            """
            SELECT id FROM orders
            WHERE api_client_id = ? AND idempotency_key = ?
            """,
            (api_client_id, idempotency_key),
        )
        row = await cur.fetchone()
        if row:
            await conn.commit()
            return int(row["id"]), False

        try:
            cur = await conn.execute(
                """
                INSERT INTO orders (
                    user_id, product_id, product_title, payment_method, status,
                    usd_base, rub_before_discounts, rub_after_discounts,
                    referral_discount_rub, wholesale_discount_rub,
                    referrer_id, commission_rub, user_note, balance_applied_rub,
                    source, api_client_id, idempotency_key, external_ref
                ) VALUES (?, ?, ?, ?, 'pending_payment', ?, ?, ?, ?, ?, ?, 0, ?, 0, 'api', ?, ?, ?)
                """,
                (
                    owner_user_id,
                    product_id,
                    product_title,
                    payment_method,
                    usd_base,
                    rub_before,
                    rub_after,
                    referral_discount_rub,
                    wholesale_discount_rub,
                    referrer_id,
                    user_note,
                    api_client_id,
                    idempotency_key,
                    external_ref,
                ),
            )
            oid = int(cur.lastrowid)
            await conn.commit()
            return oid, True
        except (sqlite3.IntegrityError, aiosqlite.IntegrityError):
            await conn.rollback()
            await conn.execute("BEGIN IMMEDIATE")
            cur = await conn.execute(
                "SELECT id FROM orders WHERE api_client_id = ? AND idempotency_key = ?",
                (api_client_id, idempotency_key),
            )
            row2 = await cur.fetchone()
            await conn.commit()
            if row2:
                return int(row2["id"]), False
            raise
    except Exception:
        await conn.rollback()
        raise


async def list_orders_api_for_owner(
    conn: aiosqlite.Connection,
    owner_user_id: int,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE user_id = ? AND source = 'api'
        ORDER BY id DESC LIMIT ? OFFSET ?
        """,
        (owner_user_id, limit, offset),
    )
    return await cur.fetchall()


async def get_order_api_for_owner(
    conn: aiosqlite.Connection,
    order_id: int,
    owner_user_id: int,
) -> aiosqlite.Row | None:
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE id = ? AND user_id = ? AND source = 'api'
        """,
        (order_id, owner_user_id),
    )
    return await cur.fetchone()
