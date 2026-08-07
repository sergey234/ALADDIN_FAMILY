"""AssistantOrchestrator — KB + tools + LLM + validate + persist."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

import aiosqlite
from aiogram import Bot

from bot.assistant import repo as as_repo
from bot.assistant.html_sanitize import sanitize_telegram_html
from bot.assistant.kb import retrieve_kb
from bot.assistant.llm_client import (
    FALLBACK_USER_HTML,
    chat_complete,
    llm_configured,
    should_alert_admin_llm_down,
)
from bot.assistant.policy import (
    SYSTEM_PROMPT,
    TOPIC_TO_KB,
    detect_immediate_escalate,
    looks_like_injection,
    validate_assistant_reply,
)
from bot.assistant.redact import redact_for_llm
from bot.assistant.tools import get_my_orders, get_my_profile, get_my_vpn, open_human_ticket, run_tool
from bot.config import Settings
from bot.services import analytics_repo, marketing

logger = logging.getLogger(__name__)

_ORDER_ID_RE = re.compile(r"#?\s*(\d{1,8})")
_STATUS_RE = re.compile(r"статус|заказ|оплат|где\s+(мой|заказ)", re.I)
_VPN_RE = re.compile(r"\bvpn\b|хэпп|happ|подписк|не\s+работает|не\s+подключ", re.I)
_BALANCE_RE = re.compile(r"баланс|бонус|реферал", re.I)


@dataclass
class OrchestratorResult:
    html: str
    session_id: int
    escalate_ticket_id: int | None = None
    support_url: str | None = None
    kb_ids: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    topic_guess: str | None = None
    llm_down: bool = False


def _guess_topic(text: str) -> str | None:
    t = (text or "").lower()
    if "android" in t or "андройд" in t or "андрод" in t:
        return "happ_android"
    if "iphone" in t or "ios" in t or "айфон" in t:
        return "happ_ios"
    if "капч" in t:
        return "captcha"
    if "бонус" in t or "реферал" in t or "приглас" in t:
        return "ref"
    if "возврат" in t or "верн" in t:
        return "refund"
    if any(
        w in t
        for w in (
            "сколько стоит",
            "цена",
            "цены",
            "тариф",
            "прайс",
            "стоимость",
            "почём",
            "почем",
        )
    ):
        return "catalog"
    if _VPN_RE.search(t):
        return "vpn_down"
    if _STATUS_RE.search(t):
        return "pay_status"
    return None


async def _maybe_alert_admin(
    bot: Bot | None,
    settings: Settings,
    text: str,
) -> None:
    if bot is None:
        return
    raw = (settings.assistant_admin_chat_id or "").strip()
    if not raw:
        return
    try:
        chat_id = int(raw)
    except ValueError:
        return
    try:
        await bot.send_message(chat_id, text[:3500])
    except Exception as e:
        logger.warning("assistant_admin_notify_failed: %s", e)


async def handle_user_message(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    user_id: int,
    text: str,
    username: str | None = None,
    bot: Bot | None = None,
    topic_hint: str | None = None,
) -> OrchestratorResult:
    session_id = await as_repo.get_or_create_session(
        conn,
        user_id,
        ttl_min=int(settings.assistant_session_ttl_min or 30),
        max_turns=int(settings.assistant_session_max_turns or 20),
    )

    daily = await as_repo.count_user_msgs_today(conn, user_id)
    limit = int(settings.assistant_daily_msg_limit or 40)
    if daily >= limit:
        html = (
            f"Достигнут лимит сообщений помощнику за сутки ({limit}). "
            "Нажмите <b>👨‍💼 Человек</b> или зайдите завтра."
        )
        await as_repo.add_turn(
            conn, session_id=session_id, user_id=user_id, role="assistant", content=html
        )
        return OrchestratorResult(html=html, session_id=session_id)

    clean = redact_for_llm((text or "").strip())
    topic = topic_hint or _guess_topic(clean)
    await as_repo.add_turn(
        conn,
        session_id=session_id,
        user_id=user_id,
        role="user",
        content=clean,
        topic_guess=topic,
    )
    await as_repo.bump_turn(conn, session_id)
    try:
        await analytics_repo.log_event(
            conn, user_id=user_id, event_type="assistant_msg", meta={"via": topic or "chat"}
        )
    except Exception:
        pass

    # Immediate escalate paths
    esc = detect_immediate_escalate(clean)
    if esc == "esc.refund":
        return await _escalate_path(
            conn,
            settings,
            bot=bot,
            user_id=user_id,
            session_id=session_id,
            reason=esc,
            summary=clean[:500],
            username=username,
            extra_html=marketing.refund_policy_blurb_html(settings),
        )

    if looks_like_injection(clean):
        html = (
            "Не могу менять правила или выполнять админ-действия. "
            "Могу помочь с VPN, оплатой и гайдами Happ — или соединить с человеком."
        )
        html = sanitize_telegram_html(html)
        await as_repo.add_turn(
            conn, session_id=session_id, user_id=user_id, role="assistant", content=html
        )
        return OrchestratorResult(html=html, session_id=session_id, topic_guess=topic)

    # Deterministic tool gathers (no write tools)
    tools_used: list[str] = []
    tool_payload: dict[str, Any] = {}

    hint_ids = TOPIC_TO_KB.get(topic or "", None)
    chunks = await retrieve_kb(conn, clean, topic_hint_ids=hint_ids, limit=2)
    kb_ids = [c["id"] for c in chunks]
    tools_used.append("get_kb")
    tool_payload["kb"] = [
        {"id": c["id"], "text": (c["text_plain"] or "")[:450]} for c in chunks
    ]

    if _STATUS_RE.search(clean) or _ORDER_ID_RE.search(clean):
        oid = None
        m = re.search(r"заказ[^\d]{0,10}#?\s*(\d{1,8})", clean, re.I)
        if m:
            oid = int(m.group(1))
        else:
            m2 = re.search(r"#\s*(\d{1,8})", clean)
            if m2:
                oid = int(m2.group(1))
        tool_payload["orders"] = await get_my_orders(conn, user_id, limit=5, order_id=oid)
        tools_used.append("get_my_orders")
        # pay stuck escalate
        for o in tool_payload["orders"].get("orders") or []:
            st = str(o.get("status") or "")
            if st in {"paid", "processing"}:
                # Lightweight: user asking status on stuck — escalate if SLA exceeded via created_at string compare optional
                pass

    if _VPN_RE.search(clean) or topic in {"vpn_down", "happ_android", "happ_ios"}:
        vpn = await get_my_vpn(settings, user_id)
        tool_payload["vpn"] = vpn
        tools_used.append("get_my_vpn")
        if str(vpn.get("status") or "") in {"vpn_failed", "vpn_manual_override"}:
            return await _escalate_path(
                conn,
                settings,
                bot=bot,
                user_id=user_id,
                session_id=session_id,
                reason="esc.vpn_failed",
                summary=f"VPN status={vpn.get('status')}. {clean[:300]}",
                username=username,
            )

    if _BALANCE_RE.search(clean) or topic == "ref":
        tool_payload["profile"] = await get_my_profile(conn, settings, user_id)
        tools_used.append("get_my_profile")

    # pay_stuck: any own paid/processing older than SLA minutes
    if "orders" in tool_payload:
        sla = int(settings.assistant_pay_sla_min or 30)
        for o in tool_payload["orders"].get("orders") or []:
            if str(o.get("status") or "") not in {"paid", "processing"}:
                continue
            cur = await conn.execute(
                """
                SELECT CASE WHEN datetime(created_at, ?) < datetime('now') THEN 1 ELSE 0 END AS stuck
                FROM orders WHERE id = ? AND user_id = ?
                """,
                (f"+{sla} minutes", int(o["id"]), int(user_id)),
            )
            row = await cur.fetchone()
            if row and int(row["stuck"] or 0) == 1 and _STATUS_RE.search(clean):
                return await _escalate_path(
                    conn,
                    settings,
                    bot=bot,
                    user_id=user_id,
                    session_id=session_id,
                    reason="esc.pay_stuck",
                    summary=f"Order #{o['id']} status={o['status']} >{sla}m. {clean[:300]}",
                    username=username,
                )

    history = await as_repo.recent_turns(conn, session_id, limit=4)
    system_text = SYSTEM_PROMPT
    if bool(getattr(settings, "assistant_brand_voice_enabled", True)):
        from bot.assistant.brand_gold_answers import (
            brand_tone_rules_compact,
            format_fewshot_block,
            select_gold_fewshots,
        )

        system_text = SYSTEM_PROMPT + "\n" + brand_tone_rules_compact()
        golds = select_gold_fewshots(topic, clean, limit=2, max_chars_each=380)
        few = format_fewshot_block(golds, max_chars_each=380)
        if few:
            system_text = system_text + "\n" + few[:900]
    messages = [{"role": "system", "content": system_text}]
    compact_tools = json.dumps(tool_payload, ensure_ascii=False)
    if len(compact_tools) > 1600:
        # Prefer KB + short orders/vpn summary under tight LLM budget.
        slim = {
            "kb": tool_payload.get("kb") or [],
            "orders": (tool_payload.get("orders") or {}).get("orders", [])[:2],
            "vpn": {
                k: tool_payload["vpn"].get(k)
                for k in ("status", "has_sub_link", "paid_until")
                if "vpn" in tool_payload
            }
            if tool_payload.get("vpn")
            else None,
            "profile": tool_payload.get("profile"),
        }
        compact_tools = json.dumps(slim, ensure_ascii=False)[:1600]
    messages.append({"role": "system", "content": "TOOL_RESULTS_JSON:\n" + compact_tools})
    for h in history[:-1][-2:]:
        role = "assistant" if h["role"] == "assistant" else "user"
        messages.append({"role": role, "content": h["content"][:350]})
    messages.append({"role": "user", "content": clean[:500]})

    if not llm_configured(settings):
        return await _llm_down(
            conn,
            settings,
            bot=bot,
            user_id=user_id,
            session_id=session_id,
            kb_ids=kb_ids,
            tools_used=tools_used,
            topic=topic,
            tool_payload=tool_payload,
        )

    llm = await chat_complete(settings, messages)
    if not llm.ok and str(llm.error or "").startswith("http_402"):
        # Ultra-compact retry for low OpenRouter credit budgets.
        mini_kb = (tool_payload.get("kb") or [{}])[:1]
        mini = [{"role": "system", "content": SYSTEM_PROMPT}]
        mini.append(
            {
                "role": "system",
                "content": "KB:\n"
                + json.dumps(mini_kb, ensure_ascii=False)[:700]
                + "\nОтветь кратко по KB + citation.",
            }
        )
        mini.append({"role": "user", "content": clean[:300]})
        llm = await chat_complete(settings, mini)
        messages = mini
    if not llm.ok:
        if should_alert_admin_llm_down():
            await _maybe_alert_admin(
                bot, settings, f"Assistant LLM down: {llm.error} user={user_id}"
            )
        return await _llm_down(
            conn,
            settings,
            bot=bot,
            user_id=user_id,
            session_id=session_id,
            kb_ids=kb_ids,
            tools_used=tools_used,
            topic=topic,
            tool_payload=tool_payload,
            err=llm.error,
        )

    vr = validate_assistant_reply(llm.text, user_text=clean, kb_chunk_ids=kb_ids)
    if not vr.ok and vr.escalate_code == "esc.low_conf":
        # Retry once with stronger KB insistence if we have chunks
        if kb_ids:
            messages.append(
                {
                    "role": "system",
                    "content": "Ответь строго по KB chunks выше и поставь citation [kb.id]. Иначе скажи что не уверен.",
                }
            )
            llm2 = await chat_complete(settings, messages)
            if llm2.ok:
                vr = validate_assistant_reply(
                    llm2.text, user_text=clean, kb_chunk_ids=kb_ids, allow_howto_without_kb=True
                )
        if not vr.ok:
            return await _escalate_path(
                conn,
                settings,
                bot=bot,
                user_id=user_id,
                session_id=session_id,
                reason="esc.low_conf",
                summary=clean[:500],
                username=username,
            )

    html = sanitize_telegram_html(vr.text)
    await as_repo.add_turn(
        conn,
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content=html,
        topic_guess=topic,
        tool_names=tools_used,
        kb_chunk_ids=kb_ids,
    )
    try:
        await analytics_repo.log_event(
            conn,
            user_id=user_id,
            event_type="assistant_tool",
            meta={"via": ",".join(tools_used)[:200]},
        )
    except Exception:
        pass

    return OrchestratorResult(
        html=html,
        session_id=session_id,
        kb_ids=kb_ids,
        tools_used=tools_used,
        topic_guess=topic,
    )


async def _llm_down(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    bot: Bot | None,
    user_id: int,
    session_id: int,
    kb_ids: list[str],
    tools_used: list[str],
    topic: str | None,
    tool_payload: dict[str, Any],
    err: str | None = None,
) -> OrchestratorResult:
    _ = (bot, err)
    # Best-effort: if we have KB / tool facts, answer without LLM.
    parts: list[str] = [FALLBACK_USER_HTML]
    kb = tool_payload.get("kb") or []
    if kb:
        snippet = str(kb[0].get("text") or "")[:900]
        if snippet:
            parts.append(f"\n\n<b>Краткая подсказка из гайда</b> [{kb[0].get('id')}]:\n{snippet}")
    orders = (tool_payload.get("orders") or {}).get("orders") or []
    if orders:
        lines = []
        for o in orders[:3]:
            lines.append(f"#{o.get('id')} — {o.get('status')} — {o.get('amount_rub')} ₽")
        parts.append("\n\n<b>Ваши заказы (из базы):</b>\n" + "\n".join(lines))
    vpn = tool_payload.get("vpn")
    if vpn and vpn.get("summary_html"):
        parts.append("\n\n<b>VPN:</b>\n" + str(vpn["summary_html"]))

    html = sanitize_telegram_html("\n".join(parts))
    await as_repo.add_turn(
        conn,
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content=html,
        topic_guess=topic,
        tool_names=tools_used,
        kb_chunk_ids=kb_ids,
    )
    return OrchestratorResult(
        html=html,
        session_id=session_id,
        kb_ids=kb_ids,
        tools_used=tools_used,
        topic_guess=topic,
        llm_down=True,
    )


async def _escalate_path(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    bot: Bot | None,
    user_id: int,
    session_id: int,
    reason: str,
    summary: str,
    username: str | None,
    extra_html: str = "",
) -> OrchestratorResult:
    res = await open_human_ticket(
        conn,
        settings,
        telegram_user_id=user_id,
        session_id=session_id,
        reason=reason,
        summary=summary,
        urgency="high" if reason in {"esc.refund", "esc.vpn_failed", "esc.abuse"} else "normal",
        username=username,
    )
    if not res.get("ok"):
        html = (
            "Сейчас слишком много обращений к человеку за сутки. "
            "Напишите в поддержку по кнопке ниже или подождите до завтра."
        )
        if res.get("support_url"):
            html += f'\n\n<a href="{res["support_url"]}">Открыть поддержку</a>'
        html = sanitize_telegram_html(html)
        await as_repo.add_turn(
            conn, session_id=session_id, user_id=user_id, role="assistant", content=html
        )
        return OrchestratorResult(
            html=html,
            session_id=session_id,
            support_url=res.get("support_url"),
        )

    tid = int(res["ticket_id"])
    html = (
        f"Передал человеку. Тикет <b>#{tid}</b>.\n"
        "Оператор увидит кратко суть вашего вопроса."
    )
    if extra_html:
        html += "\n\n" + extra_html
    if res.get("support_url"):
        html += f'\n\n<a href="{res["support_url"]}">Написать в поддержку с № тикета</a>'
    html = sanitize_telegram_html(html)

    await as_repo.add_turn(
        conn,
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content=html,
        tool_names=["open_human_ticket"],
    )
    try:
        await analytics_repo.log_event(
            conn,
            user_id=user_id,
            event_type="assistant_escalate",
            meta={"code": reason, "via": str(tid)},
        )
    except Exception:
        pass

    admin_msg = (
        f"🎫 Assistant ticket #{tid}\n"
        f"user={user_id} @{username or '-'}\n"
        f"reason={reason}\n"
        f"{summary[:800]}"
    )
    await _maybe_alert_admin(bot, settings, admin_msg)
    return OrchestratorResult(
        html=html,
        session_id=session_id,
        escalate_ticket_id=tid,
        support_url=res.get("support_url"),
    )


async def escalate_user_button(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    user_id: int,
    username: str | None,
    bot: Bot | None,
    session_id: int | None = None,
) -> OrchestratorResult:
    if session_id is None:
        session_id = await as_repo.get_or_create_session(
            conn,
            user_id,
            ttl_min=int(settings.assistant_session_ttl_min or 30),
            max_turns=int(settings.assistant_session_max_turns or 20),
        )
    turns = await as_repo.recent_turns(conn, session_id, limit=10)
    summary = " | ".join(f"{t['role']}:{t['content'][:80]}" for t in turns)[:500] or "user pressed human"
    return await _escalate_path(
        conn,
        settings,
        bot=bot,
        user_id=user_id,
        session_id=session_id,
        reason="esc.user",
        summary=summary,
        username=username,
    )


# Silence unused import warning helpers for external direct tool use.
_ = run_tool
