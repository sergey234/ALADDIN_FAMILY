"""Antifake analysis — SFM execute + honest rule_engine fallback (no mock)."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"
FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback"})

TEXT_AGENT = "fake_news_detection_agent"
URL_AGENTS = ("phishing_protection_agent", "ai_agent_phishingprotection")
AUDIO_AGENT = "audio_deepfake_detection"
VIDEO_AGENTS = ("ai_agent_deepfakeprotectionsystem", "ai_agent_deepfakeanalysisresult")
DOCUMENT_AGENT = "fake_documents_agent"

FAKE_TEXT_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("sensationalism", "шокирующая правда"),
    ("sensationalism", "they don't want you to know"),
    ("urgency", "действуй сейчас"),
    ("urgency", "act now"),
    ("no_source", "анонимных источников"),
    ("scam", "переведите деньги"),
    ("scam", "send money immediately"),
    ("scam", "ваш счёт заблокирован"),
)

AUTHORITY_SPOOF_LABELS = (
    "банк",
    "bank",
    "сбер",
    "втб",
    "тинькофф",
    "tinkoff",
    "police",
    "полици",
    "налог",
    "tax",
    "gosuslugi",
    "госуслуг",
    "support",
    "apple",
    "microsoft",
    "мтс",
    "beeline",
    "мегафон",
)

GENERIC_CALLER_LABELS = (
    "unknown",
    "wireless",
    "неизвест",
    "private",
    "скрыт",
    "anonymous",
)

SUSPICIOUS_URL_PATTERNS = (
    r"@",
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"login[-_]?secure",
    r"verify[-_]?account",
    r"\.ru\.com\b",
    r"bit\.ly/",
    r"tinyurl\.com/",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sfm_execute(function_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps({"function": function_id, "params": params}).encode("utf-8")
    request = urllib.request.Request(
        SFM_EXECUTE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"success": False, "error": raw or str(exc)}


def _verdict_from_score(score: float) -> str:
    if score >= 0.65:
        return "likely_fake"
    if score >= 0.35:
        return "uncertain"
    return "likely_real"


def _build_response(
    *,
    verdict: str,
    confidence: float,
    reasons: List[str],
    source: str,
    agent: str,
    job_id: Optional[str] = None,
    premium_required: bool = False,
) -> Dict[str, Any]:
    if source in FORBIDDEN_SOURCES:
        raise ValueError(f"forbidden source {source}")
    return {
        "verdict": verdict,
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
        "reasons": reasons[:8],
        "source": source,
        "agent": agent,
        "job_id": job_id,
        "checked_at": _utc_now(),
        "premium_required": premium_required,
    }


def _analyze_text_heuristic(text: str, mode: str = "news") -> Dict[str, Any]:
    lowered = (text or "").lower().strip()
    if not lowered:
        return _build_response(
            verdict="uncertain",
            confidence=0.0,
            reasons=["empty_text"],
            source="rule_engine",
            agent="heuristic_text",
        )

    hits: List[str] = []
    for tag, pattern in FAKE_TEXT_PATTERNS:
        if pattern.lower() in lowered:
            hits.append(tag)

    url_count = len(re.findall(r"https?://\S+", lowered))
    if url_count >= 2:
        hits.append("multiple_links")
    if mode == "email" and "reply-to:" in lowered:
        hits.append("email_header_suspicious")

    score = min(1.0, 0.15 * len(hits) + (0.1 if len(lowered) < 40 else 0))
    return _build_response(
        verdict=_verdict_from_score(score if hits else 0.1),
        confidence=score if hits else 0.15,
        reasons=hits or ["no_suspicious_patterns"],
        source="rule_engine",
        agent="heuristic_text",
    )


def _analyze_url_heuristic(url: str) -> Dict[str, Any]:
    raw = (url or "").strip()
    if not raw:
        return _build_response(
            verdict="uncertain",
            confidence=0.0,
            reasons=["empty_url"],
            source="rule_engine",
            agent="heuristic_url",
        )

    reasons: List[str] = []
    for pattern in SUSPICIOUS_URL_PATTERNS:
        if re.search(pattern, raw, re.IGNORECASE):
            reasons.append(f"pattern:{pattern}")

    if raw.startswith("http://"):
        reasons.append("insecure_http")

    score = min(1.0, 0.2 * len(reasons))
    return _build_response(
        verdict=_verdict_from_score(score if reasons else 0.12),
        confidence=score if reasons else 0.12,
        reasons=reasons or ["url_looks_neutral"],
        source="rule_engine",
        agent="heuristic_url",
    )


def _normalize_sfm_result(
    outcome: Dict[str, Any],
    *,
    agent: str,
    fallback_fn,
) -> Dict[str, Any]:
    if not outcome.get("success"):
        return fallback_fn()

    result = outcome.get("result")
    if isinstance(result, dict):
        if result.get("status") == "success" and "verdict" not in result:
            return fallback_fn()
        if result.get("status") == "error":
            return fallback_fn()

        verdict = result.get("verdict") or result.get("label")
        confidence = result.get("confidence") or result.get("score") or 0.5
        if verdict in ("fake", "likely_fake", "FAKE"):
            verdict_norm = "likely_fake"
        elif verdict in ("real", "likely_real", "REAL", "safe"):
            verdict_norm = "likely_real"
        elif verdict in ("uncertain", "unknown"):
            verdict_norm = "uncertain"
        else:
            # Numeric score from agent
            try:
                numeric = float(confidence)
                verdict_norm = _verdict_from_score(numeric)
            except (TypeError, ValueError):
                return fallback_fn()

        reasons = result.get("reasons") or result.get("patterns") or []
        if isinstance(reasons, str):
            reasons = [reasons]
        if result.get("message") and not reasons:
            reasons = [str(result.get("message"))[:200]]

        source = str(outcome.get("source") or "real_sfm")
        if source in FORBIDDEN_SOURCES:
            return fallback_fn()

        return _build_response(
            verdict=verdict_norm,
            confidence=float(confidence) if isinstance(confidence, (int, float)) else 0.5,
            reasons=[str(r) for r in reasons][:8] or ["sfm_agent"],
            source="real_agent",
            agent=agent,
        )

    if isinstance(result, str) and result.strip():
        return fallback_fn()

    return fallback_fn()


def check_text(text: str, mode: str = "news") -> Dict[str, Any]:
    def fallback():
        return _analyze_text_heuristic(text, mode)

    outcome = _sfm_execute(TEXT_AGENT, {"text": text, "mode": mode})
    return _normalize_sfm_result(outcome, agent=TEXT_AGENT, fallback_fn=fallback)


def check_url(url: str) -> Dict[str, Any]:
    def fallback():
        return _analyze_url_heuristic(url)

    for agent in URL_AGENTS:
        outcome = _sfm_execute(agent, {"url": url})
        if outcome.get("success"):
            return _normalize_sfm_result(outcome, agent=agent, fallback_fn=fallback)
    return fallback()


def _normalize_phone_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _analyze_caller_spoof_heuristics(
    caller_id: Optional[str],
    display_name: Optional[str],
) -> Tuple[List[str], float]:
    """af-4-05: metadata-only spoof hints (caller_id vs display_name)."""
    reasons: List[str] = []
    score = 0.0

    cid = _normalize_phone_digits(caller_id or "")
    dn = (display_name or "").strip()
    dn_lower = dn.lower()
    dn_digits = _normalize_phone_digits(dn)

    if not cid and not dn:
        return reasons, score

    if dn_digits and cid and dn_digits != cid and len(dn_digits) >= 7:
        reasons.append("display_number_mismatch")
        score += 0.35

    if dn and any(label in dn_lower for label in AUTHORITY_SPOOF_LABELS):
        if not cid:
            reasons.append("authority_label_no_caller_id")
            score += 0.25
        elif len(cid) >= 10 and not cid.startswith(("7800", "8800", "7495")):
            reasons.append("authority_label_personal_number")
            score += 0.4

    if cid and dn and not dn_digits:
        if not any(label in dn_lower for label in GENERIC_CALLER_LABELS):
            if len(cid) >= 10 and any(label in dn_lower for label in AUTHORITY_SPOOF_LABELS):
                reasons.append("authority_name_non_service_number")
                score += 0.3

    return reasons, min(1.0, score)


def _merge_call_spoof_into_verdict(
    base: Dict[str, Any],
    spoof_reasons: List[str],
    spoof_score: float,
) -> Dict[str, Any]:
    if not spoof_reasons:
        return base

    merged_reasons = list(base.get("reasons") or []) + spoof_reasons
    confidence = max(float(base.get("confidence") or 0.0), spoof_score)
    verdict = base.get("verdict") or "uncertain"
    if spoof_score >= 0.35:
        verdict = _verdict_from_score(confidence)

    return _build_response(
        verdict=verdict,
        confidence=confidence,
        reasons=merged_reasons[:8],
        source=str(base.get("source") or "rule_engine"),
        agent=f"call_spoof+{base.get('agent', 'call')}",
        job_id=base.get("job_id"),
        premium_required=bool(base.get("premium_required")),
    )


def check_media(
    *,
    media_type: str,
    file_name: str,
    file_bytes: bytes,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run media check — sync lightweight probe; full worker in af-3."""
    extra = extra or {}
    if media_type in ("audio", "call"):
        agent = AUDIO_AGENT
    elif media_type == "video":
        agent = VIDEO_AGENTS[0]
    else:
        agent = DOCUMENT_AGENT

    outcome = _sfm_execute(
        agent,
        {
            "file_name": file_name,
            "size_bytes": len(file_bytes),
            "content_type": media_type,
            **extra,
        },
    )

    def fallback():
        # Size/heuristic only — honest uncertain, not mock success
        reasons = [f"{media_type}_agent_unavailable"]
        if len(file_bytes) == 0:
            reasons.append("empty_file")
        return _build_response(
            verdict="uncertain",
            confidence=0.25,
            reasons=reasons,
            source="rule_engine",
            agent=f"heuristic_{media_type}",
        )

    base = _normalize_sfm_result(outcome, agent=agent, fallback_fn=fallback)

    if media_type == "call":
        spoof_reasons, spoof_score = _analyze_caller_spoof_heuristics(
            extra.get("caller_id"),
            extra.get("display_name"),
        )
        return _merge_call_spoof_into_verdict(base, spoof_reasons, spoof_score)

    return base
