# -*- coding: utf-8 -*-
"""P3-01 / P3-02 — Family-safe image/video generation stubs."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .feature_flags import IMAGE_GEN_ENABLED, VIDEO_GEN_ENABLED


def generate_companion_image(
    prompt: str,
    *,
    age_band: str,
    character_id: str = "unicorn",
) -> Dict[str, Any]:
    if not IMAGE_GEN_ENABLED:
        return {"ok": False, "error": "image_gen_disabled"}
    safe = (prompt or "")[:500]
    return {
        "ok": True,
        "status": "stub",
        "image_url": None,
        "message": "Image generation queued (family-safe filter applied).",
        "prompt_redacted": safe[:120],
        "character_id": character_id,
        "age_band": age_band,
    }


def generate_companion_video(
    prompt: str,
    *,
    age_band: str,
) -> Dict[str, Any]:
    if not VIDEO_GEN_ENABLED:
        return {"ok": False, "error": "video_gen_disabled"}
    return {
        "ok": True,
        "status": "stub",
        "video_url": None,
        "message": "Video generation not available in Family app MVP.",
        "age_band": age_band,
    }
