"""fsl-13 / fsl-15 — soft presence («я в порядке» + заряд). No GPS track."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_family_store import (
    get_parent_user_ids,
    get_push_tokens,
    resolve_primary_family_id,
)

logger = logging.getLogger(__name__)

_CREATE = """
CREATE TABLE IF NOT EXISTS family_member_presence (
    family_id VARCHAR(64) NOT NULL,
    member_id VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    display_name VARCHAR(128) NOT NULL DEFAULT '',
    battery_percent SMALLINT,
    last_im_ok_at TIMESTAMPTZ NOT NULL,
    last_online_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (family_id, member_id)
);
CREATE INDEX IF NOT EXISTS idx_family_presence_family
    ON family_member_presence (family_id, last_im_ok_at DESC);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        for stmt in _CREATE.strip().split(";"):
            line = stmt.strip()
            if line:
                conn.execute(text(line))


def _member_row(user_id: int, family_id: str) -> Optional[Dict[str, Any]]:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT id, name, user_id
                FROM family_members
                WHERE family_id = :fid AND user_id = :uid
                ORDER BY id DESC
                LIMIT 1
                """
            ),
            {"fid": family_id, "uid": int(user_id)},
        ).mappings().first()
    return dict(row) if row else None


def upsert_im_ok(
    *,
    user_id: int,
    battery_percent: Optional[int] = None,
) -> Dict[str, Any]:
    """Record «я в порядке». Returns {ok, member_id, family_id, parents_notified}."""
    ensure_tables()
    family_id = resolve_primary_family_id(int(user_id))
    if not family_id:
        return {"ok": False, "error": "no_family", "parents_notified": 0}

    member = _member_row(int(user_id), family_id)
    if not member:
        return {"ok": False, "error": "no_member", "parents_notified": 0}

    member_id = str(member["id"])
    display_name = (str(member.get("name") or "").strip()) or "Участник"
    now = datetime.now(timezone.utc)
    batt: Optional[int] = None
    if battery_percent is not None:
        try:
            batt = max(0, min(100, int(battery_percent)))
        except (TypeError, ValueError):
            batt = None

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_member_presence (
                    family_id, member_id, user_id, display_name,
                    battery_percent, last_im_ok_at, last_online_at, updated_at
                ) VALUES (
                    :fid, :mid, :uid, :name,
                    :batt, :now, :now, :now
                )
                ON CONFLICT (family_id, member_id) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    battery_percent = EXCLUDED.battery_percent,
                    last_im_ok_at = EXCLUDED.last_im_ok_at,
                    last_online_at = EXCLUDED.last_online_at,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "fid": family_id,
                "mid": member_id,
                "uid": int(user_id),
                "name": display_name[:128],
                "batt": batt,
                "now": now,
            },
        )

    parents_notified = _notify_parents_im_ok(
        member_user_id=int(user_id),
        display_name=display_name,
        battery_percent=batt,
    )
    return {
        "ok": True,
        "member_id": member_id,
        "family_id": family_id,
        "parents_notified": parents_notified,
    }


def list_family_presence(*, user_id: int) -> Dict[str, Any]:
    """Soft presence for the caller's family (no GPS)."""
    ensure_tables()
    family_id = resolve_primary_family_id(int(user_id))
    if not family_id:
        return {"ok": True, "members": []}

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT member_id, display_name, battery_percent,
                       last_im_ok_at, last_online_at
                FROM family_member_presence
                WHERE family_id = :fid
                ORDER BY last_im_ok_at DESC
                LIMIT 40
                """
            ),
            {"fid": family_id},
        ).mappings().all()

    members: List[Dict[str, Any]] = []
    for row in rows:
        im_ok = row.get("last_im_ok_at")
        online = row.get("last_online_at")
        members.append(
            {
                "member_id": str(row["member_id"]),
                "display_name": str(row.get("display_name") or ""),
                "battery_percent": row.get("battery_percent"),
                "last_im_ok_at": im_ok.isoformat() if hasattr(im_ok, "isoformat") else None,
                "last_online_at": online.isoformat() if hasattr(online, "isoformat") else None,
            }
        )
    return {"ok": True, "members": members}


def notify_parents_urgent_signal(
    *,
    member_user_id: int,
    display_name: str,
    reason: str,
) -> Dict[str, Any]:
    """Send urgent/help APNs to family parents without writing plaintext chat."""
    family_id = resolve_primary_family_id(int(member_user_id))
    if not family_id:
        return {"ok": False, "error": "no_family", "parents_notified": 0}

    member = _member_row(int(member_user_id), family_id)
    if not member:
        return {"ok": False, "error": "no_member", "parents_notified": 0}

    name = (display_name or str(member.get("name") or "")).strip() or "Family member"
    parent_ids = get_parent_user_ids(int(member_user_id))
    if not parent_ids:
        return {"ok": True, "parents_notified": 0, "reason": "no_parents"}

    sent = 0
    for parent_id in parent_ids:
        for token in get_push_tokens(parent_id):
            if _send_apns_sync(
                token,
                "Need help",
                f"{name}: urgent family signal",
                {
                    "type": "urgent_signal",
                    "reason": reason or "manual",
                    "deepLink": "aladdin://family",
                    "priority": "critical",
                },
            ):
                sent += 1
    return {"ok": True, "parents_notified": sent}


def _notify_parents_im_ok(
    *,
    member_user_id: int,
    display_name: str,
    battery_percent: Optional[int],
) -> int:
    parent_ids = get_parent_user_ids(int(member_user_id))
    if not parent_ids:
        return 0
    batt = f" · заряд {battery_percent}%" if battery_percent is not None else ""
    title = "Я в порядке"
    body = f"{display_name}: я в порядке{batt}"
    sent = 0
    for parent_id in parent_ids:
        for token in get_push_tokens(parent_id):
            if _send_apns_sync(
                token,
                title,
                body,
                {"type": "im_ok", "deepLink": "aladdin://family"},
            ):
                sent += 1
    return sent


def _send_apns_sync(token: str, title: str, body: str, extra: Dict[str, str]) -> bool:
    try:
        from app.security.notifications.apns_sender import send_apns_alert

        return asyncio.run(send_apns_alert(token, title, body, extra=extra))
    except Exception as exc:
        logger.warning("family_presence im_ok apns failed: %s", exc)
        return False
