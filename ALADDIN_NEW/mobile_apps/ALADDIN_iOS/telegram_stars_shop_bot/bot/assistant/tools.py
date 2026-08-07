"""Read-only tools allowlist (R3, R7). telegram_user_id всегда из update."""

from __future__ import annotations

import logging
from typing import Any

import aiosqlite

from bot.assistant import repo as as_repo
from bot.assistant.kb import retrieve_kb
from bot.assistant.redact import mask_sub_urls
from bot.config import Settings
from bot.support_links import support_prefill_url

logger = logging.getLogger(__name__)

ALLOWED_TOOLS = frozenset(
    {
        "get_my_profile",
        "get_my_orders",
        "get_my_vpn",
        "get_kb",
        "open_human_ticket",
    }
)


def _row_get(row: Any, key: str, default: Any = None) -> Any:
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        return default


async def get_my_profile(
    conn: aiosqlite.Connection,
    settings: Settings,
    telegram_user_id: int,
) -> dict[str, Any]:
    from bot.services import users_repo

    stats = await users_repo.user_stats(conn, telegram_user_id)
    row = await users_repo.get_user(conn, telegram_user_id)
    created = str(_row_get(row, "created_at", "") or "") if row else ""
    return {
        "user_id": int(telegram_user_id),
        "reg_date": created,
        "balance_rub": float(stats.get("balance_rub") or 0),
        "ref_balance_rub": float(stats.get("ref_balance_rub") or 0),
        "ref_bonus_vpn_only": bool(getattr(settings, "ref_bonus_vpn_only", True)),
        "completed_orders": int(stats.get("completed_orders") or 0),
    }


async def get_my_orders(
    conn: aiosqlite.Connection,
    telegram_user_id: int,
    *,
    limit: int = 5,
    order_id: int | None = None,
) -> dict[str, Any]:
    from bot.services import orders_repo

    lim = max(1, min(5, int(limit or 5)))
    if order_id is not None:
        row = await orders_repo.get_order(conn, int(order_id))
        if row is None:
            return {"orders": [], "note": "order_not_found"}
        owner = int(_row_get(row, "user_id") or 0)
        if owner != int(telegram_user_id):
            # R3: never leak foreign order details
            return {"orders": [], "note": "order_not_found_or_no_access"}
        return {"orders": [_order_public(row)]}

    rows = await orders_repo.list_user_orders(conn, int(telegram_user_id), limit=lim)
    return {"orders": [_order_public(r) for r in rows]}


def _order_public(row: Any) -> dict[str, Any]:
    return {
        "id": int(_row_get(row, "id") or 0),
        "product_title": str(_row_get(row, "product_title") or ""),
        "status": str(_row_get(row, "status") or ""),
        "amount_rub": float(_row_get(row, "rub_after_discounts") or 0),
        "created_at": str(_row_get(row, "created_at") or ""),
        "product_kind": str(_row_get(row, "product_kind") or ""),
    }


async def get_my_vpn(
    settings: Settings,
    telegram_user_id: int,
) -> dict[str, Any]:
    from bot.services import vpn_admin_support_repo
    from bot.services.vpn_user_status import vpn_user_status_block_html_from_row

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return {
            "status": "unknown",
            "has_sub_link": False,
            "summary_html": "VPN база не настроена на этом хосте.",
        }
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, int(telegram_user_id))
    if not row:
        return {
            "status": "none",
            "has_sub_link": False,
            "paid_until": "",
            "account_kind": "",
            "trial": False,
            "summary_html": "VPN не активен.",
        }
    status = str(row.get("status") or "")
    opaque = str(row.get("opaque_token") or "").strip()
    has_link = status == "vpn_active" and bool(opaque)
    summary = vpn_user_status_block_html_from_row(row, inactive_variant="vpn_section")
    return {
        "status": status,
        "paid_until": str(row.get("paid_until") or ""),
        "account_kind": str(row.get("account_kind") or ""),
        "trial": bool(str(row.get("trial_used_at") or "").strip())
        or str(row.get("account_kind") or "") == "trial",
        "has_sub_link": has_link,
        "summary_html": mask_sub_urls(summary),
    }


async def get_kb_tool(
    conn: aiosqlite.Connection,
    *,
    chunk_ids: list[str] | None = None,
    topic: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    if chunk_ids:
        chunks = await as_repo.get_kb_chunks(conn, chunk_ids=chunk_ids)
    elif topic:
        chunks = await as_repo.get_kb_chunks(conn, topic=topic)
    elif query:
        chunks = await retrieve_kb(conn, query, limit=3)
    else:
        chunks = []
    return {
        "chunks": [
            {"id": c["id"], "topic": c["topic"], "text": (c["text_plain"] or "")[:2500]}
            for c in chunks
        ]
    }


async def open_human_ticket(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    telegram_user_id: int,
    session_id: int | None,
    reason: str,
    summary: str,
    urgency: str = "normal",
    username: str | None = None,
) -> dict[str, Any]:
    limit = int(getattr(settings, "assistant_ticket_daily_limit", 5) or 5)
    used = await as_repo.count_tickets_today(conn, telegram_user_id)
    if used >= limit:
        url = support_prefill_url(
            settings,
            f"Поддержка AiMonkey (лимит тикетов). user_id={telegram_user_id}",
        )
        return {
            "ok": False,
            "error": "ticket_daily_limit",
            "ticket_id": None,
            "support_url": url,
            "used_today": used,
            "limit": limit,
        }

    tid = await as_repo.create_ticket(
        conn,
        user_id=telegram_user_id,
        session_id=session_id,
        reason_code=reason or "esc.user",
        summary=summary or "user_request",
        urgency=urgency or "normal",
        meta={"username": username or ""},
    )
    prefill = (
        f"Тикет помощника #{tid}. reason={reason}. "
        f"user_id={telegram_user_id}"
        + (f" @{username}" if username else "")
        + f". {summary[:200]}"
    )
    url = support_prefill_url(settings, prefill)
    return {
        "ok": True,
        "ticket_id": tid,
        "support_url": url,
        "reason": reason,
    }


async def run_tool(
    name: str,
    conn: aiosqlite.Connection,
    settings: Settings,
    telegram_user_id: int,
    *,
    session_id: int | None = None,
    args: dict[str, Any] | None = None,
    username: str | None = None,
) -> dict[str, Any]:
    if name not in ALLOWED_TOOLS:
        return {"error": "tool_not_allowed", "name": name}
    a = args or {}
    # Drop any attempted foreign user_id
    a.pop("telegram_user_id", None)
    a.pop("user_id", None)

    if name == "get_my_profile":
        return await get_my_profile(conn, settings, telegram_user_id)
    if name == "get_my_orders":
        oid = a.get("order_id")
        try:
            oid_i = int(oid) if oid is not None else None
        except (TypeError, ValueError):
            oid_i = None
        return await get_my_orders(
            conn,
            telegram_user_id,
            limit=int(a.get("limit") or 5),
            order_id=oid_i,
        )
    if name == "get_my_vpn":
        return await get_my_vpn(settings, telegram_user_id)
    if name == "get_kb":
        ids = a.get("chunk_ids")
        if isinstance(ids, str):
            ids = [ids]
        if not isinstance(ids, list):
            ids = None
        return await get_kb_tool(
            conn,
            chunk_ids=[str(x) for x in ids] if ids else None,
            topic=str(a["topic"]) if a.get("topic") else None,
            query=str(a["query"]) if a.get("query") else None,
        )
    if name == "open_human_ticket":
        return await open_human_ticket(
            conn,
            settings,
            telegram_user_id=telegram_user_id,
            session_id=session_id,
            reason=str(a.get("reason") or "esc.user"),
            summary=str(a.get("summary") or ""),
            urgency=str(a.get("urgency") or "normal"),
            username=username,
        )
    return {"error": "tool_not_allowed", "name": name}
