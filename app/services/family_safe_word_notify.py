"""fws-01: parent APNs when a family member fails safe-word verification."""
from __future__ import annotations

import asyncio
import logging
import time
from threading import Lock
from typing import Dict

from app.services.antifake_family_store import get_parent_user_ids, get_push_tokens

logger = logging.getLogger(__name__)

_lock = Lock()
_last_push_by_member: Dict[int, float] = {}
COOLDOWN_SEC = 15 * 60


def maybe_notify_parents_safe_word_mismatch(
    *,
    member_user_id: int,
    family_id: str,
    context: str = "antifake",
) -> int:
    """Send APNs to parents; returns count of successful push attempts."""
    now = time.time()
    with _lock:
        last = _last_push_by_member.get(int(member_user_id), 0.0)
        if now - last < COOLDOWN_SEC:
            return 0
        _last_push_by_member[int(member_user_id)] = now

    parent_ids = get_parent_user_ids(int(member_user_id))
    if not parent_ids:
        return 0

    title = "ALADDIN: неверное семейное слово"
    body = (
        "Член семьи ввёл неверную фразу при проверке звонка. "
        "Свяжитесь с ним и убедитесь, что всё в порядке."
    )
    extra = {
        "deepLink": "aladdin://family/safe-word-alert",
        "family_id": family_id,
        "context": context,
        "alert_type": "safe_word_mismatch",
    }

    sent = 0
    for parent_id in parent_ids:
        for token in get_push_tokens(parent_id):
            if _send_apns_sync(token, title, body, extra):
                sent += 1

    if sent:
        logger.info(
            "family_safe_word_mismatch_notify member=%s family=%s parents=%s pushes=%s",
            member_user_id,
            family_id,
            len(parent_ids),
            sent,
        )
    return sent


def _send_apns_sync(token: str, title: str, body: str, extra: Dict[str, str]) -> bool:
    try:
        from app.security.notifications.apns_sender import send_apns_alert

        return asyncio.run(send_apns_alert(token, title, body, extra=extra))
    except Exception as exc:
        logger.warning("family_safe_word_notify apns failed: %s", exc)
        return False
