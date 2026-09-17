"""Shared ensemble voting for antifake text/audio channels."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.services import antifake_service
from app.services.antifake_calibration import aggregate_verdict


def _is_zero_weight_channel(payload: Dict[str, Any]) -> bool:
    """RH-X01: stub / empty SFM echo must not lift ensemble confidence."""
    reasons = [str(r) for r in (payload.get("reasons") or [])]
    if "sfm_executed_stub" in reasons:
        return True
    if reasons == ["sfm_agent"]:
        return True
    source = str(payload.get("source") or "")
    if source in antifake_service.FORBIDDEN_SOURCES:
        return True
    agent = str(payload.get("agent") or "")
    if agent.endswith("_stub") or agent == "sfm_stub":
        return True
    return False


def _ensemble_confidence(verdict: str, signals: List[Dict[str, Any]]) -> float:
    matching = [
        float(sig.get("confidence") or 0.0)
        for sig in signals
        if sig.get("verdict") == verdict
    ]
    if matching:
        return max(matching)
    all_conf = [float(sig.get("confidence") or 0.0) for sig in signals]
    if not all_conf:
        return 0.0
    peak = max(all_conf)
    if verdict == "uncertain":
        return min(peak, 0.55)
    if verdict == "likely_real":
        return min(peak, 0.45)
    return peak


def vote_ensemble_channels(
    channels: List[Tuple[str, Dict[str, Any]]],
    *,
    source: str,
    agent: str,
    model_card: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not channels:
        payload = antifake_service._build_response(
            verdict="insufficient_data",
            confidence=0.0,
            reasons=["no_signals"],
            source=source,
            agent=agent,
        )
        if model_card:
            payload["model_card"] = model_card
        return payload

    active = [
        (name, payload)
        for name, payload in channels
        if payload.get("verdict") != "insufficient_data"
        and not _is_zero_weight_channel(payload)
    ]
    if not active:
        name, only = channels[0]
        payload = antifake_service._build_response(
            verdict="insufficient_data",
            confidence=float(only.get("confidence") or 0.0),
            reasons=[f"{name}:{r}" for r in (only.get("reasons") or ["insufficient_data"])][:8],
            source=source,
            agent=agent,
            sources=[{"channel": name, **{k: only.get(k) for k in ("verdict", "confidence", "source")}}],
        )
        if model_card:
            payload["model_card"] = model_card
        return payload

    payloads = [payload for _, payload in active]
    verdicts = [str(p.get("verdict") or "uncertain") for p in payloads]
    final_verdict = aggregate_verdict(verdicts)

    fake_votes = sum(1 for p in payloads if p.get("verdict") == "likely_fake")
    if fake_votes >= 2:
        final_verdict = "likely_fake"

    confidence = _ensemble_confidence(final_verdict, payloads)
    if final_verdict == "likely_fake" and fake_votes >= 2:
        fake_conf = [
            float(p.get("confidence") or 0.0)
            for p in payloads
            if p.get("verdict") == "likely_fake"
        ]
        if fake_conf:
            confidence = max(confidence, max(fake_conf))

    reasons: List[str] = []
    channel_meta: List[Dict[str, Any]] = []
    active_names = {name for name, _ in active}
    for name, payload in active:
        channel_meta.append(
            {
                "channel": name,
                "verdict": payload.get("verdict"),
                "confidence": payload.get("confidence"),
                "source": payload.get("source"),
                "agent": payload.get("agent"),
            }
        )
        for reason in payload.get("reasons") or []:
            tagged = f"{name}:{reason}"
            if tagged not in reasons:
                reasons.append(tagged)

    # afhub-p2-02: keep insufficient_data channels visible in sources (no vote weight)
    # so UI/finalize still see ONNX AV1/decode reasons.
    for name, payload in channels:
        if name in active_names or _is_zero_weight_channel(payload):
            continue
        channel_meta.append(
            {
                "channel": name,
                "verdict": payload.get("verdict"),
                "confidence": payload.get("confidence"),
                "source": payload.get("source"),
                "agent": payload.get("agent"),
            }
        )
        for reason in payload.get("reasons") or []:
            tagged = f"{name}:{reason}"
            if tagged not in reasons:
                reasons.append(tagged)

    result = antifake_service._build_response(
        verdict=final_verdict,
        confidence=confidence,
        reasons=reasons[:12] or ["ensemble_vote"],
        source=source,
        agent=agent,
        sources=channel_meta,
    )
    if model_card:
        result["model_card"] = model_card
    return result
