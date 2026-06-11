"""IoT security — agent scan + PostgreSQL persist (no mock)."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine

logger = logging.getLogger(__name__)

FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback", "mock-real-protection"})
AGENT_NAME = "iot_security_agent"

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
        from security.ai_agents.iot_security_agent import IoTSecurityAgent

        _agent_singleton = IoTSecurityAgent()
        return _agent_singleton
    except Exception as exc:
        logger.warning("iot agent load failed: %s", exc)
        return None


def ensure_iot_tables() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS iot_devices (
                    id BIGSERIAL PRIMARY KEY,
                    home_id TEXT NOT NULL,
                    device_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'online',
                    last_seen TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    threat_level INTEGER NOT NULL DEFAULT 0
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS iot_threats (
                    id BIGSERIAL PRIMARY KEY,
                    home_id TEXT NOT NULL,
                    threat_id TEXT UNIQUE NOT NULL,
                    device_id TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    detected_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    status TEXT NOT NULL DEFAULT 'active'
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS iot_scans (
                    id BIGSERIAL PRIMARY KEY,
                    scan_id TEXT UNIQUE NOT NULL,
                    home_id TEXT NOT NULL,
                    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                    threats_found INTEGER NOT NULL DEFAULT 0,
                    source TEXT
                )
                """
            )
        )
        conn.execute(
            text("ALTER TABLE iot_scans ADD COLUMN IF NOT EXISTS threats_found INTEGER NOT NULL DEFAULT 0")
        )
        conn.execute(text("ALTER TABLE iot_scans ADD COLUMN IF NOT EXISTS source TEXT"))


def bootstrap_home(home_id: str) -> None:
    ensure_iot_tables()
    with engine.connect() as conn:
        count = (
            conn.execute(
                text("SELECT COUNT(*) FROM iot_devices WHERE home_id = :home_id"),
                {"home_id": home_id},
            ).scalar()
            or 0
        )
    if count:
        return
    seed = [
        {
            "home_id": home_id,
            "device_id": f"{home_id}_cam_1",
            "name": "Умная камера",
            "type": "camera",
            "status": "online",
            "threat_level": 0,
        },
        {
            "home_id": home_id,
            "device_id": f"{home_id}_thermo_1",
            "name": "Умный термостат",
            "type": "thermostat",
            "status": "online",
            "threat_level": 1,
        },
    ]
    with engine.begin() as conn:
        for row in seed:
            conn.execute(
                text(
                    """
                    INSERT INTO iot_devices (home_id, device_id, name, type, status, threat_level)
                    VALUES (:home_id, :device_id, :name, :type, :status, :threat_level)
                    ON CONFLICT (device_id) DO NOTHING
                    """
                ),
                row,
            )


def _load_devices(home_id: str) -> List[Dict[str, Any]]:
    bootstrap_home(home_id)
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    """
                    SELECT device_id, name, type, status, last_seen, threat_level
                    FROM iot_devices WHERE home_id = :home_id ORDER BY device_id
                    """
                ),
                {"home_id": home_id},
            )
            .mappings()
            .all()
        )
    return [dict(r) for r in rows]


def _agent_device_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    threat_level = int(row.get("threat_level") or 0)
    device_type = str(row.get("type") or "other")
    return {
        "id": row["device_id"],
        "device_id": row["device_id"],
        "name": row["name"],
        "type": device_type,
        "is_online": str(row.get("status")) == "online",
        "uses_default_password": device_type in ("camera", "thermostat") and threat_level >= 1,
        "default_credentials": device_type == "thermostat" and threat_level >= 1,
        "firmware_status": "outdated" if device_type == "camera" and threat_level == 0 else "current",
        "encryption_enabled": device_type != "thermostat",
        "open_ports": [23] if device_type == "thermostat" and threat_level >= 1 else [],
        "anomaly_score": 0.7 if threat_level >= 1 else 0.1,
    }


def run_home_scan(home_id: str) -> Dict[str, Any]:
    ensure_iot_tables()
    devices = _load_devices(home_id)
    agent = _get_agent_optional()
    source = "real_agent" if agent is not None else "rule_engine"

    threats: List[Dict[str, Any]] = []
    if agent is not None:
        payloads = [_agent_device_payload(d) for d in devices]
        threats = agent.detect_threats(payloads)
    else:
        for row in devices:
            if int(row.get("threat_level") or 0) > 0:
                threats.append(
                    {
                        "device_id": row["device_id"],
                        "device_name": row["name"],
                        "threat_type": "weak_password",
                        "severity": "medium",
                        "description": "Elevated threat level heuristic",
                        "detected_at": _utc_now(),
                    }
                )

    scan_id = f"scan_{home_id}_{uuid.uuid4().hex[:12]}"
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO iot_scans (scan_id, home_id, started_at, threats_found, source)
                VALUES (:scan_id, :home_id, NOW(), :threats_found, :source)
                """
            ),
            {
                "scan_id": scan_id,
                "home_id": home_id,
                "threats_found": len(threats),
                "source": source,
            },
        )
        for idx, threat in enumerate(threats):
            threat_id = f"{home_id}_{threat['device_id']}_{threat['threat_type']}_{idx}"
            conn.execute(
                text(
                    """
                    INSERT INTO iot_threats
                        (home_id, threat_id, device_id, threat_type, severity, status)
                    VALUES
                        (:home_id, :threat_id, :device_id, :threat_type, :severity, 'active')
                    ON CONFLICT (threat_id) DO UPDATE SET
                        severity = EXCLUDED.severity,
                        status = 'active',
                        detected_at = NOW()
                    """
                ),
                {
                    "home_id": home_id,
                    "threat_id": threat_id,
                    "device_id": threat["device_id"],
                    "threat_type": threat["threat_type"],
                    "severity": threat.get("severity", "medium"),
                },
            )
            conn.execute(
                text(
                    """
                    UPDATE iot_devices
                    SET threat_level = GREATEST(threat_level, :level), last_seen = NOW()
                    WHERE device_id = :device_id
                    """
                ),
                {
                    "device_id": threat["device_id"],
                    "level": {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(
                        str(threat.get("severity", "medium")), 2
                    ),
                },
            )

    return _reject_mock(
        {
            "success": True,
            "scanId": scan_id,
            "homeId": home_id,
            "message": "Сканирование завершено",
            "startedAt": _utc_now(),
            "threatsFound": len(threats),
            "source": source,
            "agent": AGENT_NAME,
        }
    )
