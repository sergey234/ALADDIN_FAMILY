"""fws-02: family-wide habit reminder templates (parent configures, members schedule locally)."""
from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_family_store import (
    get_member_role,
    is_family_member,
    resolve_primary_family_id,
)

_PARENT_ROLES = frozenset({"parent", "elderly"})
_VALID_PRESETS = frozenset({"water", "phone_down", "wind_down", "medicine"})
# fhc-07 — custom habit modes (local schedule on device; once_at scheduled in fhc-15)
_VALID_CUSTOM_MODES = frozenset({"window", "once_daily", "once_at"})
_MAX_CUSTOM = 5
_CUSTOM_TITLE_MAX = 40
_CUSTOM_INTERVAL_MIN = 15
_CUSTOM_INTERVAL_MAX = 180

_DEFAULT_CONFIG: Dict[str, Any] = {
    "presets": {
        "water": {
            "enabled": False,
            "hour": 9,
            "minute": 0,
            "end_hour": 21,
            "end_minute": 0,
            "interval_minutes": 120,
            "daily_liters": 2.0,
            # p1-7a — water Due-ping OFF by default
            "ping_until_done": False,
            "ping_interval_minutes": 20,
            "ping_max_per_day": 6,
        },
        "phone_down": {
            "enabled": False,
            "hour": 21,
            "minute": 0,
            "ping_until_done": False,
            "ping_interval_minutes": 20,
            "ping_max_per_day": 6,
        },
        "wind_down": {
            "enabled": False,
            "hour": 22,
            "minute": 30,
            "ping_until_done": False,
            "ping_interval_minutes": 20,
            "ping_max_per_day": 6,
        },
        # Medicine: same day window as water (start→end + interval)
        "medicine": {
            "enabled": False,
            "hour": 9,
            "minute": 0,
            "end_hour": 21,
            "end_minute": 0,
            "interval_minutes": 180,
            "daily_liters": 2.0,
            "ping_until_done": True,
            "ping_interval_minutes": 20,
            "ping_max_per_day": 6,
        },
    },
    "member_ids": [],
    "custom": [],
}

_ALLOWED_WATER_LITERS = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
_ALLOWED_WATER_INTERVALS = (60, 90, 120, 180)
_ALLOWED_PING_INTERVALS = (15, 20, 25, 30)

_CREATE = """
CREATE TABLE IF NOT EXISTS family_habit_reminders (
    family_id VARCHAR(64) PRIMARY KEY,
    config_json JSONB NOT NULL,
    updated_by_user_id BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        conn.execute(text(_CREATE.strip()))


def _nearest(value: float, options: tuple) -> float:
    return min(options, key=lambda x: abs(float(x) - float(value)))


def _normalize_preset(raw: Any, preset_id: str = "") -> Dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    hour = int(data.get("hour", 11 if preset_id != "water" else 9))
    minute = int(data.get("minute", 0))
    # p1-7a: default ping OFF (especially water); clamp interval 15–30, max 1–12
    ping_interval = int(data.get("ping_interval_minutes", 20))
    ping_max = int(data.get("ping_max_per_day", 6))
    out: Dict[str, Any] = {
        "enabled": bool(data.get("enabled", False)),
        "hour": max(0, min(23, hour)),
        "minute": max(0, min(59, minute)),
        "ping_until_done": bool(data.get("ping_until_done", False)),
        "ping_interval_minutes": int(_nearest(ping_interval, _ALLOWED_PING_INTERVALS)),
        "ping_max_per_day": max(1, min(12, ping_max)),
    }
    if preset_id in ("water", "medicine"):
        default_end = 21
        default_interval = 120 if preset_id == "water" else 180
        end_hour = int(data.get("end_hour", default_end))
        end_minute = int(data.get("end_minute", 0))
        interval = int(data.get("interval_minutes", default_interval))
        liters = float(data.get("daily_liters", 2.0))
        out["end_hour"] = max(0, min(23, end_hour))
        out["end_minute"] = max(0, min(59, end_minute))
        out["interval_minutes"] = int(_nearest(interval, _ALLOWED_WATER_INTERVALS))
        out["daily_liters"] = float(_nearest(liters, _ALLOWED_WATER_LITERS))
        if preset_id == "water" and "ping_until_done" not in data:
            out["ping_until_done"] = False
        elif preset_id == "medicine" and "ping_until_done" not in data:
            out["ping_until_done"] = True
    return out


def _first_emoji(value: str) -> str:
    emoji = (value or "").strip()
    if not emoji:
        return "⭐️"
    # Keep a short grapheme-ish prefix (ZWJ sequences may exceed 1 codepoint).
    return emoji[:8]


def _normalize_custom_item(raw: Any, sort_fallback: int) -> Optional[Dict[str, Any]]:
    """fhc-07 — one custom reminder; empty title → drop; unknown mode → keep disabled."""
    if not isinstance(raw, dict):
        return None
    title = str(raw.get("title") or "").strip()
    if not title:
        return None
    if len(title) > _CUSTOM_TITLE_MAX:
        title = title[:_CUSTOM_TITLE_MAX]

    item_id = str(raw.get("id") or "").strip() or str(uuid.uuid4())
    mode = str(raw.get("mode") or "once_daily").strip() or "once_daily"
    mode_ok = mode in _VALID_CUSTOM_MODES
    enabled = bool(raw.get("enabled", True)) if mode_ok else False

    hour = int(raw.get("hour", 21))
    minute = int(raw.get("minute", 0))
    end_hour = int(raw.get("end_hour", 21))
    end_minute = int(raw.get("end_minute", 0))
    interval = int(raw.get("interval_minutes", 60))
    ping_interval = int(raw.get("ping_interval_minutes", 20))
    ping_max = int(raw.get("ping_max_per_day", 6))
    sort_order = int(raw.get("sort_order", sort_fallback))

    fire_at_raw = raw.get("fire_at")
    fire_at: Optional[str]
    if fire_at_raw is None:
        fire_at = None
    else:
        fire_at = str(fire_at_raw).strip() or None

    return {
        "id": item_id,
        "title": title,
        "emoji": _first_emoji(str(raw.get("emoji") or "⭐️")),
        "enabled": enabled,
        "mode": mode,
        "hour": max(0, min(23, hour)),
        "minute": max(0, min(59, minute)),
        "end_hour": max(0, min(23, end_hour)),
        "end_minute": max(0, min(59, end_minute)),
        "interval_minutes": max(
            _CUSTOM_INTERVAL_MIN, min(_CUSTOM_INTERVAL_MAX, interval)
        ),
        "ping_until_done": bool(raw.get("ping_until_done", False)),
        "ping_interval_minutes": int(_nearest(ping_interval, _ALLOWED_PING_INTERVALS)),
        "ping_max_per_day": max(1, min(12, ping_max)),
        "sort_order": max(0, sort_order),
        "fire_at": fire_at,
    }


def _normalize_custom_list(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, Any]] = []
    seen_ids = set()
    for index, item in enumerate(raw):
        if len(out) >= _MAX_CUSTOM:
            break
        normalized = _normalize_custom_item(item, sort_fallback=index)
        if not normalized:
            continue
        if normalized["id"] in seen_ids:
            normalized["id"] = str(uuid.uuid4())
        seen_ids.add(normalized["id"])
        out.append(normalized)
    out.sort(key=lambda row: (int(row.get("sort_order", 0)), str(row.get("id", ""))))
    return out


def normalize_config(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    base = deepcopy(_DEFAULT_CONFIG)
    if not isinstance(raw, dict):
        return base
    presets_in = raw.get("presets") if isinstance(raw.get("presets"), dict) else {}
    for key in _VALID_PRESETS:
        if key in presets_in:
            base["presets"][key] = _normalize_preset(presets_in.get(key), preset_id=key)
        elif key == "water":
            base["presets"][key] = _normalize_preset(base["presets"].get(key, {}), preset_id="water")
    member_ids = raw.get("member_ids")
    if isinstance(member_ids, list):
        base["member_ids"] = [str(m).strip() for m in member_ids if str(m).strip()]
    # Absent custom (legacy clients) → []; present → normalize max 5
    if "custom" in raw:
        base["custom"] = _normalize_custom_list(raw.get("custom"))
    else:
        base["custom"] = []
    return base


def get_config_for_user(user_id: int) -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {"family_id": None, "config": normalize_config(None), "configured": False}
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT config_json, updated_at, updated_by_user_id
                FROM family_habit_reminders
                WHERE family_id = :fid
                LIMIT 1
                """
            ),
            {"fid": family_id},
        ).first()
    if not row:
        return {
            "family_id": family_id,
            "config": normalize_config(None),
            "configured": False,
        }
    payload = row[0]
    if isinstance(payload, str):
        payload = json.loads(payload)
    return {
        "family_id": family_id,
        "config": normalize_config(payload if isinstance(payload, dict) else None),
        "configured": True,
        "updated_at": row[1].isoformat() if row[1] else None,
        "updated_by_user_id": int(row[2]) if row[2] is not None else None,
    }


def set_config_for_user(*, user_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        raise PermissionError("no_family")
    role = (get_member_role(user_id, family_id) or "").lower()
    if role not in _PARENT_ROLES:
        raise PermissionError("parent_only")

    # fhc-07 / G4 — old clients omit `custom`; do not wipe stored custom[].
    incoming = dict(config) if isinstance(config, dict) else {}
    if "custom" not in incoming:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT config_json FROM family_habit_reminders
                    WHERE family_id = :fid LIMIT 1
                    """
                ),
                {"fid": family_id},
            ).first()
        if row and row[0] is not None:
            payload = row[0]
            if isinstance(payload, str):
                payload = json.loads(payload)
            if isinstance(payload, dict) and "custom" in payload:
                incoming["custom"] = payload.get("custom")

    normalized = normalize_config(incoming)
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_habit_reminders
                    (family_id, config_json, updated_by_user_id, updated_at)
                VALUES (:fid, CAST(:cfg AS JSONB), :uid, :now)
                ON CONFLICT (family_id) DO UPDATE SET
                    config_json = EXCLUDED.config_json,
                    updated_by_user_id = EXCLUDED.updated_by_user_id,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "fid": family_id,
                "cfg": json.dumps(normalized),
                "uid": int(user_id),
                "now": now,
            },
        )
    return {
        "family_id": family_id,
        "config": normalized,
        "configured": True,
        "updated_at": now.isoformat(),
    }


def if_then_lines_for_sync(config: Dict[str, Any]) -> List[str]:
    """Optional wellness/habits sync strings."""
    normalized = normalize_config(config)
    lines: List[str] = []
    mapping = {
        "water": "Если настало время, то выпить стакан воды 💧",
        "phone_down": "Если вечер, то убрать телефон из рук 📵",
        "wind_down": "Если поздно, то начать спокойный вечерний ритуал 😴",
        "medicine": "Если настало время, то принять лекарство 💊",
    }
    for preset_id, phrase in mapping.items():
        preset = normalized["presets"].get(preset_id, {})
        if preset.get("enabled"):
            h = int(preset.get("hour", 0))
            m = int(preset.get("minute", 0))
            lines.append(f"Если {h:02d}:{m:02d}, то {phrase.split(' то ', 1)[-1]}")
    return lines
