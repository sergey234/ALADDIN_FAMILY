"""Русские тексты ops-алертов для единого чата ALERT_TELEGRAM_CHAT_ID."""

from __future__ import annotations

import re

from bot.util_html import esc

_SEV_EMOJI = {
    "critical": "🔴",
    "warning": "⚠️",
    "info": "ℹ️",
}


def format_admin_bot_alert_html(*, severity: str, title: str, body: str) -> str:
    """Перевод известных ops-алертов в русский HTML."""
    sev = (severity or "info").strip().lower()
    emoji = _SEV_EMOJI.get(sev, "📢")
    t = (title or "").strip()
    b = (body or "").strip()
    low_t = t.lower()

    if "автовыдача: заказ выдан" in low_t or "auto_fulfill" in low_t and "completed" in b:
        m_oid = re.search(r"order_id=#?(\d+)", b)
        oid = m_oid.group(1) if m_oid else "?"
        return (
            f"{emoji} <b>Заказ #{esc(oid)} выдан (автовыдача)</b>\n\n"
            f"{esc(_body_lines_ru(b))}"
        )

    if "ton balance below" in low_t or "istar_low_ton" in b:
        bal = _kv(b, "balance_ton")
        thr = _kv(b, "threshold_ton")
        return (
            f"{emoji} <b>Мало TON на кошельке iStar</b>\n\n"
            f"Баланс: <b>{esc(bal or '?')} TON</b>\n"
            f"Порог: <code>{esc(thr or '?')} TON</code>\n\n"
            f"<i>Автовыдача приостановлена — пополните TON-кошелёк iStar.</i>"
        )

    if "5xx on recipient search" in low_t or "istar_search_http" in b:
        oid = _kv(b, "order_id") or _re_group(b, r"order_id=(\d+)")
        rcpt = _kv(b, "recipient") or ""
        return (
            f"{emoji} <b>iStar недоступен (ошибка поиска получателя)</b>\n\n"
            f"Заказ: <code>#{esc(oid or '?')}</code>\n"
            f"Получатель: <code>{esc(rcpt)}</code>\n\n"
            f"<i>Это сбой на стороне iStar. Заказ в очереди — бот повторит сам.</i>"
        )

    if "insufficient ton" in low_t:
        oid = _kv(b, "order_id") or _re_group(b, r"order_id=(\d+)")
        return (
            f"{emoji} <b>Не хватило TON для выдачи</b>\n\n"
            f"Заказ: <code>#{esc(oid or '?')}</code>\n"
            f"<i>Пополните TON-кошелёк iStar и сбросьте попытки в карточке заказа.</i>"
        )

    if "circuit breaker" in low_t or "на паузе" in low_t:
        return (
            f"{emoji} <b>Автовыдача на паузе (серия сбоев iStar)</b>\n\n"
            f"{esc(b)}\n\n"
            f"<i>Через ~30 мин воркер продолжит сам. При долгом простое — ручная выдача.</i>"
        )

    if "stuck paid orders (no processing)" in low_t:
        cnt = _kv(b, "count")
        ids = _kv(b, "sample_ids")
        mins = _kv(b, "minutes")
        return (
            f"{emoji} <b>Заказы оплачены, но не в работе</b>\n\n"
            f"Дольше <code>{esc(mins or '?')}</code> мин без выдачи: <b>{esc(cnt or '?')}</b> шт.\n"
            f"Примеры: <code>{esc(ids or '—')}</code>"
        )

    if "stuck paid orders detected" in low_t:
        cnt = _kv(b, "count")
        ids = _kv(b, "sample_ids")
        hrs = _kv(b, "hours")
        return (
            f"{emoji} <b>Зависшие оплаченные заказы</b>\n\n"
            f"Дольше <code>{esc(hrs or '?')}</code> ч: <b>{esc(cnt or '?')}</b> шт.\n"
            f"Примеры: <code>{esc(ids or '—')}</code>"
        )

    if "stuck processing" in low_t:
        cnt = _kv(b, "count")
        ids = _kv(b, "sample_ids")
        mins = _kv(b, "minutes")
        return (
            f"{emoji} <b>Заказы долго «в работе»</b>\n\n"
            f"Больше <code>{esc(mins or '?')}</code> мин: <b>{esc(cnt or '?')}</b> шт.\n"
            f"Примеры: <code>{esc(ids or '—')}</code>\n"
            f"<i>Проверьте webhook iStar или дождитесь опроса статуса.</i>"
        )

    # Body already trusted HTML from vpn_ops_health (short alert / recovered).
    # Do NOT wrap in <code>{esc(b)}</code> — that shows raw <b>/<code> tags to the operator.
    if "vpn ops health" in low_t:
        if "recovered" in low_t:
            title_ru = "VPN ops: восстановлено"
        elif "critical" in low_t:
            title_ru = "VPN ops health: critical"
        elif "degraded" in low_t:
            title_ru = "VPN ops health: degraded"
        else:
            title_ru = t or "VPN ops health"
        return f"{emoji} <b>{esc(title_ru)}</b>\n\n{b}" if b else f"{emoji} <b>{esc(title_ru)}</b>"

    if low_t.startswith("problem:"):
        name = t.split(":", 1)[-1].strip()
        return f"{emoji} <b>Проблема: {esc(_watchdog_name_ru(name))}</b>\n\n<code>{esc(b)}</code>"

    if low_t.startswith("recovery:"):
        name = t.split(":", 1)[-1].strip()
        return f"✅ <b>Восстановлено: {esc(_watchdog_name_ru(name))}</b>\n\n<code>{esc(b)}</code>"

    if "break-glass" in low_t:
        return f"{emoji} <b>Ручная отметка «Оплачен» (break-glass)</b>\n\n<code>{esc(b)}</code>"

    if "create_failed" in low_t:
        return f"{emoji} <b>Ошибка создания заказа в iStar</b>\n\n<code>{esc(b)}</code>"

    return f"{emoji} <b>{esc(t)}</b>\n\n<code>{esc(b)}</code>" if b else f"{emoji} <b>{esc(t)}</b>"


def _kv(body: str, key: str) -> str | None:
    m = re.search(rf"\b{re.escape(key)}=([^\s]+)", body)
    return m.group(1) if m else None


def _re_group(body: str, pattern: str) -> str | None:
    m = re.search(pattern, body)
    return m.group(1) if m else None


def _body_lines_ru(body: str) -> str:
    lines = []
    for part in body.replace("\n", " ").split():
        if "=" in part:
            k, _, v = part.partition("=")
            lines.append(f"{k}: {v}")
    return "\n".join(lines) if lines else body


def _watchdog_name_ru(name: str) -> str:
    mapping = {
        "bot_log_error_burst": "всплеск ошибок в логах",
        "partner_api_health": "health Partner API",
        "webhook_backlog": "очередь исходящих webhook",
        "redis_fallback_memory": "Redis rate-limit → память",
        "service:aladdin-telegram-bot.service": "сервис Telegram-бота",
        "service:aladdin-partner-api.service": "сервис Partner API",
        "service:aladdin-webhook-worker.service": "сервис webhook-worker",
    }
    return mapping.get(name, name)
