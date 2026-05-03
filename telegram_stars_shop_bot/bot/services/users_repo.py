from __future__ import annotations

import time

import aiosqlite


async def upsert_user(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    username: str | None,
    first_name: str | None,
) -> None:
    await conn.execute(
        """
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name
        """,
        (user_id, username, first_name),
    )
    await conn.commit()


async def set_referrer_if_empty(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    referrer_id: int,
) -> bool:
    if user_id == referrer_id:
        return False
    cur = await conn.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if row is None:
        await upsert_user(conn, user_id=user_id, username=None, first_name=None)
    cur = await conn.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if row and row["referrer_id"] is not None:
        return False
    await conn.execute(
        "UPDATE users SET referrer_id = ? WHERE user_id = ? AND referrer_id IS NULL",
        (referrer_id, user_id),
    )
    await conn.commit()
    return True


async def get_user(conn: aiosqlite.Connection, user_id: int) -> aiosqlite.Row | None:
    cur = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return await cur.fetchone()


async def get_locale(conn: aiosqlite.Connection, user_id: int) -> str | None:
    """None или пусто — пользователь ещё не выбрал язык (показываем экран шага 0)."""
    row = await get_user(conn, user_id)
    if row is None:
        return None
    try:
        raw = row["locale"]
    except (KeyError, IndexError):
        return None
    if raw is None:
        return None
    s = str(raw).strip()
    return s if s else None


async def set_locale(conn: aiosqlite.Connection, user_id: int, locale: str) -> None:
    code = (locale or "").strip().lower()[:16]
    if not code:
        return
    await conn.execute("UPDATE users SET locale = ? WHERE user_id = ?", (code, user_id))
    await conn.commit()


async def has_terms_accepted(conn: aiosqlite.Connection, user_id: int) -> bool:
    row = await get_user(conn, user_id)
    if row is None:
        return False
    try:
        v = row["terms_accepted_at"]
    except (KeyError, IndexError):
        return False
    return v is not None and str(v).strip() != ""


async def accept_terms(conn: aiosqlite.Connection, user_id: int) -> None:
    await conn.execute(
        "UPDATE users SET terms_accepted_at = datetime('now') WHERE user_id = ?",
        (user_id,),
    )
    await conn.commit()


async def is_onboarding_completed(conn: aiosqlite.Connection, user_id: int) -> bool:
    row = await get_user(conn, user_id)
    if row is None:
        return False
    try:
        v = row["onboarding_completed_at"]
    except (KeyError, IndexError):
        return False
    return v is not None and str(v).strip() != ""


async def complete_onboarding(conn: aiosqlite.Connection, user_id: int) -> None:
    await conn.execute(
        "UPDATE users SET onboarding_completed_at = datetime('now') WHERE user_id = ?",
        (user_id,),
    )
    await conn.commit()


async def checkout_captcha_valid(conn: aiosqlite.Connection, user_id: int) -> bool:
    row = await get_user(conn, user_id)
    if row is None:
        return False
    try:
        raw = row["checkout_captcha_ok_until"]
    except (KeyError, IndexError):
        return False
    if raw is None:
        return False
    try:
        until = int(raw)
    except (TypeError, ValueError):
        return False
    return int(time.time()) <= until


async def extend_checkout_captcha(conn: aiosqlite.Connection, user_id: int, ttl_seconds: int) -> None:
    until = int(time.time()) + max(60, int(ttl_seconds))
    await conn.execute(
        "UPDATE users SET checkout_captcha_ok_until = ? WHERE user_id = ?",
        (until, user_id),
    )
    await conn.commit()


async def throttle_start_allowed(conn: aiosqlite.Connection, user_id: int, min_seconds: int) -> bool:
    if min_seconds <= 0:
        return True
    now = int(time.time())
    row = await get_user(conn, user_id)
    last: int | None = None
    if row is not None:
        try:
            raw = row["last_start_command_at"]
            last = int(raw) if raw is not None else None
        except (KeyError, TypeError, ValueError):
            last = None
    if last is not None and (now - last) < min_seconds:
        return False
    await conn.execute(
        "UPDATE users SET last_start_command_at = ? WHERE user_id = ?",
        (now, user_id),
    )
    await conn.commit()
    return True


async def has_seen_channel_member_ack(conn: aiosqlite.Connection, user_id: int) -> bool:
    cur = await conn.execute(
        "SELECT channel_member_ack_shown FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    return bool(row and int(row["channel_member_ack_shown"] or 0) == 1)


async def mark_channel_member_ack_seen(conn: aiosqlite.Connection, user_id: int) -> None:
    await conn.execute(
        "UPDATE users SET channel_member_ack_shown = 1 WHERE user_id = ?",
        (user_id,),
    )
    await conn.commit()


async def user_stats(conn: aiosqlite.Connection, user_id: int) -> dict[str, float | int]:
    from bot.services import balance_repo
    cur = await conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0) AS completed_cnt,
            COALESCE(SUM(CASE WHEN status = 'completed' THEN rub_after_discounts ELSE 0 END), 0) AS spent_rub
        FROM orders WHERE user_id = ?
        """,
        (user_id,),
    )
    row = await cur.fetchone()
    u = await get_user(conn, user_id)
    ref_balance = float(u["ref_balance_rub"]) if u else 0.0
    bal = await balance_repo.get_balance(conn, user_id)
    rcur = await conn.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM users WHERE referrer_id = ?) AS ref_invited,
            (
                SELECT COUNT(DISTINCT o.user_id)
                FROM orders o
                INNER JOIN users u ON u.user_id = o.user_id AND u.referrer_id = ?
                WHERE o.status = 'completed'
            ) AS ref_buyers_done,
            (
                SELECT COALESCE(SUM(commission_rub), 0)
                FROM orders
                WHERE referrer_id = ? AND COALESCE(commission_paid, 0) = 1
            ) AS ref_comm_earned
        """,
        (user_id, user_id, user_id),
    )
    rrow = await rcur.fetchone()
    return {
        "completed_orders": int(row["completed_cnt"] if row else 0),
        "spent_rub": float(row["spent_rub"] if row else 0),
        "ref_balance_rub": ref_balance,
        "balance_rub": bal,
        "referral_invited_count": int(rrow["ref_invited"] if rrow else 0),
        "referral_buyers_completed_count": int(rrow["ref_buyers_done"] if rrow else 0),
        "referral_commission_earned_rub": float(rrow["ref_comm_earned"] if rrow else 0.0),
    }
