"""Button after a call → parent push. Any family role. Not an antifake verdict."""
from __future__ import annotations

import asyncio
import logging
import time
from threading import Lock
from typing import Dict, Optional, Tuple

from app.services.antifake_family_store import (
    get_member_role,
    get_parent_user_ids,
    get_push_tokens,
    resolve_primary_family_id,
)

logger = logging.getLogger(__name__)

_lock = Lock()
_last_push_by_member: Dict[int, float] = {}
DEBOUNCE_SEC = 8
FAMILY_ROLES = frozenset({"parent", "child", "teenager", "elderly"})


def push_copy(display_name: Optional[str]) -> Tuple[str, str]:
    """Human pressed the button. No model score."""
    who = (display_name or "").strip()
    if not who:
        who = "Близкий человек"
    title = "Подозрительный звонок"
    body = f"{who} сообщил: просили деньги или код. Позвоните ему."
    return title, body


def member_display_name(member_user_id: int) -> Optional[str]:
    family_id = resolve_primary_family_id(int(member_user_id))
    if not family_id:
        return None
    from sqlalchemy import text

    from app.database.database import engine

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT name FROM family_members
                WHERE user_id = :uid AND family_id = :fid
                LIMIT 1
                """
            ),
            {"uid": int(member_user_id), "fid": family_id},
        ).first()
    if not row or row[0] is None:
        return None
    name = str(row[0]).strip()
    return name or None


def caller_has_family_role(member_user_id: int) -> bool:
    """Parent, child, teenager, or elderly. Unknown roles do not send."""
    family_id = resolve_primary_family_id(int(member_user_id))
    if not family_id:
        return False
    role = get_member_role(int(member_user_id), family_id)
    return (role or "") in FAMILY_ROLES


def maybe_notify_parents_money_or_code(*, member_user_id: int) -> Tuple[int, bool, str]:
    """Returns (pushes_sent, deduped, reason). Does not call the antifake 15-minute path.

    Recipients are other parents in the family. The person who pressed is excluded
    inside get_parent_user_ids, so a parent does not get their own push.
    """
    now = time.time()
    member_id = int(member_user_id)
    with _lock:
        last = _last_push_by_member.get(member_id, 0.0)
        if now - last < DEBOUNCE_SEC:
            return 0, True, "deduped"

    parent_ids = get_parent_user_ids(member_id)
    if not parent_ids:
        return 0, False, "no_other_parent"

    title, body = push_copy(member_display_name(member_id))
    extra = {
        "type": "elderly_scam_call",
        "deepLink": "aladdin://family",
    }

    sent = 0
    for parent_id in parent_ids:
        for token in get_push_tokens(parent_id):
            if _send_apns_sync(token, title, body, extra):
                sent += 1

    if sent:
        with _lock:
            _last_push_by_member[member_id] = time.time()
        logger.info(
            "elderly_scam_call_notify member=%s parents=%s pushes=%s",
            member_id,
            len(parent_ids),
            sent,
        )
        return sent, False, "sent"
    return 0, False, "push_failed"


def _send_apns_sync(token: str, title: str, body: str, extra: Dict[str, str]) -> bool:
    try:
        from app.security.notifications.apns_sender import send_apns_alert

        return asyncio.run(send_apns_alert(token, title, body, extra=extra))
    except Exception as exc:
        logger.warning("elderly_scam_call_notify apns failed: %s", exc)
        return False
