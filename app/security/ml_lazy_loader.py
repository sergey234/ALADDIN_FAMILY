"""B2-10 / af-1-03 — lazy heavy ML deps (torch, transformers, cv2) for worker paths only."""
from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

_lock = threading.Lock()
_torch: Any = None
_transformers: Any = None
_cv2: Any = None
_np: Any = None

_fake_news_agent: Any = None
_fake_documents_agent: Any = None


def get_torch() -> Any:
    global _torch
    if _torch is not None:
        return _torch
    with _lock:
        if _torch is None:
            import torch

            _torch = torch
            logger.info("ml_lazy_loader: torch loaded")
    return _torch


def get_transformers() -> Any:
    global _transformers
    if _transformers is not None:
        return _transformers
    with _lock:
        if _transformers is None:
            import transformers

            _transformers = transformers
            logger.info("ml_lazy_loader: transformers loaded")
    return _transformers


def get_cv2() -> Any:
    global _cv2
    if _cv2 is not None:
        return _cv2
    with _lock:
        if _cv2 is None:
            import cv2

            _cv2 = cv2
            logger.info("ml_lazy_loader: cv2 loaded")
    return _cv2


def get_numpy() -> Any:
    global _np
    if _np is not None:
        return _np
    with _lock:
        if _np is None:
            import numpy as np

            _np = np
            logger.info("ml_lazy_loader: numpy loaded")
    return _np


def warm_worker_deps(*, load_torch: bool = True, load_cv2: bool = True) -> dict[str, bool]:
    """Optional warm-up on worker start (not on API import)."""
    status: dict[str, bool] = {"torch": False, "transformers": False, "cv2": False}
    if load_torch:
        try:
            get_torch()
            get_transformers()
            status["torch"] = True
            status["transformers"] = True
        except ImportError as exc:
            logger.warning("warm_worker_deps torch/transformers skipped: %s", exc)
    if load_cv2:
        try:
            get_cv2()
            status["cv2"] = True
        except ImportError as exc:
            logger.warning("warm_worker_deps cv2 skipped: %s", exc)
    return status


def get_fake_news_agent():
    global _fake_news_agent
    if _fake_news_agent is not None:
        return _fake_news_agent
    with _lock:
        if _fake_news_agent is None:
            try:
                from app.security.ai_agents.fake_news_detection_agent import FakeNewsDetectionAgent
            except ImportError:
                from security.ai_agents.fake_news_detection_agent import FakeNewsDetectionAgent

            _fake_news_agent = FakeNewsDetectionAgent()
    return _fake_news_agent


def get_fake_documents_agent():
    global _fake_documents_agent
    if _fake_documents_agent is not None:
        return _fake_documents_agent
    with _lock:
        if _fake_documents_agent is None:
            from security.ai_agents.fake_documents_agent import FakeDocumentsAgent

            _fake_documents_agent = FakeDocumentsAgent()
    return _fake_documents_agent


def run_text_check(text: str, mode: str = "news") -> dict:
    agent = get_fake_news_agent()
    return agent.detect_fake_news(text, metadata={"mode": mode})


def run_document_check(image_path: str) -> dict:
    agent = get_fake_documents_agent()
    return agent.detect_fake_document(image_path)


MAX_VIDEO_PROBE_BYTES = 512 * 1024


def probe_audio_bytes(file_bytes: bytes) -> dict:
    """F-11: lightweight audio probe when SFM unavailable (worker path)."""
    if not file_bytes:
        return {
            "verdict": "uncertain",
            "confidence": 0.2,
            "reasons": ["empty_file"],
            "source": "audio_probe",
        }
    reasons: list[str] = []
    score = 0.25
    if len(file_bytes) < 512:
        reasons.append("audio_too_short")
        score = 0.35
    header = file_bytes[:12]
    if header[:4] == b"RIFF" and b"WAVE" in file_bytes[:16]:
        reasons.append("wav_container")
    elif file_bytes[:3] == b"ID3" or file_bytes[:2] == b"\xff\xfb":
        reasons.append("mp3_container")
    else:
        reasons.append("unknown_audio_container")
        score = max(score, 0.4)
    return {
        "verdict": "uncertain",
        "confidence": score,
        "reasons": reasons[:4],
        "source": "audio_probe",
    }


def probe_video_bytes(file_bytes: bytes) -> dict:
    """F-02: cv2 frame probe when available; honest uncertain otherwise."""
    if not file_bytes:
        return {
            "verdict": "uncertain",
            "confidence": 0.2,
            "reasons": ["empty_file"],
            "source": "video_probe",
        }
    reasons: list[str] = ["video_bytes_received"]
    score = 0.3
    try:
        cv2 = get_cv2()
        np = get_numpy()
        buf = np.frombuffer(file_bytes[: MAX_VIDEO_PROBE_BYTES], dtype=np.uint8)
        # JPEG/PNG magic — quick sanity; MP4 needs container parse
        if buf.size >= 3 and bytes(buf[:3]) == b"\xff\xd8\xff":
            reasons.append("jpeg_magic")
        arr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if arr is not None and arr.size > 0:
            h, w = arr.shape[:2]
            reasons.append(f"frame_decoded_{w}x{h}")
            gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
            blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            if blur < 35.0:
                reasons.append("low_detail_frame")
                score = max(score, 0.55)
            else:
                reasons.append("frame_detail_ok")
        else:
            reasons.append("cv2_no_frame")
    except ImportError:
        reasons.append("cv2_unavailable")
    except Exception:
        reasons.append("video_probe_error")
    # F-02: probe never returns likely_fake — hints only (full ML via worker/SFM).
    return {
        "verdict": "uncertain",
        "confidence": min(0.69, score),
        "reasons": reasons[:6],
        "source": "video_probe",
    }


def lazy_singleton(factory: Callable[[], T]) -> Callable[[], T]:
    """Thread-safe lazy singleton helper for worker-only agents."""
    holder: dict[str, Optional[T]] = {"value": None}

    def getter() -> T:
        if holder["value"] is None:
            with _lock:
                if holder["value"] is None:
                    holder["value"] = factory()
        return holder["value"]  # type: ignore[return-value]

    return getter
