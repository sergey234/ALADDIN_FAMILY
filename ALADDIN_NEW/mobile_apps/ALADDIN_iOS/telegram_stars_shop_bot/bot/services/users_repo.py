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


def _col_accepted(row: aiosqlite.Row | None, column: str) -> bool:
    if row is None:
        return False
    try:
        v = row[column]
    except (KeyError, IndexError):
        return False
    return v is not None and str(v).strip() != ""


async def vpn_legal_ack_flags(conn: aiosqlite.Connection, user_id: int) -> tuple[bool, bool]:
    row = await get_user(conn, user_id)
    privacy = _col_accepted(row, "vpn_privacy_accepted_at")
    terms = _col_accepted(row, "vpn_terms_accepted_at")
    return privacy, terms


async def has_vpn_legal_accepted(conn: aiosqlite.Connection, user_id: int) -> bool:
    """VPN docs gate: skip if shop onboarding terms already accepted (согласие один раз на старте)."""
    if await has_terms_accepted(conn, user_id):
        return True
    p, t = await vpn_legal_ack_flags(conn, user_id)
    return p and t


async def accept_vpn_privacy(conn: aiosqlite.Connection, user_id: int) -> None:
    await conn.execute(
        "UPDATE users SET vpn_privacy_accepted_at = datetime('now') WHERE user_id = ?",
        (user_id,),
    )
    await conn.commit()


async def accept_vpn_terms(conn: aiosqlite.Connection, user_id: int) -> None:
    await conn.execute(
        "UPDATE users SET vpn_terms_accepted_at = datetime('now') WHERE user_id = ?",
        (user_id,),
    )
    await conn.commit()


async def accept_vpn_legal_both(conn: aiosqlite.Connection, user_id: int) -> None:
    """Одно подтверждение: политика + соглашение VPN сразу."""
    await conn.execute(
        "UPDATE users SET "
        "vpn_privacy_accepted_at = COALESCE(vpn_privacy_accepted_at, datetime('now')), "
        "vpn_terms_accepted_at = COALESCE(vpn_terms_accepted_at, datetime('now')) "
        "WHERE user_id = ?",
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


async def clear_checkout_captcha(conn: aiosqlite.Connection, user_id: int) -> None:
    """Сброс окна капчи — следующий заказ снова потребует проверку."""
    await conn.execute(
        "UPDATE users SET checkout_captcha_ok_until = NULL WHERE user_id = ?",
        (user_id,),
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
                SELECT COUNT(DISTINCT o.user_id)
                FROM orders o
                INNER JOIN users u ON u.user_id = o.user_id AND u.referrer_id = ?
                WHERE o.status = 'completed'
                  AND LOWER(COALESCE(o.product_kind, '')) = 'vpn'
                  AND o.fulfillment_applied_at IS NOT NULL
            ) AS ref_vpn_buyers_done,
            (
                SELECT COALESCE(SUM(commission_rub), 0)
                FROM orders
                WHERE referrer_id = ? AND COALESCE(commission_paid, 0) = 1
            ) AS ref_comm_earned
        """,
        (user_id, user_id, user_id, user_id),
    )
    rrow = await rcur.fetchone()
    partner_status = "basic"
    override_pct: float | None = None
    if u is not None:
        try:
            partner_status = str(u["ref_partner_status"] or "basic").strip().lower() or "basic"
        except (KeyError, IndexError, TypeError):
            partner_status = "basic"
        try:
            raw_ov = u["ref_commission_override_pct"]
            if raw_ov is not None:
                override_pct = float(raw_ov)
        except (KeyError, IndexError, TypeError, ValueError):
            override_pct = None
    return {
        "completed_orders": int(row["completed_cnt"] if row else 0),
        "spent_rub": float(row["spent_rub"] if row else 0),
        "ref_balance_rub": ref_balance,
        "balance_rub": bal,
        "referral_invited_count": int(rrow["ref_invited"] if rrow else 0),
        "referral_buyers_completed_count": int(rrow["ref_buyers_done"] if rrow else 0),
        "referral_vpn_buyers_completed_count": int(rrow["ref_vpn_buyers_done"] if rrow else 0),
        "referral_commission_earned_rub": float(rrow["ref_comm_earned"] if rrow else 0.0),
        "ref_partner_status": partner_status,
        "ref_commission_override_pct": override_pct if override_pct is not None else -1.0,
    }


async def find_user_id_by_username(conn: aiosqlite.Connection, username: str) -> int | None:
    nick = (username or "").strip().lstrip("@").lower()
    if len(nick) < 2:
        return None
    cur = await conn.execute(
        """
        SELECT user_id FROM users
        WHERE LOWER(TRIM(COALESCE(username, ''))) = ?
        LIMIT 1
        """,
        (nick,),
    )
    row = await cur.fetchone()
    return int(row["user_id"]) if row else None


async def user_product_counts(
    conn: aiosqlite.Connection, user_id: int
) -> dict[str, int | float]:
    """Completed units/revenue by product kind for admin card."""
    cur = await conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN LOWER(COALESCE(product_kind,'')) = 'vpn'
                OR LOWER(COALESCE(product_id,'')) LIKE 'vpn%' THEN 1 ELSE 0 END), 0) AS vpn_n,
            COALESCE(SUM(CASE WHEN LOWER(COALESCE(product_kind,'')) = 'vpn'
                OR LOWER(COALESCE(product_id,'')) LIKE 'vpn%'
                THEN rub_after_discounts ELSE 0 END), 0) AS vpn_rub,
            COALESCE(SUM(CASE WHEN LOWER(COALESCE(product_kind,'')) IN ('stars','star')
                OR LOWER(COALESCE(product_id,'')) LIKE 'stars%' THEN 1 ELSE 0 END), 0) AS stars_n,
            COALESCE(SUM(CASE WHEN LOWER(COALESCE(product_kind,'')) IN ('stars','star')
                OR LOWER(COALESCE(product_id,'')) LIKE 'stars%'
                THEN rub_after_discounts ELSE 0 END), 0) AS stars_rub,
            COALESCE(SUM(CASE WHEN LOWER(COALESCE(product_kind,'')) IN ('premium','tg_premium')
                OR LOWER(COALESCE(product_id,'')) LIKE 'premium%' THEN 1 ELSE 0 END), 0) AS prem_n,
            COALESCE(SUM(CASE WHEN LOWER(COALESCE(product_kind,'')) IN ('premium','tg_premium')
                OR LOWER(COALESCE(product_id,'')) LIKE 'premium%'
                THEN rub_after_discounts ELSE 0 END), 0) AS prem_rub
        FROM orders
        WHERE user_id = ? AND status = 'completed'
        """,
        (user_id,),
    )
    row = await cur.fetchone()
    cur2 = await conn.execute(
        """
        SELECT COUNT(*) AS open_n FROM orders
        WHERE user_id = ? AND status IN ('paid', 'processing')
        """,
        (user_id,),
    )
    open_row = await cur2.fetchone()
    return {
        "vpn_units": int(row["vpn_n"] if row else 0),
        "vpn_rub": float(row["vpn_rub"] if row else 0),
        "stars_units": int(row["stars_n"] if row else 0),
        "stars_rub": float(row["stars_rub"] if row else 0),
        "premium_units": int(row["prem_n"] if row else 0),
        "premium_rub": float(row["prem_rub"] if row else 0),
        "open_orders": int(open_row["open_n"] if open_row else 0),
    }


async def resolve_admin_user_query(
    conn: aiosqlite.Connection, query: str
) -> tuple[int | None, str]:
    """Resolve TG id / @username / order # / ref_ link → user_id.

    Returns (user_id|None, how_resolved).
    """
    q = (query or "").strip()
    if not q:
        return None, "empty"
    low = q.lower()
    # ref deep-link or ref_123
    if "start=ref_" in low:
        low = low.split("start=ref_", 1)[-1]
        q = low.split("&")[0].split()[0]
        low = q.lower()
    if low.startswith("ref_"):
        q = q[4:]
        low = q.lower()
    # order id
    order_raw = q
    if order_raw.startswith("#"):
        order_raw = order_raw[1:]
    if low.startswith("order:") or low.startswith("order "):
        order_raw = q.split(":", 1)[-1].strip() if ":" in q else q.split(None, 1)[-1]
    if order_raw.isdigit() and (q.startswith("#") or low.startswith("order")):
        from bot.services import orders_repo

        order = await orders_repo.get_order(conn, int(order_raw))
        if order is not None:
            return int(order["user_id"]), "order"
        return None, "order_missing"
    # plain digits: prefer TG user_id if exists, else try as order id
    if q.isdigit():
        uid = int(q)
        u = await get_user(conn, uid)
        if u is not None:
            return uid, "tg_id"
        from bot.services import orders_repo

        order = await orders_repo.get_order(conn, uid)
        if order is not None:
            return int(order["user_id"]), "order"
        # still return as tg id for VPN lookup even if no shop row
        return uid, "tg_id_raw"
    # @username / username
    found = await find_user_id_by_username(conn, q)
    if found is not None:
        return found, "username"
    # web nickname → telegram via accounts
    try:
        from bot.services import accounts_repo

        data = await accounts_repo.find_accounts_orders_by_nickname(
            conn, q.lstrip("@"), limit=5
        )
        acc = data.get("account") or {}
        tid = acc.get("telegram_user_id")
        if tid is not None and str(tid).strip().isdigit():
            return int(tid), "nickname"
        orders = data.get("orders") or []
        if orders:
            return int(orders[0]["user_id"]), "nickname_order"
    except Exception:
        pass
    return None, "not_found"
