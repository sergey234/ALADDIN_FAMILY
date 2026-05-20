# -*- coding: utf-8 -*-
"""E1.3 — Family chat message v2 (ciphertext) helpers."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy import text

from app.routers.family_chat_v2_pure import (
    FamilyChatV2Error,
    build_send_insert_params as _build_send_insert_params,
    build_ws_new_message_payload,
    row_to_api_message,
    sanitize_ws_payload,
    _b64decode,
    _b64encode,
    resolve_envelope_version,
    family_chat_require_e2ee,
)

_CHAT_V2_COLUMNS_READY = False


def ensure_chat_v2_columns(db) -> None:
    global _CHAT_V2_COLUMNS_READY
    if _CHAT_V2_COLUMNS_READY:
        return
    db.execute(
        text(
            """
            ALTER TABLE family_chat_messages
                ADD COLUMN IF NOT EXISTS envelope_version SMALLINT NOT NULL DEFAULT 1
            """
        )
    )
    db.execute(text("ALTER TABLE family_chat_messages ADD COLUMN IF NOT EXISTS sender_device_id TEXT"))
    db.execute(text("ALTER TABLE family_chat_messages ADD COLUMN IF NOT EXISTS ciphertext BYTEA"))
    db.execute(
        text(
            """
            ALTER TABLE family_chat_messages
                ADD COLUMN IF NOT EXISTS ciphertext_content_type SMALLINT DEFAULT 0
            """
        )
    )
    db.execute(text("ALTER TABLE family_chat_messages ADD COLUMN IF NOT EXISTS media_ciphertext_url TEXT"))
    db.execute(text("ALTER TABLE family_chat_messages ADD COLUMN IF NOT EXISTS media_ciphertext_hash TEXT"))
    _CHAT_V2_COLUMNS_READY = True


def build_send_insert_params(
    payload: Any,
    *,
    message_id: str,
    family_id: str,
    user_id: int,
    sender_name: str,
    timestamp: str,
) -> Dict[str, Any]:
    try:
        return _build_send_insert_params(
            payload,
            message_id=message_id,
            family_id=family_id,
            user_id=user_id,
            sender_name=sender_name,
            timestamp=timestamp,
        )
    except FamilyChatV2Error as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


INSERT_MESSAGE_SQL = """
    INSERT INTO family_chat_messages (
        id, family_id, sender_user_id, sender_name, text, timestamp,
        message_type, voice_url, voice_duration, media_url, media_thumbnail_url,
        media_type, reply_to_message_id, read_status,
        envelope_version, sender_device_id, ciphertext, ciphertext_content_type,
        media_ciphertext_url, media_ciphertext_hash
    ) VALUES (
        :id, :family_id, :sender_user_id, :sender_name, :text, :timestamp,
        :message_type, :voice_url, :voice_duration, :media_url, :media_thumbnail_url,
        :media_type, :reply_to_message_id, :read_status,
        :envelope_version, :sender_device_id, :ciphertext, :ciphertext_content_type,
        :media_ciphertext_url, :media_ciphertext_hash
    )
"""


SELECT_MESSAGES_SQL = """
    SELECT id, sender_name, text, timestamp, message_type, voice_url, voice_duration,
           media_url, media_thumbnail_url, media_type, reply_to_message_id, edited_at,
           read_status, read_at, envelope_version, sender_device_id, ciphertext,
           ciphertext_content_type, sender_user_id, media_ciphertext_url, media_ciphertext_hash
    FROM family_chat_messages
    WHERE family_id = :family_id
    ORDER BY timestamp ASC
    LIMIT 300
"""
