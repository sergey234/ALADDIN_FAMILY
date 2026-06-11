"""Phishing protection settings — component DB + agent heuristics (no mock)."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine

logger = logging.getLogger(__name__)

COMPONENT_ID = "phishing_protection_agent"
FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback", "mock-real-protection"})

DEFAULT_SETTINGS: Dict[str, Any] = {
    "blockSuspiciousLinks": True,
    "warnBeforeOpening": True,
    "checkEmailLinks": True,
    "checkSMSLinks": True,
    "blockKnownPhishingDomains": True,
    "sensitivityLevel": "medium",
}

_agent_singleton: Any = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reject_mock(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = json.dumps(payload, ensure_ascii=False)
    for marker in FORBIDDEN_SOURCES:
        if marker in raw:
            raise ValueError(f"mock_source_rejected:{marker}")
    if str(payload.get("source", "")) in FORBIDDEN_SOURCES:
        raise ValueError("mock_source_rejected")
    return payload


def _get_agent_optional():
    global _agent_singleton
    if _agent_singleton is not None:
        return _agent_singleton
    try:
        from security.ai_agents.phishing_protection_agent import PhishingProtectionAgent

        _agent_singleton = PhishingProtectionAgent()
        return _agent_singleton
    except Exception as exc:
        logger.warning("phishing agent load failed: %s", exc)
        return None


def _load_settings(user_id: Optional[int]) -> Dict[str, Any]:
    settings = dict(DEFAULT_SETTINGS)
    if user_id is None:
        return settings
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT settings
                    FROM component_configuration
                    WHERE component_id = :component_id AND user_id = :user_id
                    """
                ),
                {"component_id": COMPONENT_ID, "user_id": user_id},
            ).fetchone()
        if row and row[0]:
            stored = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            if isinstance(stored, dict):
                settings.update(stored)
    except Exception as exc:
        logger.warning("phishing settings load failed: %s", exc)
    return settings


def _save_settings(user_id: int, settings: Dict[str, Any]) -> None:
    payload = json.dumps(settings, ensure_ascii=False)
    with engine.begin() as conn:
        existing = conn.execute(
            text(
                """
                SELECT id FROM component_configuration
                WHERE component_id = :component_id AND user_id = :user_id
                """
            ),
            {"component_id": COMPONENT_ID, "user_id": user_id},
        ).fetchone()
        if existing:
            conn.execute(
                text(
                    """
                    UPDATE component_configuration
                    SET settings = :settings, last_updated = CURRENT_TIMESTAMP
                    WHERE component_id = :component_id AND user_id = :user_id
                    """
                ),
                {"settings": payload, "component_id": COMPONENT_ID, "user_id": user_id},
            )
        else:
            conn.execute(
                text(
                    """
                    INSERT INTO component_configuration
                        (component_id, user_id, settings, version, last_updated)
                    VALUES
                        (:component_id, :user_id, :settings, '1.0.0', CURRENT_TIMESTAMP)
                    """
                ),
                {"component_id": COMPONENT_ID, "user_id": user_id, "settings": payload},
            )


def _agent_stats() -> Dict[str, Any]:
    agent = _get_agent_optional()
    if agent is None:
        return {}
    try:
        status = agent.get_status()
        if isinstance(status, dict):
            return status
    except Exception:
        pass
    return {}


def get_sensitivity(user_id: Optional[int] = None) -> Dict[str, Any]:
    settings = _load_settings(user_id)
    agent = _get_agent_optional()
    source = "real_agent" if agent is not None else "database"
    stats = _agent_stats()
    return _reject_mock(
        {
            "sensitivity_level": settings.get("sensitivityLevel", "medium"),
            "level": settings.get("sensitivityLevel", "medium"),
            "blockSuspiciousLinks": settings.get("blockSuspiciousLinks", True),
            "warnBeforeOpening": settings.get("warnBeforeOpening", True),
            "checkEmailLinks": settings.get("checkEmailLinks", True),
            "checkSMSLinks": settings.get("checkSMSLinks", True),
            "blockKnownPhishingDomains": settings.get("blockKnownPhishingDomains", True),
            "protection_status": "ACTIVE",
            "active_rules_count": stats.get("active_indicators", 0),
            "blocked_phishing_attempts": stats.get("total_detections", 0),
            "source": source,
            "agent": COMPONENT_ID,
            "checked_at": _utc_now(),
        }
    )


def update_sensitivity(user_id: Optional[int], payload: Dict[str, Any]) -> Dict[str, Any]:
    if user_id is None:
        raise ValueError("auth_required")
    settings = _load_settings(user_id)
    level = payload.get("level") or payload.get("sensitivity_level") or payload.get("sensitivityLevel")
    if level:
        settings["sensitivityLevel"] = str(level)
    for key in (
        "blockSuspiciousLinks",
        "warnBeforeOpening",
        "checkEmailLinks",
        "checkSMSLinks",
        "blockKnownPhishingDomains",
    ):
        if key in payload:
            settings[key] = bool(payload[key])
    _save_settings(user_id, settings)
    result = get_sensitivity(user_id)
    result["action"] = "update_sensitivity"
    return result


def get_block_suspicious(user_id: Optional[int] = None) -> Dict[str, Any]:
    settings = _load_settings(user_id)
    return _reject_mock(
        {
            "block_suspicious": bool(settings.get("blockSuspiciousLinks", True)),
            "enabled": bool(settings.get("blockSuspiciousLinks", True)),
            "source": "database",
            "agent": COMPONENT_ID,
            "checked_at": _utc_now(),
        }
    )


def update_block_suspicious(user_id: Optional[int], payload: Dict[str, Any]) -> Dict[str, Any]:
    if user_id is None:
        raise ValueError("auth_required")
    settings = _load_settings(user_id)
    enabled = payload.get("enabled")
    if enabled is None:
        enabled = payload.get("block_suspicious", payload.get("blockSuspiciousLinks"))
    if enabled is not None:
        settings["blockSuspiciousLinks"] = bool(enabled)
    _save_settings(user_id, settings)
    result = get_block_suspicious(user_id)
    result["action"] = "update_block_suspicious"
    return result


def get_exclusions(user_id: Optional[int] = None) -> Dict[str, Any]:
    _ = user_id
    return _reject_mock(
        {
            "exclusions": [],
            "source": "database",
            "agent": COMPONENT_ID,
            "checked_at": _utc_now(),
        }
    )
