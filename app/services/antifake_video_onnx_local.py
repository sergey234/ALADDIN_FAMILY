"""RH-AG07 / afhub-p2-02 — light CPU video analysis (frames + ONNX).

ONNX/frame channel is ON by default (set ANTIFAKE_VIDEO_ONNX=0 to disable).
Without a model file / onnxruntime: honest frame heuristics (never the stub DPS class).
With models/antifake_video_onnx/model.onnx: onnxruntime CPU inference on sampled frames.
Face-quality gates block hard «likely_fake» on blurry / no-face frames.
Decode / AV1 failures → insufficient_data (never green likely_real).

Never imports the stub deepfake protection class.
"""
from __future__ import annotations

import logging
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# VPS-safe defaults (plan §3)
ONNX_MAX_BYTES = int(os.environ.get("ANTIFAKE_VIDEO_ONNX_MAX_BYTES", str(12 * 1024 * 1024)))
ONNX_MAX_FRAMES = int(os.environ.get("ANTIFAKE_VIDEO_ONNX_MAX_FRAMES", "12"))
ONNX_FRAME_SIZE = int(os.environ.get("ANTIFAKE_VIDEO_ONNX_FRAME_SIZE", "224"))
ONNX_TIMEOUT_SEC = float(os.environ.get("ANTIFAKE_VIDEO_ONNX_TIMEOUT_SEC", "90"))
ONNX_CONFIDENCE_CEILING = 0.88
# ViT ImageNet-style (deepfake_vs_real): mean/std 0.5 after /255
_ONNX_MEAN = (0.5, 0.5, 0.5)
_ONNX_STD = (0.5, 0.5, 0.5)
_FAKE_CLASS_INDEX = 1  # id2label: 0=Real, 1=Fake

_DEFAULT_MODEL = (
    Path(__file__).resolve().parents[2] / "models" / "antifake_video_onnx" / "model.onnx"
)
MODEL_PATH = Path(
    os.environ.get("ANTIFAKE_VIDEO_ONNX_MODEL_PATH", str(_DEFAULT_MODEL))
)

_onnx_lock = threading.Semaphore(1)
_session_lock = threading.Lock()
_ort_session = None


def video_onnx_enabled() -> bool:
    """afhub-p2-02 — ONNX/frame channel ON by default (set ANTIFAKE_VIDEO_ONNX=0 to disable)."""
    raw = os.environ.get("ANTIFAKE_VIDEO_ONNX", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def assess_face_quality(frames: List[Any]) -> Tuple[bool, List[str]]:
    """Face / subject quality gates (afhub-p2-02).

    Returns (ok_for_hard_fake, reasons). When not ok — do not claim near-certain
    deepfake from weak / muddy frames alone.
    """
    import numpy as np

    reasons: List[str] = []
    if not frames:
        return False, ["face_quality_no_frames"]

    face_boxes = 0
    blur_scores: List[float] = []
    try:
        import cv2

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(cascade_path)
        for f in frames[: min(6, len(frames))]:
            gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f
            blur_scores.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
            if cascade is not None and not cascade.empty():
                faces = cascade.detectMultiScale(gray, 1.1, 4, minSize=(24, 24))
                face_boxes += len(faces)
    except Exception:
        for f in frames[: min(6, len(frames))]:
            g = f.mean(axis=2) if getattr(f, "ndim", 0) == 3 else f
            blur_scores.append(float(np.var(g)))

    mean_blur = float(sum(blur_scores) / len(blur_scores)) if blur_scores else 0.0
    if mean_blur < 25.0:
        reasons.append("face_quality_blurry")
    if face_boxes == 0:
        reasons.append("face_not_detected")
    else:
        reasons.append(f"faces_detected_{face_boxes}")

    ok = face_boxes >= 1 and mean_blur >= 25.0
    if not ok and not reasons:
        reasons.append("face_quality_insufficient")
    return ok, reasons


def model_file_present() -> bool:
    try:
        # Ignore tiny placeholder (<1 MB); require real weights
        return MODEL_PATH.is_file() and MODEL_PATH.stat().st_size > 1_000_000
    except OSError:
        return False


def onnxruntime_available() -> bool:
    try:
        import onnxruntime  # noqa: F401

        return True
    except Exception:
        return False


def _get_ort_session():
    global _ort_session
    if not model_file_present() or not onnxruntime_available():
        return None
    with _session_lock:
        if _ort_session is not None:
            return _ort_session
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        # q4f16 community exports may break LayerNorm fusion on some ORT builds
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        _ort_session = ort.InferenceSession(
            str(MODEL_PATH),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        return _ort_session


def _looks_like_av1(file_bytes: bytes) -> bool:
    """True when MP4/ISOBMFF brands suggest AV1 (often fails on CPU OpenCV builds)."""
    head = file_bytes[: min(64 * 1024, len(file_bytes))]
    # ftyp brands / codec fourccs commonly seen with AV1 in Telegram exports
    markers = (b"av01", b"AV01", b"av1C", b"dav1")
    return any(m in head for m in markers)


def extract_frames_bgr(
    file_bytes: bytes,
    *,
    max_frames: int = ONNX_MAX_FRAMES,
    size: int = ONNX_FRAME_SIZE,
) -> Tuple[List[Any], List[str]]:
    """Decode video/image bytes → list of BGR uint8 arrays (H,W,3)."""
    reasons: List[str] = []
    if not file_bytes:
        return [], ["empty_file"]
    if len(file_bytes) > ONNX_MAX_BYTES:
        reasons.append("video_onnx_clip_truncated")
        file_bytes = file_bytes[:ONNX_MAX_BYTES]

    try:
        import cv2
        import numpy as np
    except Exception:
        return [], reasons + ["cv2_unavailable"]

    # JPEG masquerading as video — single frame
    if file_bytes[:3] == b"\xff\xd8\xff":
        arr = np.frombuffer(file_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return [], reasons + ["video_decode_failed"]
        img = cv2.resize(img, (size, size))
        reasons.append("jpeg_single_frame")
        return [img], reasons

    # G5: skip OpenCV decode for AV1 — CPU builds often hang/spam without frames
    if _looks_like_av1(file_bytes):
        return [], reasons + ["video_codec_av1_unsupported", "video_no_frames"]

    suffix = ".mp4"
    if file_bytes[:4] == b"RIFF":
        suffix = ".avi"
    path = None
    try:
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.write(fd, file_bytes)
        os.close(fd)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            fail = ["video_decode_failed"]
            if _looks_like_av1(file_bytes):
                fail.append("video_codec_av1_unsupported")
            return [], reasons + fail
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        frames: List[Any] = []
        if total <= 0:
            # read sequentially up to max_frames
            while len(frames) < max_frames:
                ok, frame = cap.read()
                if not ok:
                    break
                frames.append(cv2.resize(frame, (size, size)))
        else:
            step = max(1, total // max_frames)
            for i in range(0, total, step):
                if len(frames) >= max_frames:
                    break
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ok, frame = cap.read()
                if not ok:
                    continue
                frames.append(cv2.resize(frame, (size, size)))
        cap.release()
        if not frames:
            fail = ["video_no_frames"]
            if _looks_like_av1(file_bytes):
                fail.append("video_codec_av1_unsupported")
            return [], reasons + fail
        reasons.append(f"frames_sampled_{len(frames)}")
        return frames, reasons
    except Exception as exc:
        logger.debug("frame extract failed: %s", exc)
        fail = ["video_decode_failed"]
        if _looks_like_av1(file_bytes):
            fail.append("video_codec_av1_unsupported")
        return [], reasons + fail
    finally:
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


def _heuristic_score(frames: List[Any]) -> Tuple[float, List[str]]:
    """CPU-light signals when ONNX model missing or as soft prior."""
    import numpy as np

    reasons: List[str] = []
    if not frames:
        return 0.0, ["video_no_frames"]

    score = 0.15
    grays = [f.mean(axis=2) if f.ndim == 3 else f for f in frames]
    means = [float(g.mean()) for g in grays]
    vars_ = [float(g.var()) for g in grays]

    if max(vars_) < 40.0:
        reasons.append("video_frames_low_texture")
        score = max(score, 0.42)
    if len(means) >= 2:
        jumps = [abs(means[i] - means[i - 1]) for i in range(1, len(means))]
        if max(jumps) > 55:
            reasons.append("video_temporal_jump")
            score = max(score, 0.48)
        if max(jumps) < 1.5 and max(vars_) < 80:
            reasons.append("video_near_static")
            score = max(score, 0.36)

    # Extreme flat black/white (synthetic stub frames)
    if all(m < 8 for m in means) or all(m > 247 for m in means):
        reasons.append("video_frames_flat")
        score = max(score, 0.55)

    if not reasons:
        reasons.append("video_frames_heuristic_neutral")
    return min(0.72, score), reasons


def _preprocess_frame_nchw(frame_bgr: Any, size: int = 224) -> Any:
    """BGR uint8 HWC → float32 NCHW normalized for ViT deepfake classifier."""
    import cv2
    import numpy as np

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    rgb = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_LINEAR)
    x = rgb.astype("float32") / 255.0
    for c in range(3):
        x[:, :, c] = (x[:, :, c] - _ONNX_MEAN[c]) / _ONNX_STD[c]
    return np.transpose(x, (2, 0, 1))


def _onnx_score(frames: List[Any]) -> Tuple[Optional[float], List[str]]:
    session = _get_ort_session()
    if session is None:
        return None, ["video_onnx_model_missing"]

    import numpy as np

    try:
        inp = session.get_inputs()[0]
        name = inp.name
        size = ONNX_FRAME_SIZE
        shape = list(inp.shape)
        try:
            if len(shape) == 4 and shape[2] not in (None, "None") and str(shape[2]).isdigit():
                size = int(shape[2])
        except Exception:
            pass

        probs: List[float] = []
        for f in frames[: min(len(frames), ONNX_MAX_FRAMES)]:
            nchw = _preprocess_frame_nchw(f, size=size)
            x = nchw[None, ...].astype("float32")
            outs = session.run(None, {name: x})
            flat = np.asarray(outs[0], dtype="float32").reshape(-1)
            if flat.size >= 2:
                e = np.exp(flat - flat.max())
                fake_p = float((e / e.sum())[_FAKE_CLASS_INDEX])
            else:
                fake_p = float(1.0 / (1.0 + np.exp(-flat[0])))
            probs.append(fake_p)

        if not probs:
            return None, ["video_onnx_inference_failed"]
        prob = float(sum(probs) / len(probs))
        return min(ONNX_CONFIDENCE_CEILING, max(0.0, prob)), [
            "video_onnx_scored",
            f"video_onnx_frames_{len(probs)}",
        ]
    except Exception as exc:
        logger.warning("onnx inference failed: %s", exc)
        return None, ["video_onnx_inference_failed"]


def analyze_video_onnx_local(
    file_bytes: bytes,
    *,
    file_name: str = "upload.mp4",
) -> Dict[str, Any]:
    """
    Returns antifake-shaped dict: verdict, confidence, reasons, source, agent.
    """
    started = time.monotonic()
    reasons: List[str] = []

    if not file_bytes:
        return _resp("insufficient_data", 0.0, ["empty_file"], "rule_engine", "heuristic_video")

    if len(file_bytes) < 64:
        return _resp(
            "insufficient_data",
            0.1,
            ["video_too_small"],
            "rule_engine",
            "heuristic_video",
        )

    acquired = _onnx_lock.acquire(timeout=ONNX_TIMEOUT_SEC)
    if not acquired:
        return _resp(
            "uncertain",
            0.2,
            ["video_onnx_busy"],
            "local_video_ml",
            "video_onnx_local",
        )

    try:
        if time.monotonic() - started > ONNX_TIMEOUT_SEC:
            return _resp(
                "uncertain",
                0.2,
                ["video_onnx_timeout"],
                "local_video_ml",
                "video_onnx_local",
            )

        frames, fr_reasons = extract_frames_bgr(file_bytes)
        reasons.extend(fr_reasons)

        if not frames:
            # AV1 / decode fail — never green (afhub-p2-02 / G5)
            if "video_codec_av1_unsupported" in reasons or _looks_like_av1(file_bytes):
                if "video_codec_av1_unsupported" not in reasons:
                    reasons.append("video_codec_av1_unsupported")
            elif "video_decode_failed" not in reasons and "video_no_frames" not in reasons:
                reasons.append("video_decode_failed")
            return _resp(
                "insufficient_data",
                0.15,
                reasons or ["video_decode_failed"],
                "local_video_ml",
                "video_onnx_local",
            )

        h_score, h_reasons = _heuristic_score(frames)
        reasons.extend(h_reasons)

        face_ok, face_reasons = assess_face_quality(frames)
        reasons.extend(face_reasons)

        onnx_prob, o_reasons = _onnx_score(frames)
        reasons.extend(o_reasons)

        if onnx_prob is not None:
            score = min(ONNX_CONFIDENCE_CEILING, 0.45 * h_score + 0.55 * onnx_prob)
            source = "local_video_ml"
            agent = "video_onnx_local"
            reasons.append("video_onnx_active")
        else:
            score = min(0.72, h_score)
            source = "local_video_ml"
            agent = "video_frame_heuristic"
            if "video_onnx_model_missing" in o_reasons:
                reasons.append("video_onnx_fallback_heuristic")

        if time.monotonic() - started > ONNX_TIMEOUT_SEC:
            reasons.append("video_onnx_timeout")
            score = min(score, 0.35)

        verdict = _verdict_from_score(score)
        # JPEG-as-mp4: allow likely_fake from strong heuristic
        if "jpeg_single_frame" in reasons and "extension_container_mismatch" not in reasons:
            # ensemble metadata usually adds mismatch; bump slightly
            if file_name.lower().endswith((".mp4", ".mov", ".m4v")):
                reasons.append("jpeg_as_video_name")
                score = max(score, 0.62)
                verdict = _verdict_from_score(score)

        # Face-gates: muddy / no-face → never scream deepfake
        if verdict == "likely_fake" and not face_ok:
            reasons.append("face_quality_gate_blocked")
            verdict = "uncertain"
            score = min(score, 0.45)

        return _resp(verdict, score, reasons[:12], source, agent)
    finally:
        _onnx_lock.release()


def sfm_video_onnx_handler(**params: Any) -> Dict[str, Any]:
    """SFM mirror — same local path (optional wire after A3)."""
    raw_b64 = params.get("file_bytes_b64") or params.get("content_b64")
    file_name = str(params.get("file_name") or "upload.mp4")
    file_bytes = b""
    if isinstance(raw_b64, str) and raw_b64:
        import base64

        try:
            file_bytes = base64.b64decode(raw_b64)
        except Exception:
            return {
                "status": "error",
                "function_id": "video_onnx_local",
                "message": "invalid_b64",
            }
    elif isinstance(params.get("file_bytes"), (bytes, bytearray)):
        file_bytes = bytes(params["file_bytes"])

    result = analyze_video_onnx_local(file_bytes, file_name=file_name)
    return {
        "status": "ok",
        "verdict": result.get("verdict"),
        "confidence": result.get("confidence"),
        "fake_risk": result.get("fake_risk"),
        "reasons": result.get("reasons"),
        "source": result.get("source"),
        "agent": result.get("agent"),
    }


def _verdict_from_score(score: float) -> str:
    if score >= 0.65:
        return "likely_fake"
    if score >= 0.35:
        return "uncertain"
    if score <= 0.0:
        return "insufficient_data"
    return "likely_real"


def _resp(
    verdict: str,
    confidence: float,
    reasons: List[str],
    source: str,
    agent: str,
) -> Dict[str, Any]:
    conf = float(min(ONNX_CONFIDENCE_CEILING, max(0.0, confidence)))
    return {
        "verdict": verdict,
        "confidence": conf,
        "fake_risk": conf if verdict == "likely_fake" else conf * 0.5,
        "reasons": list(reasons)[:10],
        "source": source,
        "agent": agent,
        "job_id": None,
        "premium_required": False,
        "model_version": "antifake-video-onnx-v1",
    }
