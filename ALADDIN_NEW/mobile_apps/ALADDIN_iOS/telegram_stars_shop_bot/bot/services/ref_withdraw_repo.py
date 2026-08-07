"""Заявки на вывод реферального бонуса: карта или крипта (ручная обработка)."""

from __future__ import annotations

import re

import aiosqlite

MIN_WITHDRAW_RUB = 1000.0

METHOD_CARD = "card"
METHOD_CRYPTO = "crypto"
CHANNEL_TRC20 = "usdt_trc20"
CHANNEL_CRYPTOBOT = "cryptobot"

_TRC20_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")
_CRYPTOBOT_RE = re.compile(r"^@?[A-Za-z][A-Za-z0-9_]{4,31}$")


def normalize_payout_target(*, method: str, crypto_channel: str | None, raw: str) -> str:
    t = (raw or "").strip()
    if method == METHOD_CARD:
        return t[:200] if t else "card_payout_request"
    ch = (crypto_channel or "").strip().lower()
    if ch == CHANNEL_TRC20:
        if not _TRC20_RE.match(t):
            raise ValueError("bad_trc20")
        return t
    if ch == CHANNEL_CRYPTOBOT:
        if not _CRYPTOBOT_RE.match(t):
            raise ValueError("bad_cryptobot")
        u = t if t.startswith("@") else f"@{t}"
        return u
    raise ValueError("bad_channel")


async def has_pending_withdraw(conn: aiosqlite.Connection, user_id: int) -> bool:
    cur = await conn.execute(
        """
        SELECT 1 FROM ref_withdraw_requests
        WHERE user_id = ? AND status = 'pending'
        LIMIT 1
        """,
        (int(user_id),),
    )
    return (await cur.fetchone()) is not None


async def create_withdraw_request(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    amount_rub: float,
    method: str = METHOD_CARD,
    crypto_channel: str | None = None,
    payout_target: str = "",
    details: str = "",
) -> int:
    amount = round(float(amount_rub), 2)
    if amount + 1e-6 < MIN_WITHDRAW_RUB:
        raise ValueError("below_min")
    if await has_pending_withdraw(conn, user_id):
        raise ValueError("pending_exists")

    method_n = (method or METHOD_CARD).strip().lower()
    if method_n not in (METHOD_CARD, METHOD_CRYPTO):
        raise ValueError("bad_method")

    channel_n: str | None = None
    if method_n == METHOD_CRYPTO:
        channel_n = (crypto_channel or "").strip().lower()
        if channel_n not in (CHANNEL_TRC20, CHANNEL_CRYPTOBOT):
            raise ValueError("bad_channel")
        target = normalize_payout_target(
            method=method_n, crypto_channel=channel_n, raw=payout_target
        )
        details_n = details.strip()[:500] if details else f"crypto:{channel_n}"
    else:
        target = normalize_payout_target(
            method=METHOD_CARD, crypto_channel=None, raw=payout_target or "card_payout_request"
        )
        details_n = (details or "card_payout_request").strip()[:500]

    cur = await conn.execute(
        """
        INSERT INTO ref_withdraw_requests (
            user_id, amount_rub, status, details, method, crypto_channel, payout_target
        )
        VALUES (?, ?, 'pending', ?, ?, ?, ?)
        """,
        (int(user_id), amount, details_n, method_n, channel_n, target),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def list_pending(conn: aiosqlite.Connection, *, limit: int = 20) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT id, user_id, amount_rub, details, method, crypto_channel, payout_target, created_at
        FROM ref_withdraw_requests
        WHERE status = 'pending'
        ORDER BY id ASC
        LIMIT ?
        """,
        (int(limit),),
    )
    return list(await cur.fetchall())


async def list_by_status(
    conn: aiosqlite.Connection,
    *,
    status: str,
    limit: int = 20,
) -> list[aiosqlite.Row]:
    st = (status or "").strip().lower()
    cur = await conn.execute(
        """
        SELECT id, user_id, amount_rub, details, method, crypto_channel, payout_target,
               status, created_at, updated_at
        FROM ref_withdraw_requests
        WHERE status = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (st, int(limit)),
    )
    return list(await cur.fetchall())


async def withdraw_status_summary(conn: aiosqlite.Connection) -> dict[str, float | int]:
    cur = await conn.execute(
        """
        SELECT status,
               COUNT(*) AS n,
               COALESCE(SUM(amount_rub), 0) AS rub
        FROM ref_withdraw_requests
        GROUP BY status
        """
    )
    rows = await cur.fetchall()
    out: dict[str, float | int] = {
        "pending_count": 0,
        "pending_rub": 0.0,
        "paid_count": 0,
        "paid_rub": 0.0,
        "rejected_count": 0,
        "rejected_rub": 0.0,
    }
    for r in rows:
        st = str(r["status"] or "").strip().lower()
        n = int(r["n"] or 0)
        rub = float(r["rub"] or 0)
        if st == "pending":
            out["pending_count"] = n
            out["pending_rub"] = rub
        elif st == "paid":
            out["paid_count"] = n
            out["paid_rub"] = rub
        elif st == "rejected":
            out["rejected_count"] = n
            out["rejected_rub"] = rub
    return out


async def set_withdraw_status(
    conn: aiosqlite.Connection,
    *,
    request_id: int,
    status: str,
    admin_note: str = "",
) -> bool:
    st = (status or "").strip().lower()
    if st not in ("paid", "rejected", "pending"):
        raise ValueError("bad_status")
    cur = await conn.execute(
        """
        UPDATE ref_withdraw_requests
        SET status = ?, admin_note = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (st, (admin_note or "").strip()[:500], int(request_id)),
    )
    await conn.commit()
    return cur.rowcount == 1


async def get_withdraw(conn: aiosqlite.Connection, request_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute(
        "SELECT * FROM ref_withdraw_requests WHERE id = ?",
        (int(request_id),),
    )
    return await cur.fetchone()


def format_withdraw_method_label(row: aiosqlite.Row | dict) -> str:
    keys = row.keys() if hasattr(row, "keys") else row
    method = str((row["method"] if "method" in keys else None) or "card").strip().lower()
    if method != METHOD_CRYPTO:
        return "card"
    ch = str((row["crypto_channel"] if "crypto_channel" in keys else None) or "").strip().lower()
    if ch == CHANNEL_TRC20:
        return "crypto/trc20"
    if ch == CHANNEL_CRYPTOBOT:
        return "crypto/cryptobot"
    return "crypto"
