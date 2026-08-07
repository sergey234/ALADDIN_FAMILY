"""Промокоды: активация в кабинете, скидка в quote без ломки checkout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import aiosqlite

PromoFail = Literal[
    "not_found",
    "inactive",
    "not_started",
    "expired",
    "limit",
    "already_used",
    "personal",
    "new_users_only",
    "empty",
]


@dataclass(frozen=True)
class PromoOffer:
    promo_id: int
    activation_id: int
    code: str
    discount_type: str  # percent | fixed_rub
    discount_value: float
    scope: str  # all | stars | premium | vpn
    reward_kind: str = "discount"


def normalize_promo_code(raw: str) -> str:
    return "".join((raw or "").strip().upper().split())


def _parse_allowed_ids(raw: str) -> set[int]:
    out: set[int] = set()
    for part in (raw or "").replace(";", ",").split(","):
        p = part.strip()
        if not p:
            continue
        try:
            out.add(int(p))
        except ValueError:
            continue
    return out


def _row_scope_ok(scope: str, product_kind: str) -> bool:
    s = (scope or "all").strip().lower()
    if s in ("", "all", "*"):
        return True
    return s == (product_kind or "").strip().lower()


async def get_by_code(conn: aiosqlite.Connection, code: str) -> aiosqlite.Row | None:
    c = normalize_promo_code(code)
    if not c:
        return None
    cur = await conn.execute("SELECT * FROM promo_codes WHERE code = ?", (c,))
    return await cur.fetchone()


async def list_promos(conn: aiosqlite.Connection, *, limit: int = 30) -> list[aiosqlite.Row]:
    cur = await conn.execute(
        "SELECT * FROM promo_codes ORDER BY id DESC LIMIT ?",
        (max(1, min(100, int(limit))),),
    )
    return await cur.fetchall()


async def create_promo(
    conn: aiosqlite.Connection,
    *,
    code: str,
    title: str,
    discount_type: str,
    discount_value: float,
    scope: str = "all",
    starts_at: str | None = None,
    ends_at: str | None = None,
    max_activations: int | None = None,
    once_per_user: bool = True,
    new_users_only: bool = False,
    allowed_user_ids: str = "",
    is_active: bool = True,
    reward_kind: str = "discount",
) -> int:
    c = normalize_promo_code(code)
    if not c:
        raise ValueError("empty code")
    dt = (discount_type or "").strip().lower()
    if dt not in ("percent", "fixed_rub", "pct", "rub"):
        raise ValueError("discount_type")
    if dt == "pct":
        dt = "percent"
    if dt == "rub":
        dt = "fixed_rub"
    sc = (scope or "all").strip().lower() or "all"
    cur = await conn.execute(
        """
        INSERT INTO promo_codes (
            code, title, reward_kind, discount_type, discount_value, scope,
            starts_at, ends_at, max_activations, once_per_user, new_users_only,
            is_active, allowed_user_ids
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            c,
            (title or c).strip()[:120],
            (reward_kind or "discount").strip() or "discount",
            dt,
            float(discount_value),
            sc,
            starts_at,
            ends_at,
            max_activations,
            1 if once_per_user else 0,
            1 if new_users_only else 0,
            1 if is_active else 0,
            (allowed_user_ids or "").strip(),
        ),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def set_promo_active(conn: aiosqlite.Connection, promo_id: int, *, active: bool) -> bool:
    cur = await conn.execute(
        "UPDATE promo_codes SET is_active = ? WHERE id = ?",
        (1 if active else 0, int(promo_id)),
    )
    await conn.commit()
    return cur.rowcount > 0


async def _user_has_completed_order(conn: aiosqlite.Connection, user_id: int) -> bool:
    cur = await conn.execute(
        """
        SELECT 1 FROM orders
        WHERE user_id = ? AND status IN ('paid', 'processing', 'completed')
        LIMIT 1
        """,
        (int(user_id),),
    )
    return await cur.fetchone() is not None


async def _validate_promo_for_user(
    conn: aiosqlite.Connection,
    row: aiosqlite.Row,
    *,
    user_id: int,
) -> PromoFail | None:
    if int(row["is_active"] or 0) != 1:
        return "inactive"
    starts = (row["starts_at"] or "").strip()
    ends = (row["ends_at"] or "").strip()
    if starts:
        cur = await conn.execute(
            "SELECT 1 WHERE datetime('now') >= datetime(?)",
            (starts,),
        )
        if await cur.fetchone() is None:
            return "not_started"
    if ends:
        cur = await conn.execute(
            "SELECT 1 WHERE datetime('now') <= datetime(?)",
            (ends,),
        )
        if await cur.fetchone() is None:
            return "expired"
    max_a = row["max_activations"]
    if max_a is not None and int(max_a) >= 0:
        if int(row["activation_count"] or 0) >= int(max_a):
            return "limit"
    allowed = _parse_allowed_ids(str(row["allowed_user_ids"] or ""))
    if allowed and int(user_id) not in allowed:
        return "personal"
    if int(row["new_users_only"] or 0) == 1 and await _user_has_completed_order(conn, user_id):
        return "new_users_only"
    cur = await conn.execute(
        "SELECT id, status FROM promo_activations WHERE promo_id = ? AND user_id = ?",
        (int(row["id"]), int(user_id)),
    )
    prev = await cur.fetchone()
    if prev is not None and int(row["once_per_user"] or 1) == 1:
        return "already_used"
    return None


async def activate_promo(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    code: str,
) -> tuple[Literal["ok"], PromoOffer] | tuple[Literal["fail"], PromoFail]:
    c = normalize_promo_code(code)
    if not c:
        return "fail", "empty"
    row = await get_by_code(conn, c)
    if row is None:
        return "fail", "not_found"
    # Treat inactive/expired as not_found for user-facing copy (ТЗ).
    err = await _validate_promo_for_user(conn, row, user_id=user_id)
    if err in ("inactive", "not_started", "expired"):
        return "fail", "not_found"
    if err is not None:
        return "fail", err

    await conn.execute("BEGIN IMMEDIATE")
    try:
        # re-check under lock
        cur = await conn.execute("SELECT * FROM promo_codes WHERE id = ?", (int(row["id"]),))
        locked = await cur.fetchone()
        if locked is None:
            await conn.execute("ROLLBACK")
            return "fail", "not_found"
        err2 = await _validate_promo_for_user(conn, locked, user_id=user_id)
        if err2 in ("inactive", "not_started", "expired"):
            await conn.execute("ROLLBACK")
            return "fail", "not_found"
        if err2 is not None:
            await conn.execute("ROLLBACK")
            return "fail", err2

        cur = await conn.execute(
            """
            INSERT INTO promo_activations (promo_id, user_id, status)
            VALUES (?, ?, 'bound')
            """,
            (int(locked["id"]), int(user_id)),
        )
        act_id = int(cur.lastrowid)
        await conn.execute(
            "UPDATE promo_codes SET activation_count = activation_count + 1 WHERE id = ?",
            (int(locked["id"]),),
        )
        await conn.execute(
            "UPDATE users SET active_promo_activation_id = ? WHERE user_id = ?",
            (act_id, int(user_id)),
        )
        await conn.commit()
    except aiosqlite.IntegrityError:
        await conn.execute("ROLLBACK")
        return "fail", "already_used"
    except Exception:
        await conn.execute("ROLLBACK")
        raise

    offer = PromoOffer(
        promo_id=int(locked["id"]),
        activation_id=act_id,
        code=str(locked["code"]),
        discount_type=str(locked["discount_type"]),
        discount_value=float(locked["discount_value"]),
        scope=str(locked["scope"] or "all"),
        reward_kind=str(locked["reward_kind"] or "discount"),
    )
    return "ok", offer


async def get_active_offer_for_user(conn: aiosqlite.Connection, user_id: int) -> PromoOffer | None:
    cur = await conn.execute(
        "SELECT active_promo_activation_id FROM users WHERE user_id = ?",
        (int(user_id),),
    )
    u = await cur.fetchone()
    if u is None:
        return None
    act_id = u["active_promo_activation_id"]
    if act_id is None:
        return None
    cur = await conn.execute(
        """
        SELECT a.id AS activation_id, a.status, p.*
        FROM promo_activations a
        JOIN promo_codes p ON p.id = a.promo_id
        WHERE a.id = ? AND a.user_id = ?
        """,
        (int(act_id), int(user_id)),
    )
    row = await cur.fetchone()
    if row is None or str(row["status"] or "") != "bound":
        return None
    if int(row["is_active"] or 0) != 1:
        return None
    # soft date check — if expired, don't apply
    ends = (row["ends_at"] or "").strip()
    if ends:
        cur = await conn.execute("SELECT 1 WHERE datetime('now') <= datetime(?)", (ends,))
        if await cur.fetchone() is None:
            return None
    return PromoOffer(
        promo_id=int(row["id"]),
        activation_id=int(row["activation_id"]),
        code=str(row["code"]),
        discount_type=str(row["discount_type"]),
        discount_value=float(row["discount_value"]),
        scope=str(row["scope"] or "all"),
        reward_kind=str(row["reward_kind"] or "discount"),
    )


def compute_promo_discount_rub(
    *,
    rub_list: float,
    rub_after_other: float,
    product_kind: str,
    promo: PromoOffer,
) -> float:
    if (promo.reward_kind or "discount") != "discount":
        return 0.0
    if not _row_scope_ok(promo.scope, product_kind):
        return 0.0
    dt = (promo.discount_type or "").strip().lower()
    if dt == "percent":
        disc = round(float(rub_list) * (float(promo.discount_value) / 100.0), 2)
    else:
        disc = round(float(promo.discount_value), 2)
    return max(0.0, min(disc, max(0.0, float(rub_after_other))))


async def redeem_activation_for_order(
    conn: aiosqlite.Connection,
    *,
    order_id: int,
    user_id: int,
    activation_id: int | None = None,
) -> bool:
    """Пометить активацию redeemed после оплаты; сбросить active у user."""
    act_id = activation_id
    if act_id is None:
        cur = await conn.execute(
            "SELECT active_promo_activation_id FROM users WHERE user_id = ?",
            (int(user_id),),
        )
        u = await cur.fetchone()
        if u is None or u["active_promo_activation_id"] is None:
            # fallback: order.promo_code
            cur = await conn.execute(
                "SELECT promo_code FROM orders WHERE id = ?",
                (int(order_id),),
            )
            o = await cur.fetchone()
            code = (o["promo_code"] if o else None) or ""
            if not code:
                return False
            cur = await conn.execute(
                """
                SELECT a.id FROM promo_activations a
                JOIN promo_codes p ON p.id = a.promo_id
                WHERE a.user_id = ? AND p.code = ? AND a.status = 'bound'
                ORDER BY a.id DESC LIMIT 1
                """,
                (int(user_id), normalize_promo_code(code)),
            )
            row = await cur.fetchone()
            if row is None:
                return False
            act_id = int(row["id"])
        else:
            act_id = int(u["active_promo_activation_id"])

    cur = await conn.execute(
        """
        UPDATE promo_activations
        SET status = 'redeemed',
            redeemed_order_id = ?,
            redeemed_at = datetime('now')
        WHERE id = ? AND user_id = ? AND status = 'bound'
        """,
        (int(order_id), int(act_id), int(user_id)),
    )
    if cur.rowcount <= 0:
        return False
    await conn.execute(
        """
        UPDATE users SET active_promo_activation_id = NULL
        WHERE user_id = ? AND active_promo_activation_id = ?
        """,
        (int(user_id), int(act_id)),
    )
    return True


def fail_message(fail: PromoFail) -> str:
    from bot.services.promo_copy import (
        promo_already_used_html,
        promo_limit_html,
        promo_not_found_html,
        promo_personal_html,
        promo_new_users_only_html,
        promo_empty_html,
    )

    if fail == "already_used":
        return promo_already_used_html()
    if fail == "limit":
        return promo_limit_html()
    if fail == "personal":
        return promo_personal_html()
    if fail == "new_users_only":
        return promo_new_users_only_html()
    if fail == "empty":
        return promo_empty_html()
    return promo_not_found_html()


def offer_to_dict(offer: PromoOffer) -> dict[str, Any]:
    return {
        "promo_id": offer.promo_id,
        "activation_id": offer.activation_id,
        "code": offer.code,
        "discount_type": offer.discount_type,
        "discount_value": offer.discount_value,
        "scope": offer.scope,
        "reward_kind": offer.reward_kind,
    }
