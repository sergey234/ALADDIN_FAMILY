from __future__ import annotations

import sqlite3

import aiosqlite

from bot.config import Settings
from bot.services.profit_compute import (
    fee_percent_for_rail,
    infer_payment_rail,
    net_profit_rub,
    payment_gateway_fee_rub,
    resolve_cogs_rub_for_order,
)


async def attach_promo_snapshot(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    promo_code: str,
    promo_discount_rub: float,
) -> None:
    """Снимок промо на заказе (колонки из migrate). Без commit — вызывающий коммитит."""
    code = (promo_code or "").strip()
    disc = float(promo_discount_rub or 0.0)
    if not code or disc <= 0:
        return
    await conn.execute(
        """
        UPDATE orders
        SET promo_code = ?, promo_discount_rub = ?
        WHERE id = ?
        """,
        (code[:64], disc, int(order_id)),
    )


async def set_payment_rail(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    payment_rail: str,
) -> None:
    """Persist payment rail (sbp / lava_card / crypto_bot / xrocket). No commit."""
    from bot.services.profit_compute import normalize_payment_rail

    rail = normalize_payment_rail(payment_rail)
    await conn.execute(
        """
        UPDATE orders SET payment_rail = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (rail, int(order_id)),
    )


async def write_profit_snapshot(
    conn: aiosqlite.Connection,
    order_id: int,
    settings: Settings,
    *,
    force: bool = False,
) -> None:
    """Заполняет fee/COGS/net после completed. Без force не переписывает уже зафиксированный snapshot."""
    from bot.services import fin_settings_repo

    row = await get_order(conn, order_id)
    if row is None or str(row["status"] or "").strip().lower() != "completed":
        return
    if not force:
        try:
            if row["profit_snapshot_at"]:
                return
        except (KeyError, IndexError, TypeError):
            pass
    settings = await fin_settings_repo.settings_with_overrides(conn, settings)
    sale = float(row["rub_after_discounts"] or 0)
    usd_base = float(row["usd_base"] or 0)
    referral_disc = float(row["referral_discount_rub"] or 0)
    ref_bonus = float(row["commission_rub"] or 0)
    try:
        product_kind = str(row["product_kind"] or "")
    except (KeyError, IndexError, TypeError):
        product_kind = ""
    try:
        stars_qty = row["stars_qty"]
        stars_qty_i = int(stars_qty) if stars_qty is not None else None
    except (KeyError, IndexError, TypeError, ValueError):
        stars_qty_i = None
    try:
        prem = row["premium_months"]
        prem_i = int(prem) if prem is not None else None
    except (KeyError, IndexError, TypeError, ValueError):
        prem_i = None
    try:
        existing_rail = str(row["payment_rail"] or "") or None
    except (KeyError, IndexError, TypeError):
        existing_rail = None
    try:
        inv_prov = str(row["invoice_last_provider"] or "") or None
    except (KeyError, IndexError, TypeError):
        inv_prov = None
    try:
        pm = str(row["payment_method"] or "") or None
    except (KeyError, IndexError, TypeError):
        pm = None

    rail = infer_payment_rail(
        payment_rail=existing_rail,
        payment_method=pm,
        invoice_last_provider=inv_prov,
    )
    fee_pct = fee_percent_for_rail(settings, rail, product_kind=product_kind)
    fee = payment_gateway_fee_rub(sale, fee_pct)
    try:
        manual_v = row["manual_cogs_rub"]
    except (KeyError, IndexError, TypeError):
        manual_v = None
    manual: float | None
    try:
        manual = float(manual_v) if manual_v is not None else None
    except (TypeError, ValueError):
        manual = None
    rate = float(settings.usd_rub_rate)
    try:
        snap = row["usd_rub_rate_snapshot"]
        if snap is not None:
            rate = float(snap)
    except (KeyError, IndexError, TypeError, ValueError):
        pass
    cogs_usdt_box: list[float] = []
    cogs = resolve_cogs_rub_for_order(
        product_kind=product_kind,
        manual_cogs_rub=manual,
        usd_base=usd_base,
        usd_rub_rate=rate,
        auto_cogs_fraction=settings.auto_cogs_usd_fraction,
        vpn_cogs_rub=settings.vpn_cogs_rub,
        stars_qty=stars_qty_i,
        premium_months=prem_i,
        settings=settings,
        cogs_usdt_out=cogs_usdt_box,
    )
    cogs_usdt = float(cogs_usdt_box[0]) if cogs_usdt_box else 0.0
    net = net_profit_rub(
        sale_rub=sale,
        cogs_rub=cogs,
        payment_fee_rub=fee,
        referral_bonus_rub=ref_bonus,
        referral_discount_rub=referral_disc,
    )
    await conn.execute(
        """
        UPDATE orders SET
          buyer_username = (SELECT u.username FROM users u WHERE u.user_id = orders.user_id),
          completed_at = COALESCE(completed_at, datetime('now')),
          payment_rail = COALESCE(NULLIF(payment_rail, ''), ?),
          payment_gateway_fee_rub = ?,
          payment_fee_percent_snapshot = ?,
          cogs_rub = ?,
          cogs_usdt = ?,
          cogs_currency = 'USDT',
          net_profit_rub = ?,
          profit_snapshot_at = datetime('now'),
          updated_at = datetime('now')
        WHERE id = ?
        """,
        (rail, fee, fee_pct, cogs, cogs_usdt, net, order_id),
    )


async def set_manual_cogs_and_recalc(
    conn: aiosqlite.Connection,
    order_id: int,
    settings: Settings,
    *,
    manual_cogs_rub: float,
) -> bool:
    row = await get_order(conn, order_id)
    if row is None or str(row["status"] or "").strip().lower() != "completed":
        return False
    await conn.execute(
        """
        UPDATE orders SET manual_cogs_rub = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (round(max(0.0, float(manual_cogs_rub)), 2), order_id),
    )
    await write_profit_snapshot(conn, order_id, settings, force=True)
    await conn.commit()
    return True


async def recalc_completed_profit_snapshots(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    order_id: int | None = None,
    product_kind: str | None = None,
) -> int:
    """Пересчитать снимки прибыли для completed-заказов (опционально по id или product_kind).

    Явный admin recalc = force (перезапись). Обычный completed flow не трогает уже зафиксированное.
    """
    sql = "SELECT id FROM orders WHERE LOWER(TRIM(status)) = 'completed'"
    params: list[object] = []
    if order_id is not None:
        sql += " AND id = ?"
        params.append(int(order_id))
    if product_kind is not None:
        sql += " AND LOWER(TRIM(COALESCE(product_kind, ''))) = ?"
        params.append(str(product_kind).strip().lower())
    sql += " ORDER BY id"
    cur = await conn.execute(sql, params)
    rows = await cur.fetchall()
    n = 0
    for r in rows:
        await write_profit_snapshot(conn, int(r[0]), settings, force=True)
        n += 1
    if n:
        await conn.commit()
    return n


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
    product_kind: str = "",
    stars_qty: int | None = None,
    premium_months: int | None = None,
    referral_discount_percent: float = 0.0,
    usd_rub_rate_snapshot: float | None = None,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO orders (
            user_id, product_id, product_title, payment_method, status,
            usd_base, rub_before_discounts, rub_after_discounts,
            referral_discount_rub, wholesale_discount_rub,
            referrer_id, commission_rub, user_note, balance_applied_rub,
            product_kind, stars_qty, premium_months,
            referral_discount_percent, usd_rub_rate_snapshot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            (product_kind or "").strip().lower(),
            stars_qty,
            premium_months,
            round(max(0.0, float(referral_discount_percent)), 4),
            usd_rub_rate_snapshot,
        ),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def create_web_order(
    conn: aiosqlite.Connection,
    *,
    account_id: str,
    vpn_subject_id: int,
    product_id: str,
    product_title: str,
    rub_after: float,
    referrer_id: int | None,
    vpn_subscription_days: int,
    buyer_nickname: str | None = None,
) -> int:
    """VPN order from get.aladdin-ai.ru (source=web). user_id = vpn_subject_id."""
    nick = (buyer_nickname or "").strip() or None
    cur = await conn.execute(
        """
        INSERT INTO orders (
            user_id, product_id, product_title, payment_method, status,
            usd_base, rub_before_discounts, rub_after_discounts,
            referral_discount_rub, wholesale_discount_rub,
            referrer_id, commission_rub, user_note, balance_applied_rub,
            product_kind, stars_qty, premium_months,
            referral_discount_percent, usd_rub_rate_snapshot,
            source, account_id, buyer_nickname
        ) VALUES (?, ?, ?, 'fiat', 'pending_payment', 0, ?, ?, 0, 0, ?, 0, ?, 0,
                  'vpn', NULL, NULL, 0, NULL, 'web', ?, ?)
        """,
        (
            int(vpn_subject_id),
            product_id,
            product_title,
            float(rub_after),
            float(rub_after),
            referrer_id,
            f"web vpn {int(vpn_subscription_days)}d",
            account_id,
            nick,
        ),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def list_orders_for_account(
    conn: aiosqlite.Connection, account_id: str, *, limit: int = 30
) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE account_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (account_id, int(limit)),
    )
    return list(await cur.fetchall())


async def update_status(conn: aiosqlite.Connection, order_id: int, status: str) -> None:
    row = await get_order(conn, order_id)
    if row is None:
        raise ValueError("order_not_found")
    from bot.services.order_status import require_transition

    require_transition(str(row["status"]), status)
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


async def count_user_orders_by_status(conn: aiosqlite.Connection, user_id: int, status: str) -> int:
    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM orders WHERE user_id = ? AND status = ?",
        (user_id, status),
    )
    row = await cur.fetchone()
    return int(row["c"] if row else 0)


async def list_user_pending_payment_order_ids(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    limit: int = 12,
) -> list[int]:
    """ID заказов пользователя в статусе pending_payment (новые сверху) - для памятки оператору при сверке bc."""
    lim = max(1, min(50, int(limit)))
    cur = await conn.execute(
        """
        SELECT id FROM orders
        WHERE user_id = ? AND status = 'pending_payment'
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, lim),
    )
    rows = await cur.fetchall()
    return [int(r[0]) for r in rows]


async def list_lava_pending_payment_orders(
    conn: aiosqlite.Connection,
    *,
    limit: int = 20,
) -> list[aiosqlite.Row]:
    """pending_payment с выставленным счётом LAVA — для сверки по API, если webhook не пришёл."""
    lim = max(1, min(100, int(limit)))
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE status = 'pending_payment'
          AND LOWER(TRIM(COALESCE(invoice_last_provider, ''))) = 'lava'
          AND invoice_last_external_id IS NOT NULL
          AND TRIM(COALESCE(invoice_last_external_id, '')) != ''
        ORDER BY id ASC
        LIMIT ?
        """,
        (lim,),
    )
    return await cur.fetchall()


async def list_lava_recent_expired_payment_orders(
    conn: aiosqlite.Connection,
    *,
    lookback_hours: int = 48,
    limit: int = 20,
) -> list[aiosqlite.Row]:
    """
    Недавно истекшие LAVA-заказы со счётом — late success после TTL pending.
    """
    lim = max(1, min(100, int(limit)))
    hours = max(1, min(168, int(lookback_hours)))
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE status = 'expired'
          AND LOWER(TRIM(COALESCE(invoice_last_provider, ''))) = 'lava'
          AND invoice_last_external_id IS NOT NULL
          AND TRIM(COALESCE(invoice_last_external_id, '')) != ''
          AND datetime(updated_at) >= datetime('now', ?)
        ORDER BY id DESC
        LIMIT ?
        """,
        (f"-{hours} hours", lim),
    )
    return await cur.fetchall()


async def require_pending_order_cap(conn: aiosqlite.Connection, user_id: int, settings: Settings) -> None:
    cap = settings.max_pending_payment_orders_per_user
    if cap <= 0:
        return
    n = await count_user_orders_by_status(conn, user_id, "pending_payment")
    if n >= cap:
        raise ValueError("order_pending_cap")


async def assert_invoice_request_allowed(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    cooldown_seconds: int,
) -> tuple[bool, float]:
    """
    Транзакционно проверяет и фиксирует момент запроса счёта для order_id.
    Ожидаемый сценарий: вызывать перед генерацией LAVA/Crypto счёта.
    Возвращает (allowed, wait_seconds).
    """
    cd = max(0, int(cooldown_seconds))
    await conn.execute("BEGIN IMMEDIATE")
    try:
        row = await get_order(conn, order_id)
        if row is None:
            await conn.rollback()
            return False, 0.0
        status = str(row["status"] or "").strip().lower()
        if status != "pending_payment":
            await conn.rollback()
            return False, 0.0

        wait_seconds = 0.0
        if cd > 0 and row["invoice_last_requested_at"]:
            cur = await conn.execute(
                """
                SELECT
                  MAX(
                    0,
                    CAST(
                      ROUND((julianday(invoice_last_requested_at) + (? / 86400.0) - julianday('now')) * 86400)
                      AS INTEGER
                    )
                  ) AS wait_s
                FROM orders
                WHERE id = ?
                """,
                (cd, order_id),
            )
            got = await cur.fetchone()
            wait_seconds = float(got["wait_s"] or 0)
            if wait_seconds > 0:
                await conn.rollback()
                return False, wait_seconds

        await conn.execute(
            """
            UPDATE orders
            SET invoice_last_requested_at = datetime('now'),
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (order_id,),
        )
        await conn.commit()
        return True, 0.0
    except Exception:
        await conn.rollback()
        raise


async def set_invoice_provider_metadata(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    provider: str,
    external_id: str | None,
    pay_url: str | None = None,
    lava_attempt: int | None = None,
) -> None:
    prov = (provider or "").strip().lower()[:32]
    ext = (external_id or "").strip()[:255] or None
    if not prov:
        return
    url = (pay_url or "").strip()[:512] or None
    att = int(lava_attempt) if lava_attempt is not None and int(lava_attempt) > 0 else None
    if att is not None:
        await conn.execute(
            """
            UPDATE orders
            SET invoice_last_provider = ?,
                invoice_last_external_id = ?,
                invoice_last_pay_url = COALESCE(?, invoice_last_pay_url),
                invoice_lava_attempt = ?,
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (prov, ext, url, att, order_id),
        )
    else:
        await conn.execute(
            """
            UPDATE orders
            SET invoice_last_provider = ?,
                invoice_last_external_id = ?,
                invoice_last_pay_url = COALESCE(?, invoice_last_pay_url),
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (prov, ext, url, order_id),
        )
    await conn.commit()


async def expire_other_pending_payment_orders(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    keep_order_id: int,
) -> list[int]:
    """
    Закрывает прочие pending_payment того же пользователя (один активный счёт).
    Возвращает id истёкших заказов.
    """
    await conn.execute("BEGIN IMMEDIATE")
    try:
        cur = await conn.execute(
            """
            UPDATE orders
            SET status = 'expired', updated_at = datetime('now')
            WHERE user_id = ?
              AND status = 'pending_payment'
              AND id != ?
            RETURNING id
            """,
            (user_id, keep_order_id),
        )
        rows = await cur.fetchall()
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return [int(r["id"]) for r in rows]


async def expire_other_pending_payment_orders_for_account(
    conn: aiosqlite.Connection,
    *,
    account_id: str,
    keep_order_id: int,
) -> list[int]:
    """Web-аккаунт: закрыть прочие pending_payment того же account_id."""
    aid = (account_id or "").strip()
    if not aid:
        return []
    await conn.execute("BEGIN IMMEDIATE")
    try:
        cur = await conn.execute(
            """
            UPDATE orders
            SET status = 'expired', updated_at = datetime('now')
            WHERE account_id = ?
              AND status = 'pending_payment'
              AND id != ?
            RETURNING id
            """,
            (aid, int(keep_order_id)),
        )
        rows = await cur.fetchall()
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return [int(r["id"]) for r in rows]


async def cancel_account_pending_order(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    account_id: str,
) -> str:
    """Web: отменить свой pending_payment → expired. ok | not_found | wrong_account | wrong_status"""
    row = await get_order(conn, order_id)
    if not row:
        return "not_found"
    if str(row["account_id"] or "").strip() != str(account_id or "").strip():
        return "wrong_account"
    if str(row["status"] or "").strip().lower() != "pending_payment":
        return "wrong_status"
    await update_status(conn, order_id, "expired")
    return "ok"


async def cancel_user_pending_order(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    user_id: int,
) -> str:
    """
    Покупатель отменяет свой неоплаченный заказ → expired.
    Коды: ok | not_found | wrong_user | wrong_status
    """
    row = await get_order(conn, order_id)
    if not row:
        return "not_found"
    if int(row["user_id"]) != int(user_id):
        return "wrong_user"
    if str(row["status"] or "").strip().lower() != "pending_payment":
        return "wrong_status"
    await update_status(conn, order_id, "expired")
    return "ok"


async def cancel_all_user_pending_orders(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
) -> list[int]:
    """Отменить (expired) все pending_payment пользователя. Возвращает id заказов."""
    await conn.execute("BEGIN IMMEDIATE")
    try:
        cur = await conn.execute(
            """
            SELECT id FROM orders
            WHERE user_id = ? AND status = 'pending_payment'
            ORDER BY id ASC
            """,
            (user_id,),
        )
        rows = await cur.fetchall()
        cancelled: list[int] = []
        for row in rows:
            oid = int(row["id"])
            await update_status_no_commit(conn, oid, "expired")
            cancelled.append(oid)
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return cancelled


async def touch_bc_payment_claim_if_allowed(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    user_id: int,
    cooldown_seconds: int,
) -> tuple[str, int]:
    """
    Покупатель нажал «Я оплатил» после оплаты на универсальной bc-странице Ckassa.
    Возвращает (код, секунд_до_повтора). код: ok | not_found | wrong_user | wrong_status | cooldown.
    """
    row = await get_order(conn, order_id)
    if row is None:
        return ("not_found", 0)
    if int(row["user_id"]) != int(user_id):
        return ("wrong_user", 0)
    try:
        st = str(row["status"] or "").strip().lower()
    except (KeyError, IndexError, TypeError):
        st = ""
    if st != "pending_payment":
        return ("wrong_status", 0)
    cool = max(0, int(cooldown_seconds))
    if cool == 0:
        await conn.execute(
            """
            UPDATE orders
            SET bc_payment_claim_at = datetime('now'), updated_at = datetime('now')
            WHERE id = ? AND user_id = ? AND status = 'pending_payment'
            """,
            (order_id, user_id),
        )
        await conn.commit()
        return ("ok", 0)
    cur = await conn.execute(
        """
        UPDATE orders
        SET bc_payment_claim_at = datetime('now'), updated_at = datetime('now')
        WHERE id = ?
          AND user_id = ?
          AND status = 'pending_payment'
          AND (
            bc_payment_claim_at IS NULL
            OR CAST((julianday('now') - julianday(bc_payment_claim_at)) * 86400 AS INTEGER) >= ?
          )
        """,
        (order_id, user_id, cool),
    )
    await conn.commit()
    if cur.rowcount and int(cur.rowcount) > 0:
        return ("ok", 0)
    cur2 = await conn.execute(
        """
        SELECT CAST(
          MAX(
            0,
            ? - CAST((julianday('now') - julianday(bc_payment_claim_at)) * 86400 AS INTEGER)
          ) AS INTEGER
        )
        FROM orders
        WHERE id = ? AND user_id = ? AND bc_payment_claim_at IS NOT NULL
        """,
        (cool, order_id, user_id),
    )
    r2 = await cur2.fetchone()
    wait = int(r2[0]) if r2 and r2[0] is not None else cool
    return ("cooldown", max(0, wait))


async def expire_stale_pending_payment_orders(
    conn: aiosqlite.Connection,
    *,
    ttl_minutes: int,
) -> list[tuple[int, int]]:
    """
    Переводит pending_payment → expired, если с момента created_at прошло ≥ ttl_minutes.
    Возвращает (order_id, user_id) для уведомлений пользователю.
    """
    if ttl_minutes <= 0:
        return []
    mod = f"+{int(ttl_minutes)} minutes"
    await conn.execute("BEGIN IMMEDIATE")
    try:
        cur = await conn.execute(
            """
            UPDATE orders
            SET status = 'expired', updated_at = datetime('now')
            WHERE status = 'pending_payment'
              AND datetime(created_at, ?) < datetime('now')
            RETURNING id, user_id
            """,
            (mod,),
        )
        rows = await cur.fetchall()
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return [(int(r["id"]), int(r["user_id"])) for r in rows]


def _balance_applied_from_row(order: aiosqlite.Row) -> float:
    try:
        return float(order["balance_applied_rub"] or 0)
    except (KeyError, IndexError, TypeError):
        return 0.0


def _bonus_applied_from_row(order: aiosqlite.Row) -> float:
    try:
        return float(order["bonus_applied_rub"] or 0)
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
    settings: Settings,
    product_kind: str = "",
    stars_qty: int | None = None,
    premium_months: int | None = None,
    referral_discount_percent: float = 0.0,
    usd_rub_rate_snapshot: float | None = None,
) -> int:
    """Атомарно: dual-wallet списание + заказ paid + ledger order_pay / bonus_order_pay."""
    from bot.services import balance_repo
    from bot.services.dual_wallet import wallet_plan_for_kind

    due = round(float(rub_after), 2)
    vpn_only = bool(settings.ref_bonus_vpn_only)
    pk = (product_kind or "").strip().lower()

    await conn.execute("BEGIN IMMEDIATE")
    try:
        await balance_repo.ensure_balance_user_row(conn, user_id)
        main_bal, bonus_bal = await balance_repo.get_balances(conn, user_id)
        plan = wallet_plan_for_kind(
            pk,
            due,
            main_bal,
            bonus_bal,
            ref_bonus_vpn_only=vpn_only,
        )

        cur = await conn.execute(
            """
            INSERT INTO orders (
                user_id, product_id, product_title, payment_method, status,
                usd_base, rub_before_discounts, rub_after_discounts,
                referral_discount_rub, wholesale_discount_rub,
                referrer_id, commission_rub, user_note, balance_applied_rub,
                bonus_applied_rub,
                product_kind, stars_qty, premium_months,
                referral_discount_percent, usd_rub_rate_snapshot
            ) VALUES (?, ?, ?, 'balance', 'paid', ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?)
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
                plan.main_use,
                plan.bonus_use,
                pk,
                stars_qty,
                premium_months,
                round(max(0.0, float(referral_discount_percent)), 4),
                usd_rub_rate_snapshot,
            ),
        )
        oid = int(cur.lastrowid)

        if plan.bonus_use > 0:
            await balance_repo.debit_bonus_in_txn(
                conn,
                user_id=user_id,
                amount=plan.bonus_use,
                kind="bonus_order_pay",
                ref_type="order",
                ref_id=oid,
            )
        if plan.main_use > 0:
            await balance_repo.debit_main_in_txn(
                conn,
                user_id=user_id,
                amount=plan.main_use,
                kind="order_pay",
                ref_type="order",
                ref_id=oid,
            )

        await conn.commit()
        return oid
    except ValueError:
        await conn.rollback()
        raise
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
    settings: Settings,
    product_kind: str = "",
    stars_qty: int | None = None,
    premium_months: int | None = None,
    referral_discount_percent: float = 0.0,
    usd_rub_rate_snapshot: float | None = None,
) -> int:
    """
    Списывает balance_apply с кошелька(ов), создаёт заказ.
    VPN + REF_BONUS_VPN_ONLY: bonus-first в пределах apply_amount.
    Если доплата ~0 - сразу paid; иначе pending_payment и payment_method mix_fiat / mix_crypto.
    """
    from bot.services import balance_repo
    from bot.services.dual_wallet import wallet_plan_partial_apply

    balance_apply = round(balance_apply, 2)
    if balance_apply <= 0:
        raise ValueError("invalid_balance_apply")
    remainder = round(rub_invoice_total - balance_apply, 2)
    if remainder < -1e-6:
        raise ValueError("balance_exceeds_total")

    pk = (product_kind or "").strip().lower()
    vpn_only = bool(settings.ref_bonus_vpn_only)

    await conn.execute("BEGIN IMMEDIATE")
    try:
        if remainder > 0.01:
            await require_pending_order_cap(conn, user_id, settings)
        await balance_repo.ensure_balance_user_row(conn, user_id)
        main_bal, bonus_bal = await balance_repo.get_balances(conn, user_id)
        plan = wallet_plan_partial_apply(
            pk,
            balance_apply,
            main_bal,
            bonus_bal,
            ref_bonus_vpn_only=vpn_only,
        )

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
                referrer_id, commission_rub, user_note, balance_applied_rub,
                bonus_applied_rub,
                product_kind, stars_qty, premium_months,
                referral_discount_percent, usd_rub_rate_snapshot
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?)
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
                plan.main_use,
                plan.bonus_use,
                pk,
                stars_qty,
                premium_months,
                round(max(0.0, float(referral_discount_percent)), 4),
                usd_rub_rate_snapshot,
            ),
        )
        oid = int(cur.lastrowid)

        if plan.bonus_use > 0:
            await balance_repo.debit_bonus_in_txn(
                conn,
                user_id=user_id,
                amount=plan.bonus_use,
                kind="bonus_order_pay",
                ref_type="order",
                ref_id=oid,
            )
        if plan.main_use > 0:
            await balance_repo.debit_main_in_txn(
                conn,
                user_id=user_id,
                amount=plan.main_use,
                kind="order_pay",
                ref_type="order",
                ref_id=oid,
            )

        await conn.commit()
        return oid
    except ValueError:
        await conn.rollback()
        raise
    except Exception:
        await conn.rollback()
        raise


def amount_due_external(order: aiosqlite.Row) -> float:
    """Сколько ещё оплатить внешне (фиат/крипта)."""
    total = float(order["rub_after_discounts"] or 0)
    applied_main = _balance_applied_from_row(order)
    applied_bonus = _bonus_applied_from_row(order)
    return max(0.0, round(total - applied_main - applied_bonus, 2))


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
    settings: Settings,
    product_kind: str = "",
    stars_qty: int | None = None,
    premium_months: int | None = None,
    referral_discount_percent: float = 0.0,
    usd_rub_rate_snapshot: float | None = None,
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

        await require_pending_order_cap(conn, owner_user_id, settings)

        try:
            cur = await conn.execute(
                """
                INSERT INTO orders (
                    user_id, product_id, product_title, payment_method, status,
                    usd_base, rub_before_discounts, rub_after_discounts,
                    referral_discount_rub, wholesale_discount_rub,
                    referrer_id, commission_rub, user_note, balance_applied_rub,
                    source, api_client_id, idempotency_key, external_ref,
                    product_kind, stars_qty, premium_months,
                    referral_discount_percent, usd_rub_rate_snapshot
                ) VALUES (?, ?, ?, ?, 'pending_payment', ?, ?, ?, ?, ?, ?, 0, ?, 0, 'api', ?, ?, ?, ?, ?, ?, ?, ?)
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
                    (product_kind or "").strip().lower(),
                    stars_qty,
                    premium_months,
                    round(max(0.0, float(referral_discount_percent)), 4),
                    usd_rub_rate_snapshot,
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


async def list_orders_for_auto_fulfill(conn: aiosqlite.Connection, *, limit: int) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE status = 'paid'
          AND LOWER(TRIM(COALESCE(fulfillment_mode, 'auto'))) != 'manual_only'
          AND (fulfillment_provider_ref IS NULL OR TRIM(COALESCE(fulfillment_provider_ref, '')) = '')
          AND (
            fulfillment_retry_after IS NULL
            OR TRIM(COALESCE(fulfillment_retry_after, '')) = ''
            OR fulfillment_retry_after <= datetime('now')
          )
        ORDER BY id ASC
        LIMIT ?
        """,
        (max(1, int(limit)),),
    )
    return await cur.fetchall()


async def list_processing_orders_for_istar_poll(
    conn: aiosqlite.Connection,
    *,
    min_processing_minutes: int,
    limit: int = 20,
) -> list[aiosqlite.Row]:
    mins = max(1, int(min_processing_minutes))
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE status = 'processing'
          AND fulfillment_provider_ref IS NOT NULL
          AND TRIM(COALESCE(fulfillment_provider_ref, '')) != ''
          AND updated_at <= datetime('now', ?)
        ORDER BY id ASC
        LIMIT ?
        """,
        (f"-{mins} minutes", max(1, int(limit))),
    )
    return await cur.fetchall()


async def list_recent_completed_orders(
    conn: aiosqlite.Connection,
    *,
    limit: int = 15,
) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        """
        SELECT * FROM orders
        WHERE status = 'completed'
        ORDER BY COALESCE(fulfillment_applied_at, updated_at, created_at) DESC
        LIMIT ?
        """,
        (max(1, int(limit)),),
    )
    return await cur.fetchall()


async def claim_auto_fulfill_attempt_slot(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    max_attempts: int,
) -> aiosqlite.Row | None:
    """
    Атомарно увеличивает fulfillment_attempt_count для заказа в paid+auto без provider_ref,
    если не исчерпан лимит попыток. Возвращает строку заказа после UPDATE или None.
    """
    cap = max(1, int(max_attempts))
    await conn.execute("BEGIN IMMEDIATE")
    try:
        cur = await conn.execute(
            """
            UPDATE orders SET
              fulfillment_attempt_count = COALESCE(fulfillment_attempt_count, 0) + 1,
              fulfillment_last_attempt_at = datetime('now'),
              fulfillment_last_error = NULL,
              updated_at = datetime('now')
            WHERE id = ?
              AND status = 'paid'
              AND LOWER(TRIM(COALESCE(fulfillment_mode, 'auto'))) != 'manual_only'
              AND (fulfillment_provider_ref IS NULL OR TRIM(COALESCE(fulfillment_provider_ref, '')) = '')
              AND (fulfillment_attempt_count IS NULL OR fulfillment_attempt_count < ?)
            RETURNING *
            """,
            (order_id, cap),
        )
        row = await cur.fetchone()
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return row


async def revert_auto_fulfill_attempt_claim(
    conn: aiosqlite.Connection,
    order_id: int,
) -> None:
    """Откат +1 попытки после временного сбоя iStar (5xx / сеть)."""
    await conn.execute(
        """
        UPDATE orders SET
          fulfillment_attempt_count = CASE
            WHEN COALESCE(fulfillment_attempt_count, 0) > 0
            THEN fulfillment_attempt_count - 1
            ELSE 0
          END,
          updated_at = datetime('now')
        WHERE id = ? AND status = 'paid'
        """,
        (order_id,),
    )
    await conn.commit()


async def schedule_auto_fulfill_transient_retry(
    conn: aiosqlite.Connection,
    order_id: int,
    *,
    error_message: str,
    backoff_minutes: int,
) -> int:
    """Ставит паузу перед следующей попыткой; возвращает новый transient_fail_count."""
    mins = max(1, int(backoff_minutes))
    msg = (error_message or "")[:2000]
    await conn.execute("BEGIN IMMEDIATE")
    cur = await conn.execute(
        """
        UPDATE orders SET
          fulfillment_transient_fail_count = COALESCE(fulfillment_transient_fail_count, 0) + 1,
          fulfillment_retry_after = datetime('now', ?),
          fulfillment_last_error = ?,
          updated_at = datetime('now')
        WHERE id = ? AND status = 'paid'
        RETURNING fulfillment_transient_fail_count
        """,
        (f"+{mins} minutes", msg, order_id),
    )
    row = await cur.fetchone()
    await conn.commit()
    if row is None:
        return 0
    try:
        return int(row[0])
    except (TypeError, ValueError, KeyError, IndexError):
        return 0


async def set_fulfillment_last_error(
    conn: aiosqlite.Connection,
    order_id: int,
    message: str,
) -> None:
    msg = (message or "")[:2000]
    await conn.execute(
        """
        UPDATE orders SET fulfillment_last_error = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (msg, order_id),
    )
    await conn.commit()


async def set_fulfillment_provider_ref(
    conn: aiosqlite.Connection,
    order_id: int,
    provider_ref: str,
) -> None:
    ref = (provider_ref or "").strip()[:500]
    await conn.execute(
        """
        UPDATE orders SET
          fulfillment_provider_ref = ?,
          fulfillment_last_error = NULL,
          fulfillment_retry_after = NULL,
          fulfillment_transient_fail_count = 0,
          updated_at = datetime('now')
        WHERE id = ? AND status = 'processing'
        """,
        (ref, order_id),
    )
    await conn.commit()


async def get_order_by_fulfillment_provider_ref(
    conn: aiosqlite.Connection,
    provider_ref: str,
) -> aiosqlite.Row | None:
    cur = await conn.execute(
        "SELECT * FROM orders WHERE fulfillment_provider_ref = ? LIMIT 1",
        ((provider_ref or "").strip(),),
    )
    return await cur.fetchone()


async def set_order_fulfillment_mode(
    conn: aiosqlite.Connection,
    order_id: int,
    *,
    mode: str | None,
) -> bool:
    """
    mode=None или 'auto' → в БД значение `auto` (колонка NOT NULL).
    mode='manual_only' → только ручная выдача, воркер не берёт заказ.
    Разрешено для заказов в paid / processing (не completed / expired).
    """
    norm = (mode or "").strip().lower()
    if norm in ("", "auto"):
        val = "auto"
    elif norm == "manual_only":
        val = "manual_only"
    else:
        raise ValueError("invalid_fulfillment_mode")

    await conn.execute("BEGIN IMMEDIATE")
    cur = await conn.execute(
        """
        UPDATE orders SET fulfillment_mode = ?, updated_at = datetime('now')
        WHERE id = ? AND status IN ('paid', 'processing')
        """,
        (val, order_id),
    )
    n = cur.rowcount or 0
    await conn.commit()
    return n == 1


async def super_reset_paid_auto_fulfill_fields(conn: aiosqlite.Connection, order_id: int) -> bool:
    """
    Супер-админ: сброс полей авто-выдачи для заказа в paid (повтор в очереди воркера).
    Не трогает processing с ref - там риск дубля у провайдера.
    """
    await conn.execute("BEGIN IMMEDIATE")
    cur = await conn.execute(
        """
        UPDATE orders SET
          fulfillment_attempt_count = 0,
          fulfillment_last_error = NULL,
          fulfillment_last_attempt_at = NULL,
          fulfillment_provider_ref = NULL,
          fulfillment_retry_after = NULL,
          fulfillment_transient_fail_count = 0,
          fulfillment_mode = 'auto',
          updated_at = datetime('now')
        WHERE id = ? AND status = 'paid'
        """,
        (order_id,),
    )
    ok = (cur.rowcount or 0) == 1
    await conn.commit()
    return ok


async def revert_processing_to_paid_after_auto_fulfill_failure(
    conn: aiosqlite.Connection,
    order_id: int,
) -> bool:
    """
    Только если заказ в processing без fulfillment_provider_ref (create у провайдера не прошёл).
    Возвращает True если откат выполнен.
    """
    from bot.services.order_status import require_transition

    await conn.execute("BEGIN IMMEDIATE")
    try:
        row = await get_order(conn, order_id)
        if row is None or str(row["status"] or "").strip().lower() != "processing":
            await conn.rollback()
            return False
        ref = str(row["fulfillment_provider_ref"] or "").strip()
        if ref:
            await conn.rollback()
            return False
        require_transition("processing", "paid")
        await update_status_no_commit(conn, order_id, "paid")
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return True


async def revert_failed_processing_to_paid_for_retry(
    conn: aiosqlite.Connection,
    order_id: int,
) -> bool:
    """
    processing после failed-выдачи у провайдера → paid + сброс ff-полей для повторной create.
    """
    from bot.services.order_status import require_transition

    await conn.execute("BEGIN IMMEDIATE")
    try:
        row = await get_order(conn, order_id)
        if row is None or str(row["status"] or "").strip().lower() != "processing":
            await conn.rollback()
            return False
        err = str(row["fulfillment_last_error"] or "").strip()
        if not err:
            await conn.rollback()
            return False
        require_transition("processing", "paid")
        await update_status_no_commit(conn, order_id, "paid")
        await conn.execute(
            """
            UPDATE orders SET
              fulfillment_attempt_count = 0,
              fulfillment_last_error = NULL,
              fulfillment_last_attempt_at = NULL,
              fulfillment_provider_ref = NULL,
              fulfillment_retry_after = NULL,
              fulfillment_transient_fail_count = 0,
              fulfillment_mode = 'auto',
              updated_at = datetime('now')
            WHERE id = ?
            """,
            (order_id,),
        )
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    return True


async def list_order_ids_stuck_paid_or_processing(
    conn: aiosqlite.Connection,
    *,
    hours_without_update: int,
    limit: int = 200,
) -> list[int]:
    """
    Заказы в paid или processing, у которых updated_at старше N часов (алерт «нет движения»).
    """
    if hours_without_update <= 0:
        return []
    mod = f"-{int(hours_without_update)} hours"
    cur = await conn.execute(
        """
        SELECT id FROM orders
        WHERE status IN ('paid', 'processing')
          AND LOWER(TRIM(COALESCE(fulfillment_mode, 'auto'))) != 'manual_only'
          AND datetime(updated_at) < datetime('now', ?)
        ORDER BY id ASC
        LIMIT ?
        """,
        (mod, int(limit)),
    )
    rows = await cur.fetchall()
    return [int(r["id"]) for r in rows]


async def list_order_ids_stuck_paid_only(
    conn: aiosqlite.Connection,
    *,
    minutes_without_update: int,
    limit: int = 200,
) -> list[int]:
    """Заказы в paid без перехода в processing дольше N минут (быстрый ops-алерт)."""
    if minutes_without_update <= 0:
        return []
    mod = f"-{int(minutes_without_update)} minutes"
    cur = await conn.execute(
        """
        SELECT id FROM orders
        WHERE status = 'paid'
          AND LOWER(TRIM(COALESCE(fulfillment_mode, 'auto'))) != 'manual_only'
          AND datetime(updated_at) < datetime('now', ?)
        ORDER BY id ASC
        LIMIT ?
        """,
        (mod, int(limit)),
    )
    rows = await cur.fetchall()
    return [int(r["id"]) for r in rows]


async def list_order_ids_stuck_processing_only(
    conn: aiosqlite.Connection,
    *,
    minutes_without_update: int,
    limit: int = 200,
) -> list[int]:
    """Заказы в processing без обновления дольше N минут (отдельный ops-алерт)."""
    if minutes_without_update <= 0:
        return []
    mod = f"-{int(minutes_without_update)} minutes"
    cur = await conn.execute(
        """
        SELECT id FROM orders
        WHERE status = 'processing'
          AND LOWER(TRIM(COALESCE(fulfillment_mode, 'auto'))) != 'manual_only'
          AND datetime(updated_at) < datetime('now', ?)
        ORDER BY id ASC
        LIMIT ?
        """,
        (mod, int(limit)),
    )
    rows = await cur.fetchall()
    return [int(r["id"]) for r in rows]


async def list_orders_operator_attention_queue(
    conn: aiosqlite.Connection,
    *,
    processing_idle_minutes: int,
    limit: int = 25,
) -> list[aiosqlite.Row]:
    """
    Очередь для оператора: paid с непустой fulfillment_last_error или processing «без движения»
    дольше processing_idle_minutes.
    """
    idle = max(1, int(processing_idle_minutes))
    mod = f"-{idle} minutes"
    cur = await conn.execute(
        """
        SELECT id, status, product_title, fulfillment_last_error, updated_at, user_note
        FROM orders
        WHERE (
            (status = 'paid' AND fulfillment_last_error IS NOT NULL
             AND length(trim(fulfillment_last_error)) > 0)
            OR (status = 'processing' AND datetime(updated_at) < datetime('now', ?))
        )
        ORDER BY id ASC
        LIMIT ?
        """,
        (mod, int(limit)),
    )
    rows = await cur.fetchall()
    return list(rows)


async def allow_order_create_interval(
    conn: aiosqlite.Connection,
    user_id: int,
    min_seconds: float,
) -> bool:
    """Не чаще одного нового заказа за min_seconds (по MAX(created_at))."""
    if min_seconds <= 0:
        return True
    cur = await conn.execute(
        "SELECT MAX(created_at) AS m FROM orders WHERE user_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    if not row or row["m"] is None:
        return True
    from datetime import datetime, timezone

    raw = str(row["m"]).strip()
    try:
        if "T" in raw:
            last = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
        else:
            last = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    delta = (datetime.now(timezone.utc) - last).total_seconds()
    return delta >= float(min_seconds) - 1e-6


async def last_vpn_order_id_for_user(conn: aiosqlite.Connection, user_id: int) -> int | None:
    """Последний заказ пользователя с VPN-продуктом (vpn-14 admin extend)."""
    cur = await conn.execute(
        """
        SELECT id FROM orders
        WHERE user_id = ?
          AND (
            LOWER(TRIM(COALESCE(product_kind, ''))) = 'vpn'
            OR LOWER(TRIM(COALESCE(product_id, ''))) LIKE 'vpn%'
          )
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,),
    )
    row = await cur.fetchone()
    return int(row["id"]) if row else None
