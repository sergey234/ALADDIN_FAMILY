from __future__ import annotations

import asyncio
import logging
import time

import httpx

from bot.config import Settings

_log = logging.getLogger(__name__)
_dedupe_lock: asyncio.Lock | None = None
_dedupe_last_sent_ts: dict[str, float] = {}


async def _dedupe_allowed(dedupe_key: str, cooldown_seconds: int, now_ts: float | None = None) -> bool:
    now = now_ts if now_ts is not None else time.time()
    if cooldown_seconds <= 0:
        return True
    global _dedupe_lock
    if _dedupe_lock is None:
        _dedupe_lock = asyncio.Lock()
    async with _dedupe_lock:
        prev = _dedupe_last_sent_ts.get(dedupe_key)
        if prev is not None and (now - prev) < cooldown_seconds:
            return False
        _dedupe_last_sent_ts[dedupe_key] = now
        return True


def _render_message(severity: str, title: str, body: str) -> str:
    sev = (severity or "info").strip().upper()
    t = (title or "Alert").strip()
    b = (body or "").strip()
    return f"[{sev}] {t}\n{b}" if b else f"[{sev}] {t}"


async def _send_telegram(settings: Settings, message: str) -> bool:
    token = (settings.alert_telegram_bot_token or "").strip()
    chat_id = (settings.alert_telegram_chat_id or "").strip()
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message[:3500],
                    "disable_web_page_preview": True,
                },
            )
        if r.status_code >= 300:
            _log.warning("alerts_telegram_send_failed status=%s body=%s", r.status_code, r.text[:300])
            return False
        return True
    except Exception:
        _log.exception("alerts_telegram_send_exception")
        return False


async def _send_pagerduty(settings: Settings, severity: str, title: str, body: str, dedupe_key: str) -> bool:
    routing_key = (settings.pagerduty_routing_key or "").strip()
    if not routing_key:
        return False
    payload = {
        "routing_key": routing_key,
        "event_action": "trigger",
        "dedup_key": dedupe_key,
        "payload": {
            "summary": title[:1024],
            "severity": (severity or "warning").strip().lower(),
            "source": "telegram-stars-shop-bot",
            "custom_details": {"body": body[:2048]},
        },
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post("https://events.pagerduty.com/v2/enqueue", json=payload)
        if r.status_code >= 300:
            _log.warning("alerts_pagerduty_send_failed status=%s body=%s", r.status_code, r.text[:300])
            return False
        return True
    except Exception:
        _log.exception("alerts_pagerduty_send_exception")
        return False


async def send_alert(
    settings: Settings,
    severity: str,
    title: str,
    body: str,
    dedupe_key: str,
) -> bool:
    """
    Единая отправка ops-алертов с дедупом по dedupe_key.
    Если ALERTS_ENABLED=false, просто выходим без ошибок.
    """
    if not bool(settings.alerts_enabled):
        return False
    key = (dedupe_key or "").strip()
    if not key:
        key = f"{severity}:{title}"
    cooldown = max(0, int(settings.alert_cooldown_seconds))
    if not await _dedupe_allowed(key, cooldown):
        return False

    msg = _render_message(severity=severity, title=title, body=body)
    tg_ok, pd_ok = await asyncio.gather(
        _send_telegram(settings, msg),
        _send_pagerduty(settings, severity=severity, title=title, body=body, dedupe_key=key),
    )
    if not tg_ok and not pd_ok:
        _log.warning("alerts_no_transport_succeeded dedupe_key=%s", key)
    return tg_ok or pd_ok
