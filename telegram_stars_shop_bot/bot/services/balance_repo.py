from __future__ import annotations

import aiosqlite


async def get_balance(conn: aiosqlite.Connection, user_id: int) -> float:
    cur = await conn.execute("SELECT balance_rub FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if not row:
        return 0.0
    return float(row["balance_rub"] or 0)


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
    """Увеличить баланс, записать ledger. Возвращает новый баланс."""
    bal = await get_balance(conn, user_id)
    new_bal = round(bal + delta, 2)
    await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, user_id))
    await _append_ledger(conn, user_id=user_id, amount_rub=delta, balance_after=new_bal, kind=kind, ref_type=ref_type, ref_id=ref_id)
    await conn.commit()
    return new_bal


async def charge_balance(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount: float,
    kind: str,
    ref_type: str | None = None,
    ref_id: int | None = None,
) -> float:
    """Списать с баланса (amount > 0). Возвращает новый баланс. ValueError если не хватает."""
    bal = await get_balance(conn, user_id)
    if bal + 1e-6 < amount:
        raise ValueError("insufficient_balance")
    new_bal = round(bal - amount, 2)
    await conn.execute("UPDATE users SET balance_rub = ? WHERE user_id = ?", (new_bal, user_id))
    await _append_ledger(conn, user_id=user_id, amount_rub=-amount, balance_after=new_bal, kind=kind, ref_type=ref_type, ref_id=ref_id)
    await conn.commit()
    return new_bal


async def create_topup_request(conn: aiosqlite.Connection, *, user_id: int, amount_rub: float) -> int:
    cur = await conn.execute(
        "INSERT INTO topup_requests (user_id, amount_rub, status) VALUES (?, ?, 'pending')",
        (user_id, amount_rub),
    )
    await conn.commit()
    return int(cur.lastrowid)


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


async def approve_topup(conn: aiosqlite.Connection, topup_id: int) -> bool:
    row = await get_topup(conn, topup_id)
    if not row or row["status"] != "pending":
        return False
    uid = int(row["user_id"])
    amount = float(row["amount_rub"])
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
        "UPDATE topup_requests SET status = 'completed' WHERE id = ?",
        (topup_id,),
    )
    await conn.commit()
    return True
