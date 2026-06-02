# -*- coding: utf-8
"""Sleep wind-down audio catalog (p3-17)."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from security.services.ai_platform.wellness_i18n_loader import (
    _load_json,
    i18n_block_text,
    normalize_wellness_locale,
)

# Prod static path (nginx) — override via WELLNESS_SLEEP_CDN_BASE
_DEFAULT_SLEEP_BASE = "https://aladdin-ai.ru/static/wellness/sleep"


def sleep_audio_base_url() -> str:
    base = (os.environ.get("WELLNESS_SLEEP_CDN_BASE") or _DEFAULT_SLEEP_BASE).rstrip("/")
    return base


def _resolve_audio_url(raw: Any) -> str:
    url = str(raw or "").strip()
    if not url:
        return ""
    if "cdn.aladdin-ai.ru" in url:
        # Legacy placeholder host → active static on main domain
        path = url.split("/wellness/sleep/", 1)[-1]
        return f"{sleep_audio_base_url()}/{path}"
    return url


def list_sleep_stories(*, locale: str = "ru") -> List[Dict[str, Any]]:
    loc = normalize_wellness_locale(locale)
    try:
        data = _load_json("sleep_stories_v1.json")
        rows = data.get("stories") or []
    except (OSError, KeyError):
        return []
    out: List[Dict[str, Any]] = []
    for row in rows:
        audio = _resolve_audio_url(row.get("audio_url"))
        out.append(
            {
                "id": row.get("id"),
                "title": i18n_block_text(row.get("title"), loc),
                "duration_min": row.get("duration_min"),
                "audio_url": audio,
            }
        )
    return out
