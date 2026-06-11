"""Parental monitoring detail/events — explicit FastAPI (B1-10), no mock envelope."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from security.api.routers.parental_control_router import (
    MonitoringIngestRequest,
    ParentalMonitoringDetailResponse,
    _build_parental_monitoring_detail,
    _resolve_target_user_id,
)

logger = logging.getLogger(__name__)

FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback", "mock-real-protection"})


def _reject_mock_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = json.dumps(payload, ensure_ascii=False)
    for marker in FORBIDDEN_SOURCES:
        if marker in raw:
            raise ValueError(f"mock_source_rejected:{marker}")
    if "mock-real-protection" in raw:
        raise ValueError("mock_source_rejected")
    return payload


def _ensure_parental_monitoring_events_table(db: Session) -> None:
    try:
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS parental_monitoring_events (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    kind VARCHAR(64) NOT NULL,
                    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        db.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_parental_monitoring_events_user_created "
                "ON parental_monitoring_events (user_id, created_at DESC)"
            )
        )
        db.execute(
            text(
                """
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'parental_monitoring_events'
                          AND column_name = 'user_id'
                          AND data_type = 'integer'
                    ) THEN
                        ALTER TABLE parental_monitoring_events
                            ALTER COLUMN user_id TYPE BIGINT;
                    END IF;
                END $$;
                """
            )
        )
        db.commit()
    except Exception as exc:
        logger.info("ensure_parental_monitoring_events_table: %s", exc)
        db.rollback()


def get_monitoring_detail(
    db: Session,
    *,
    child_id: Optional[str],
    current_user: dict,
) -> ParentalMonitoringDetailResponse:
    target = _resolve_target_user_id(child_id, current_user, db)
    if target is None:
        response = ParentalMonitoringDetailResponse()
    else:
        response = _build_parental_monitoring_detail(db, target)
    _reject_mock_payload(response.model_dump())
    return response


def _numeric_user_id(current_user: dict) -> int:
    raw_uid = current_user.get("id")
    if isinstance(raw_uid, int):
        return raw_uid
    if isinstance(raw_uid, str) and raw_uid.isdigit():
        return int(raw_uid)
    raise HTTPException(status_code=401, detail="Numeric user id required for monitoring ingest")


async def ingest_monitoring_events(
    db: Session,
    *,
    current_user: dict,
    payload: MonitoringIngestRequest,
) -> Dict[str, Any]:
    uid = _numeric_user_id(current_user)
    if not payload.events:
        return _reject_mock_payload({"success": True, "inserted": 0, "source": "database"})

    _ensure_parental_monitoring_events_table(db)
    try:
        for ev in payload.events:
            kind = (ev.kind or "event")[:64]
            pjson = json.dumps(ev.payload or {}, ensure_ascii=False)
            db.execute(
                text(
                    """
                    INSERT INTO parental_monitoring_events (user_id, kind, payload)
                    VALUES (:uid, :kind, CAST(:payload AS jsonb))
                    """
                ),
                {"uid": uid, "kind": kind, "payload": pjson},
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("monitoring ingest failed: %s", exc)
        raise HTTPException(status_code=500, detail="Monitoring ingest failed") from exc

    return _reject_mock_payload(
        {"success": True, "inserted": len(payload.events), "source": "database"}
    )
