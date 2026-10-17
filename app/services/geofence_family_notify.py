"""WAVE3 L4 — geofence enter/exit → parent APNs (no continuous GPS track)."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from app.services.antifake_family_store import get_parent_user_ids, get_push_tokens

logger = logging.getLogger(__name__)

# Per parent + region + direction cooldown (seconds)
_COOLDOWN_SEC = 5 * 60
_last_sent: Dict[str, float] = {}


def notify_parents_geofence_event(
    *,
    member_user_id: int,
    display_name: str,
    place_name: str,
    is_arrival: bool,
    region_id: str,
    event_type: str,
) -> Dict[str, Any]:
    parent_ids = get_parent_user_ids(int(member_user_id))
    if not parent_ids:
        return {"ok": True, "parents_notified": 0, "reason": "no_parents"}

    place = (place_name or "место").strip() or "место"
    name = (display_name or "Член семьи").strip() or "Член семьи"
    if is_arrival:
        title = "Прибытие"
        body = f"{name}: на месте «{place}»"
    else:
        title = "Уход"
        body = f"{name}: вышел(а) из «{place}»"

    sent = 0
    skipped_cooldown = 0
    now = time.time()
    for parent_id in parent_ids:
        cool_key = f"{parent_id}:{region_id}:{'in' if is_arrival else 'out'}"
        last = _last_sent.get(cool_key, 0.0)
        if last and (now - last) < _COOLDOWN_SEC:
            skipped_cooldown += 1
            continue
        for token in get_push_tokens(parent_id):
            if _send_apns_sync(
                token,
                title,
                body,
                {
                    "type": event_type or ("geofence_place_arrival" if is_arrival else "geofence_place_departure"),
                    "deepLink": "aladdin://family/location",
                    "place": place,
                    "priority": "high",
                },
            ):
                sent += 1
                _last_sent[cool_key] = now

    return {
        "ok": True,
        "parents_notified": sent,
        "skipped_cooldown": skipped_cooldown,
    }


def _send_apns_sync(token: str, title: str, body: str, extra: Dict[str, str]) -> bool:
    try:
        from app.security.notifications.apns_sender import send_apns_alert

        return asyncio.run(send_apns_alert(token, title, body, extra=extra))
    except Exception as exc:
        logger.warning("geofence_family_notify apns failed: %s", exc)
        return False
