"""Local audio deepfake / synthetic-voice heuristics (numpy FFT).

Used when SFM agent has no real handler or returns a stub. Honest signals only —
never claims 100% deepfake; returns likely_fake / uncertain / likely_real.
"""
from __future__ import annotations

import io
import struct
import wave
from typing import Any, Dict, List, Optional, Tuple


def _pcm_from_wav(file_bytes: bytes) -> Optional[Tuple[List[float], int]]:
    try:
        with wave.open(io.BytesIO(file_bytes), "rb") as wf:
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            rate = wf.getframerate()
            n = wf.getnframes()
            raw = wf.readframes(n)
    except Exception:
        return None
    if width != 2 or rate < 8000 or not raw:
        return None
    samples = list(struct.unpack("<" + "h" * (len(raw) // 2), raw))
    if channels > 1:
        samples = samples[::channels]
    if len(samples) < rate // 4:
        return None
    # normalize to [-1, 1]
    pcm = [s / 32768.0 for s in samples]
    return pcm, rate


def _pcm_from_mp3_header_skip(file_bytes: bytes) -> Optional[Tuple[List[float], int]]:
    """Best-effort: if torchaudio unavailable, refuse mp3 decode (caller uses probe)."""
    return None


def _load_pcm(file_bytes: bytes) -> Optional[Tuple[List[float], int]]:
    if not file_bytes:
        return None
    if file_bytes[:4] == b"RIFF" and b"WAVE" in file_bytes[:16]:
        return _pcm_from_wav(file_bytes)
    # try numpy+torch as last resort for other containers
    try:
        import numpy as np
        import torch
        import torchaudio  # type: ignore

        tensor, rate = torchaudio.load(io.BytesIO(file_bytes))
        mono = tensor.mean(dim=0).numpy().astype(np.float32)
        if mono.size < int(rate) // 4:
            return None
        return mono.tolist(), int(rate)
    except Exception:
        return _pcm_from_mp3_header_skip(file_bytes)


def analyze_audio_bytes(file_bytes: bytes, *, file_name: str = "") -> Dict[str, Any]:
    """Return antifake-shaped verdict for voice / call recordings."""
    reasons: List[str] = []
    loaded = _load_pcm(file_bytes)
    if loaded is None:
        # container-only fallback
        if file_bytes[:4] == b"RIFF":
            reasons.append("wav_container")
        elif file_bytes[:3] == b"ID3" or file_bytes[:2] == b"\xff\xfb":
            reasons.append("mp3_container_undecoded")
        else:
            reasons.append("audio_decode_failed")
        return {
            "verdict": "uncertain",
            "confidence": 0.35,
            "reasons": reasons[:6],
            "source": "local_audio_ml",
            "agent": "audio_deepfake_local",
        }

    pcm, rate = loaded
    try:
        import numpy as np
    except ImportError:
        return {
            "verdict": "uncertain",
            "confidence": 0.3,
            "reasons": ["numpy_unavailable"],
            "source": "local_audio_ml",
            "agent": "audio_deepfake_local",
        }

    x = np.asarray(pcm, dtype=np.float32)
    # trim silence edges
    abs_x = np.abs(x)
    thr = max(0.01, float(np.percentile(abs_x, 20)))
    mask = abs_x > thr
    if mask.any():
        idx = np.where(mask)[0]
        x = x[idx[0] : idx[-1] + 1]
    if x.size < rate // 5:
        return {
            "verdict": "insufficient_data",
            "confidence": 0.0,
            "reasons": ["audio_too_short"],
            "source": "local_audio_ml",
            "agent": "audio_deepfake_local",
        }

    # frame features
    frame = max(256, int(rate * 0.025))
    hop = max(128, frame // 2)
    zcr_list = []
    rms_list = []
    flat_list = []
    for start in range(0, x.size - frame, hop):
        seg = x[start : start + frame]
        # zero-crossing rate
        zcr = float(np.mean(np.abs(np.diff(np.signbit(seg)))))
        zcr_list.append(zcr)
        rms = float(np.sqrt(np.mean(seg * seg) + 1e-12))
        rms_list.append(rms)
        # spectral flatness
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) + 1e-12
        geo = float(np.exp(np.mean(np.log(spec))))
        arith = float(np.mean(spec))
        flat_list.append(geo / arith)

    zcr = float(np.mean(zcr_list)) if zcr_list else 0.0
    rms_std = float(np.std(rms_list)) if rms_list else 0.0
    rms_mean = float(np.mean(rms_list)) if rms_list else 0.0
    flat = float(np.mean(flat_list)) if flat_list else 0.0
    # pitch-ish regularity via autocorrelation peak strength
    # downsample for speed
    step = max(1, rate // 8000)
    xd = x[::step]
    if xd.size > 4000:
        xd = xd[:4000]
    corr = np.correlate(xd, xd, mode="full")
    corr = corr[corr.size // 2 :]
    corr = corr / (corr[0] + 1e-12)
    # ignore lag 0..~2ms
    min_lag = max(2, int(0.002 * rate / step))
    peak = float(np.max(corr[min_lag : min_lag + int(0.02 * rate / step) + 1])) if corr.size > min_lag + 5 else 0.0

    score = 0.22
    # synthetic / TTS often: high spectral flatness, very steady RMS, strong periodic pitch
    if flat > 0.42:
        reasons.append("high_spectral_flatness")
        score += 0.24
    if rms_mean > 0.02 and rms_std / (rms_mean + 1e-6) < 0.28:
        reasons.append("overly_steady_energy")
        score += 0.20
    if peak > 0.52:
        reasons.append("strong_periodic_pitch")
        score += 0.18
    if zcr < 0.025:
        reasons.append("unnaturally_low_zcr")
        score += 0.14
    if zcr > 0.35:
        reasons.append("noisy_or_artifacts")
        score += 0.08

    # afhub-p2-01 — clipping / hard limiter (common in synthetic renders)
    peak_abs = float(np.max(np.abs(x)))
    clip_ratio = float(np.mean(np.abs(x) > 0.98)) if x.size else 0.0
    if clip_ratio > 0.02:
        reasons.append("clipping_artifacts")
        score += 0.14
    # Mid-band concentration (telephone TTS often 300–3400 Hz heavy)
    try:
        n_fft = min(4096, int(2 ** np.floor(np.log2(max(256, x.size)))))
        spec_full = np.abs(np.fft.rfft(x[:n_fft] * np.hanning(n_fft))) + 1e-12
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / rate)
        mid = (freqs >= 300) & (freqs <= 3400)
        hi = freqs > 5000
        mid_e = float(np.sum(spec_full[mid] ** 2))
        hi_e = float(np.sum(spec_full[hi] ** 2)) + 1e-12
        if mid_e / hi_e > 40 and flat > 0.3:
            reasons.append("narrowband_synthetic_profile")
            score += 0.16
    except Exception:
        pass

    # natural speech markers lower score
    if 0.05 < zcr < 0.25 and 0.3 < (rms_std / (rms_mean + 1e-6)) < 1.8 and flat < 0.35:
        reasons.append("natural_voice_features")
        score = max(0.12, score - 0.18)

    score = float(min(0.94, max(0.08, score)))
    if score >= 0.62:
        verdict = "likely_fake"
        if "synthetic_voice" not in reasons:
            reasons.insert(0, "synthetic_voice")
    elif score >= 0.35:
        verdict = "uncertain"
    else:
        verdict = "likely_real"

    if not reasons:
        reasons.append("local_ml_analysis")

    return {
        "verdict": verdict,
        "confidence": round(score, 3),
        "reasons": reasons[:8],
        "source": "local_audio_ml",
        "agent": "audio_deepfake_local",
        "features": {
            "zcr": round(zcr, 4),
            "spectral_flatness": round(flat, 4),
            "rms_cv": round(rms_std / (rms_mean + 1e-6), 4),
            "pitch_peak": round(peak, 4),
            "rate": rate,
            "seconds": round(len(pcm) / rate, 2),
            "file_name": file_name[:80],
        },
    }


def sfm_audio_deepfake_handler(**params: Any) -> Dict[str, Any]:
    """SFM-compatible handler for function_id audio_deepfake_detection."""
    import base64

    file_bytes = b""
    for key in ("file_bytes_b64", "file_b64", "content_b64", "audio_b64"):
        b64 = params.get(key)
        if isinstance(b64, str) and b64:
            try:
                file_bytes = base64.b64decode(b64, validate=False)
                break
            except Exception:
                file_bytes = b""
    raw = params.get("file_bytes")
    if isinstance(raw, (bytes, bytearray)) and raw:
        file_bytes = bytes(raw)

    analysis = analyze_audio_bytes(file_bytes, file_name=str(params.get("file_name") or ""))
    return {
        "status": "success",
        "verdict": analysis["verdict"],
        "confidence": analysis["confidence"],
        "reasons": analysis["reasons"],
        "source": analysis["source"],
        "agent": analysis["agent"],
        "features": analysis.get("features"),
    }
