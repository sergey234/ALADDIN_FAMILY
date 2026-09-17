"""afhub-p2-04 — one-tap share verdict with family (incident + parent push)."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.antifake_family_store import (
    get_parent_user_ids,
    get_push_tokens,
    resolve_primary_family_id,
)

logger = logging.getLogger(__name__)


def share_verdict_with_family(
    *,
    user_id: int,
    verdict: str,
    confidence: float,
    job_id: Optional[str] = None,
    summary: Optional[str] = None,
    lang: str = "ru",
) -> Dict[str, Any]:
    """Record family incident + notify parents. Does not replace iOS Share sheet."""
    family_id = resolve_primary_family_id(int(user_id))
    if not family_id:
        return {"ok": False, "reason": "no_family", "notified": 0}

    conf_pct = int(max(0.0, min(1.0, float(confidence or 0.0))) * 100)
    verdict_key = str(verdict or "uncertain")

    try:
        from app.services.family_incidents_store import append_incident

        append_incident(
            family_id=family_id,
            member_user_id=int(user_id),
            incident_type="antifake_alert",
            severity="high" if verdict_key == "likely_fake" else "medium",
            meta={
                "manual_share": True,
                "job_id": job_id,
                "verdict": verdict_key,
                "confidence": conf_pct,
                "summary": (summary or "")[:400],
            },
        )
    except Exception as exc:
        logger.warning("family share incident failed: %s", exc)
        return {"ok": False, "reason": "incident_failed", "notified": 0}

    lang_key = "en" if str(lang).lower().startswith("en") else "ru"
    if lang_key == "en":
        title = "ALADDIN: family Antifake share"
        body = f"A family member shared a check result: {verdict_key} ({conf_pct}%). Open Hub → Antifake."
    else:
        title = "ALADDIN: проверка от семьи"
        body = f"Член семьи поделился результатом: {verdict_key} ({conf_pct}%). Откройте Hub → Antifake."

    extra = {
        "deepLink": f"aladdin://antifake/family-share?job_id={job_id or ''}",
        "job_id": job_id,
        "verdict": verdict_key,
        "manual_share": True,
    }

    notified = 0
    try:
        from app.services.antifake_family_notify import _send_apns_sync

        parent_ids = get_parent_user_ids(int(user_id))
        for parent_id in parent_ids:
            if parent_id == int(user_id):
                continue
            for token in get_push_tokens(parent_id):
                if _send_apns_sync(token, title, body, extra):
                    notified += 1
    except Exception as exc:
        logger.debug("family share push skipped: %s", exc)

    return {
        "ok": True,
        "family_id": family_id,
        "notified": notified,
        "reason": None,
    }
