from __future__ import annotations

import secrets
import string
from typing import Any

import aiosqlite

from bot.config import Settings

_CODE_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits
_CODE_LEN = 8


def is_vpn_order_row(order: aiosqlite.Row) -> bool:
    pk = str(order["product_kind"] or "").strip().lower()
    pid = str(order["product_id"] or "").strip().lower()
    return pk == "vpn" or pid.startswith("vpn")


async def resolve_code_owner(conn: aiosqlite.Connection, code: str) -> int | None:
    c = (code or "").strip()
    if len(c) < 4 or len(c) > 32:
        return None
    cur = await conn.execute("SELECT user_id FROM vpn_referral_codes WHERE code = ?", (c,))
    row = await cur.fetchone()
    if row is None:
        return None
    return int(row["user_id"])


def _random_code() -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LEN))


async def ensure_my_vpn_referral_code(conn: aiosqlite.Connection, user_id: int) -> str:
    cur = await conn.execute("SELECT code FROM vpn_referral_codes WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    if row and row["code"]:
        return str(row["code"])
    for _ in range(12):
        code = _random_code()
        try:
            await conn.execute(
                "INSERT INTO vpn_referral_codes (user_id, code) VALUES (?, ?)",
                (user_id, code),
            )
            await conn.commit()
            return code
        except aiosqlite.IntegrityError:
            await conn.rollback()
            continue
    raise RuntimeError("vpn_referral_codes: could not allocate unique code")


async def user_vpn_referral_stats(conn: aiosqlite.Connection, user_id: int) -> dict[str, Any]:
    cur = await conn.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM vpn_referral_grants WHERE referrer_user_id = ?) AS vpn_buyers,
            (SELECT COALESCE(SUM(referrer_days), 0) FROM vpn_referral_grants WHERE referrer_user_id = ?) AS days_earned
        """,
        (user_id, user_id),
    )
    row = await cur.fetchone()
    return {
        "vpn_referral_buyers": int(row["vpn_buyers"] or 0) if row else 0,
        "vpn_referral_days_earned": int(row["days_earned"] or 0) if row else 0,
    }


async def try_insert_vpn_referral_grant(
    conn: aiosqlite.Connection,
    order: aiosqlite.Row,
    settings: Settings,
) -> dict[str, Any] | None:
    """Один бонус на приглашённого за первую выданную VPN-покупку. Возвращает dict для вызова VPN API после commit."""
    ref_d = int(settings.vpn_referral_referrer_days)
    friend_d = int(settings.vpn_referral_friend_days)
    if ref_d <= 0 and friend_d <= 0:
        return None
    if not is_vpn_order_row(order):
        return None
    ref = order["referrer_id"]
    if ref is None:
        return None
    referrer_id = int(ref)
    user_id = int(order["user_id"])
    order_id = int(order["id"])
    if referrer_id == user_id:
        return None

    cur = await conn.execute(
        """
        SELECT COUNT(*) AS c FROM orders
        WHERE user_id = ? AND status = 'completed' AND id <> ?
          AND (
            lower(trim(COALESCE(product_kind, ''))) = 'vpn'
            OR lower(trim(product_id)) LIKE 'vpn%'
          )
        """,
        (user_id, order_id),
    )
    row = await cur.fetchone()
    if row and int(row["c"] or 0) > 0:
        return None

    try:
        await conn.execute(
            """
            INSERT INTO vpn_referral_grants (
                referred_user_id, referrer_user_id, order_id, friend_days, referrer_days
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, referrer_id, order_id, friend_d, ref_d),
        )
    except aiosqlite.IntegrityError:
        return None

    return {
        "order_id": order_id,
        "referred_user_id": user_id,
        "referrer_user_id": referrer_id,
        "friend_days": friend_d,
        "referrer_days": ref_d,
    }


async def record_grant_api_results(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    friend: tuple[bool, str] | None,
    referrer: tuple[bool, str] | None,
) -> None:
    """Фиксирует результат вызова VPN API по сторонам бонуса (идемпотентные ключи на стороне VPN API)."""
    sets: list[str] = []
    args: list[Any] = []
    if friend is not None:
        ok, err = friend
        if ok:
            sets.append("api_friend_ok = 1")
            sets.append("api_friend_last_error = NULL")
        else:
            sets.append("api_friend_attempts = api_friend_attempts + 1")
            sets.append("api_friend_last_error = ?")
            args.append((err or "")[:900])
    if referrer is not None:
        ok, err = referrer
        if ok:
            sets.append("api_referrer_ok = 1")
            sets.append("api_referrer_last_error = NULL")
        else:
            sets.append("api_referrer_attempts = api_referrer_attempts + 1")
            sets.append("api_referrer_last_error = ?")
            args.append((err or "")[:900])
    if not sets:
        return
    args.append(order_id)
    sql = f"UPDATE vpn_referral_grants SET {', '.join(sets)} WHERE order_id = ?"
    await conn.execute(sql, args)
    await conn.commit()


async def list_grants_needing_vpn_api_retry(
    conn: aiosqlite.Connection,
    *,
    max_attempts: int,
    limit: int = 12,
) -> list[aiosqlite.Row]:
    lim = max(1, min(50, int(limit)))
    ma = max(1, int(max_attempts))
    cur = await conn.execute(
        """
        SELECT id, order_id, referred_user_id, referrer_user_id, friend_days, referrer_days,
               api_friend_ok, api_referrer_ok, api_friend_attempts, api_referrer_attempts
        FROM vpn_referral_grants
        WHERE
          (friend_days > 0 AND api_friend_ok = 0 AND api_friend_attempts < ?)
          OR (referrer_days > 0 AND api_referrer_ok = 0 AND api_referrer_attempts < ?)
        ORDER BY created_at ASC
        LIMIT ?
        """,
        (ma, ma, lim),
    )
    return await cur.fetchall()
