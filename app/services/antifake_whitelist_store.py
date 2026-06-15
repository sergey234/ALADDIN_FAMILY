"""I-05: per-user trusted numbers — skip scam reports for whitelisted phones."""
from __future__ import annotations

import re
from typing import List

from sqlalchemy import text

from app.database.database import engine

_CREATE = """
CREATE TABLE IF NOT EXISTS antifake_whitelist (
    user_id BIGINT NOT NULL,
    phone_e164 VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, phone_e164)
);
"""


def _normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) < 10 or len(digits) > 15:
        return None
    return digits


def ensure_table() -> None:
    with engine.begin() as conn:
        conn.execute(text(_CREATE))


def is_whitelisted(user_id: int, phone: str) -> bool:
    normalized = _normalize_phone(phone)
    if not normalized:
        return False
    ensure_table()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1 FROM antifake_whitelist
                WHERE user_id = :uid AND phone_e164 = :phone
                """
            ),
            {"uid": int(user_id), "phone": normalized},
        ).first()
    return row is not None


def add_phones(user_id: int, phones: List[str]) -> int:
    ensure_table()
    added = 0
    with engine.begin() as conn:
        for raw in phones:
            normalized = _normalize_phone(raw)
            if not normalized:
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO antifake_whitelist (user_id, phone_e164)
                    VALUES (:uid, :phone)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {"uid": int(user_id), "phone": normalized},
            )
            added += 1
    return added


def list_phones(user_id: int) -> List[str]:
    ensure_table()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT phone_e164 FROM antifake_whitelist
                WHERE user_id = :uid ORDER BY phone_e164
                """
            ),
            {"uid": int(user_id)},
        ).scalars().all()
    return [str(p) for p in rows]


def remove_phone(user_id: int, phone: str) -> bool:
    normalized = _normalize_phone(phone)
    if not normalized:
        return False
    ensure_table()
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                DELETE FROM antifake_whitelist
                WHERE user_id = :uid AND phone_e164 = :phone
                """
            ),
            {"uid": int(user_id), "phone": normalized},
        )
    return (result.rowcount or 0) > 0
