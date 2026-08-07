from __future__ import annotations

import aiosqlite

from bot.config import Settings
from bot.services import balance_repo, orders_repo, vpn_referral_extensions, vpn_referral_repo
from bot.services.pricing import commission_for_first_order
from bot.services.referral_partner import count_qualified_vpn_referrals, level_for_qualified_count
from bot.services.vpn_referral_notify import schedule_paid_referral_bonus_messages


def _fulfillment_applied_at(order: aiosqlite.Row) -> str | None:
    try:
        v = order["fulfillment_applied_at"]
    except (KeyError, IndexError):
        return None
    return str(v) if v is not None else None


def _order_kind(order: aiosqlite.Row) -> str:
    try:
        k = str(order["product_kind"] or "").strip().lower()
    except (KeyError, IndexError, TypeError):
        k = ""
    if k:
        return k
    try:
        pid = str(order["product_id"] or "").strip().lower()
    except (KeyError, IndexError, TypeError):
        pid = ""
    if pid.startswith("vpn"):
        return "vpn"
    if "premium" in pid:
        return "premium"
    if "star" in pid or "gift" in pid:
        return "stars"
    return ""


async def _referrer_override_pct(conn: aiosqlite.Connection, referrer_id: int) -> float | None:
    rcur = await conn.execute(
        "SELECT ref_commission_override_pct FROM users WHERE user_id = ?",
        (int(referrer_id),),
    )
    rrow = await rcur.fetchone()
    if rrow is None or rrow["ref_commission_override_pct"] is None:
        return None
    try:
        return float(rrow["ref_commission_override_pct"])
    except (TypeError, ValueError):
        return None


async def _vpn_commission_already_paid(
    conn: aiosqlite.Connection, *, invitee_id: int, referrer_id: int, exclude_order_id: int
) -> bool:
    cur = await conn.execute(
        """
        SELECT 1 FROM orders
        WHERE user_id = ?
          AND referrer_id = ?
          AND id <> ?
          AND COALESCE(commission_paid, 0) = 1
          AND LOWER(COALESCE(product_kind, '')) = 'vpn'
          AND COALESCE(commission_rub, 0) > 0
        LIMIT 1
        """,
        (int(invitee_id), int(referrer_id), int(exclude_order_id)),
    )
    return (await cur.fetchone()) is not None


async def _compute_referral_commission_rub(
    conn: aiosqlite.Connection,
    order: aiosqlite.Row,
    settings: Settings,
) -> float:
    """
    Канон 2026-07-28:
    - VPN: % один раз с первой VPN-покупки друга (уровневый 15–30% или admin override).
    - Stars/Premium/gift: % с каждой выданной покупки (уровневый 1–3%; override если задан).
    """
    referrer_id = order["referrer_id"]
    if not referrer_id:
        return 0.0
    if int(order["commission_paid"] or 0) == 1:
        return 0.0
    rub = float(order["rub_after_discounts"] or 0)
    if rub <= 0:
        return 0.0
    kind = _order_kind(order)
    rid = int(referrer_id)
    override = await _referrer_override_pct(conn, rid)
    qualified = await count_qualified_vpn_referrals(conn, rid)
    lvl = level_for_qualified_count(qualified)

    if kind == "vpn":
        if await _vpn_commission_already_paid(
            conn,
            invitee_id=int(order["user_id"]),
            referrer_id=rid,
            exclude_order_id=int(order["id"]),
        ):
            return 0.0
        pct = float(override) if override is not None else float(lvl["vpn_first_percent"])
        return commission_for_first_order(rub, settings, override_percent=pct)

    if kind in ("stars", "premium", "gift"):
        pct = float(override) if override is not None else float(lvl["stars_premium_percent"])
        return commission_for_first_order(rub, settings, override_percent=pct)

    # неизвестный kind — legacy: только если это вообще первая покупка друга
    return 0.0


async def apply_completed_side_effects(conn: aiosqlite.Connection, order_id: int, settings: Settings) -> None:
    """
    После status=completed. Идемпотентно через fulfillment_applied_at.

    - first_order_completed: при первой выдаче покупателя.
    - Реф ₽: VPN раз / Stars+Premium каждая (см. _compute_referral_commission_rub).
    - VPN days grant: как раньше.
    """
    await conn.execute("BEGIN IMMEDIATE")
    try:
        order = await orders_repo.get_order(conn, order_id)
        if order is None or str(order["status"]) != "completed":
            await conn.rollback()
            return
        if _fulfillment_applied_at(order):
            await conn.rollback()
            return

        user_id = int(order["user_id"])
        cur = await conn.execute(
            """
            SELECT COUNT(*) AS c FROM orders
            WHERE user_id = ? AND status = 'completed' AND id <> ?
            """,
            (user_id, order_id),
        )
        row = await cur.fetchone()
        had_completed_before = int(row["c"] if row else 0) > 0
        if not had_completed_before:
            await conn.execute(
                "UPDATE users SET first_order_completed = 1 WHERE user_id = ?",
                (user_id,),
            )

        commission = await _compute_referral_commission_rub(conn, order, settings)
        referrer_id = order["referrer_id"]
        grant_info = None

        if referrer_id and commission > 0:
            ucur = await conn.execute(
                """
                UPDATE orders
                SET commission_rub = ?, commission_paid = 1,
                    fulfillment_applied_at = datetime('now')
                WHERE id = ? AND commission_paid = 0 AND fulfillment_applied_at IS NULL
                """,
                (commission, order_id),
            )
            if ucur.rowcount != 1:
                await conn.rollback()
                return
            await balance_repo.credit_bonus_in_txn(
                conn,
                user_id=int(referrer_id),
                amount=commission,
                kind="bonus_credit",
                ref_type="order",
                ref_id=order_id,
            )
            grant_info = await vpn_referral_repo.try_insert_vpn_referral_grant(conn, order, settings)
        else:
            await conn.execute(
                """
                UPDATE orders SET fulfillment_applied_at = datetime('now')
                WHERE id = ? AND fulfillment_applied_at IS NULL
                """,
                (order_id,),
            )
            grant_info = await vpn_referral_repo.try_insert_vpn_referral_grant(conn, order, settings)

        await orders_repo.write_profit_snapshot(conn, order_id, settings)
        await conn.commit()
        if grant_info:
            await vpn_referral_extensions.apply_vpn_referral_extensions(conn, grant_info, settings)
            schedule_paid_referral_bonus_messages(settings, grant_info)
    except Exception:
        await conn.rollback()
        raise
