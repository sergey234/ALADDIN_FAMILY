# -*- coding: utf-8 -*-
"""P2-04 — Photo/PDF attachment validation and prompt hints (MVP)."""

from __future__ import annotations

import base64
import re
from typing import Any, Dict, List, Tuple

_MAX_B64_LEN = 400_000
_ALLOWED_KINDS = frozenset({"image", "pdf"})
_IMAGE_MIME = re.compile(r"^image/(jpeg|png|webp|heic)$", re.I)
_PDF_MIME = re.compile(r"^application/pdf$", re.I)


def validate_and_format_attachments(
    attachments: List[Dict[str, Any]],
    *,
    age_band: str,
) -> Tuple[List[Dict[str, str]], str, List[str]]:
    """
    Returns (accepted_meta, prompt_hint, errors).
    MVP: accept metadata + small base64; no vision model — describe for LLM.
    """
    accepted: List[Dict[str, str]] = []
    errors: List[str] = []
    for idx, raw in enumerate(attachments or []):
        kind = str(raw.get("kind") or "").lower()
        filename = str(raw.get("filename") or f"file_{idx}")[:128]
        mime = str(raw.get("mime_type") or "").lower()
        b64 = raw.get("content_b64")

        if kind not in _ALLOWED_KINDS:
            errors.append(f"unsupported_kind:{kind}")
            continue
        if kind == "image" and mime and not _IMAGE_MIME.match(mime):
            errors.append(f"bad_mime:{mime}")
            continue
        if kind == "pdf" and mime and not _PDF_MIME.match(mime):
            errors.append(f"bad_mime:{mime}")
            continue
        if b64:
            if len(str(b64)) > _MAX_B64_LEN:
                errors.append("attachment_too_large")
                continue
            try:
                base64.b64decode(str(b64)[:200], validate=True)
            except Exception:
                errors.append("invalid_base64")
                continue

        accepted.append({"kind": kind, "filename": filename, "mime_type": mime or kind})

    if not accepted:
        return [], "", errors

    if age_band == "child":
        hint = (
            "[Attachments: пользователь приложил файл(ы). "
            "Опиши, что обычно бывает на таких фото/PDF, без личных данных. "
            "Не проси прислать паспорт или адрес.]\n"
        )
    else:
        hint = (
            "[Attachments: user attached file(s). "
            "Acknowledge the upload; help with safe, general guidance.]\n"
        )
    names = ", ".join(a["filename"] for a in accepted)
    hint += f"files={names}\n"
    return accepted, hint, errors
