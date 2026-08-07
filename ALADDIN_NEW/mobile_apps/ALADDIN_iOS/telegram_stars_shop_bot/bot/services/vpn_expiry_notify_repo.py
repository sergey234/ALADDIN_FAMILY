"""Идемпотентность + retry VPN expiry/trial push в shop.db."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import aiosqlite

CHANNEL_TELEGRAM = "telegram"
STATUS_DELIVERED = "delivered"
STATUS_PENDING = "pending"
STATUS_FAILED = "failed"
STATUS_BLOCKED = "blocked"

MAX_ATTEMPTS = 3
RETRY_MINUTES = 30


async def ensure_vpn_expiry_notices_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vpn_expiry_notices (
            telegram_user_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            sent_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (telegram_user_id, kind)
        )
        """
    )
    for col, decl in (
        ("channel", "TEXT NOT NULL DEFAULT 'telegram'"),
        ("status", "TEXT NOT NULL DEFAULT 'delivered'"),
        ("attempts", "INTEGER NOT NULL DEFAULT 1"),
        ("last_error", "TEXT"),
        ("next_retry_at", "TEXT"),
    ):
        try:
            await conn.execute(
                f"ALTER TABLE vpn_expiry_notices ADD COLUMN {col} {decl}"
            )
        except Exception:
            pass
    await conn.commit()


async def notice_already_sent(
    conn: aiosqlite.Connection, *, telegram_user_id: int, kind: str
) -> bool:
    """True если уже доставлено или заблокировано / исчерпаны попытки."""
    cur = await conn.execute(
        """
        SELECT status, attempts FROM vpn_expiry_notices
        WHERE telegram_user_id = ? AND kind = ? LIMIT 1
        """,
        (int(telegram_user_id), str(kind).strip()),
    )
    row = await cur.fetchone()
    if row is None:
        return False
    status = str(row[0] or STATUS_DELIVERED).strip().lower()
    attempts = int(row[1] or 1)
    if status == STATUS_DELIVERED:
        return True
    if status == STATUS_BLOCKED:
        return True
    if status in (STATUS_PENDING, STATUS_FAILED) and attempts >= MAX_ATTEMPTS:
        return True
    return False


async def notice_ready_for_retry(
    conn: aiosqlite.Connection, *, telegram_user_id: int, kind: str, now: datetime | None = None
) -> bool:
    """Есть запись pending/failed с attempts < max и next_retry_at <= now."""
    cur = await conn.execute(
        """
        SELECT status, attempts, next_retry_at FROM vpn_expiry_notices
        WHERE telegram_user_id = ? AND kind = ? LIMIT 1
        """,
        (int(telegram_user_id), str(kind).strip()),
    )
    row = await cur.fetchone()
    if row is None:
        return False
    status = str(row[0] or "").strip().lower()
    attempts = int(row[1] or 0)
    if status not in (STATUS_PENDING, STATUS_FAILED):
        return False
    if attempts >= MAX_ATTEMPTS:
        return False
    raw = str(row[2] or "").strip()
    if not raw:
        return True
    try:
        retry_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    ref = now or datetime.now(timezone.utc)
    return retry_at <= ref


async def mark_notice_sent(
    conn: aiosqlite.Connection,
    *,
    telegram_user_id: int,
    kind: str,
    channel: str = CHANNEL_TELEGRAM,
) -> None:
    await conn.execute(
        """
        INSERT INTO vpn_expiry_notices (
            telegram_user_id, kind, sent_at, channel, status, attempts, last_error, next_retry_at
        ) VALUES (?, ?, datetime('now'), ?, ?, 1, NULL, NULL)
        ON CONFLICT(telegram_user_id, kind) DO UPDATE SET
            sent_at = datetime('now'),
            channel = excluded.channel,
            status = excluded.status,
            attempts = 1,
            last_error = NULL,
            next_retry_at = NULL
        """,
        (int(telegram_user_id), str(kind).strip(), channel, STATUS_DELIVERED),
    )
    await conn.commit()


async def mark_notice_failed(
    conn: aiosqlite.Connection,
    *,
    telegram_user_id: int,
    kind: str,
    error: str,
    blocked: bool = False,
    channel: str = CHANNEL_TELEGRAM,
) -> None:
    cur = await conn.execute(
        "SELECT attempts FROM vpn_expiry_notices WHERE telegram_user_id = ? AND kind = ?",
        (int(telegram_user_id), str(kind).strip()),
    )
    row = await cur.fetchone()
    attempts = int(row[0] or 0) + 1 if row else 1
    status = STATUS_BLOCKED if blocked else (
        STATUS_FAILED if attempts >= MAX_ATTEMPTS else STATUS_PENDING
    )
    next_retry = None
    if status == STATUS_PENDING:
        next_retry = (
            datetime.now(timezone.utc) + timedelta(minutes=RETRY_MINUTES)
        ).replace(microsecond=0).isoformat()
    err = (error or "")[:500]
    await conn.execute(
        """
        INSERT INTO vpn_expiry_notices (
            telegram_user_id, kind, sent_at, channel, status, attempts, last_error, next_retry_at
        ) VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?)
        ON CONFLICT(telegram_user_id, kind) DO UPDATE SET
            sent_at = datetime('now'),
            channel = excluded.channel,
            status = excluded.status,
            attempts = excluded.attempts,
            last_error = excluded.last_error,
            next_retry_at = excluded.next_retry_at
        """,
        (
            int(telegram_user_id),
            str(kind).strip(),
            channel,
            status,
            attempts,
            err,
            next_retry,
        ),
    )
    await conn.commit()


async def clear_notices_for_user(conn: aiosqlite.Connection, *, telegram_user_id: int) -> int:
    """Сброс цикла напоминаний после продления / нового trial."""
    cur = await conn.execute(
        "DELETE FROM vpn_expiry_notices WHERE telegram_user_id = ?",
        (int(telegram_user_id),),
    )
    await conn.commit()
    return int(cur.rowcount or 0)


async def list_recent_notices(
    conn: aiosqlite.Connection, *, limit: int = 30
) -> list[dict]:
    await ensure_vpn_expiry_notices_table(conn)
    cur = await conn.execute(
        """
        SELECT telegram_user_id, kind, sent_at, channel, status, attempts, last_error
        FROM vpn_expiry_notices
        ORDER BY sent_at DESC
        LIMIT ?
        """,
        (max(1, min(int(limit), 200)),),
    )
    rows = await cur.fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "telegram_user_id": int(r[0]),
                "kind": str(r[1]),
                "sent_at": str(r[2] or ""),
                "channel": str(r[3] or CHANNEL_TELEGRAM),
                "status": str(r[4] or STATUS_DELIVERED),
                "attempts": int(r[5] or 1),
                "last_error": str(r[6] or ""),
            }
        )
    return out
