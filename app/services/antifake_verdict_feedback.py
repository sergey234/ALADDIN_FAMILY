"""T5-02 / TI-08 — verdict feedback (false positive) + lightweight rule tweaks + ingest."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from sqlalchemy import text

from app.database.database import engine

_FP_THRESHOLD = 5
_FP_WINDOW_DAYS = 7
_TWEAKS_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "antifake" / "rule_tweaks.json"
)
_URL_RE = re.compile(
    r"https?://[^\s<>\"']+|(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?",
    re.I,
)

_CREATE = """
CREATE TABLE IF NOT EXISTS antifake_verdict_feedback (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id UUID,
    verdict VARCHAR(32) NOT NULL,
    confidence SMALLINT,
    reasons JSONB NOT NULL DEFAULT '[]',
    source VARCHAR(32),
    feedback VARCHAR(16) NOT NULL DEFAULT 'incorrect',
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_antifake_verdict_feedback_created
    ON antifake_verdict_feedback (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_antifake_verdict_feedback_reason
    ON antifake_verdict_feedback ((reasons::text));
"""


def ensure_table() -> None:
    with engine.begin() as conn:
        for stmt in _CREATE.strip().split(";"):
            line = stmt.strip()
            if line:
                conn.execute(text(line))


def _extract_domain_from_note(note: Optional[str]) -> Optional[str]:
    if not note:
        return None
    match = _URL_RE.search(note)
    if not match:
        return None
    raw = match.group(0)
    if not raw.startswith("http"):
        raw = "https://" + raw
    from app.services.antifake_phishing_domains_store import _normalize_domain

    return _normalize_domain(raw)


def _maybe_ingest_user_report(note: Optional[str], feedback: str) -> Dict[str, Any]:
    """TI-08: confirmed phishing + URL in note → upsert domain."""
    if feedback not in ("correct", "confirmed", "phishing", "report"):
        return {"ingested": False}
    domain = _extract_domain_from_note(note)
    if not domain:
        return {"ingested": False, "reason": "no_domain_in_note"}
    from app.services.antifake_phishing_domains_store import upsert_domain

    ok = upsert_domain(
        domain,
        source="user_report",
        label="User confirmed phishing",
        confidence=88,
        category="phishing",
    )
    return {"ingested": bool(ok), "domain": domain}


def record_feedback(
    *,
    user_id: int,
    job_id: Optional[str],
    verdict: str,
    confidence: Optional[int],
    reasons: List[str],
    source: Optional[str],
    note: Optional[str],
    feedback: str = "incorrect",
) -> Dict[str, Any]:
    ensure_table()
    feedback_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    clean_reasons = [str(r) for r in (reasons or [])[:12]]
    fb = (feedback or "incorrect").strip().lower() or "incorrect"
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO antifake_verdict_feedback
                    (id, user_id, job_id, verdict, confidence, reasons, source, feedback, note, created_at)
                VALUES
                    (CAST(:id AS UUID), :user_id, CAST(:job_id AS UUID), :verdict, :confidence,
                     CAST(:reasons AS JSONB), :source, :feedback, :note, :now)
                """
            ),
            {
                "id": feedback_id,
                "user_id": int(user_id),
                "job_id": job_id,
                "verdict": verdict,
                "confidence": confidence,
                "reasons": json.dumps(clean_reasons),
                "source": source,
                "feedback": fb,
                "note": note,
                "now": now,
            },
        )
    if fb == "incorrect":
        maybe_refresh_rule_tweaks()
    ingest = _maybe_ingest_user_report(note, fb)
    lexicon_queue: Dict[str, Any] = {"queued": False, "count": 0}
    # afhub-p3-01: «это был скам» / confirmed miss → review queue only (no live lexicon write)
    if fb in ("was_scam", "scam", "missed_scam", "false_negative") or (
        fb in ("correct", "confirmed") and str(verdict or "") in ("likely_real", "uncertain", "insufficient_data")
    ):
        try:
            from app.services.antifake_lexicon_review_queue import enqueue_from_feedback

            lexicon_queue = enqueue_from_feedback(
                note=note,
                feedback_id=feedback_id,
                user_id=int(user_id),
                job_id=job_id,
                verdict=verdict,
                feedback=fb,
            )
        except Exception:
            lexicon_queue = {"queued": False, "count": 0, "reason": "queue_error"}
    return {
        "id": feedback_id,
        "feedback": fb,
        "recorded": True,
        "ingest": ingest,
        "lexicon_review": lexicon_queue,
    }


def fp_metrics(window_days: int = _FP_WINDOW_DAYS) -> Dict[str, Any]:
    ensure_table()
    since = datetime.now(timezone.utc) - timedelta(days=window_days)
    with engine.connect() as conn:
        total = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM antifake_verdict_feedback
                WHERE feedback = 'incorrect' AND created_at >= :since
                """
            ),
            {"since": since},
        ).scalar()
        rows = conn.execute(
            text(
                """
                SELECT reasons::text AS reasons_json, COUNT(*) AS cnt
                FROM antifake_verdict_feedback
                WHERE feedback = 'incorrect' AND created_at >= :since
                GROUP BY reasons::text
                ORDER BY cnt DESC
                LIMIT 20
                """
            ),
            {"since": since},
        ).mappings().all()

    by_reason: Dict[str, int] = {}
    for row in rows:
        try:
            reasons = json.loads(row["reasons_json"] or "[]")
        except json.JSONDecodeError:
            reasons = []
        for reason in reasons:
            key = str(reason)
            by_reason[key] = by_reason.get(key, 0) + int(row["cnt"] or 0)

    return {
        "window_days": window_days,
        "false_positive_reports": int(total or 0),
        "by_reason": dict(sorted(by_reason.items(), key=lambda x: -x[1])[:15]),
        "downrank_reasons": sorted(load_downrank_reasons()),
    }


def load_downrank_reasons() -> Set[str]:
    if not _TWEAKS_PATH.is_file():
        return set()
    try:
        data = json.loads(_TWEAKS_PATH.read_text(encoding="utf-8"))
        return {str(r) for r in data.get("downrank_reasons", [])}
    except (json.JSONDecodeError, OSError):
        return set()


def maybe_refresh_rule_tweaks() -> Dict[str, Any]:
    """Recompute downrank list when a reason hits FP threshold in the window."""
    metrics = fp_metrics()
    downrank = {r for r, c in metrics["by_reason"].items() if c >= _FP_THRESHOLD}
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "fp_threshold": _FP_THRESHOLD,
        "window_days": _FP_WINDOW_DAYS,
        "downrank_reasons": sorted(downrank),
        "by_reason": metrics["by_reason"],
    }
    _TWEAKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _TWEAKS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def confidence_penalty_for_reasons(reasons: List[str]) -> float:
    """Apply downrank penalty in heuristics when reason was flagged as FP."""
    downrank = load_downrank_reasons()
    if not downrank:
        return 0.0
    hits = sum(1 for r in reasons if r in downrank)
    if hits <= 0:
        return 0.0
    return min(0.25, 0.08 * hits)
