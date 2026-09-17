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

from app.services.antifake_scam_lexicon import (
    SCAM_LEXICON_PATTERNS,
    anti_green_verdict,
    apply_scam_score_floors,
    has_urgency_and_money,
    match_lexicon_tags,
)
from app.services.antifake_scam_intent import (
    classify_scam_intent,
    merge_intent_into_hits,
)

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"
FORBIDDEN_SOURCES = frozenset({"sfm_mock", "mock", "sfm_stub", "sfm_fallback"})
# RH-A05: honest local media sources are first-class AI path markers
ALLOWED_AI_SOURCES = frozenset(
    {"real_agent", "local_ml", "local_audio_ml", "local_video_ml"}
)
ALLOWED_SOURCES = frozenset(
    {
        *ALLOWED_AI_SOURCES,
        "rule_engine",
        "threat_feed",
        "fuzzy",
        "rkn_signal",
        "video_metadata",
        "video_probe",
        "audio_probe",
        "stt_ru",
        "ensemble_text",
        "ensemble_audio",
        "ensemble_video",
        "document_provenance",
    }
)
SFM_422_BACKOFF_SEC = (0.35, 0.7, 1.0, 1.5, 2.0)
# RH-A01: SFM no-handler stub shapes must never become source=real_agent
_SFM_ANALYSIS_KEYS = frozenset(
    {
        "verdict",
        "label",
        "analysis",
        "confidence",
        "score",
        "fake_score",
        "reasons",
        "patterns",
        "authenticity_level",
        "credibility_level",
    }
)

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

# SSOT: app.services.antifake_scam_lexicon (afhub-p0-02)
FAKE_TEXT_PATTERNS: Tuple[Tuple[str, str], ...] = SCAM_LEXICON_PATTERNS

AUTHORITY_SPOOF_LABELS = (
    "банк",
    "bank",
    "сбер",
    "sber",
    "втб",
    "vtb",
    "тинькофф",
    "tinkoff",
    "tbank",
    "альфа",
    "alfa",
    "police",
    "полици",
    "мвд",
    "фсб",
    "налог",
    "tax",
    "irs",
    "gosuslugi",
    "госуслуг",
    "support",
    "служба безопасности",
    "security",
    "apple",
    "microsoft",
    "paypal",
    "amazon",
    "мтс",
    "beeline",
    "мегафон",
    "tele2",
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


def is_sfm_stub_payload(result: Any) -> bool:
    """RH-A01: detect SFM no-handler stub ({status:executed} / params-echo)."""
    if not isinstance(result, dict):
        return False
    status = str(result.get("status") or "").strip().lower()
    if status == "executed":
        return True
    has_analysis = any(k in result for k in _SFM_ANALYSIS_KEYS)
    if has_analysis:
        return False
    # Classic stub: function_id + params echo, no analysis fields
    if ("function_id" in result or "function" in result) and "params" in result:
        return True
    # Params-only echo without success/error analysis envelope
    if status not in ("success", "error") and "params" in result and len(result) <= 4:
        return True
    return False


def _normalize_source(source: str) -> str:
    """RH-A05: map aliases; never emit forbidden sources."""
    raw = (source or "").strip()
    aliases = {
        "real_sfm": "real_agent",
        "sfm": "real_agent",
        "local_audio": "local_audio_ml",
        "local_video": "local_video_ml",
    }
    normalized = aliases.get(raw, raw)
    if normalized in FORBIDDEN_SOURCES:
        raise ValueError(f"forbidden source {normalized}")
    return normalized


def _build_response(
    *,
    verdict: str,
    confidence: float,
    reasons: List[str],
    source: str,
    agent: str,
    job_id: Optional[str] = None,
    premium_required: bool = False,
    sources: Optional[List[Dict[str, Any]]] = None,
    provenance: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source = _normalize_source(source)
    if source in FORBIDDEN_SOURCES:
        raise ValueError(f"forbidden source {source}")
    fake_risk = round(max(0.0, min(1.0, confidence)), 3)
    payload: Dict[str, Any] = {
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
    if sources:
        payload["sources"] = sources[:6]
    if provenance:
        payload["provenance"] = provenance
    # afl10n-p0-05: do not bake RU reasons_human here.
    # SSOT human copy = router `_client_verdict` / `attach_human_reasons` with request lang.
    return payload


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

    hits: List[str] = match_lexicon_tags(lowered)
    hits = merge_intent_into_hits(hits, classify_scam_intent(lowered))

    url_count = len(re.findall(r"https?://\S+", lowered))
    if url_count >= 2:
        hits.append("multiple_links")
    if mode == "email" and "reply-to:" in lowered:
        hits.append("email_header_suspicious")

    # Deduplicate while preserving order
    seen_hits = set()
    uniq_hits: List[str] = []
    for h in hits:
        if h not in seen_hits:
            uniq_hits.append(h)
            seen_hits.add(h)
    hits = uniq_hits

    score = min(1.0, 0.22 * len(hits) + (0.1 if len(lowered) < 40 else 0))
    intent_n = sum(1 for h in hits if str(h).startswith("intent_"))
    from app.services.antifake_scam_lexicon import has_strong_scam_phrase

    strong_hit = has_strong_scam_phrase(lowered)
    hard_intent = any(
        h in hits
        for h in (
            "intent_money_transfer",
            "intent_card",
            "intent_otp",
            "intent_sbp",
            "intent_prize",
        )
    )
    # Multi-hit boost only when signal is strong (not «сбер» + authority alone)
    if len(hits) >= 3 and (strong_hit or hard_intent or "urgency" in hits):
        score = max(score, 0.68)
    elif len(hits) >= 2 and "scam" in hits and (strong_hit or hard_intent or "urgency" in hits):
        score = max(score, 0.66)
    elif intent_n >= 2:
        score = max(score, 0.66)
    score = apply_scam_score_floors(tags=hits, score=score, mode=mode, text=lowered)
    # RH-B04: SMS can be short but still actionable
    min_chars = 12 if mode == "sms" else MIN_TEXT_ANALYSIS_CHARS
    if not hits and len(lowered) < min_chars:
        return _build_response(
            verdict="insufficient_data",
            confidence=0.0,
            reasons=["text_too_short"],
            source="rule_engine",
            agent="heuristic_text",
        )
    try:
        from app.services.antifake_verdict_feedback import confidence_penalty_for_reasons

        score = max(0.0, score - confidence_penalty_for_reasons(hits))
    except Exception:
        pass
    verdict = _verdict_from_score(score if hits else 0.1)
    confidence = score if hits else 0.15
    reasons = hits or ["no_suspicious_patterns"]
    verdict, confidence = anti_green_verdict(verdict, reasons, confidence)
    return _build_response(
        verdict=verdict,
        confidence=confidence,
        reasons=reasons,
        source="rule_engine",
        agent="heuristic_text",
    )


def _analyze_url_heuristic(url: str) -> Dict[str, Any]:
    from app.services.antifake_url_trust import analyze_url_signals

    raw = (url or "").strip()
    if not raw:
        return _build_response(
            verdict="uncertain",
            confidence=0.0,
            reasons=["empty_url"],
            source="rule_engine",
            agent="heuristic_url",
        )

    reasons, sources = analyze_url_signals(raw)
    score = min(1.0, 0.2 * len([r for r in reasons if r != "url_looks_neutral"]))
    if "url_phishing_path" in reasons or "url_credential_trap" in reasons:
        score = max(score, 0.66)
    if "url_typosquat_tld" in reasons:
        score = max(score, 0.7)
    from app.services.antifake_verdict_feedback import confidence_penalty_for_reasons

    score = max(0.0, score - confidence_penalty_for_reasons(reasons))
    neutral = not reasons or reasons == ["url_looks_neutral"]
    return _build_response(
        verdict=_verdict_from_score(score if not neutral else 0.12),
        confidence=score if not neutral else 0.12,
        reasons=reasons,
        sources=sources,
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
    # RH-A01: stub executed / params-echo → honest fallback, never real_agent
    if is_sfm_stub_payload(result):
        return fallback_fn()

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
            # No explicit verdict and only default confidence → not a real analysis
            if verdict is None and "confidence" not in result and "score" not in result:
                return fallback_fn()
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

        sources_raw = result.get("sources")
        sources: List[Dict[str, Any]] = []
        if isinstance(sources_raw, list):
            sources = [s for s in sources_raw if isinstance(s, dict)]

        source = str(outcome.get("source") or "real_sfm")
        if source in FORBIDDEN_SOURCES:
            return fallback_fn()

        return _build_response(
            verdict=verdict_norm,
            confidence=float(confidence) if isinstance(confidence, (int, float)) else 0.5,
            reasons=[str(r) for r in reasons][:8] or ["sfm_agent"],
            sources=sources or None,
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

    # afhub-p0-03: urgency+money from agent tags → floor likely_fake
    agent_tags = []
    if "urgency_manipulation" in reasons or "urgency" in reasons:
        agent_tags.append("urgency")
    if "financial_scam" in reasons or "scam" in reasons:
        agent_tags.append("scam")
    if has_urgency_and_money(agent_tags):
        fake_score = max(fake_score, 0.85)
        verdict = "likely_fake"
    # SMS: financial_scam alone is actionable — never leave uncertain due to too_short
    if mode == "sms" and "scam" in agent_tags:
        fake_score = max(fake_score, 0.72)
        verdict = "likely_fake"
        reasons = [r for r in reasons if r != "too_short"] or reasons

    confidence = max(fake_score, 0.35 if verdict == "likely_fake" else fake_score)
    verdict, confidence = anti_green_verdict(verdict, reasons, confidence)
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
    # afhub-p0: heuristic likely_fake always wins over soft ML likely_real
    if heuristic.get("verdict") == "likely_fake":
        if local.get("verdict") == "likely_fake":
            return local
        merged_reasons = list(local.get("reasons") or [])
        for reason in heuristic.get("reasons") or []:
            if reason not in merged_reasons:
                merged_reasons.append(reason)
        confidence = max(
            float(local.get("confidence") or 0.0),
            float(heuristic.get("confidence") or 0.0),
        )
        return _build_response(
            verdict="likely_fake",
            confidence=confidence,
            reasons=merged_reasons[:8],
            source="local_ml",
            agent=str(local.get("agent") or f"local_{TEXT_AGENT}"),
            job_id=local.get("job_id"),
            premium_required=bool(local.get("premium_required")),
        )
    # If heuristic is uncertain with manipulation but local is green — prefer heuristic floor
    if heuristic.get("verdict") == "uncertain" and local.get("verdict") == "likely_real":
        h_reasons = list(heuristic.get("reasons") or [])
        if anti_green_verdict("likely_real", h_reasons, float(heuristic.get("confidence") or 0))[0] != "likely_real":
            return heuristic
    return local


def _tier2_text_fallback(text: str, mode: str = "news") -> Dict[str, Any]:
    """SFM unavailable → local ML → regex heuristic."""
    heuristic = _analyze_text_heuristic(text, mode)
    local = _try_local_ml_text(text, mode)
    if local is not None:
        return _merge_local_with_heuristic(local, heuristic)
    return heuristic


def check_text(text: str, mode: str = "news") -> Dict[str, Any]:
    from app.services.antifake_text_ensemble import ensemble_check_text

    return ensemble_check_text(text, mode=mode)


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

    # afhub-p1-02 — redirect probe (SSRF-safe); soft-fail offline
    redirect_reasons: List[str] = []
    analyze_url = safe_url
    try:
        from app.services.antifake_url_redirect import enrich_url_check_with_redirects

        analyze_url, redirect_reasons, _redir_conf, _final = enrich_url_check_with_redirects(
            safe_url,
            base_reasons=[],
            base_confidence=0.0,
        )
        if not analyze_url:
            analyze_url = safe_url
        try:
            analyze_url = validate_check_url(analyze_url)
        except AntifakeSecurityError:
            analyze_url = safe_url
            if "url_redirect_blocked_hop" not in redirect_reasons:
                redirect_reasons.append("url_redirect_blocked_hop")
    except Exception:
        analyze_url = safe_url
        redirect_reasons = []

    from app.services.antifake_phishing_domains_store import lookup_url_domain

    feed_hit = lookup_url_domain(analyze_url) or lookup_url_domain(safe_url)
    if feed_hit:
        from app.services.antifake_url_trust import analyze_url_signals

        conf = float(feed_hit["confidence"]) / 100.0
        reasons, sources = analyze_url_signals(analyze_url)
        merged_reasons = ["feed_known_phishing_domain"] + [
            r for r in reasons if r not in ("url_looks_neutral",)
        ] + [r for r in redirect_reasons if r not in ("url_looks_neutral",)]
        return _build_response(
            verdict="likely_fake",
            confidence=conf,
            reasons=merged_reasons[:8],
            sources=sources,
            source="threat_feed",
            agent="phishing_domain_feed",
        )

    # TI-04 / TI-04b — fuzzy typosquat after feed miss, before SFM
    from app.services.antifake_url_fuzzy import analyze_fuzzy_url

    fuzzy_hit = analyze_fuzzy_url(analyze_url) or analyze_fuzzy_url(safe_url)
    if fuzzy_hit and not fuzzy_hit.get("allowlisted"):
        from app.services.antifake_url_trust import analyze_url_signals

        reasons, sources = analyze_url_signals(analyze_url)
        merged = ["fuzzy_typosquat"] + list(fuzzy_hit.get("reasons") or []) + [
            r for r in reasons if r not in ("url_looks_neutral",)
        ] + [r for r in redirect_reasons if r not in reasons]
        return _build_response(
            verdict="likely_fake",
            confidence=float(fuzzy_hit.get("confidence") or 0.8),
            reasons=merged[:8],
            sources=sources,
            source="fuzzy",
            agent="url_fuzzy",
        )

    # Redirect brand lookalike alone (no fuzzy on start URL)
    if "brand_lookalike_redirect" in redirect_reasons:
        from app.services.antifake_url_trust import analyze_url_signals

        reasons, sources = analyze_url_signals(analyze_url)
        merged = list(redirect_reasons) + [
            r for r in reasons if r not in ("url_looks_neutral",)
        ]
        return _build_response(
            verdict="likely_fake",
            confidence=0.82,
            reasons=merged[:8],
            sources=sources,
            source="redirect",
            agent="url_redirect",
        )

    from app.services.antifake_phishing_domains_store import lookup_rkn_blocked

    rkn_hit = lookup_rkn_blocked(analyze_url) or lookup_rkn_blocked(safe_url)

    def fallback():
        base = _analyze_url_heuristic(analyze_url)
        if redirect_reasons:
            reasons = list(redirect_reasons) + [
                r for r in (base.get("reasons") or []) if r not in redirect_reasons
            ]
            conf = float(base.get("confidence") or 0)
            if "url_redirect_host_mismatch" in redirect_reasons:
                conf = max(conf, 0.55)
                if base.get("verdict") == "likely_real":
                    return _build_response(
                        verdict="uncertain",
                        confidence=conf,
                        reasons=reasons[:8],
                        sources=base.get("sources"),
                        source="redirect",
                        agent="url_redirect",
                    )
            base = _build_response(
                verdict=str(base.get("verdict") or "uncertain"),
                confidence=conf,
                reasons=reasons[:8],
                sources=base.get("sources"),
                source=str(base.get("source") or "rule_engine"),
                agent=str(base.get("agent") or "heuristic_url"),
            )
        # TI-RKN-05: RKN alone never upgrades to likely_fake
        if rkn_hit and base.get("verdict") != "likely_fake":
            reasons = ["rkn_blocked_signal"] + list(base.get("reasons") or [])
            return _build_response(
                verdict="uncertain",
                confidence=min(0.7, float(rkn_hit.get("confidence") or 65) / 100.0),
                reasons=reasons[:8],
                sources=base.get("sources"),
                source="rkn_signal",
                agent="rkn_mirror",
            )
        return base

    # RH-C01 / RH-AG02: live PhishingProtectionAgent as secondary (never SFM stub)
    phishing = _try_phishing_protection_secondary(analyze_url)
    if phishing is not None:
        if rkn_hit and phishing.get("verdict") == "likely_real":
            reasons = ["rkn_blocked_signal"] + list(phishing.get("reasons") or [])
            return _build_response(
                verdict="uncertain",
                confidence=min(0.7, float(rkn_hit.get("confidence") or 65) / 100.0),
                reasons=reasons[:8],
                sources=phishing.get("sources"),
                source="rkn_signal",
                agent="rkn_mirror",
            )
        if redirect_reasons:
            reasons = list(redirect_reasons) + list(phishing.get("reasons") or [])
            return _build_response(
                verdict=str(phishing.get("verdict") or "uncertain"),
                confidence=float(phishing.get("confidence") or 0),
                reasons=reasons[:8],
                sources=phishing.get("sources"),
                source=str(phishing.get("source") or "agent"),
                agent=str(phishing.get("agent") or "phishing"),
            )
        return phishing

    return fallback()


def _try_phishing_protection_secondary(url: str) -> Optional[Dict[str, Any]]:
    """RH-AG02: sync PhishingProtectionAgent — secondary after feed/fuzzy; allowlist-safe."""
    try:
        from urllib.parse import urlparse

        from app.services.antifake_url_fuzzy import BRAND_ALLOWLIST, is_allowlisted

        host = (urlparse(url).hostname or "").lower().strip(".")
        if host and is_allowlisted(host):
            return None

        try:
            from app.security.ai_agents.phishing_protection_agent import PhishingProtectionAgent
        except ImportError:
            from security.ai_agents.phishing_protection_agent import PhishingProtectionAgent  # type: ignore

        agent = PhishingProtectionAgent()
        agent.trusted_domains.update(BRAND_ALLOWLIST)
        detection = agent.analyze_url(url)
        if detection is None:
            return None

        conf = float(getattr(detection, "confidence", 0.0) or 0.0)
        if conf < 0.65:
            return None

        from app.services.antifake_url_trust import analyze_url_signals

        reasons, sources = analyze_url_signals(url)
        matched = list(getattr(detection, "indicators_matched", None) or [])
        merged = ["phishing_agent_hit"] + [f"phish_ind:{m}" for m in matched[:3]]
        merged += [r for r in reasons if r not in ("url_looks_neutral",)]
        return _build_response(
            verdict="likely_fake",
            confidence=min(0.95, conf),
            reasons=merged[:8],
            sources=sources,
            source="real_agent",
            agent="phishing_protection_agent",
        )
    except Exception:
        return None


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
        elif len(cid) <= 4 or cid in ("900", "911", "112", "101", "102", "103", "104"):
            # RH-E03: short codes (900) + authority display name
            reasons.append("authority_label_short_code")
            score += 0.45
        elif len(cid) >= 10 and not cid.startswith(("7800", "8800", "7495")):
            reasons.append("authority_label_personal_number")
            score += 0.4

    if cid and dn and not dn_digits:
        if not any(label in dn_lower for label in GENERIC_CALLER_LABELS):
            if len(cid) >= 10 and any(label in dn_lower for label in AUTHORITY_SPOOF_LABELS):
                reasons.append("authority_name_non_service_number")
                score += 0.3
            elif len(cid) <= 4 and any(label in dn_lower for label in AUTHORITY_SPOOF_LABELS):
                reasons.append("authority_label_short_code")
                score += 0.45

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
        from app.services.antifake_audio_ensemble import ensemble_check_audio

        return ensemble_check_audio(
            media_type=media_type,
            file_name=file_name,
            file_bytes=file_bytes,
            extra=extra,
        )

    if media_type == "video":
        from app.services.antifake_video_ensemble import ensemble_check_video

        return ensemble_check_video(
            file_name=file_name,
            file_bytes=file_bytes,
            extra=extra,
        )

    # RH-D05: document worker-primary (local bytes analysis); SFM optional mirror
    if media_type == "document":
        return _check_document_primary(file_name=file_name, file_bytes=file_bytes, extra=extra)

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

    return _normalize_sfm_result(outcome, agent=agent, fallback_fn=fallback)


def _check_document_primary(
    *,
    file_name: str,
    file_bytes: bytes,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """RH-D02/D04/D05 + D03 provenance reasons."""
    extra = extra or {}
    from app.services.antifake_document_local import analyze_document_bytes
    from app.services.antifake_document_provenance import analyze_document_provenance

    local = analyze_document_bytes(file_bytes, file_name=file_name)
    base = _build_response(
        verdict=str(local.get("verdict") or "uncertain"),
        confidence=float(local.get("confidence") or 0.3),
        reasons=list(local.get("reasons") or ["document_local"]),
        source=str(local.get("source") or "local_ml"),
        agent=str(local.get("agent") or "fake_documents_local"),
    )

    prov = analyze_document_provenance(
        file_bytes,
        file_name=file_name,
        fake_score=float(base.get("confidence") or 0.0),
        verdict=str(base.get("verdict") or ""),
    )
    reasons = list(base.get("reasons") or [])
    # RH-D03: always surface provenance as reasons
    status = str(prov.get("status") or "")
    if status == "tampered":
        if "provenance_tampered" not in reasons:
            reasons.append("provenance_tampered")
        verdict = "likely_fake"
        confidence = max(float(base.get("confidence") or 0.0), 0.68)
    elif status == "missing":
        if "provenance_missing" not in reasons:
            reasons.append("provenance_missing")
        verdict = str(base.get("verdict") or "uncertain")
        confidence = float(base.get("confidence") or 0.0)
    elif status == "found":
        if "provenance_found" not in reasons:
            reasons.append("provenance_found")
        verdict = str(base.get("verdict") or "uncertain")
        confidence = float(base.get("confidence") or 0.0)
    else:
        verdict = str(base.get("verdict") or "uncertain")
        confidence = float(base.get("confidence") or 0.0)

    return _build_response(
        verdict=verdict,
        confidence=confidence,
        reasons=reasons[:8],
        sources=base.get("sources"),
        provenance=prov,
        source=str(base.get("source") or "local_ml"),
        agent=str(base.get("agent") or DOCUMENT_AGENT),
        job_id=base.get("job_id"),
        premium_required=bool(base.get("premium_required")),
    )
