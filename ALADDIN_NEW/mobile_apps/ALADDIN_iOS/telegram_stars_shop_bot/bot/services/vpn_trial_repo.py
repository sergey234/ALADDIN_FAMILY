"""Идемпотентность trial-запросов в shop.db."""

from __future__ import annotations

from pathlib import Path

import aiosqlite


async def ensure_vpn_trial_requests_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vpn_trial_requests (
            telegram_user_id INTEGER PRIMARY KEY,
            requested_at TEXT NOT NULL,
            provision_order_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
        """
    )
    await conn.commit()


async def upsert_trial_request(
    conn: aiosqlite.Connection,
    *,
    telegram_user_id: int,
    provision_order_id: int,
    status: str = "pending",
) -> None:
    await ensure_vpn_trial_requests_table(conn)
    await conn.execute(
        """
        INSERT INTO vpn_trial_requests (telegram_user_id, requested_at, provision_order_id, status)
        VALUES (?, datetime('now'), ?, ?)
        ON CONFLICT(telegram_user_id) DO UPDATE SET
            requested_at = excluded.requested_at,
            provision_order_id = excluded.provision_order_id,
            status = excluded.status
        """,
        (int(telegram_user_id), int(provision_order_id), str(status)),
    )
    await conn.commit()


async def mark_trial_delivered(conn: aiosqlite.Connection, *, telegram_user_id: int) -> None:
    await ensure_vpn_trial_requests_table(conn)
    await conn.execute(
        """
        UPDATE vpn_trial_requests SET status = 'delivered'
        WHERE telegram_user_id = ? AND status IN ('pending', 'delivered')
        """,
        (int(telegram_user_id),),
    )
    await conn.commit()


async def mark_trial_expired(conn: aiosqlite.Connection, *, telegram_user_id: int) -> None:
    await ensure_vpn_trial_requests_table(conn)
    await conn.execute(
        """
        UPDATE vpn_trial_requests SET status = 'expired'
        WHERE telegram_user_id = ?
        """,
        (int(telegram_user_id),),
    )
    await conn.commit()


async def sync_trial_request_statuses_from_vpn(
    shop: aiosqlite.Connection,
    vpn_db_path: Path | str,
) -> dict[str, int]:
    """
    Выравнивает shop.vpn_trial_requests по vpn.db (delivered / expired / paid_after_trial).
    Не трогает строки без записи в vpn_accounts.
    """
    await ensure_vpn_trial_requests_table(shop)
    vpn = await aiosqlite.connect(str(vpn_db_path))
    vpn.row_factory = aiosqlite.Row
    updated = {"delivered": 0, "expired": 0, "paid_after_trial": 0}
    try:
        cur = await shop.execute("SELECT telegram_user_id, status FROM vpn_trial_requests")
        rows = await cur.fetchall()
        for row in rows:
            tid = int(row["telegram_user_id"])
            old = str(row["status"] or "")
            vcur = await vpn.execute(
                """
                SELECT status, account_kind FROM vpn_accounts
                WHERE telegram_user_id = ? LIMIT 1
                """,
                (tid,),
            )
            vrow = await vcur.fetchone()
            if vrow is None:
                continue
            vst = str(vrow["status"] or "")
            kind = str(vrow["account_kind"] or "")
            if vst == "vpn_expired" and old != "expired":
                await mark_trial_expired(shop, telegram_user_id=tid)
                updated["expired"] += 1
            elif kind == "paid" and old not in ("paid_after_trial", "expired"):
                await shop.execute(
                    "UPDATE vpn_trial_requests SET status = 'paid_after_trial' "
                    "WHERE telegram_user_id = ?",
                    (tid,),
                )
                await shop.commit()
                updated["paid_after_trial"] += 1
            elif vst == "vpn_active" and kind == "trial" and old == "pending":
                await mark_trial_delivered(shop, telegram_user_id=tid)
                updated["delivered"] += 1
    finally:
        await vpn.close()
    return updated
