# -*- coding: utf-8 -*-
"""Structured wellness API errors with ru/en copy (p18-15)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from security.services.ai_platform.wellness_i18n_loader import (
    normalize_wellness_locale,
    wellness_error_from_i18n,
    wellness_errors_catalog_from_i18n,
)


def wellness_error_payload(code: str, *, locale: str = "ru") -> Dict[str, Any]:
    loc = normalize_wellness_locale(locale)
    entry = wellness_error_from_i18n(code, locale=loc)
    return {
        "code": code,
        "message_key": entry.get("message_key") or "wellness_error_generic",
        "message": entry.get("message") or "",
        "http_status": int(entry.get("http_status") or 400),
    }


def raise_wellness_error(
    code: str,
    status: Optional[int] = None,
    *,
    locale: str = "ru",
) -> None:
    payload = wellness_error_payload(code, locale=locale)
    raise HTTPException(
        status_code=int(status or payload.get("http_status") or 400),
        detail=payload,
    )


def build_errors_catalog(*, locale: str = "ru") -> List[Dict[str, Any]]:
    return wellness_errors_catalog_from_i18n(locale=locale)
