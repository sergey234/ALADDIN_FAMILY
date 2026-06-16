"""Antifake analysis — SFM execute + honest rule_engine fallback (no mock)."""
from __future__ import annotations

import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"
FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback"})
ALLOWED_AI_SOURCES = frozenset({"real_agent", "local_ml"})
SFM_422_BACKOFF_SEC = (0.35, 0.7, 1.0, 1.5, 2.0)

TEXT_AGENT = "fake_news_detection_agent"
URL_AGENTS = ("phishing_protection_agent", "ai_agent_phishingprotection")
AUDIO_AGENT = "audio_deepfake_detection"
VIDEO_AGENTS = ("ai_agent_deepfakeprotectionsystem", "ai_agent_deepfakeanalysisresult")
DOCUMENT_AGENT = "fake_documents_agent"

MAX_AUDIO_SFM_BYTES = 2 * 1024 * 1024
MAX_VIDEO_SFM_BYTES = 512 * 1024

# F-04 latency SLA targets (ms) for client progress UX
SLA_MS = {
    "text": 8_000,
    "url": 8_000,
    "audio": 120_000,
    "video": 300_000,
    "call": 180_000,
    "document": 120_000,
}

MODEL_VERSION = os.environ.get("ANTIFAKE_MODEL_VERSION", "antifake-v1.0.0")
MIN_TEXT_ANALYSIS_CHARS = 40

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
    last_body: Dict[str, Any] = {"success": False, "error": "sfm_unreachable"}
    max_attempts = max(3, len(SFM_422_BACKOFF_SEC))
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode() or "{}")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                last_body = json.loads(raw)
            except json.JSONDecodeError:
                last_body = {"success": False, "error": raw or str(exc)}
            err_text = str(last_body.get("error") or raw or "").lower()
            is_limit = exc.code == 422 and "лимит" in err_text
            if is_limit and attempt < max_attempts - 1:
                delay = SFM_422_BACKOFF_SEC[min(attempt, len(SFM_422_BACKOFF_SEC) - 1)]
                time.sleep(delay)
                continue
            return last_body
        except urllib.error.URLError as exc:
            last_body = {"success": False, "error": str(exc)}
            if attempt < max_attempts - 1:
                time.sleep(0.2)
                continue
    return last_body


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
    fake_risk = round(max(0.0, min(1.0, confidence)), 3)
    return {
        "verdict": verdict,
        "confidence": fake_risk,
        "fake_risk": fake_risk,
        "reasons": reasons[:8],
        "source": source,
        "agent": agent,
        "job_id": job_id,
        "checked_at": _utc_now(),
        "premium_required": premium_required,
        "model_version": MODEL_VERSION,
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

    score = min(1.0, 0.22 * len(hits) + (0.1 if len(lowered) < 40 else 0))
    if len(hits) >= 3:
        score = max(score, 0.68)
    elif len(hits) >= 2 and "scam" in hits:
        score = max(score, 0.66)
    if not hits and len(lowered) < MIN_TEXT_ANALYSIS_CHARS:
        return _build_response(
            verdict="insufficient_data",
            confidence=0.0,
            reasons=["text_too_short"],
            source="rule_engine",
            agent="heuristic_text",
        )
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
        if result.get("status") == "success" and "analysis" in result:
            analysis = result.get("analysis") or {}
            if isinstance(analysis, dict):
                return _normalize_local_ml_text_result(
                    analysis,
                    source="real_agent",
                    agent=agent,
                )
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


def _normalize_local_ml_text_result(
    result: Dict[str, Any],
    *,
    mode: str = "news",
    source: str = "local_ml",
    agent: Optional[str] = None,
) -> Dict[str, Any]:
    """F-12: map FakeNewsDetectionAgent output → antifake verdict contract."""
    fake_score = float(result.get("fake_score") or result.get("model_score") or 0.0)
    credibility = str(result.get("credibility_level") or "").lower()
    pattern_hits = result.get("pattern_hits") or {}
    structural_flags = result.get("structural_flags") or {}
    has_pattern_hits = isinstance(pattern_hits, dict) and bool(pattern_hits)
    too_short = isinstance(structural_flags, dict) and bool(structural_flags.get("too_short"))

    if too_short and not has_pattern_hits and fake_score < 0.35:
        return _build_response(
            verdict="insufficient_data",
            confidence=0.0,
            reasons=["text_too_short"],
            source=source,
            agent=agent or f"local_{TEXT_AGENT}",
        )

    if credibility in ("fake", "suspicious") or fake_score >= 0.65:
        verdict = "likely_fake"
    elif fake_score >= 0.35 or credibility == "low_credibility":
        verdict = "uncertain"
    else:
        verdict = "likely_real"

    reasons: List[str] = []
    if isinstance(pattern_hits, dict):
        for category in pattern_hits:
            if category not in reasons:
                reasons.append(str(category))
    for flag, active in structural_flags.items():
        if active and str(flag) not in reasons:
            reasons.append(str(flag))
    if not reasons:
        reasons = ["local_ml_analysis"]

    confidence = max(fake_score, 0.35 if verdict == "likely_fake" else fake_score)
    return _build_response(
        verdict=verdict,
        confidence=confidence,
        reasons=reasons[:8],
        source=source,
        agent=agent or f"local_{TEXT_AGENT}",
    )


def _try_local_ml_text(text: str, mode: str = "news") -> Optional[Dict[str, Any]]:
    try:
        from app.security.ml_lazy_loader import run_text_check

        raw = run_text_check(text, metadata={"mode": mode})
        if not isinstance(raw, dict):
            return None
        return _normalize_local_ml_text_result(raw, mode=mode)
    except Exception:
        try:
            from app.security.ai_agents.fake_news_detection_agent import FakeNewsDetectionAgent

            raw = FakeNewsDetectionAgent().detect_fake_news(text, metadata={"mode": mode})
            if isinstance(raw, dict):
                return _normalize_local_ml_text_result(raw, mode=mode)
        except Exception:
            pass
    return None


def _merge_local_with_heuristic(local: Dict[str, Any], heuristic: Dict[str, Any]) -> Dict[str, Any]:
    """Prefer local_ml source; boost obvious scam when ML is uncertain (F-12)."""
    if heuristic.get("verdict") != "likely_fake":
        return local
    if local.get("verdict") == "likely_fake":
        return local
    merged_reasons = list(local.get("reasons") or [])
    for reason in heuristic.get("reasons") or []:
        if reason not in merged_reasons:
            merged_reasons.append(reason)
    confidence = max(float(local.get("confidence") or 0.0), float(heuristic.get("confidence") or 0.0))
    return _build_response(
        verdict="likely_fake",
        confidence=confidence,
        reasons=merged_reasons[:8],
        source="local_ml",
        agent=str(local.get("agent") or f"local_{TEXT_AGENT}"),
        job_id=local.get("job_id"),
        premium_required=bool(local.get("premium_required")),
    )


def _tier2_text_fallback(text: str, mode: str = "news") -> Dict[str, Any]:
    """SFM unavailable → local ML → regex heuristic."""
    heuristic = _analyze_text_heuristic(text, mode)
    local = _try_local_ml_text(text, mode)
    if local is not None:
        return _merge_local_with_heuristic(local, heuristic)
    return heuristic


def check_text(text: str, mode: str = "news") -> Dict[str, Any]:
    outcome = _sfm_execute(TEXT_AGENT, {"text": text, "mode": mode})
    if outcome.get("success"):
        return _normalize_sfm_result(
            outcome,
            agent=TEXT_AGENT,
            fallback_fn=lambda: _tier2_text_fallback(text, mode),
        )
    return _tier2_text_fallback(text, mode)


def check_url(url: str) -> Dict[str, Any]:
    from app.services.antifake_security import AntifakeSecurityError, validate_check_url

    try:
        safe_url = validate_check_url(url)
    except AntifakeSecurityError:
        return _build_response(
            verdict="uncertain",
            confidence=0.0,
            reasons=["blocked_url"],
            source="rule_engine",
            agent="url_security_gate",
        )

    def fallback():
        return _analyze_url_heuristic(safe_url)

    for agent in URL_AGENTS:
        outcome = _sfm_execute(agent, {"url": safe_url})
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


def _media_bytes_payload(file_bytes: bytes, media_type: str) -> Dict[str, Any]:
    """F-11: pass capped byte sample to SFM, not metadata-only."""
    cap = MAX_AUDIO_SFM_BYTES if media_type in ("audio", "call") else MAX_VIDEO_SFM_BYTES
    sample = file_bytes[:cap] if file_bytes else b""
    return {
        "file_bytes_b64": base64.b64encode(sample).decode("ascii"),
        "file_bytes_len": len(file_bytes),
        "file_bytes_sample_len": len(sample),
    }


_PROBE_SOURCES = frozenset({"audio_probe", "video_probe"})


def _source_has_ml(source: str) -> bool:
    lowered = (source or "").lower()
    return "real_agent" in lowered or "local_ml" in lowered


def _merge_probe_into_verdict(
    base: Dict[str, Any],
    probe: Dict[str, Any],
) -> Dict[str, Any]:
    if not probe:
        return base
    reasons = list(base.get("reasons") or [])
    for reason in probe.get("reasons") or []:
        if reason not in reasons:
            reasons.append(reason)
    confidence = float(base.get("confidence") or 0.0)
    probe_score = float(probe.get("confidence") or 0.0)
    verdict = base.get("verdict") or _verdict_from_score(confidence)
    source = base.get("source") or "rule_engine"
    probe_source = str(probe.get("source") or "")

    if probe_source in _PROBE_SOURCES:
        # F-02 / F-11: probe adds hints only — no likely_fake without ML tier.
        merged_conf = min(0.69, max(confidence, probe_score))
        if verdict == "likely_fake" and not _source_has_ml(source):
            verdict = "uncertain"
            merged_conf = min(merged_conf, 0.69)
        if probe_source and probe_source not in source:
            source = f"{source}+{probe_source}"
    else:
        merged_conf = min(0.99, max(confidence, probe_score))
        if probe.get("verdict") == "likely_fake" and verdict != "likely_fake":
            verdict = "likely_fake"
            merged_conf = max(merged_conf, 0.72)
        if probe_source and probe_source not in source:
            source = f"{source}+{probe_source}"

    return _build_response(
        verdict=verdict,
        confidence=merged_conf,
        reasons=reasons[:8],
        source=source,
        agent=str(base.get("agent") or "media"),
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

    sfm_params: Dict[str, Any] = {
        "file_name": file_name,
        "size_bytes": len(file_bytes),
        "content_type": media_type,
        **_media_bytes_payload(file_bytes, media_type),
        **extra,
    }

    outcome = _sfm_execute(agent, sfm_params)

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

    if media_type in ("audio", "call") and file_bytes:
        try:
            from app.security.ml_lazy_loader import probe_audio_bytes

            base = _merge_probe_into_verdict(base, probe_audio_bytes(file_bytes))
        except Exception:
            pass

    if media_type == "video" and file_bytes:
        try:
            from app.security.ml_lazy_loader import probe_video_bytes

            base = _merge_probe_into_verdict(base, probe_video_bytes(file_bytes))
        except Exception:
            pass

    if media_type == "call":
        spoof_reasons, spoof_score = _analyze_caller_spoof_heuristics(
            extra.get("caller_id"),
            extra.get("display_name"),
        )
        return _merge_call_spoof_into_verdict(base, spoof_reasons, spoof_score)

    return base
