"""C-04: auto-ingest scam numbers from call analyze + user reports."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from app.services.antifake_call_directory_store import phone_log_hash, upsert_number

logger = logging.getLogger(__name__)

MIN_CONFIDENCE_FOR_INGEST = 0.72
REPORT_SOURCES = frozenset({"user_report", "report", "appeal"})


def _normalize_caller(raw: Optional[str]) -> Optional[str]:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) < 10 or len(digits) > 15:
        return None
    return digits


def maybe_ingest_from_call_verdict(
    verdict: Dict[str, Any],
    *,
    caller_id: Optional[str] = None,
    display_name: Optional[str] = None,
    user_id: Optional[int] = None,
) -> bool:
    """Upsert caller into fraud DB when call analysis is likely_fake."""
    if str(verdict.get("verdict") or "") != "likely_fake":
        return False

    confidence = float(verdict.get("confidence") or 0.0)
    if confidence < MIN_CONFIDENCE_FOR_INGEST:
        return False

    phone = _normalize_caller(caller_id)
    if not phone:
        return False

    label = (display_name or "").strip() or None
    ok = upsert_number(
        phone,
        source="call_analyze",
        label=label,
        confidence=int(min(99, confidence * 100)),
        block=False,
    )
    if ok:
        logger.info(
            "antifake_fraud_ingest call_analyze user=%s phone_hash=%s conf=%.2f",
            user_id,
            phone_log_hash(phone),
            confidence,
        )
    return ok


def ingest_from_report(
    *,
    phone: str,
    label: Optional[str] = None,
    confidence: int = 85,
    source: str = "user_report",
    block: bool = False,
) -> bool:
    """Ingest explicit user report (I-batch hook; safe to call from future report API)."""
    normalized = _normalize_caller(phone)
    if not normalized:
        return False
    src = source if source in REPORT_SOURCES or source == "call_analyze" else "user_report"
    ok = upsert_number(
        normalized,
        source=src,
        label=label,
        confidence=confidence,
        block=block,
    )
    if ok:
        logger.info(
            "antifake_fraud_ingest report source=%s phone_hash=%s",
            src,
            phone_log_hash(normalized),
        )
    return ok
