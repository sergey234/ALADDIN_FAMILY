"""Fraud numbers for iOS Call Directory sync (C-01…C-03)."""
from __future__ import annotations

import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine

MAX_CALL_DIRECTORY_ENTRIES = 50_000

_CREATE = """
CREATE TABLE IF NOT EXISTS antifake_scam_numbers (
    id BIGSERIAL PRIMARY KEY,
    phone_e164 VARCHAR(20) NOT NULL UNIQUE,
    label VARCHAR(128),
    source VARCHAR(32) NOT NULL DEFAULT 'manual',
    confidence SMALLINT NOT NULL DEFAULT 80,
    block BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_antifake_scam_numbers_active
    ON antifake_scam_numbers (active, updated_at);
"""

_QA_PHONES_FOR_DEVICE_QA = frozenset({"74951234567", "78005553535", "79001234567"})

_RU_V1_CSV = (
    Path(__file__).resolve().parents[2] / "data" / "antifake" / "scam_numbers_ru_v1.csv"
)
MIN_RU_SEED_COUNT = 100


def phone_log_hash(phone: str) -> str:
    """N-02: never log raw E.164 in ops logs."""
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return "empty"
    return hashlib.sha256(digits.encode("utf-8")).hexdigest()[:16]


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
        _bootstrap_ru_v1_if_needed(conn)


def qa_numbers_present() -> bool:
    """C-11: QA test numbers for device QA (D-03)."""
    ensure_table()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT phone_e164 FROM antifake_scam_numbers
                WHERE active = TRUE AND source = 'qa'
                """
            )
        ).scalars().all()
    present = {str(r) for r in rows}
    return _QA_PHONES_FOR_DEVICE_QA.issubset(present)


def _bootstrap_ru_v1_if_needed(conn) -> None:
    """C-08: ensure ≥100 active RU numbers from bundled CSV when DB is sparse."""
    count = conn.execute(
        text("SELECT COUNT(*) FROM antifake_scam_numbers WHERE active = TRUE")
    ).scalar()
    if int(count or 0) >= MIN_RU_SEED_COUNT:
        return
    if not _RU_V1_CSV.is_file():
        return
    with _RU_V1_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        phone = row.get("phone") or row.get("phone_e164") or ""
        normalized = _normalize_phone(phone)
        if not normalized:
            continue
        now = datetime.now(timezone.utc)
        conn.execute(
            text(
                """
                INSERT INTO antifake_scam_numbers
                    (phone_e164, label, source, confidence, block, active, created_at, updated_at)
                VALUES
                    (:phone, :label, :source, :confidence, :block, TRUE, :now, :now)
                ON CONFLICT (phone_e164) DO NOTHING
                """
            ),
            {
                "phone": normalized,
                "label": row.get("label") or None,
                "source": row.get("source") or "ru_v1",
                "confidence": int(row.get("confidence") or 80),
                "block": str(row.get("block", "")).lower() in ("1", "true", "yes"),
                "now": now,
            },
        )


def active_count() -> int:
    ensure_table()
    with engine.connect() as conn:
        total = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM antifake_scam_numbers
                WHERE active = TRUE
                  AND (expires_at IS NULL OR expires_at > NOW())
                """
            )
        ).scalar()
    return int(total or 0)


def get_call_directory_payload(
    since: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return identified/blocked lists for GET /call-directory."""
    ensure_table()
    params: Dict[str, Any] = {"limit": MAX_CALL_DIRECTORY_ENTRIES}
    since_clause = ""
    if since is not None:
        since_clause = "AND updated_at > :since"
        params["since"] = since

    query = f"""
        SELECT phone_e164, label, block, updated_at
        FROM antifake_scam_numbers
        WHERE active = TRUE
          AND (expires_at IS NULL OR expires_at > NOW())
          {since_clause}
        ORDER BY phone_e164
        LIMIT :limit
    """
    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()
        total = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM antifake_scam_numbers
                WHERE active = TRUE
                  AND (expires_at IS NULL OR expires_at > NOW())
                """
            )
        ).scalar()
        latest = conn.execute(
            text(
                """
                SELECT MAX(updated_at) FROM antifake_scam_numbers
                WHERE active = TRUE
                """
            )
        ).scalar()

    identified: List[Dict[str, Optional[str]]] = []
    blocked: List[str] = []
    for row in rows:
        phone = str(row["phone_e164"])
        if row["block"]:
            blocked.append(phone)
        else:
            identified.append({"phone": phone, "label": row["label"]})

    updated_at = latest or datetime.now(timezone.utc)
    if isinstance(updated_at, datetime) and updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    total_int = int(total or 0)
    returned = len(rows)
    truncated = total_int > returned or total_int > MAX_CALL_DIRECTORY_ENTRIES

    return {
        "identified": identified,
        "blocked": blocked,
        "total_count": total_int,
        "updated_at": updated_at.isoformat(),
        "truncated": truncated,
        "max_entries": MAX_CALL_DIRECTORY_ENTRIES,
    }


def upsert_number(
    phone: str,
    *,
    source: str = "manual",
    label: Optional[str] = None,
    confidence: int = 80,
    block: bool = False,
    active: bool = True,
) -> bool:
    normalized = _normalize_phone(phone)
    if not normalized:
        return False
    ensure_table()
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO antifake_scam_numbers
                    (phone_e164, label, source, confidence, block, active, created_at, updated_at)
                VALUES
                    (:phone, :label, :source, :confidence, :block, :active, :now, :now)
                ON CONFLICT (phone_e164) DO UPDATE SET
                    label = COALESCE(EXCLUDED.label, antifake_scam_numbers.label),
                    source = EXCLUDED.source,
                    confidence = EXCLUDED.confidence,
                    block = EXCLUDED.block,
                    active = EXCLUDED.active,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "phone": normalized,
                "label": label,
                "source": source,
                "confidence": confidence,
                "block": block,
                "active": active,
                "now": now,
            },
        )
    return True


def import_csv_rows(rows: List[Dict[str, str]]) -> Tuple[int, int]:
    """Import CSV rows; returns (inserted_or_updated, skipped)."""
    ok = 0
    skipped = 0
    for row in rows:
        phone = row.get("phone") or row.get("phone_e164") or ""
        if not upsert_number(
            phone,
            source=row.get("source") or "csv",
            label=row.get("label") or None,
            confidence=int(row.get("confidence") or 80),
            block=str(row.get("block", "")).lower() in ("1", "true", "yes"),
        ):
            skipped += 1
        else:
            ok += 1
    return ok, skipped
