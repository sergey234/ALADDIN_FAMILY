"""Location bubble — agent + user-scoped DB (no mock)."""
from __future__ import annotations

import json
import logging
import math
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import urllib.error
import urllib.request
from sqlalchemy import text

from app.database.database import engine

logger = logging.getLogger(__name__)

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"
FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback", "mock-real-protection"})
AGENT_NAME = "location_bubble_agent"

_agent_singleton: Any = None
_fallback_settings: Dict[str, Dict[str, Dict[str, Any]]] = {}
_fallback_history: Dict[str, List[Dict[str, Any]]] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reject_mock(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = json.dumps(payload, ensure_ascii=False)
    for marker in FORBIDDEN_SOURCES:
        if marker in raw:
            raise ValueError(f"mock_source_rejected:{marker}")
    source = str(payload.get("source", ""))
    if source in FORBIDDEN_SOURCES:
        raise ValueError(f"mock_source_rejected:{source}")
    return payload


def _probe_user_id_column() -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'location'
                  AND table_name = 'location_requests'
                  AND column_name = 'user_id'
                LIMIT 1
                """
            )
        ).first()
        return row is not None


def _user_predicate(user_id: int) -> tuple[str, Dict[str, Any]]:
    if _probe_user_id_column():
        return "user_id::text = :user_id", {"user_id": str(user_id)}
    return "1 = 0", {}


def _sfm_execute(function_id: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    payload = json.dumps({"function": function_id, "params": params}).encode("utf-8")
    request = urllib.request.Request(
        SFM_EXECUTE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode() or "{}")
    except Exception:
        return None
    if not body.get("success"):
        return None
    result = body.get("result", body)
    return result if isinstance(result, dict) else None


def _get_agent_optional():
    global _agent_singleton
    if _agent_singleton is not None:
        return _agent_singleton
    try:
        from security.ai_agents.location_bubble_agent import LocationBubbleAgent

        _agent_singleton = LocationBubbleAgent({})
        return _agent_singleton
    except Exception as exc:
        logger.warning("location bubble agent load failed: %s", exc)
        return None


def _rule_engine_bubble(lat: float, lon: float, radius: int = 500) -> Dict[str, Any]:
    distance = random.uniform(0, radius)
    angle = random.uniform(0, 2 * math.pi)
    lat_offset = (distance * math.cos(angle)) / 111000.0
    lon_offset = (distance * math.sin(angle)) / (111000.0 * math.cos(math.radians(lat)))
    return {
        "approximate_latitude": lat + lat_offset,
        "approximate_longitude": lon + lon_offset,
        "radius": radius,
        "accuracy": float(radius),
        "generated_at": datetime.now(timezone.utc).timestamp(),
    }


def _persist_request(
    user_id: int,
    *,
    app_name: str,
    action: str,
    accuracy: Optional[str] = None,
) -> str:
    if not _probe_user_id_column():
        raise ValueError("user_scope_unavailable")
    req_id = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO location.location_requests
                    (id, user_id, app_name, action, accuracy, timestamp)
                VALUES
                    (CAST(:id AS uuid), :user_id, :app_name, :action, :accuracy, CURRENT_TIMESTAMP)
                """
            ),
            {
                "id": req_id,
                "user_id": user_id,
                "app_name": app_name[:255],
                "action": action,
                "accuracy": accuracy,
            },
        )
    return req_id


def get_stats(user_id: int) -> Dict[str, Any]:
    sfm_result = _sfm_execute("get_location_bubble_agent_stats", {"user_id": user_id})
    if sfm_result and "blockedRequests" in sfm_result:
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        return _reject_mock(sfm_result)

    predicate, params = _user_predicate(user_id)
    with engine.connect() as conn:
        row = conn.execute(
            text(
                f"""
                SELECT
                  COALESCE(SUM(CASE WHEN action = 'blocked' THEN 1 ELSE 0 END), 0)::int AS blocked,
                  COALESCE(SUM(CASE WHEN action = 'allowed' THEN 1 ELSE 0 END), 0)::int AS allowed,
                  COALESCE(SUM(CASE WHEN action = 'modified' THEN 1 ELSE 0 END), 0)::int AS modified,
                  COALESCE(MODE() WITHIN GROUP (ORDER BY accuracy), 'medium') AS current_accuracy
                FROM location.location_requests
                WHERE {predicate}
                """
            ),
            params,
        ).mappings().first()

    data = dict(row or {})
    return _reject_mock(
        {
            "blockedRequests": data.get("blocked") or 0,
            "allowedRequests": data.get("allowed") or 0,
            "modifiedRequests": data.get("modified") or 0,
            "currentAccuracy": data.get("current_accuracy") or "medium",
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def get_requests(user_id: int, *, limit: int = 50) -> Dict[str, Any]:
    if not _probe_user_id_column():
        return _reject_mock(
            {
                "requests": [],
                "total": 0,
                "source": "database",
                "agent": AGENT_NAME,
                "checked_at": _utc_now(),
            }
        )

    params = {"user_id": str(user_id), "limit": min(max(limit, 1), 100)}
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id::text AS id,
                       app_name AS "appName",
                       action,
                       accuracy,
                       timestamp
                FROM location.location_requests
                WHERE user_id::text = :user_id
                ORDER BY timestamp DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

    items: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        ts = item.get("timestamp")
        if hasattr(ts, "isoformat"):
            item["timestamp"] = ts.isoformat()
        items.append(item)

    return _reject_mock(
        {
            "requests": items,
            "total": len(items),
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def generate_bubble(
    user_id: int,
    *,
    latitude: float,
    longitude: float,
    person_id: str = "self",
    radius: Optional[int] = None,
) -> Dict[str, Any]:
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("invalid_coordinates")

    uid = str(user_id)
    agent = _get_agent_optional()
    source = "rule_engine"
    bubble: Dict[str, Any]

    if agent is not None:
        try:
            bubble = agent.get_bubble_location(
                uid,
                person_id,
                latitude,
                longitude,
                radius=radius,
            )
            source = "real_agent"
        except Exception as exc:
            logger.warning("agent bubble generate failed: %s", exc)
            bubble = _rule_engine_bubble(latitude, longitude, radius or 500)
    else:
        bubble = _rule_engine_bubble(latitude, longitude, radius or 500)

    req_id = _persist_request(
        user_id,
        app_name=f"bubble:{person_id}",
        action="modified",
        accuracy="medium" if (radius or 500) <= 500 else "low",
    )

    payload = {
        **bubble,
        "request_id": req_id,
        "person_id": person_id,
        "source": source,
        "agent": AGENT_NAME,
        "checked_at": _utc_now(),
    }
    uid = str(user_id)
    _fallback_history.setdefault(uid, []).append(dict(payload))
    if len(_fallback_history[uid]) > 100:
        _fallback_history[uid] = _fallback_history[uid][-100:]
    return _reject_mock(payload)


def get_settings(user_id: int, person_id: Optional[str] = None) -> Dict[str, Any]:
    agent = _get_agent_optional()
    uid = str(user_id)
    if agent is None:
        stored = _fallback_settings.get(uid, {})
        if person_id:
            data = stored.get(person_id, {"person_id": person_id, "default_radius_m": 500, "enabled": True})
            return _reject_mock(
                {
                    "person_id": person_id,
                    "settings": data,
                    "source": "rule_engine",
                    "agent": AGENT_NAME,
                    "checked_at": _utc_now(),
                }
            )
        return _reject_mock(
            {
                "settings": stored,
                "source": "rule_engine",
                "agent": AGENT_NAME,
                "checked_at": _utc_now(),
            }
        )

    if person_id:
        settings = agent.get_person_settings(uid, person_id)
        data = settings.to_dict() if hasattr(settings, "to_dict") else dict(settings)
        return _reject_mock(
            {
                "person_id": person_id,
                "settings": data,
                "source": "real_agent",
                "agent": AGENT_NAME,
                "checked_at": _utc_now(),
            }
        )

    return _reject_mock(
        {
            "settings": agent.get_all_person_settings(uid),
            "source": "real_agent",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def set_settings(
    user_id: int,
    *,
    person_id: str,
    default_radius_m: int = 500,
    enabled: bool = True,
) -> Dict[str, Any]:
    agent = _get_agent_optional()
    uid = str(user_id)
    if agent is None:
        data = {
            "person_id": person_id,
            "default_radius_m": default_radius_m,
            "enabled": enabled,
        }
        _fallback_settings.setdefault(uid, {})[person_id] = data
        return _reject_mock(
            {
                "person_id": person_id,
                "settings": data,
                "source": "rule_engine",
                "agent": AGENT_NAME,
                "checked_at": _utc_now(),
            }
        )

    from security.ai_agents.location_bubble_agent import BubbleRadius

    radius_enum = BubbleRadius.MEDIUM
    if default_radius_m <= 100:
        radius_enum = BubbleRadius.SMALL
    elif default_radius_m >= 1000:
        radius_enum = BubbleRadius.LARGE
    else:
        radius_enum = BubbleRadius.MEDIUM

    result = agent.set_person_settings(
        str(user_id),
        person_id,
        radius_enum,
        enabled=enabled,
    )
    return _reject_mock(
        {
            "person_id": person_id,
            "settings": result,
            "source": "real_agent",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def get_history(user_id: int, *, limit: int = 20) -> Dict[str, Any]:
    agent = _get_agent_optional()
    if agent is None:
        history = _fallback_history.get(str(user_id), [])[-limit:]
        return _reject_mock(
            {
                "history": history,
                "total": len(history),
                "source": "rule_engine",
                "agent": AGENT_NAME,
                "checked_at": _utc_now(),
            }
        )

    history = agent.get_generation_history(str(user_id), limit=limit)
    return _reject_mock(
        {
            "history": history,
            "total": len(history),
            "source": "real_agent",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def allow_request(user_id: int, request_id: str) -> Dict[str, Any]:
    if not _probe_user_id_column():
        raise ValueError("user_scope_unavailable")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE location.location_requests
                SET action = 'allowed', timestamp = CURRENT_TIMESTAMP
                WHERE id::text = :request_id AND user_id::text = :user_id
                """
            ),
            {"request_id": request_id, "user_id": str(user_id)},
        )
        if int(getattr(result, "rowcount", 0) or 0) == 0:
            raise ValueError("request_not_found")
    return _reject_mock(
        {
            "success": True,
            "request_id": request_id,
            "action": "allowed",
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def block_request(user_id: int, request_id: str) -> Dict[str, Any]:
    if not _probe_user_id_column():
        raise ValueError("user_scope_unavailable")
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE location.location_requests
                SET action = 'blocked', timestamp = CURRENT_TIMESTAMP
                WHERE id::text = :request_id AND user_id::text = :user_id
                """
            ),
            {"request_id": request_id, "user_id": str(user_id)},
        )
        if int(getattr(result, "rowcount", 0) or 0) == 0:
            raise ValueError("request_not_found")
    return _reject_mock(
        {
            "success": True,
            "request_id": request_id,
            "action": "blocked",
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def update_accuracy(user_id: int, accuracy: str) -> Dict[str, Any]:
    if accuracy not in ("high", "medium", "low"):
        raise ValueError("invalid_accuracy")
    req_id = _persist_request(
        user_id,
        app_name="accuracy_update",
        action="modified",
        accuracy=accuracy,
    )
    return _reject_mock(
        {
            "success": True,
            "request_id": req_id,
            "accuracy": accuracy,
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )
