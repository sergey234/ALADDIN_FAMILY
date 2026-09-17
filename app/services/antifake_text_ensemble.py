"""T3-01 — text ensemble: SFM + embedded URL checks + rules → vote."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from app.services import antifake_service
from app.services.antifake_calibration import aggregate_verdict
from app.services.antifake_ensemble_core import vote_ensemble_channels

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_CHANNEL_SENTINEL = object()

TEXT_MODEL_CARD: Dict[str, Any] = {
    "ensemble_version": "antifake_text_v1",
    "channels": {
        "rules": {"agent": "heuristic_text", "tier": "heuristic", "primary_for": ["sms"]},
        "sfm": {
            "agent": "fake_news_detection_agent",
            "tier": "soft_ml",
            "note": "toxic-bert soft signal; sms rules not vetoed by likely_real",
        },
        "url": {"agent": "ensemble_url", "tier": "embedded_url_check"},
    },
}


def _extract_urls(text: str) -> List[str]:
    urls: List[str] = []
    for match in _URL_RE.finditer(text or ""):
        cleaned = match.group(0).rstrip(".,);]»\"'")
        if cleaned and cleaned not in urls:
            urls.append(cleaned)
    return urls[:3]


def _rules_channel(text: str, mode: str) -> Dict[str, Any]:
    heuristic = antifake_service._analyze_text_heuristic(text, mode)
    # RH-B02/B04: for SMS, heuristic RU scam pack is primary — do not let
    # local_ml "too_short" insufficient_data replace a strong scam hit.
    if mode == "sms" and heuristic.get("verdict") == "likely_fake":
        return heuristic
    local = antifake_service._try_local_ml_text(text, mode)
    if local is not None:
        if mode == "sms" and local.get("verdict") == "insufficient_data":
            return heuristic
        return antifake_service._merge_local_with_heuristic(local, heuristic)
    return heuristic


def _sfm_channel(text: str, mode: str) -> Optional[Dict[str, Any]]:
    outcome = antifake_service._sfm_execute(
        antifake_service.TEXT_AGENT,
        {"text": text, "mode": mode},
    )
    if not outcome.get("success"):
        return None
    result = antifake_service._normalize_sfm_result(
        outcome,
        agent=antifake_service.TEXT_AGENT,
        fallback_fn=lambda: _CHANNEL_SENTINEL,
    )
    if result is _CHANNEL_SENTINEL:
        return None
    return result


def _url_channel(text: str) -> Optional[Dict[str, Any]]:
    urls = _extract_urls(text)
    if not urls:
        return None
    results: List[Dict[str, Any]] = []
    for url in urls:
        try:
            results.append(antifake_service.check_url(url))
        except Exception:
            continue
    if not results:
        return None
    verdicts = [str(r.get("verdict") or "uncertain") for r in results]
    agg_verdict = aggregate_verdict(verdicts)
    conf = max(float(r.get("confidence") or 0.0) for r in results)
    reasons: List[str] = []
    for r in results:
        for reason in r.get("reasons") or []:
            tagged = f"url:{reason}"
            if tagged not in reasons:
                reasons.append(tagged)
    return antifake_service._build_response(
        verdict=agg_verdict,
        confidence=conf,
        reasons=reasons[:8] or ["embedded_url_check"],
        source="rule_engine",
        agent="ensemble_url",
    )


def ensemble_check_text(text: str, mode: str = "news") -> Dict[str, Any]:
    mode_norm = (mode or "news").strip().lower() or "news"
    rules = _rules_channel(text, mode_norm)
    channels: List[Tuple[str, Dict[str, Any]]] = [("rules", rules)]

    # RH-B02: toxic-bert / SFM must not veto RU SMS scam rules
    sfm = _sfm_channel(text, mode_norm)
    if sfm is not None:
        if mode_norm == "sms" and rules.get("verdict") == "likely_fake":
            if sfm.get("verdict") == "likely_fake":
                channels.append(("sfm", sfm))
            # else: soft-skip SFM likely_real on scam SMS
        else:
            channels.append(("sfm", sfm))

    url_sig = _url_channel(text)
    if url_sig is not None:
        channels.append(("url", url_sig))

    result = vote_ensemble_channels(
        channels,
        source="ensemble_text",
        agent="ensemble_text_v1",
        model_card=TEXT_MODEL_CARD,
    )
    # afhub-p0-03: never green authentic when scam manipulation reasons present
    from app.services.antifake_scam_lexicon import anti_green_verdict

    v, c = anti_green_verdict(
        str(result.get("verdict") or "uncertain"),
        list(result.get("reasons") or []),
        float(result.get("confidence") or 0.0),
    )
    if v != result.get("verdict") or abs(c - float(result.get("confidence") or 0)) > 1e-6:
        result = antifake_service._build_response(
            verdict=v,
            confidence=c,
            reasons=list(result.get("reasons") or [])[:8],
            source="ensemble_text",
            agent="ensemble_text_v1",
            sources=result.get("sources"),
        )
        if TEXT_MODEL_CARD:
            result["model_card"] = TEXT_MODEL_CARD

    if mode_norm == "sms" and rules.get("verdict") == "likely_fake":
        if result.get("verdict") != "likely_fake":
            return antifake_service._build_response(
                verdict="likely_fake",
                confidence=max(
                    float(rules.get("confidence") or 0.0),
                    float(result.get("confidence") or 0.0),
                ),
                reasons=list(rules.get("reasons") or [])[:8],
                source="ensemble_text",
                agent="ensemble_text_v1",
                sources=result.get("sources"),
            )
    return result
