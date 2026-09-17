"""T3-03 — video ensemble: local deepfake + metadata + probe + optional ONNX (AG07)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.services import antifake_service
from app.services.antifake_ensemble_core import vote_ensemble_channels
from app.services.antifake_video_metadata import analyze_video_metadata

_CHANNEL_SENTINEL = object()
_PROBE_MAX_CONF = 0.69
# RH-F04: without face-swap NN, never claim near-certain deepfake
_VIDEO_DEEPFAKE_CEILING = 0.78
# AG07: with ONNX channel active, slightly higher but never 1.0
_VIDEO_ONNX_CEILING = 0.88

VIDEO_MODEL_CARD: Dict[str, Any] = {
    "ensemble_version": "antifake_video_v2",
    "channels": {
        "deepfake": {
            "agent": "video_deepfake_local",
            "tier": "local_ml",
            "note": "Container/metadata (+ cv2 when available); DeepfakeProtectionSystem OFF",
            "confidence_ceiling": _VIDEO_DEEPFAKE_CEILING,
        },
        "onnx": {
            "agent": "video_onnx_local",
            "tier": "local_ml",
            "note": "ON by default (afhub-p2-02); ANTIFAKE_VIDEO_ONNX=0 to disable; face gates + AV1 UX",
            "confidence_ceiling": _VIDEO_ONNX_CEILING,
            "flag": "ANTIFAKE_VIDEO_ONNX",
            "default": "on",
        },
        "metadata": {"agent": "video_metadata", "tier": "container"},
        "probe": {"agent": "video_probe", "tier": "heuristic", "never_likely_fake": True},
    },
}


def _active_video_ceiling() -> float:
    try:
        from app.services.antifake_video_onnx_local import video_onnx_enabled

        if video_onnx_enabled():
            return _VIDEO_ONNX_CEILING
    except Exception:
        pass
    return _VIDEO_DEEPFAKE_CEILING


def _deepfake_channel(
    *,
    file_name: str,
    file_bytes: bytes,
    extra: Dict[str, Any],
) -> Dict[str, Any]:
    # RH-F01/F02: local metadata only — never call DPS / audio-bound video SFM IDs
    try:
        reasons, score = analyze_video_metadata(file_bytes, file_name=file_name, extra=extra)
        score = min(score, _VIDEO_DEEPFAKE_CEILING)
        local_verdict = antifake_service._verdict_from_score(score)
        if local_verdict == "likely_fake" and score < 0.65:
            local_verdict = "uncertain"
        return antifake_service._build_response(
            verdict=local_verdict,
            confidence=score,
            reasons=list(reasons) or ["video_metadata_neutral"],
            source="local_video_ml",
            agent="video_deepfake_local",
        )
    except Exception:
        pass

    reasons = ["video_agent_unavailable"]
    if len(file_bytes) == 0:
        reasons.append("empty_file")
    return antifake_service._build_response(
        verdict="uncertain",
        confidence=0.25,
        reasons=reasons,
        source="rule_engine",
        agent="heuristic_video",
    )


def _metadata_channel(
    *,
    file_bytes: bytes,
    file_name: str,
    extra: Dict[str, Any],
) -> Dict[str, Any]:
    reasons, score = analyze_video_metadata(file_bytes, file_name=file_name, extra=extra)
    verdict = antifake_service._verdict_from_score(score)
    if verdict == "likely_fake" and score < 0.65:
        verdict = "uncertain"
    return antifake_service._build_response(
        verdict=verdict,
        confidence=score,
        reasons=reasons,
        source="video_metadata",
        agent="video_metadata",
    )


def _probe_channel(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    if not file_bytes:
        return None
    try:
        from app.security.ml_lazy_loader import probe_video_bytes

        probe = probe_video_bytes(file_bytes)
    except Exception:
        return None
    conf = min(_PROBE_MAX_CONF, float(probe.get("confidence") or 0.0))
    reasons = list(probe.get("reasons") or [])
    # Informational probe must NOT vote "uncertain" and override ONNX/metadata
    # (that produced "Неясно · 30%" for ordinary real clips).
    _suspicious_markers = {
        "jpeg_magic",
        "video_too_small",
        "low_detail_frame",
        "extension_container_mismatch",
        "jpeg_as_video_name",
        "jpeg_not_video_container",
    }
    suspicious = any(
        str(r) in _suspicious_markers or str(r).startswith("jpeg_") for r in reasons
    )
    verdict = "uncertain" if suspicious else "insufficient_data"
    return antifake_service._build_response(
        verdict=verdict,
        confidence=conf if suspicious else min(conf, 0.2),
        reasons=reasons,
        source="video_probe",
        agent="video_probe",
    )


def _onnx_channel(
    *,
    file_name: str,
    file_bytes: bytes,
) -> Optional[Dict[str, Any]]:
    try:
        from app.services.antifake_video_onnx_local import (
            analyze_video_onnx_local,
            video_onnx_enabled,
        )
    except Exception:
        return None
    if not video_onnx_enabled():
        return None
    try:
        return analyze_video_onnx_local(file_bytes, file_name=file_name)
    except Exception:
        return antifake_service._build_response(
            verdict="uncertain",
            confidence=0.2,
            reasons=["video_onnx_channel_error"],
            source="local_video_ml",
            agent="video_onnx_local",
        )


def _finalize_video_verdict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """F-02 / RH-F04: probe-only must not emit likely_fake; cap confidence without NN."""
    sources = payload.get("sources") or []
    channels = {str(row.get("channel")) for row in sources if isinstance(row, dict)}
    payload = dict(payload)
    ceiling = _active_video_ceiling()
    conf = float(payload.get("confidence") or 0.0)
    if conf > ceiling:
        payload["confidence"] = ceiling
        reasons = list(payload.get("reasons") or [])
        cap_reason = (
            "video_confidence_capped"
            if ceiling >= _VIDEO_ONNX_CEILING - 0.01
            else "video_confidence_capped_no_nn"
        )
        if cap_reason not in reasons:
            reasons.append(cap_reason)
        payload["reasons"] = reasons[:8]

    onnx_row = next(
        (row for row in sources if isinstance(row, dict) and row.get("channel") == "onnx"),
        None,
    )
    any_fake = any(
        isinstance(row, dict)
        and row.get("channel") in ("deepfake", "onnx", "metadata")
        and row.get("verdict") == "likely_fake"
        for row in sources
    )
    reasons_all = [str(r) for r in (payload.get("reasons") or [])]
    onnx_scored = any("video_onnx_scored" in r for r in reasons_all)

    # G5 / afhub-p2-02: AV1 always insufficient; other decode fails never green
    if any("video_codec_av1_unsupported" in r for r in reasons_all):
        payload["verdict"] = "insufficient_data"
        payload["confidence"] = min(float(payload.get("confidence") or 0.15), 0.2)
        return payload
    if payload.get("verdict") == "likely_real" and any(
        any(m in r for m in ("video_decode_failed", "video_no_frames", "cv2_unavailable", "empty_file", "video_too_small"))
        for r in reasons_all
    ):
        payload["verdict"] = "insufficient_data"
        payload["confidence"] = min(float(payload.get("confidence") or 0.15), 0.2)
        return payload

    # Plain-language path: ONNX says ordinary / likely_real and nobody says fake
    if (
        not any_fake
        and onnx_row
        and onnx_scored
        and str(onnx_row.get("verdict")) == "likely_real"
    ):
        payload["verdict"] = "likely_real"
        onnx_conf = float(onnx_row.get("confidence") or 0.4)
        payload["confidence"] = min(ceiling, max(onnx_conf, 0.4), 0.72)
        reasons = list(payload.get("reasons") or [])
        if "video_no_face_swap_signs" not in reasons:
            reasons.insert(0, "video_no_face_swap_signs")
        payload["reasons"] = reasons[:8]
        return payload

    if payload.get("verdict") != "likely_fake":
        return payload
    deepfake_fake = any(
        isinstance(row, dict)
        and row.get("channel") in ("deepfake", "onnx")
        and row.get("verdict") == "likely_fake"
        for row in sources
    )
    if deepfake_fake:
        return payload
    payload["verdict"] = "uncertain"
    payload["confidence"] = min(float(payload.get("confidence") or 0.0), _PROBE_MAX_CONF)
    reasons = list(payload.get("reasons") or [])
    if "probe_blocked_likely_fake" not in reasons:
        reasons.append("probe_blocked_likely_fake")
    payload["reasons"] = reasons[:8]
    if "probe" in channels and "deepfake" not in channels and "onnx" not in channels:
        payload["confidence"] = min(float(payload.get("confidence") or 0.0), 0.45)
    return payload


def ensemble_check_video(
    *,
    file_name: str,
    file_bytes: bytes,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    extra = extra or {}
    channels: List[Tuple[str, Dict[str, Any]]] = [
        (
            "deepfake",
            _deepfake_channel(file_name=file_name, file_bytes=file_bytes, extra=extra),
        ),
        (
            "metadata",
            _metadata_channel(file_bytes=file_bytes, file_name=file_name, extra=extra),
        ),
    ]
    onnx = _onnx_channel(file_name=file_name, file_bytes=file_bytes)
    if onnx is not None:
        o_reasons = [str(r) for r in (onnx.get("reasons") or [])]
        if any("video_codec_av1_unsupported" in r for r in o_reasons):
            # G5: do not let metadata "likely_real" hide unreadable AV1
            return antifake_service._build_response(
                verdict="insufficient_data",
                confidence=0.15,
                reasons=o_reasons[:8],
                source="ensemble_video",
                agent="ensemble_video_v2",
                sources=[{"channel": "onnx", "verdict": "insufficient_data", "confidence": 0.15}],
            )
        channels.append(("onnx", onnx))
    probe = _probe_channel(file_bytes)
    if probe is not None:
        channels.append(("probe", probe))

    result = vote_ensemble_channels(
        channels,
        source="ensemble_video",
        agent="ensemble_video_v2",
        model_card=VIDEO_MODEL_CARD,
    )
    return _finalize_video_verdict(result)
