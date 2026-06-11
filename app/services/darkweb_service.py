"""Dark Web monitoring — agent + user-scoped DB (no SFM mock)."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import urllib.error
import urllib.request
from sqlalchemy import text

from app.database.database import engine

logger = logging.getLogger(__name__)

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"
FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback", "mock-real-protection"})
SCAN_AUDIT_SOURCES = frozenset({"scan_start", "scan_fast", "scan_secure"})
AGENT_NAME = "dark_web_monitoring_agent"

_user_id_column: Optional[bool] = None


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
    if payload.get("status") == "success" and "totalLeaks" not in payload and "leaks" not in payload:
        raise ValueError("mock_success_rejected")
    return payload


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
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            return None
    except Exception:
        return None

    if not body.get("success"):
        return None
    result = body.get("result", body)
    return result if isinstance(result, dict) else None


def _has_user_id_column(conn) -> bool:
    global _user_id_column
    if _user_id_column is not None:
        return _user_id_column
    row = conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'darkweb'
              AND table_name = 'darkweb_leaks'
              AND column_name = 'user_id'
            LIMIT 1
            """
        )
    ).first()
    _user_id_column = row is not None
    return _user_id_column


def _breach_predicate(conn, user_id: int) -> Tuple[str, Dict[str, Any]]:
    parts = ["source NOT IN ('scan_start', 'scan_fast', 'scan_secure')"]
    params: Dict[str, Any] = {}
    if _has_user_id_column(conn):
        params["user_id"] = str(user_id)
        parts.append("user_id::text = :user_id")
    else:
        parts.append("1 = 0")
    return " AND ".join(parts), params


def get_stats(user_id: int) -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "get_dark_web_monitoring_agent_stats",
        {"user_id": user_id},
    )
    if sfm_result and "totalLeaks" in sfm_result:
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        sfm_result.setdefault("checked_at", _utc_now())
        return _reject_mock(sfm_result)

    with engine.connect() as conn:
        predicate, params = _breach_predicate(conn, user_id)
        row = conn.execute(
            text(
                f"""
                SELECT
                  COUNT(*)::int AS total_leaks,
                  COALESCE(SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END), 0)::int AS new_leaks,
                  COALESCE(SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END), 0)::int AS resolved_leaks,
                  COALESCE(SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END), 0)::int AS critical_leaks,
                  MAX(leak_date) AS last_scan_date
                FROM darkweb.darkweb_leaks
                WHERE {predicate}
                """
            ),
            params,
        ).mappings().first()

    data = dict(row or {})
    last = data.get("last_scan_date")
    return _reject_mock(
        {
            "totalLeaks": data.get("total_leaks") or 0,
            "newLeaks": data.get("new_leaks") or 0,
            "resolvedLeaks": data.get("resolved_leaks") or 0,
            "criticalLeaks": data.get("critical_leaks") or 0,
            "lastScanDate": last.isoformat() if hasattr(last, "isoformat") else last,
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def get_leaks(
    user_id: int,
    *,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "get_dark_web_monitoring_agent_leaks",
        {"user_id": user_id, "status": status, "limit": limit},
    )
    if sfm_result and isinstance(sfm_result.get("leaks"), list):
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        return _reject_mock(sfm_result)

    with engine.connect() as conn:
        predicate, params = _breach_predicate(conn, user_id)
        cond = f"WHERE {predicate}"
        if status:
            cond += " AND status = :status"
            params["status"] = status
        if severity:
            cond += " AND severity = :severity"
            params["severity"] = severity
        params["limit"] = min(max(limit, 1), 100)
        rows = conn.execute(
            text(
                f"""
                SELECT id::text AS id,
                       data_type AS "dataType",
                       source,
                       severity,
                       status,
                       leak_date AS "leakDate",
                       created_at AS "discoveryDate"
                FROM darkweb.darkweb_leaks
                {cond}
                ORDER BY leak_date DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

    leaks: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["value"] = "***"
        item["recommendations"] = []
        leaks.append(item)

    return _reject_mock(
        {
            "leaks": leaks,
            "total": len(leaks),
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def get_scans(user_id: int, *, limit: int = 20) -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "get_dark_web_monitoring_agent_scans",
        {"user_id": user_id, "limit": limit},
    )
    if sfm_result and isinstance(sfm_result.get("scans"), list):
        sfm_result.setdefault("source", "real_agent")
        return _reject_mock(sfm_result)

    params = {"user_id": str(user_id), "limit": min(max(limit, 1), 50)}
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id::text AS id,
                       created_at AS "scanDate",
                       method,
                       status
                FROM darkweb.scan_events
                WHERE user_id::text = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

    scans: List[Dict[str, Any]] = []
    for row in rows:
        scan_dt = row.get("scanDate")
        scans.append(
            {
                "id": row.get("id"),
                "scanDate": scan_dt.isoformat() if hasattr(scan_dt, "isoformat") else scan_dt,
                "databasesScanned": 0,
                "newLeaksFound": 0,
                "status": row.get("status") or "completed",
                "method": row.get("method"),
            }
        )

    return _reject_mock(
        {
            "scans": scans,
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def _insert_scan_event(user_id: int, method: str) -> str:
    scan_id = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO darkweb.scan_events (id, user_id, method, status, created_at)
                VALUES (CAST(:scan_id AS uuid), :user_id, :method, 'completed', CURRENT_TIMESTAMP)
                """
            ),
            {"scan_id": scan_id, "user_id": user_id, "method": method},
        )
    return scan_id


def _persist_breach(
    user_id: int,
    *,
    data_type: str,
    source: str,
    severity: str = "medium",
    leak_date: Optional[datetime] = None,
    leak_id: Optional[str] = None,
) -> str:
    leak_id = leak_id or str(uuid.uuid4())
    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                INSERT INTO darkweb.darkweb_leaks
                    (id, user_id, data_type, value_or_hash, leak_date, source, severity, status, created_at)
                VALUES
                    (CAST(:leak_id AS uuid), :user_id, :data_type, decode(md5(random()::text), 'hex'),
                     :leak_date, :source, :severity, 'new', CURRENT_TIMESTAMP)
                RETURNING id::text
                """
            ),
            {
                "leak_id": leak_id,
                "user_id": user_id,
                "data_type": data_type,
                "source": source[:255],
                "severity": severity,
                "leak_date": leak_date or datetime.now(timezone.utc),
            },
        ).scalar()
    return str(row)


def start_scan(user_id: int) -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "start_dark_web_monitoring_agent_scan",
        {"user_id": user_id},
    )
    if sfm_result and sfm_result.get("scan_id"):
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        return _reject_mock(sfm_result)

    scan_id = _insert_scan_event(user_id, "scan_start")
    return _reject_mock(
        {
            "scan_id": scan_id,
            "status": "started",
            "success": True,
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def check_identifiers(
    user_id: int,
    *,
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    from security.api.dark_web_scan_service import collect_fast_scan_results

    if not (email and email.strip()) and not (phone and str(phone).strip()):
        raise ValueError("email_or_phone_required")

    raw = collect_fast_scan_results(
        email=email.strip().lower() if email else None,
        phone=phone,
        passport=None,
        snils=None,
    )
    found_count = 0
    results: List[Dict[str, Any]] = []
    for item in raw:
        row = dict(item)
        if row.get("found"):
            found_count += 1
            leak_dt_raw = row.get("leakDate")
            leak_dt = datetime.now(timezone.utc)
            if isinstance(leak_dt_raw, str):
                try:
                    leak_dt = datetime.fromisoformat(leak_dt_raw.replace("Z", "+00:00"))
                except ValueError:
                    pass
            leak_id = _persist_breach(
                user_id,
                data_type=str(row.get("dataType") or "email"),
                source=str(row.get("source") or "haveibeenpwned"),
                severity=str(row.get("severity") or "medium"),
                leak_date=leak_dt,
                leak_id=row.get("id"),
            )
            row["id"] = leak_id
        results.append(row)

    agent_source = "real_agent" if any(r.get("found") for r in results) else "database"
    return _reject_mock(
        {
            "results": results,
            "found_count": found_count,
            "source": agent_source,
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def resolve_leak(user_id: int, leak_id: str, *, status: str = "resolved") -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "resolve_dark_web_monitoring_agent_leak",
        {"user_id": user_id, "leak_id": leak_id, "status": status},
    )
    if sfm_result:
        sfm_result.setdefault("source", "real_agent")
        return _reject_mock(sfm_result)

    with engine.begin() as conn:
        if _has_user_id_column(conn):
            result = conn.execute(
                text(
                    """
                    UPDATE darkweb.darkweb_leaks
                    SET status = :status
                    WHERE id::text = :leak_id AND user_id::text = :user_id
                    """
                ),
                {"status": status, "leak_id": leak_id, "user_id": str(user_id)},
            )
            if int(getattr(result, "rowcount", 0) or 0) == 0:
                raise ValueError("leak_not_found")
        else:
            raise ValueError("user_scope_unavailable")

    return _reject_mock(
        {
            "success": True,
            "leak_id": leak_id,
            "status": status,
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )
