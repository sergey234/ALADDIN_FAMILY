# -*- coding: utf-8
"""Dual-write hooks: SQLite (primary) → Postgres mirror (p3-11)."""

from __future__ import annotations

import logging
from typing import Any, Dict

from security.services.ai_platform.wellness_store_postgres import (
    WellnessPostgresStore,
    dual_write_enabled,
    pg_read_enabled,
)

logger = logging.getLogger(__name__)


def mirror_checkin_to_postgres(row: Dict[str, Any]) -> None:
    if not dual_write_enabled() or not row:
        return
    try:
        WellnessPostgresStore().upsert_checkin_row(row)
    except Exception as exc:
        logger.warning("wellness pg mirror checkin failed: %s", exc)


def mirror_settings_to_postgres(row: Dict[str, Any]) -> None:
    if not dual_write_enabled() or not row:
        return
    try:
        WellnessPostgresStore().upsert_settings_row(row)
    except Exception as exc:
        logger.warning("wellness pg mirror settings failed: %s", exc)


def list_checkins_preferred(store, user_id: str, *, days: int = 7):
    """Read from Postgres when WELLNESS_PG_READ=1, else SQLite store."""
    if pg_read_enabled():
        rows = WellnessPostgresStore().list_checkins(user_id, days=days)
        if rows:
            return rows
    return store.list_wellness_checkins(user_id, days=days)
