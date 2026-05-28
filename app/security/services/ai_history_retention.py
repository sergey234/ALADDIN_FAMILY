# -*- coding: utf-8 -*-
"""
E2.4 — политика хранения истории AI (hybrid D):
- Operational (support): redacted Q/A, 7 days
- Analytics: hash-only + aggregates, 365 days
- Device (iOS): local full history, 90 days (see AIAssistantLocalHistoryPolicy.swift)
"""
from __future__ import annotations

import hashlib
import os

# Operational redacted transcripts (support / abuse)
OPERATIONAL_RETENTION_DAYS = int(os.getenv("AI_HISTORY_OPERATIONAL_DAYS", "7"))

# Hash-only analytics (no plaintext Q/A)
ANALYTICS_RETENTION_DAYS = int(os.getenv("AI_HISTORY_ANALYTICS_DAYS", "365"))

# iOS local (documented; enforced on client)
LOCAL_DEVICE_RETENTION_DAYS = 90

RETENTION_POLICY_ID = "hybrid_d_v1"


def user_id_hash(user_id: str | None) -> str:
    raw = (user_id or "guest").strip()
    salt = os.getenv("AI_HISTORY_USER_SALT") or os.getenv("JWT_SECRET") or "aladdin-ai-history"
    return hashlib.sha256(f"{salt}:{raw}".encode("utf-8")).hexdigest()


def content_hash(value: str | None) -> str | None:
    if not value or not str(value).strip():
        return None
    return hashlib.sha256(str(value).strip().encode("utf-8")).hexdigest()
