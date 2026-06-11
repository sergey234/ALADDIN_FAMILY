"""Identity theft protection — RU agent + user-scoped DB (no mock)."""
from __future__ import annotations

import hashlib
import json
import logging
import re
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
AGENT_NAME = "russian_identity_theft_protection_agent"

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
    return payload


def _risk_to_verdict(risk_score: float) -> str:
    if risk_score >= 0.65:
        return "likely_fake"
    if risk_score >= 0.35:
        return "uncertain"
    return "likely_real"


def _build_verdict(
    *,
    risk_score: float,
    reasons: List[str],
    source: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "verdict": _risk_to_verdict(risk_score),
        "confidence": round(min(max(float(risk_score), 0.0), 1.0), 3),
        "reasons": reasons,
        "source": source,
        "agent": AGENT_NAME,
        "checked_at": _utc_now(),
        "risk_score": risk_score,
    }
    if extra:
        payload.update(extra)
    return _reject_mock(payload)


def _get_agent():
    global _agent_singleton
    if _agent_singleton is not None:
        return _agent_singleton
    from security.ai_agents.russian_identity_theft_protection_agent import (
        RussianIdentityTheftProtectionAgent,
    )

    _agent_singleton = RussianIdentityTheftProtectionAgent({})
    return _agent_singleton


def _get_agent_optional():
    try:
        return _get_agent()
    except Exception as exc:
        logger.warning("identity agent lazy load failed: %s", exc)
        return None


def _ensure_consent(agent: Any, user_id: str) -> None:
    agent.give_consent(
        user_id,
        {"snils": True, "passport": True, "credit": True},
        expires_days=365,
    )


def _normalize_snils(snils: str) -> str:
    return re.sub(r"\D", "", snils)


def _hash_snils(snils: str) -> str:
    return hashlib.sha256(_normalize_snils(snils).encode("utf-8")).hexdigest()


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


def _persist_attempt(
    user_id: int,
    *,
    data_type: str,
    action: str,
    severity: str,
    details: Dict[str, Any],
) -> str:
    attempt_id = str(uuid.uuid4())
    details = {**details, "user_id": str(user_id)}
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO identity.identity_attempts
                    (id, data_type, action, severity, timestamp, details)
                VALUES
                    (CAST(:id AS uuid), :data_type, :action, :severity, CURRENT_TIMESTAMP,
                     CAST(:details AS jsonb))
                """
            ),
            {
                "id": attempt_id,
                "data_type": data_type,
                "action": action,
                "severity": severity,
                "details": json.dumps(details, ensure_ascii=False),
            },
        )
    return attempt_id


def get_stats(user_id: int) -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "get_identity_theft_protection_agent_stats",
        {"user_id": user_id},
    )
    if sfm_result and "totalAttempts" in sfm_result:
        sfm_result.setdefault("source", "real_agent")
        sfm_result.setdefault("agent", AGENT_NAME)
        return _reject_mock(sfm_result)

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                  COUNT(*)::int AS total_attempts,
                  COALESCE(SUM(CASE WHEN action = 'blocked' THEN 1 ELSE 0 END), 0)::int AS blocked_attempts,
                  COALESCE(SUM(CASE WHEN action = 'suspicious' THEN 1 ELSE 0 END), 0)::int AS suspicious_activities,
                  COALESCE(SUM(CASE WHEN data_type = 'passport' THEN 1 ELSE 0 END), 0)::int AS passport_count,
                  COALESCE(SUM(CASE WHEN data_type = 'snils' THEN 1 ELSE 0 END), 0)::int AS snils_count,
                  COALESCE(SUM(CASE WHEN data_type = 'bank' THEN 1 ELSE 0 END), 0)::int AS bank_count,
                  COALESCE(SUM(CASE WHEN data_type = 'other' THEN 1 ELSE 0 END), 0)::int AS other_count
                FROM identity.identity_attempts
                WHERE details->>'user_id' = :user_id
                """
            ),
            {"user_id": str(user_id)},
        ).mappings().first()

    data = dict(row or {})
    return _reject_mock(
        {
            "totalAttempts": data.get("total_attempts") or 0,
            "blockedAttempts": data.get("blocked_attempts") or 0,
            "suspiciousActivities": data.get("suspicious_activities") or 0,
            "byDataType": {
                "passport": data.get("passport_count") or 0,
                "snils": data.get("snils_count") or 0,
                "bank": data.get("bank_count") or 0,
                "other": data.get("other_count") or 0,
            },
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def get_attempts(user_id: int, *, limit: int = 20) -> Dict[str, Any]:
    sfm_result = _sfm_execute(
        "get_identity_theft_protection_agent_attempts",
        {"user_id": user_id, "limit": limit},
    )
    if sfm_result and isinstance(sfm_result.get("attempts"), list):
        sfm_result.setdefault("source", "real_agent")
        return _reject_mock(sfm_result)

    params = {"user_id": str(user_id), "limit": min(max(limit, 1), 100)}
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id::text AS id,
                       data_type AS "dataType",
                       action,
                       severity,
                       timestamp,
                       COALESCE(details, '{}'::jsonb) AS details
                FROM identity.identity_attempts
                WHERE details->>'user_id' = :user_id
                ORDER BY timestamp DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()

    attempts = []
    for row in rows:
        item = dict(row)
        ts = item.get("timestamp")
        if hasattr(ts, "isoformat"):
            item["timestamp"] = ts.isoformat()
        item["requestSource"] = (item.get("details") or {}).get("request_source", "api")
        attempts.append(item)

    return _reject_mock(
        {
            "attempts": attempts,
            "total": len(attempts),
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def detect_theft(
    user_id: int,
    *,
    snils: Optional[str] = None,
    snils_hash: Optional[str] = None,
) -> Dict[str, Any]:
    uid = str(user_id)
    agent = _get_agent_optional()

    if snils and not snils_hash:
        digits = _normalize_snils(snils)
        if len(digits) != 11:
            raise ValueError("invalid_snils")
        snils_hash = _hash_snils(snils)

    if agent is not None:
        _ensure_consent(agent, uid)
        if snils and not snils_hash:
            if not agent._validate_snils(snils):
                raise ValueError("invalid_snils")
            snils_hash = _hash_snils(snils)
            monitor = agent.monitor_snils(snils, uid)
            if not monitor.get("success"):
                raise ValueError(monitor.get("error") or "monitor_failed")
            agent.active_monitoring.setdefault(uid, {})["snils_risk_score"] = monitor.get(
                "risk_score", 0.0
            )

        if snils_hash:
            agent.active_monitoring.setdefault(uid, {})["snils_hash"] = snils_hash

        result = agent.detect_identity_theft(uid)
        if not result.get("success"):
            raise ValueError(result.get("error") or "detect_failed")

        risk_score = float(result.get("risk_score") or 0.0)
        indicators = result.get("indicators") or {}
        reasons = [k for k, v in indicators.items() if v]
        if result.get("alerts"):
            reasons.append("alerts_generated")
        source = "real_agent"
        alerts = result.get("alerts") or []
        severity = str(result.get("severity") or "low")
    else:
        if not snils_hash:
            raise ValueError("snils_or_hash_required")
        risk_score = 0.25
        indicators = {"agent_unavailable": True}
        reasons = ["agent_unavailable", "hash_only_check"]
        source = "rule_engine"
        alerts = []
        severity = "low"

    attempt_id = _persist_attempt(
        user_id,
        data_type="snils",
        action="suspicious" if risk_score >= 0.5 else "allowed",
        severity=severity,
        details={
            "request_source": "detect",
            "snils_hash": snils_hash,
            "indicators": indicators,
            "alerts_count": len(alerts),
        },
    )

    return _build_verdict(
        risk_score=risk_score,
        reasons=reasons,
        source=source,
        extra={
            "attempt_id": attempt_id,
            "indicators": indicators,
            "alerts": alerts,
        },
    )


def monitor_credit(user_id: int) -> Dict[str, Any]:
    uid = str(user_id)
    agent = _get_agent_optional()
    if agent is None:
        return _build_verdict(
            risk_score=0.35,
            reasons=["agent_unavailable", "credit_monitor_deferred"],
            source="rule_engine",
            extra={"nbki_available": False, "okb_available": False},
        )

    _ensure_consent(agent, uid)
    result = agent.monitor_credit_report(uid)
    if not result.get("success"):
        raise ValueError(result.get("error") or "credit_monitor_failed")

    risk_score = float(result.get("risk_score") or 0.0)
    changes = result.get("suspicious_changes") or []
    reasons = [f"credit_change:{c.get('change_type', 'unknown')}" for c in changes if isinstance(c, dict)]
    if not reasons:
        reasons = ["credit_checked"]

    return _build_verdict(
        risk_score=risk_score,
        reasons=reasons,
        source="real_agent",
        extra={
            "suspicious_changes_count": result.get("suspicious_changes_count", 0),
            "nbki_available": result.get("nbki_available", False),
            "okb_available": result.get("okb_available", False),
        },
    )


def check_fraud(
    user_id: int,
    *,
    snils_hash: Optional[str] = None,
    passport_series_hash: Optional[str] = None,
    passport_number_hash: Optional[str] = None,
) -> Dict[str, Any]:
    if not any((snils_hash, passport_series_hash, passport_number_hash)):
        raise ValueError("hash_required")

    agent = _get_agent_optional()
    matches = 0
    source = "rule_engine"

    if agent is not None:
        _ensure_consent(agent, str(user_id))
        source = "real_agent"
        if snils_hash:
            matches += len(agent.fraud_index_snils.get(snils_hash, []))
        if passport_series_hash and passport_number_hash:
            passport_key = hashlib.sha256(
                f"{passport_series_hash}:{passport_number_hash}".encode("utf-8")
            ).hexdigest()
            matches += len(agent.fraud_index_passport.get(passport_key, []))
    else:
        reasons_fallback = ["agent_unavailable", "fraud_index_unavailable"]
        return _build_verdict(
            risk_score=0.35,
            reasons=reasons_fallback,
            source=source,
            extra={"matches": 0},
        )

    risk_score = 0.85 if matches > 0 else 0.15
    reasons = ["fraud_database_match"] if matches > 0 else ["no_fraud_match"]

    if matches > 0:
        _persist_attempt(
            user_id,
            data_type="snils" if snils_hash else "passport",
            action="blocked",
            severity="high",
            details={"request_source": "check_fraud", "matches": matches},
        )

    return _build_verdict(
        risk_score=risk_score,
        reasons=reasons,
        source="real_agent",
        extra={"matches": matches},
    )


def allow_attempt(user_id: int, attempt_id: str) -> Dict[str, Any]:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE identity.identity_attempts
                SET action = 'allowed', timestamp = CURRENT_TIMESTAMP
                WHERE id::text = :attempt_id AND details->>'user_id' = :user_id
                """
            ),
            {"attempt_id": attempt_id, "user_id": str(user_id)},
        )
        if int(getattr(result, "rowcount", 0) or 0) == 0:
            raise ValueError("attempt_not_found")
    return _reject_mock(
        {
            "success": True,
            "attempt_id": attempt_id,
            "action": "allowed",
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )


def block_attempt(user_id: int, attempt_id: str) -> Dict[str, Any]:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE identity.identity_attempts
                SET action = 'blocked', timestamp = CURRENT_TIMESTAMP
                WHERE id::text = :attempt_id AND details->>'user_id' = :user_id
                """
            ),
            {"attempt_id": attempt_id, "user_id": str(user_id)},
        )
        if int(getattr(result, "rowcount", 0) or 0) == 0:
            raise ValueError("attempt_not_found")
    return _reject_mock(
        {
            "success": True,
            "attempt_id": attempt_id,
            "action": "blocked",
            "source": "database",
            "agent": AGENT_NAME,
            "checked_at": _utc_now(),
        }
    )
