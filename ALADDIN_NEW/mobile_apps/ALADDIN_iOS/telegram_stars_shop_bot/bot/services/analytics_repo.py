from __future__ import annotations

import json
from typing import Any

import aiosqlite


_MAX_EVENT_TYPE_LEN = 64
_MAX_META_KEYS = 32
_MAX_META_VALUE_LEN = 256
_ALLOWED_META_KEYS = {
    "source",
    "campaign",
    "creative",
    "product_hint",
    "positioning_variant",
    "via",
    "product_id",
    "order_id",
    "card",
    "payment_method",
    "recipient_kind",
    "code",
}


def _normalize_meta(meta: dict[str, Any] | None) -> dict[str, Any] | None:
    if not meta:
        return None
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if len(out) >= _MAX_META_KEYS:
            break
        key = str(k).strip()[:64]
        if not key:
            continue
        if key in _ALLOWED_META_KEYS:
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                out[key] = str(v)[:_MAX_META_VALUE_LEN]
            else:
                out[key] = str(v)[:_MAX_META_VALUE_LEN]
            continue
        # Unknown keys are preserved under namespaced bucket for compatibility.
        bucket_key = f"x_{key}"[:64]
        if v is None:
            continue
        out[bucket_key] = str(v)[:_MAX_META_VALUE_LEN]
    if not out:
        return None
    out["schema_version"] = "v2"
    return out


async def log_event(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    event_type: str,
    meta: dict[str, Any] | None = None,
) -> None:
    """Событие воронки / поведения (не блокирует основной поток при ошибках вызывающей стороны)."""
    clean_meta = _normalize_meta(meta)
    payload = json.dumps(clean_meta, ensure_ascii=False) if clean_meta else None
    await conn.execute(
        """
        INSERT INTO analytics_events (user_id, event_type, meta_json)
        VALUES (?, ?, ?)
        """,
        (int(user_id), (event_type or "").strip()[:_MAX_EVENT_TYPE_LEN], payload),
    )
    await conn.commit()
