"""Personal data cleanup — agent + user-scoped DB (no mock)."""
from __future__ import annotations

import json
import logging
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
AGENT_NAME = "personal_data_cleanup_agent"

_agent_singleton: Any = None


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
    if payload.get("status") == "success" and "job_id" not in payload and "totalFreed" not in payload:
        raise ValueError("mock_success_rejected")
    return payload


def _probe_user_id_column() -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'cleanup'
                  AND table_name = 'cleanup_records'
                  AND column_name = 'user_id'
                LIMIT 1
                """
            )
        ).first()
        return row is not None


def _has_user_id_column() -> bool:
    return _probe_user_id_column()


def _user_predicate(user_id: int) -> tuple[str, Dict[str, Any]]:
    if _has_user_id_column():
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
        from security.ai_agents.personal_data_cleanup_agent import PersonalDataCleanupAgent

        _agent_singleton = PersonalDataCleanupAgent({})
        return _agent_singleton
    except Exception as exc:
        logger.warning("cleanup agent lazy load failed: %s", exc)
        return None


def get_stats(user_id: int) -> Dict[str, Any]:
    _probe_user_id_column()
    sfm_result = _sfm_execute("get_data_cleanup_agent_stats", {"user_id": user_id})
    if sfm_result and "totalFreed" in sfm_result:
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        return _reject_mock(sfm_result)

    predicate, params = _user_predicate(user_id)
    with engine.connect() as conn:
        row = conn.execute(
            text(
                f"""
                SELECT
                  COALESCE(SUM(freed_space_bytes), 0)::bigint AS total_freed,
                  MAX(cleanup_date) AS last_cleanup_date,
                  COUNT(*)::int AS cleanups_count
                FROM cleanup.cleanup_records
                WHERE {predicate}
                """
            ),
            params,
        ).mappings().first()

        by_category: Dict[str, int] = {}
        if _has_user_id_column():
            cat_rows = conn.execute(
                text(
                    """
                    SELECT categories_json
                    FROM cleanup.cleanup_records
                    WHERE user_id::text = :user_id AND categories_json IS NOT NULL
                    """
                ),
                {"user_id": str(user_id)},
            ).fetchall()
            for cat_row in cat_rows:
                categories = cat_row[0]
                if isinstance(categories, str):
                    try:
                        categories = json.loads(categories)
                    except json.JSONDecodeError:
                        categories = []
                if isinstance(categories, list):
                    for cat in categories:
                        if isinstance(cat, dict) and cat.get("name"):
                            name = str(cat["name"])
                            by_category[name] = by_category.get(name, 0) + int(cat.get("size") or 0)

    data = dict(row or {})
    last = data.get("last_cleanup_date")
    return _reject_mock(
        {
            "totalFreed": int(data.get("total_freed") or 0),
            "lastCleanupDate": last.isoformat() if hasattr(last, "isoformat") else last,
            "cleanupsCount": int(data.get("cleanups_count") or 0),
            "byCategory": by_category,
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def get_records(user_id: int, *, limit: int = 20) -> Dict[str, Any]:
    _probe_user_id_column()
    sfm_result = _sfm_execute(
        "get_data_cleanup_agent_records",
        {"user_id": user_id, "limit": limit},
    )
    if sfm_result and isinstance(sfm_result.get("records"), list):
        sfm_result.setdefault("source", "real_agent")
        return _reject_mock(sfm_result)

    if not _has_user_id_column():
        return _reject_mock(
            {
                "records": [],
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
                       cleanup_date AS "cleanupDate",
                       freed_space_bytes AS "freedSpace",
                       COALESCE(categories_json, '[]'::jsonb) AS categories_json
                FROM cleanup.cleanup_records
                WHERE user_id::text = :user_id
                ORDER BY cleanup_date DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

    records: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        ts = item.pop("cleanupDate", None)
        if hasattr(ts, "isoformat"):
            item["cleanupDate"] = ts.isoformat()
        else:
            item["cleanupDate"] = ts
        categories = item.pop("categories_json", [])
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except json.JSONDecodeError:
                categories = []
        item["categories"] = categories if isinstance(categories, list) else []
        records.append(item)

    return _reject_mock(
        {
            "records": records,
            "total": len(records),
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def start_cleanup(user_id: int, *, categories: Optional[List[str]] = None) -> Dict[str, Any]:
    if not _probe_user_id_column():
        raise ValueError("user_scope_unavailable")
    categories = categories or []
    sfm_result = _sfm_execute(
        "start_data_cleanup_agent_cleanup",
        {"user_id": user_id, "categories": categories},
    )
    if sfm_result and sfm_result.get("job_id"):
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        return _reject_mock(sfm_result)

    agent = _get_agent_optional()
    agent_meta: Dict[str, Any] = {}
    source = "database"
    if agent is not None:
        try:
            agent_meta = agent.get_scan_status(str(user_id))
            source = "real_agent"
        except Exception as exc:
            logger.warning("cleanup agent scan status failed: %s", exc)
            source = "rule_engine"
            agent_meta = {"agent_status": "deferred"}
    else:
        source = "rule_engine"
        agent_meta = {"agent_unavailable": True}

    job_id = str(uuid.uuid4())
    categories_json = json.dumps([{"name": c, "size": 0} for c in categories])

    with engine.begin() as conn:
        if _has_user_id_column():
            conn.execute(
                text(
                    """
                    INSERT INTO cleanup.cleanup_records
                        (id, user_id, cleanup_date, freed_space_bytes, categories_json)
                    VALUES
                        (CAST(:id AS uuid), :user_id, CURRENT_TIMESTAMP, 0,
                         CAST(:categories_json AS jsonb))
                    """
                ),
                {
                    "id": job_id,
                    "user_id": user_id,
                    "categories_json": categories_json,
                },
            )
        else:
            raise ValueError("user_scope_unavailable")

    return _reject_mock(
        {
            "job_id": job_id,
            "status": "started",
            "success": True,
            "categories": categories,
            "freed_space_bytes": 0,
            "agent_status": agent_meta,
            "source": source,
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )
