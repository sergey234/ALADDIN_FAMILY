from __future__ import annotations

import aiosqlite

from bot.config import Settings


async def ensure_balance_user_row(conn: aiosqlite.Connection, user_id: int) -> None:
    """
    Гарантирует строку users для операций с балансом.
    Вызывать сразу после BEGIN IMMEDIATE в той же транзакции, до SELECT/UPDATE баланса.
    """
    await conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))


async def get_balance(conn: aiosqlite.Connection, user_id: int) -> float:
    cur = await conn.execute("SELECT balance_rub FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if not row:
        return 0.0
    return float(row["balance_rub"] or 0)


async def get_ref_balance(conn: aiosqlite.Connection, user_id: int) -> float:
    cur = await conn.execute("SELECT ref_balance_rub FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if not row:
        return 0.0
    return float(row["ref_balance_rub"] or 0)


async def get_balances(conn: aiosqlite.Connection, user_id: int) -> tuple[float, float]:
    """(main balance_rub, bonus ref_balance_rub)."""
    cur = await conn.execute(
        "SELECT balance_rub, ref_balance_rub FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    if not row:
        return 0.0, 0.0
    return float(row["balance_rub"] or 0), float(row["ref_balance_rub"] or 0)


async def debit_main_in_txn(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> float:
    """Списать с balance_rub внутри открытой транзакции. ValueError insufficient_main."""
    amt = round(float(amount), 2)
    if amt <= 0:
        return await get_balance(conn, user_id)
    bal = await get_balance(conn, user_id)
    if bal + 1e-6 < amt:
        raise ValueError("insufficient_main")
    cur = await conn.execute(
        """
        UPDATE users
        SET balance_rub = round(balance_rub - ?, 2)
        WHERE user_id = ? AND balance_rub + 1e-6 >= ?
        """,
        (amt, user_id, amt),
    )
    if cur.rowcount != 1:
        raise ValueError("insufficient_main")
    new_bal = round(bal - amt, 2)
    await _append_ledger(
        conn,
        user_id=user_id,
        amount_rub=-amt,
        balance_after=new_bal,
        kind=kind,
        ref_type=ref_type,
        ref_id=ref_id,
    )
    return new_bal


async def debit_bonus_in_txn(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> float:
    """Списать с ref_balance_rub внутри открытой транзакции."""
    amt = round(float(amount), 2)
    if amt <= 0:
        return await get_ref_balance(conn, user_id)
    bal = await get_ref_balance(conn, user_id)
    if bal + 1e-6 < amt:
        raise ValueError("insufficient_main")
    cur = await conn.execute(
        """
        UPDATE users
        SET ref_balance_rub = round(ref_balance_rub - ?, 2)
        WHERE user_id = ? AND ref_balance_rub + 1e-6 >= ?
        """,
        (amt, user_id, amt),
    )
    if cur.rowcount != 1:
        raise ValueError("insufficient_main")
    new_bal = round(bal - amt, 2)
    await _append_ledger(
        conn,
        user_id=user_id,
        amount_rub=-amt,
        balance_after=new_bal,
        kind=kind,
        ref_type=ref_type,
        ref_id=ref_id,
    )
    return new_bal


async def credit_bonus_in_txn(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> float:
    """Начислить ref_balance_rub + ledger внутри открытой транзакции."""
    amt = round(float(amount), 2)
    if amt <= 0:
        return await get_ref_balance(conn, user_id)
    bal = await get_ref_balance(conn, user_id)
    new_bal = round(bal + amt, 2)
    await conn.execute(
        "UPDATE users SET ref_balance_rub = ? WHERE user_id = ?",
        (new_bal, user_id),
    )
    await _append_ledger(
        conn,
        user_id=user_id,
        amount_rub=amt,
        balance_after=new_bal,
        kind=kind,
        ref_type=ref_type,
        ref_id=ref_id,
    )
    return new_bal


async def _append_ledger(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount_rub: float,
    balance_after: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> None:
    await conn.execute(
        """
        INSERT INTO ledger (user_id, amount_rub, balance_after, kind, ref_type, ref_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, amount_rub, balance_after, kind, ref_type, ref_id),
    )


async def add_balance(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    delta: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> float:
    """Увеличить баланс, записать ledger. Возвращает новый баланс. Отдельная транзакция BEGIN IMMEDIATE."""
    await conn.execute("BEGIN IMMEDIATE")
    try:
        await ensure_balance_user_row(conn, user_id)
        bal = await get_balance(conn, user_id)
        new_bal = round(bal + delta, 2)
        await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, user_id))
        await _append_ledger(
            conn, user_id=user_id, amount_rub=delta, balance_after=new_bal, kind=kind, ref_type=ref_type, ref_id=ref_id
        )
        await conn.commit()
        return new_bal
    except Exception:
        await conn.rollback()
        raise


async def charge_balance(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> float:
    """Списать с баланса (amount > 0). Отдельная транзакция BEGIN IMMEDIATE. ValueError если не хватает."""
    await conn.execute("BEGIN IMMEDIATE")
    try:
        await ensure_balance_user_row(conn, user_id)
        bal = await get_balance(conn, user_id)
        if bal + 1e-6 < amount:
            await conn.rollback()
            raise ValueError("insufficient_balance")
        new_bal = round(bal - amount, 2)
        await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, user_id))
        await _append_ledger(
            conn, user_id=user_id, amount_rub=-amount, balance_after=new_bal, kind=kind, ref_type=ref_type, ref_id=ref_id
        )
        await conn.commit()
        return new_bal
    except ValueError:
        raise
    except Exception:
        await conn.rollback()
        raise


async def create_topup_request(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount_rub: float,
    settings: Settings,
) -> int:
    amt = round(float(amount_rub), 2)
    if amt + 1e-6 < settings.topup_min_rub or amt - 1e-6 > settings.topup_max_rub:
        raise ValueError("topup_amount_invalid")

    await conn.execute("BEGIN IMMEDIATE")
    try:
        cap = settings.topup_max_pending_per_user
        if cap > 0:
            cur = await conn.execute(
                "SELECT COUNT(*) AS c FROM topup_requests WHERE user_id = ? AND status = 'pending'",
                (user_id,),
            )
            row = await cur.fetchone()
            n = int(row["c"] if row else 0)
            if n >= cap:
                await conn.rollback()
                raise ValueError("topup_pending_cap")

        interval = settings.topup_min_interval_seconds
        if interval > 0:
            cur = await conn.execute(
                """
                SELECT CAST(
                    (julianday('now') - julianday(MAX(created_at))) * 86400 AS INTEGER
                ) AS secs
                FROM topup_requests WHERE user_id = ?
                """,
                (user_id,),
            )
            row = await cur.fetchone()
            secs = row["secs"] if row else None
            if secs is not None and int(secs) < interval:
                await conn.rollback()
                raise ValueError("topup_rate_limit")

        cur = await conn.execute(
            "INSERT INTO topup_requests (user_id, amount_rub, status) VALUES (?, ?, 'pending')",
            (user_id, amt),
        )
        await conn.commit()
        return int(cur.lastrowid)
    except ValueError:
        raise
    except Exception:
        await conn.rollback()
        raise


async def get_topup(conn: aiosqlite.Connection, topup_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM topup_requests WHERE id = ?", (topup_id,))
    return await cur.fetchone()


async def list_topups_for_user(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    limit: int = 50,
) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM topup_requests
        WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (user_id, limit),
    )
    return await cur.fetchall()


async def get_topup_for_user(
    conn: aiosqlite.Connection,
    topup_id: int,
    user_id: int,
) -> aiosqlite.Row | None:
    cur = await conn.execute(
        "SELECT * FROM topup_requests WHERE id = ? AND user_id = ?",
        (topup_id, user_id),
    )
    return await cur.fetchone()


async def approve_topup_no_commit(conn: aiosqlite.Connection, topup_id: int) -> bool:
    """Зачислить pending topup без commit (для webhook в общей транзакции)."""
    row = await get_topup(conn, topup_id)
    if not row or row["status"] != "pending":
        return False
    uid = int(row["user_id"])
    amount = float(row["amount_rub"])
    await ensure_balance_user_row(conn, uid)
    bal = await get_balance(conn, uid)
    new_bal = round(bal + amount, 2)
    await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, uid))
    await _append_ledger(
        conn,
        user_id=uid,
        amount_rub=amount,
        balance_after=new_bal,
        kind="topup",
        ref_type="topup_request",
        ref_id=topup_id,
    )
    await conn.execute(
        "UPDATE topup_requests SET status = 'completed' WHERE id = ? AND status = 'pending'",
        (topup_id,),
    )
    return True


async def approve_topup(conn: aiosqlite.Connection, topup_id: int) -> bool:
    await conn.execute("BEGIN IMMEDIATE")
    try:
        ok = await approve_topup_no_commit(conn, topup_id)
        if not ok:
            await conn.rollback()
            return False
        await conn.commit()
        return True
    except Exception:
        await conn.rollback()
        raise


async def attach_topup_payment_meta(
    conn: aiosqlite.Connection,
    topup_id: int,
    *,
    payment_method: str,
    payment_provider: str,
    external_invoice_id: str | None = None,
    pay_url: str | None = None,
    lava_attempt: int = 1,
) -> None:
    await conn.execute(
        """
        UPDATE topup_requests SET
            payment_method = ?,
            payment_provider = ?,
            external_invoice_id = COALESCE(?, external_invoice_id),
            pay_url = COALESCE(?, pay_url),
            lava_attempt = ?
        WHERE id = ? AND status = 'pending'
        """,
        (
            payment_method,
            payment_provider,
            external_invoice_id,
            pay_url,
            int(lava_attempt),
            topup_id,
        ),
    )
    await conn.commit()


async def cancel_topup(conn: aiosqlite.Connection, topup_id: int, user_id: int) -> bool:
    await conn.execute("BEGIN IMMEDIATE")
    try:
        row = await get_topup_for_user(conn, topup_id, user_id)
        if not row or row["status"] != "pending":
            await conn.rollback()
            return False
        await conn.execute(
            """
            UPDATE topup_requests
            SET status = 'cancelled', cancelled_at = datetime('now')
            WHERE id = ? AND user_id = ? AND status = 'pending'
            """,
            (topup_id, user_id),
        )
        await conn.commit()
        return True
    except Exception:
        await conn.rollback()
        raise


async def list_lava_pending_topups(conn: aiosqlite.Connection, *, limit: int = 20) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM topup_requests
        WHERE status = 'pending'
          AND payment_provider = 'lava'
          AND external_invoice_id IS NOT NULL
          AND TRIM(external_invoice_id) != ''
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    )
    return await cur.fetchall()
