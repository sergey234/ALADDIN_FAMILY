# -*- coding: utf-8
"""Seasonal wellness playbooks — school / exams (p3-14)."""

from __future__ import annotations

from typing import Any, Dict, List

from security.services.ai_platform.wellness_i18n_loader import (
    _load_json,
    i18n_block_text,
    normalize_wellness_locale,
)


def list_seasonal_playbooks(*, locale: str = "ru") -> List[Dict[str, Any]]:
    loc = normalize_wellness_locale(locale)
    try:
        data = _load_json("seasonal_playbooks_v1.json")
        books = data.get("playbooks") or {}
    except (OSError, KeyError):
        return []
    out: List[Dict[str, Any]] = []
    for key, block in books.items():
        tips = []
        for tip in block.get("tips") or []:
            tips.append(
                {
                    "id": tip.get("id"),
                    "text": i18n_block_text(tip.get("text"), loc),
                }
            )
        out.append(
            {
                "id": key,
                "title_key": block.get("title_key"),
                "title": i18n_block_text(block.get("title"), loc),
                "tips": tips,
            }
        )
    return out
