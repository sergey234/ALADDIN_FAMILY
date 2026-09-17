"""T3-02 / afhub-p2-01 — audio/call ensemble: deepfake + probe + spoof + STT→text scam."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.services import antifake_service
from app.services.antifake_audio_stt import try_transcript
from app.services.antifake_ensemble_core import vote_ensemble_channels

_CHANNEL_SENTINEL = object()

AUDIO_MODEL_CARD: Dict[str, Any] = {
    "ensemble_version": "antifake_audio_v2",
    "channels": {
        "deepfake": {
            "agent": "audio_deepfake_local",
            "tier": "local_ml",
            "note": "FFT/heuristic v2 on worker; SFM mirror optional",
        },
        "probe": {"agent": "audio_probe", "tier": "heuristic"},
        "spoof": {"agent": "call_spoof", "tier": "metadata", "call_only": True},
        "stt_text": {
            "agent": "stt_text_scam",
            "tier": "stt+sms_rules",
            "language": "ru+en",
            "note": "STT → same SMS scam lexicon/intent (afhub-p2-01)",
        },
    },
}


def _deepfake_channel(
    *,
    media_type: str,
    file_name: str,
    file_bytes: bytes,
    extra: Dict[str, Any],
) -> Dict[str, Any]:
    # Primary path: local audio ML on the worker (always available; SFM often
    # rejects large file_bytes_b64 and previously returned stubs).
    try:
        from app.services.antifake_audio_deepfake_local import analyze_audio_bytes

        local = analyze_audio_bytes(file_bytes, file_name=file_name)
        return antifake_service._build_response(
            verdict=str(local.get("verdict") or "uncertain"),
            confidence=float(local.get("confidence") or 0.3),
            reasons=list(local.get("reasons") or ["local_audio_ml"]),
            source=str(local.get("source") or "local_audio_ml"),
            agent=str(local.get("agent") or "audio_deepfake_local"),
        )
    except Exception:
        pass

    agent = antifake_service.AUDIO_AGENT
    sfm_params: Dict[str, Any] = {
        "file_name": file_name,
        "size_bytes": len(file_bytes),
        "content_type": media_type,
        **antifake_service._media_bytes_payload(file_bytes, media_type),
        **extra,
    }
    outcome = antifake_service._sfm_execute(agent, sfm_params)

    def fallback() -> Dict[str, Any]:
        reasons = [f"{media_type}_agent_unavailable"]
        if len(file_bytes) == 0:
            reasons.append("empty_file")
        return antifake_service._build_response(
            verdict="uncertain",
            confidence=0.25,
            reasons=reasons,
            source="rule_engine",
            agent=f"heuristic_{media_type}",
        )

    if not outcome.get("success"):
        return fallback()
    result = antifake_service._normalize_sfm_result(
        outcome,
        agent=agent,
        fallback_fn=lambda: _CHANNEL_SENTINEL,
    )
    if result is _CHANNEL_SENTINEL:
        return fallback()
    return result


def _probe_channel(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    if not file_bytes:
        return None
    try:
        from app.security.ml_lazy_loader import probe_audio_bytes

        probe = probe_audio_bytes(file_bytes)
    except Exception:
        return None
    return antifake_service._build_response(
        verdict=str(probe.get("verdict") or "uncertain"),
        confidence=float(probe.get("confidence") or 0.0),
        reasons=list(probe.get("reasons") or []),
        source="audio_probe",
        agent="audio_probe",
    )


def _spoof_channel(media_type: str, extra: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if media_type != "call":
        return None
    caller = extra.get("caller_id")
    reasons, score = antifake_service._analyze_caller_spoof_heuristics(
        caller,
        extra.get("display_name"),
    )

    # Local scam directory first
    if caller:
        try:
            from app.services.antifake_call_directory_store import lookup_scam_number

            hit = lookup_scam_number(str(caller))
            if hit:
                reasons = ["scam_directory_hit"] + reasons
                score = max(score, float(hit["confidence"]) / 100.0)
        except Exception:
            pass
        # Secondary: ktozvonil (cache, 2s) — only on miss / low score
        if score < 0.72:
            try:
                from app.services.antifake_number_reputation import lookup_ktozvonil

                rep = lookup_ktozvonil(str(caller))
                if rep and rep.get("risky"):
                    reasons = ["ktozvonil_reputation"] + reasons
                    # Secondary signal — cap below auto-block certainty
                    score = max(score, 0.7)
            except Exception:
                pass

    if not reasons:
        return None
    return antifake_service._build_response(
        verdict=antifake_service._verdict_from_score(score),
        confidence=score,
        reasons=reasons[:8],
        source="rule_engine",
        agent="call_spoof",
    )


def _stt_text_channel(
    *,
    file_bytes: bytes,
    file_name: str,
    extra: Dict[str, Any],
) -> Dict[str, Any]:
    """Mandatory STT attempt → SMS text scam pipeline (shared lexicon).

    If STT missing: uncertain + stt_unavailable (never silent green alone).
    """
    transcript, lang = try_transcript(file_bytes, file_name=file_name, extra=extra)
    if not transcript:
        return antifake_service._build_response(
            verdict="uncertain",
            confidence=0.35,
            reasons=["stt_unavailable"],
            source="stt_text",
            agent="stt_text_scam",
        )

    # Same family SMS path as text hub (floors + intent + anti-green)
    try:
        text_result = antifake_service.check_text(transcript, mode="sms")
    except Exception:
        text_result = antifake_service._analyze_text_heuristic(transcript, mode="sms")

    if text_result.get("verdict") == "insufficient_data":
        return antifake_service._build_response(
            verdict="uncertain",
            confidence=0.3,
            reasons=["stt_transcript_too_short", f"stt_lang={lang}"],
            source="stt_text",
            agent="stt_text_scam",
        )

    reasons = [
        "stt_transcript_scam_check",
        f"stt_lang={lang}",
        f"transcript_len={len(transcript)}",
    ] + list(text_result.get("reasons") or [])
    return antifake_service._build_response(
        verdict=text_result.get("verdict") or "uncertain",
        confidence=float(text_result.get("confidence") or 0.0),
        reasons=reasons[:8],
        source="stt_text",
        agent="stt_text_scam",
    )


def ensemble_check_audio(
    *,
    media_type: str,
    file_name: str,
    file_bytes: bytes,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    extra = extra or {}
    channels: List[Tuple[str, Dict[str, Any]]] = [
        (
            "deepfake",
            _deepfake_channel(
                media_type=media_type,
                file_name=file_name,
                file_bytes=file_bytes,
                extra=extra,
            ),
        )
    ]

    probe = _probe_channel(file_bytes)
    if probe is not None:
        channels.append(("probe", probe))

    spoof = _spoof_channel(media_type, extra)
    if spoof is not None:
        channels.append(("spoof", spoof))

    stt = _stt_text_channel(file_bytes=file_bytes, file_name=file_name, extra=extra)
    channels.append(("stt_text", stt))

    voted = vote_ensemble_channels(
        channels,
        source="ensemble_audio",
        agent="ensemble_audio_v2",
        model_card=AUDIO_MODEL_CARD,
    )

    # afhub-p2-01: clear spoken scam → hard fake (same idea as SMS veto)
    if (
        stt.get("verdict") == "likely_fake"
        and float(stt.get("confidence") or 0) >= 0.72
    ):
        reasons = list(voted.get("reasons") or [])
        for r in stt.get("reasons") or []:
            tagged = f"stt_text:{r}"
            if tagged not in reasons:
                reasons.append(tagged)
        out = antifake_service._build_response(
            verdict="likely_fake",
            confidence=max(float(voted.get("confidence") or 0), float(stt.get("confidence") or 0)),
            reasons=reasons[:10],
            sources=voted.get("sources"),
            source="ensemble_audio",
            agent="ensemble_audio_v2",
        )
        out["model_card"] = AUDIO_MODEL_CARD
        return out

    # Never green authentic when STT found manipulation but vote went soft
    if stt.get("verdict") in ("likely_fake", "uncertain") and "stt_unavailable" not in (
        stt.get("reasons") or []
    ):
        from app.services.antifake_scam_lexicon import anti_green_verdict

        v, c = anti_green_verdict(
            str(voted.get("verdict") or "uncertain"),
            list(stt.get("reasons") or []) + list(voted.get("reasons") or []),
            float(voted.get("confidence") or 0),
        )
        if v != voted.get("verdict") or c > float(voted.get("confidence") or 0):
            voted = antifake_service._build_response(
                verdict=v,
                confidence=c,
                reasons=list(voted.get("reasons") or [])[:10],
                sources=voted.get("sources"),
                source=str(voted.get("source") or "ensemble_audio"),
                agent=str(voted.get("agent") or "ensemble_audio_v2"),
            )
            voted["model_card"] = AUDIO_MODEL_CARD

    return voted
