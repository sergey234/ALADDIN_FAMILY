"""Партнёрские уровни + антиабуз-гейты вывода рефбонуса (канон 2026-07-28)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

import aiosqlite

# Уровень = DISTINCT друзья с completed VPN ≥30д (выдано).
QUALIFY_VPN_MIN_DAYS = 30
WITHDRAW_MIN_QUALIFIED_VPN = 5
WITHDRAW_COOLDOWN_DAYS = 7

# VPN first-purchase % / Stars+Premium recurring % по уровню
LEVELS: tuple[tuple[str, int, int, float, float], ...] = (
    # id, min_qualified, max_qualified (inclusive, -1 = ∞), vpn_first_pct, stars_prem_pct
    ("start", 0, 4, 15.0, 1.0),
    ("bronze", 5, 14, 20.0, 2.0),
    ("silver", 15, 29, 25.0, 2.5),
    ("gold", 30, -1, 30.0, 3.0),
)

LEVEL_LABEL_RU = {
    "start": "Старт",
    "bronze": "Бронза",
    "silver": "Серебро",
    "gold": "Золото",
}

_VPN_DAYS_IN_ID = re.compile(r"(\d+)\s*d", re.IGNORECASE)


def vpn_days_from_product_id(product_id: str) -> int:
    """vpn_30d / vpn_7d → дни; неизвестно → 0."""
    m = _VPN_DAYS_IN_ID.search((product_id or "").strip())
    if not m:
        return 0
    try:
        return max(0, int(m.group(1)))
    except ValueError:
        return 0


def level_for_qualified_count(n: int) -> dict[str, Any]:
    q = max(0, int(n))
    for lid, lo, hi, vpn_pct, sp_pct in LEVELS:
        if q < lo:
            continue
        if hi < 0 or q <= hi:
            return {
                "id": lid,
                "label": LEVEL_LABEL_RU.get(lid, lid),
                "qualified": q,
                "vpn_first_percent": vpn_pct,
                "stars_premium_percent": sp_pct,
                "min": lo,
                "max": hi,
            }
    lid, lo, hi, vpn_pct, sp_pct = LEVELS[-1]
    return {
        "id": lid,
        "label": LEVEL_LABEL_RU.get(lid, lid),
        "qualified": q,
        "vpn_first_percent": vpn_pct,
        "stars_premium_percent": sp_pct,
        "min": lo,
        "max": hi,
    }


def progress_to_next_level(qualified: int) -> tuple[int, int | None]:
    """(current_in_tier_display, need_for_next or None if max)."""
    q = max(0, int(qualified))
    lvl = level_for_qualified_count(q)
    if lvl["id"] == "gold":
        return q, None
    # next tier min
    for lid, lo, _hi, _a, _b in LEVELS:
        if lo > q:
            return q, lo
    return q, None


async def count_qualified_vpn_referrals(
    conn: aiosqlite.Connection,
    referrer_id: int,
    *,
    min_days: int = QUALIFY_VPN_MIN_DAYS,
) -> int:
    """
    DISTINCT друзья с хотя бы одним completed+выданным VPN-заказом,
    у которого срок тарифа ≥ min_days (7д/trial не считаются).
    """
    cur = await conn.execute(
        """
        SELECT DISTINCT o.user_id AS uid, o.product_id AS pid
        FROM orders o
        INNER JOIN users u ON u.user_id = o.user_id AND u.referrer_id = ?
        WHERE o.status = 'completed'
          AND LOWER(COALESCE(o.product_kind, '')) = 'vpn'
          AND o.fulfillment_applied_at IS NOT NULL
        """,
        (int(referrer_id),),
    )
    rows = await cur.fetchall()
    ok: set[int] = set()
    for r in rows:
        days = vpn_days_from_product_id(str(r["pid"] or ""))
        if days >= int(min_days):
            ok.add(int(r["uid"]))
    return len(ok)


async def user_has_own_paid_vpn_min_days(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    min_days: int = QUALIFY_VPN_MIN_DAYS,
) -> bool:
    """Свой completed VPN-заказ с тарифом ≥ min_days."""
    cur = await conn.execute(
        """
        SELECT product_id FROM orders
        WHERE user_id = ?
          AND status = 'completed'
          AND LOWER(COALESCE(product_kind, '')) = 'vpn'
          AND fulfillment_applied_at IS NOT NULL
        """,
        (int(user_id),),
    )
    for r in await cur.fetchall():
        if vpn_days_from_product_id(str(r["product_id"] or "")) >= int(min_days):
            return True
    return False


async def withdraw_in_cooldown(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    days: int = WITHDRAW_COOLDOWN_DAYS,
) -> bool:
    """Есть заявка pending/paid за последние `days` суток."""
    cur = await conn.execute(
        """
        SELECT 1 FROM ref_withdraw_requests
        WHERE user_id = ?
          AND status IN ('pending', 'paid')
          AND datetime(created_at) >= datetime('now', ?)
        LIMIT 1
        """,
        (int(user_id), f"-{int(days)} days"),
    )
    return (await cur.fetchone()) is not None


@dataclass(frozen=True)
class WithdrawEligibility:
    ok: bool
    balance_ok: bool
    qualified_ok: bool
    own_vpn_ok: bool
    cooldown_ok: bool
    pending_ok: bool
    balance: float
    qualified_n: int
    level: Mapping[str, Any]
    reasons: tuple[str, ...]


async def evaluate_withdraw_eligibility(
    conn: aiosqlite.Connection,
    user_id: int,
    *,
    balance: float,
    min_withdraw_rub: float,
    pending: bool,
) -> WithdrawEligibility:
    from bot.services import ref_withdraw_repo

    _ = ref_withdraw_repo
    qualified_n = await count_qualified_vpn_referrals(conn, user_id)
    level = level_for_qualified_count(qualified_n)
    own_vpn = await user_has_own_paid_vpn_min_days(conn, user_id)
    in_cd = await withdraw_in_cooldown(conn, user_id)
    bal = float(balance)
    balance_ok = bal + 1e-6 >= float(min_withdraw_rub)
    qualified_ok = qualified_n >= WITHDRAW_MIN_QUALIFIED_VPN
    own_vpn_ok = bool(own_vpn)
    cooldown_ok = not in_cd
    pending_ok = not pending
    reasons: list[str] = []
    if not balance_ok:
        reasons.append(f"нужно ≥ {float(min_withdraw_rub):.0f} ₽ на реферальном")
    if not qualified_ok:
        reasons.append(
            f"нужно ≥ {WITHDRAW_MIN_QUALIFIED_VPN} друзей с VPN от {QUALIFY_VPN_MIN_DAYS} дн. "
            f"(сейчас {qualified_n})"
        )
    if not own_vpn_ok:
        reasons.append(f"нужен свой оплаченный VPN от {QUALIFY_VPN_MIN_DAYS} дней")
    if not cooldown_ok:
        reasons.append(f"не чаще 1 заявки в {WITHDRAW_COOLDOWN_DAYS} дней")
    if not pending_ok:
        reasons.append("уже есть заявка в обработке")
    ok = balance_ok and qualified_ok and own_vpn_ok and cooldown_ok and pending_ok
    return WithdrawEligibility(
        ok=ok,
        balance_ok=balance_ok,
        qualified_ok=qualified_ok,
        own_vpn_ok=own_vpn_ok,
        cooldown_ok=cooldown_ok,
        pending_ok=pending_ok,
        balance=bal,
        qualified_n=qualified_n,
        level=level,
        reasons=tuple(reasons),
    )


def eligibility_checklist_html(el: WithdrawEligibility, *, min_withdraw_rub: float) -> str:
    from bot.util_html import esc

    def mark(ok: bool) -> str:
        return "✅" if ok else "❌"

    lines = [
        f"{mark(el.balance_ok)} Реферальный ≥ <b>{esc(f'{min_withdraw_rub:.0f}')} ₽</b> "
        f"(сейчас {esc(f'{el.balance:.2f}')} ₽)",
        f"{mark(el.qualified_ok)} ≥ <b>{WITHDRAW_MIN_QUALIFIED_VPN}</b> друзей с VPN "
        f"от {QUALIFY_VPN_MIN_DAYS} дн. (сейчас <b>{el.qualified_n}</b>)",
        f"{mark(el.own_vpn_ok)} Свой оплаченный VPN от {QUALIFY_VPN_MIN_DAYS} дн.",
        f"{mark(el.cooldown_ok)} Не чаще 1 заявки в {WITHDRAW_COOLDOWN_DAYS} дн.",
        f"{mark(el.pending_ok)} Нет заявки в обработке",
    ]
    return "\n".join(lines)
