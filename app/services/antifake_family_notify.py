"""L-01: notify parents when child/elderly check returns likely_fake."""
from __future__ import annotations

import asyncio
import logging
import time
from threading import Lock
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_family_store import get_parent_user_ids, get_push_tokens

logger = logging.getLogger(__name__)

_lock = Lock()
_last_push_by_child: Dict[int, float] = {}
COOLDOWN_SEC = 15 * 60


def _job_user_id(job_id: str) -> Optional[int]:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT user_id FROM antifake_jobs
                WHERE id = CAST(:id AS UUID) LIMIT 1
                """
            ),
            {"id": job_id},
        ).first()
    if not row or row[0] is None:
        return None
    return int(row[0])


def maybe_notify_parents_likely_fake(*, job_id: str, verdict: Dict[str, Any]) -> int:
    """Send APNs to parents; returns count of push attempts."""
    if str(verdict.get("verdict") or "") != "likely_fake":
        return 0

    child_id = _job_user_id(job_id)
    if child_id is None:
        return 0

    now = time.time()
    with _lock:
        last = _last_push_by_child.get(child_id, 0.0)
        if now - last < COOLDOWN_SEC:
            return 0
        _last_push_by_child[child_id] = now

    parent_ids = get_parent_user_ids(child_id)
    if not parent_ids:
        return 0

    conf_pct = int(float(verdict.get("confidence") or 0) * 100)
    if conf_pct <= 0:
        conf_pct = int(verdict.get("confidence") or 72)

    title = "ALADDIN: подозрительная проверка"
    body = f"Член семьи получил результат «вероятно подделка» ({conf_pct}%). Откройте Hub → Antifake."
    extra = {
        "deepLink": f"aladdin://antifake/family-alert?job_id={job_id}",
        "job_id": job_id,
        "verdict": "likely_fake",
    }

    sent = 0
    for parent_id in parent_ids:
        for token in get_push_tokens(parent_id):
            if _send_apns_sync(token, title, body, extra):
                sent += 1

    if sent:
        logger.info(
            "antifake_family_notify child=%s parents=%s pushes=%s job=%s",
            child_id,
            len(parent_ids),
            sent,
            job_id,
        )
    return sent


def _send_apns_sync(token: str, title: str, body: str, extra: Dict[str, Any]) -> bool:
    try:
        from app.security.notifications.apns_sender import send_apns_alert

        return asyncio.run(send_apns_alert(token, title, body, extra=extra))
    except Exception as exc:
        logger.warning("antifake_family_notify apns failed: %s", exc)
        return False
