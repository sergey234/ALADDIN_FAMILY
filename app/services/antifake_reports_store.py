"""I-02…I-04, I-06: scam reports moderation queue → fraud DB."""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_call_directory_store import phone_log_hash, upsert_number

HIGH_BLOCK_CONFIDENCE = 95
AUTO_APPROVE_MIN_CONFIDENCE = 72

_CREATE = """
CREATE TABLE IF NOT EXISTS antifake_reports (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id UUID,
    phone_e164 VARCHAR(20) NOT NULL,
    label VARCHAR(128),
    note TEXT,
    report_type VARCHAR(16) NOT NULL DEFAULT 'scam',
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    job_verdict VARCHAR(32),
    job_confidence SMALLINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    moderated_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_antifake_reports_status ON antifake_reports (status, created_at);
CREATE INDEX IF NOT EXISTS idx_antifake_reports_user ON antifake_reports (user_id, created_at DESC);
"""


def _normalize_phone(raw: str) -> Optional[str]:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) < 10 or len(digits) > 15:
        return None
    return digits


def ensure_table() -> None:
    with engine.begin() as conn:
        for stmt in _CREATE.strip().split(";"):
            line = stmt.strip()
            if line:
                conn.execute(text(line))


def _block_for_confidence(confidence: int) -> bool:
    """I-04: label by default; block only at high confidence."""
    return int(confidence) >= HIGH_BLOCK_CONFIDENCE


def promote_report_to_fraud_db(report: Dict[str, Any]) -> bool:
    """I-03 / I-04: approved report → antifake_scam_numbers."""
    phone = str(report["phone_e164"])
    report_type = str(report.get("report_type") or "scam")

    if report_type == "appeal":
        now = datetime.now(timezone.utc)
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE antifake_scam_numbers
                    SET active = FALSE, updated_at = :now
                    WHERE phone_e164 = :phone
                    """
                ),
                {"phone": phone, "now": now},
            )
        return True

    confidence = int(report.get("job_confidence") or 85)
    return upsert_number(
        phone,
        source="user_report",
        label=report.get("label"),
        confidence=confidence,
        block=_block_for_confidence(confidence),
        active=True,
    )


def create_report(
    *,
    user_id: int,
    phone: str,
    job_id: Optional[str],
    label: Optional[str],
    note: Optional[str],
    report_type: str,
    job_verdict: Optional[str],
    job_confidence: Optional[int],
    auto_moderate: bool = True,
) -> Dict[str, Any]:
    ensure_table()
    normalized = _normalize_phone(phone)
    if not normalized:
        raise ValueError("invalid_phone")

    report_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    status = "pending"

    from app.services.antifake_family_store import resolve_primary_family_id

    family_id = resolve_primary_family_id(user_id)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO antifake_reports
                    (id, user_id, job_id, phone_e164, label, note, report_type,
                     status, job_verdict, job_confidence, family_id, created_at, updated_at)
                VALUES
                    (CAST(:id AS UUID), :user_id, CAST(:job_id AS UUID), :phone, :label, :note,
                     :report_type, :status, :job_verdict, :job_confidence, :family_id, :now, :now)
                """
            ),
            {
                "id": report_id,
                "user_id": int(user_id),
                "job_id": job_id,
                "phone": normalized,
                "label": label,
                "note": note,
                "report_type": report_type,
                "status": status,
                "job_verdict": job_verdict,
                "job_confidence": job_confidence,
                "family_id": family_id,
                "now": now,
            },
        )

    row = get_report(report_id)
    if (
        auto_moderate
        and report_type == "scam"
        and job_verdict == "likely_fake"
        and int(job_confidence or 0) >= AUTO_APPROVE_MIN_CONFIDENCE
    ):
        row = moderate_report(report_id, action="approve", moderator="auto")
    return row or {"id": report_id, "status": status}


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    ensure_table()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT id, user_id, job_id, phone_e164, label, note, report_type,
                       status, job_verdict, job_confidence, created_at, updated_at, moderated_at
                FROM antifake_reports WHERE id = CAST(:id AS UUID)
                """
            ),
            {"id": report_id},
        ).mappings().first()
    if not row:
        return None
    return _row_to_dict(row)


def moderate_report(
    report_id: str,
    *,
    action: str,
    moderator: str = "manual",
) -> Optional[Dict[str, Any]]:
    ensure_table()
    row = get_report(report_id)
    if not row or row["status"] != "pending":
        return row

    now = datetime.now(timezone.utc)
    if action == "approve":
        promote_report_to_fraud_db(row)
        new_status = "approved"
    elif action == "reject":
        new_status = "rejected"
    else:
        raise ValueError("invalid_action")

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE antifake_reports
                SET status = :status, updated_at = :now, moderated_at = :now
                WHERE id = CAST(:id AS UUID)
                """
            ),
            {"id": report_id, "status": new_status, "now": now},
        )

    updated = get_report(report_id)
    if updated:
        import logging

        logging.getLogger(__name__).info(
            "antifake_report_moderated id=%s action=%s by=%s phone_hash=%s",
            report_id,
            action,
            moderator,
            phone_log_hash(str(row["phone_e164"])),
        )
    return updated


def list_pending(limit: int = 50) -> List[Dict[str, Any]]:
    ensure_table()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, user_id, job_id, phone_e164, label, note, report_type,
                       status, job_verdict, job_confidence, created_at
                FROM antifake_reports
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
    return [_row_to_dict(r) for r in rows]


def _row_to_dict(row) -> Dict[str, Any]:
    return {
        "id": str(row["id"]),
        "user_id": int(row["user_id"]),
        "job_id": str(row["job_id"]) if row.get("job_id") else None,
        "phone": str(row["phone_e164"]),
        "label": row.get("label"),
        "note": row.get("note"),
        "report_type": row.get("report_type"),
        "status": row.get("status"),
        "job_verdict": row.get("job_verdict"),
        "job_confidence": row.get("job_confidence"),
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
        "updated_at": row.get("updated_at").isoformat() if row.get("updated_at") else None,
        "moderated_at": row.get("moderated_at").isoformat() if row.get("moderated_at") else None,
    }
