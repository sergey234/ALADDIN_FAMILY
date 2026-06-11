"""PostgreSQL persistence for user protection category toggles."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import text

from app.database.database import engine

CANONICAL_CATEGORIES = (
    "cyberThreats",
    "fraud",
    "childThreats",
    "dataLeaks",
    "deepfakes",
    "internetThreats",
    "mobileThreats",
    "familyThreats",
    "iotThreats",
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS user_protection_settings (
    user_id BIGINT PRIMARY KEY,
    enabled_categories JSONB NOT NULL DEFAULT '{}',
    global_level INTEGER NOT NULL DEFAULT 95,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _default_categories() -> Dict[str, bool]:
    return {category: False for category in CANONICAL_CATEGORIES}


def ensure_table() -> None:
    with engine.begin() as conn:
        conn.execute(text(_CREATE_TABLE))
        # Migrate INTEGER → BIGINT if table existed from earlier deploy
        conn.execute(
            text(
                """
                DO $$ BEGIN
                  ALTER TABLE user_protection_settings
                    ALTER COLUMN user_id TYPE BIGINT;
                EXCEPTION WHEN others THEN NULL;
                END $$;
                """
            )
        )


def _normalize_categories(raw: Dict[str, Any] | None) -> Dict[str, bool]:
    merged = _default_categories()
    if raw:
        for key, value in raw.items():
            if key in merged:
                merged[key] = bool(value)
    return merged


def get_protection_settings(user_id: int) -> Dict[str, Any]:
    ensure_table()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT enabled_categories, global_level, updated_at "
                "FROM user_protection_settings WHERE user_id = :user_id"
            ),
            {"user_id": user_id},
        ).mappings().first()

    if not row:
        return {
            "enabledCategories": _default_categories(),
            "globalLevel": 95,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    categories = row["enabled_categories"]
    if isinstance(categories, str):
        categories = json.loads(categories)

    return {
        "enabledCategories": _normalize_categories(categories),
        "globalLevel": int(row["global_level"] or 95),
        "updated_at": row["updated_at"].isoformat()
        if hasattr(row["updated_at"], "isoformat")
        else str(row["updated_at"]),
    }


def upsert_protection_settings(
    user_id: int,
    enabled_categories: Dict[str, bool],
    global_level: int = 95,
) -> Dict[str, Any]:
    ensure_table()
    normalized = _normalize_categories(enabled_categories)
    now = datetime.now(timezone.utc)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO user_protection_settings (user_id, enabled_categories, global_level, updated_at)
                VALUES (:user_id, CAST(:enabled_categories AS JSONB), :global_level, :updated_at)
                ON CONFLICT (user_id) DO UPDATE SET
                    enabled_categories = EXCLUDED.enabled_categories,
                    global_level = EXCLUDED.global_level,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "user_id": user_id,
                "enabled_categories": json.dumps(normalized),
                "global_level": global_level,
                "updated_at": now,
            },
        )

    return {
        "enabledCategories": normalized,
        "globalLevel": global_level,
        "updated_at": now.isoformat(),
    }
