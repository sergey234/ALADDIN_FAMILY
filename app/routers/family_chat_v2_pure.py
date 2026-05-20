# -*- coding: utf-8 -*-
"""E1.3 — pure helpers (no SQLAlchemy) for tests and WS/send logic."""
from __future__ import annotations

import base64
import binascii
import os
from typing import Any, Dict, Optional


class FamilyChatV2Error(ValueError):
    pass


def family_chat_require_e2ee() -> bool:
    return os.getenv("FAMILY_CHAT_REQUIRE_E2EE", "true").lower() in ("1", "true", "yes")


def _b64decode(field_name: str, value: str) -> bytes:
    raw = (value or "").strip()
    if not raw:
        raise FamilyChatV2Error(f"{field_name} is required")
    try:
        return base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise FamilyChatV2Error(f"invalid base64 for {field_name}") from exc


def _b64encode(data: Optional[bytes]) -> Optional[str]:
    if not data:
        return None
    return base64.b64encode(data).decode("ascii")


def resolve_envelope_version(payload: Any) -> int:
    """Prefer explicit v2 (camelCase or snake) over model default envelope_version=1."""
    ev_snake = getattr(payload, "envelope_version", None)
    ev_camel = getattr(payload, "envelopeVersion", None)
    cipher = getattr(payload, "ciphertext", None)
    for val in (ev_camel, ev_snake):
        if val is not None:
            try:
                return int(val)
            except (TypeError, ValueError) as exc:
                raise FamilyChatV2Error("invalid envelope_version") from exc
    if cipher and str(cipher).strip():
        return 2
    return 1


def build_send_insert_params(
    payload: Any,
    *,
    message_id: str,
    family_id: str,
    user_id: int,
    sender_name: str,
    timestamp: str,
) -> Dict[str, Any]:
    envelope_version = resolve_envelope_version(payload)

    if envelope_version == 2:
        ciphertext_b64 = getattr(payload, "ciphertext", None)
        if not ciphertext_b64 or not str(ciphertext_b64).strip():
            raise FamilyChatV2Error("ciphertext is required for envelope_version=2")
        if getattr(payload, "message", None) and str(payload.message).strip():
            raise FamilyChatV2Error("plaintext message field forbidden for envelope_version=2")

        sender_device_id = (
            getattr(payload, "sender_device_id", None) or getattr(payload, "senderDeviceId", None) or ""
        ).strip()
        if not sender_device_id:
            raise FamilyChatV2Error("sender_device_id is required for envelope_version=2")

        ctype = getattr(payload, "ciphertext_content_type", None)
        if ctype is None:
            ctype = getattr(payload, "ciphertextContentType", None)
        try:
            ciphertext_content_type = int(ctype if ctype is not None else 0)
        except (TypeError, ValueError) as exc:
            raise FamilyChatV2Error("invalid ciphertext_content_type") from exc

        message_type = getattr(payload, "messageType", None) or "text"
        reply_to = getattr(payload, "replyToMessageId", None)
        media_cipher_url = (
            getattr(payload, "media_ciphertext_url", None)
            or getattr(payload, "mediaCiphertextUrl", None)
            or ""
        ).strip()
        media_cipher_hash = (
            getattr(payload, "media_ciphertext_hash", None)
            or getattr(payload, "mediaCiphertextHash", None)
            or ""
        ).strip()
        voice_duration = getattr(payload, "voiceDuration", None)

        return {
            "id": message_id,
            "family_id": family_id,
            "sender_user_id": user_id,
            "sender_name": sender_name,
            "text": None,
            "timestamp": timestamp,
            "message_type": message_type,
            "voice_url": None,
            "voice_duration": voice_duration,
            "media_url": None,
            "media_thumbnail_url": None,
            "media_type": getattr(payload, "mediaType", None),
            "reply_to_message_id": reply_to,
            "read_status": "sent",
            "envelope_version": 2,
            "sender_device_id": sender_device_id,
            "ciphertext": _b64decode("ciphertext", str(ciphertext_b64)),
            "ciphertext_content_type": ciphertext_content_type,
            "media_ciphertext_url": media_cipher_url or None,
            "media_ciphertext_hash": media_cipher_hash or None,
        }

    if family_chat_require_e2ee():
        raise FamilyChatV2Error(
            "plaintext family chat disabled; envelope_version=2 with ciphertext is required"
        )

    text_value = (getattr(payload, "message", None) or "").strip()
    if not text_value and not (getattr(payload, "mediaUrl", None) or getattr(payload, "voiceUrl", None)):
        raise FamilyChatV2Error("Empty message payload")

    return {
        "id": message_id,
        "family_id": family_id,
        "sender_user_id": user_id,
        "sender_name": sender_name,
        "text": text_value if text_value else None,
        "timestamp": timestamp,
        "message_type": getattr(payload, "messageType", None)
        or ("media" if getattr(payload, "mediaUrl", None) else "text"),
        "voice_url": getattr(payload, "voiceUrl", None),
        "voice_duration": getattr(payload, "voiceDuration", None),
        "media_url": getattr(payload, "mediaUrl", None),
        "media_thumbnail_url": getattr(payload, "mediaUrl", None),
        "media_type": getattr(payload, "mediaType", None),
        "reply_to_message_id": getattr(payload, "replyToMessageId", None),
        "read_status": "sent",
        "envelope_version": 1,
        "sender_device_id": None,
        "ciphertext": None,
        "ciphertext_content_type": 0,
        "media_ciphertext_url": None,
        "media_ciphertext_hash": None,
    }


def row_to_api_message(row: Any, current_user: dict) -> Dict[str, Any]:
    sender_name = str(row[1] or "User")
    envelope_version = int(row[14] or 1)
    sender_user_id = row[18]
    current_uid = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    is_current = False
    if sender_user_id is not None and current_uid is not None:
        try:
            is_current = int(sender_user_id) == int(current_uid)
        except (TypeError, ValueError):
            is_current = sender_name == str(current_user.get("name") or "You")
    else:
        is_current = sender_name == str(current_user.get("name") or "You")

    return {
        "id": str(row[0]),
        "sender": sender_name,
        "text": row[2] if envelope_version == 1 else None,
        "timestamp": str(row[3]),
        "isCurrentUser": is_current,
        "messageType": row[4],
        "voiceUrl": row[5] if envelope_version == 1 else None,
        "voiceDuration": float(row[6]) if row[6] is not None else None,
        "mediaUrl": row[7] if envelope_version == 1 else None,
        "mediaThumbnailUrl": row[8] if envelope_version == 1 else None,
        "mediaType": row[9],
        "replyToMessageId": row[10],
        "editedAt": row[11],
        "readStatus": row[12],
        "readAt": row[13],
        "envelopeVersion": envelope_version,
        "senderDeviceId": row[15],
        "ciphertext": _b64encode(bytes(row[16])) if row[16] is not None else None,
        "ciphertextContentType": int(row[17] or 0),
        "legacyPlaintext": envelope_version == 1,
        "isLegacyPlaintext": envelope_version == 1,
        "mediaCiphertextUrl": row[19] if envelope_version == 2 else None,
        "mediaCiphertextHash": row[20] if envelope_version == 2 else None,
    }


def sanitize_ws_payload(payload: dict) -> dict:
    env = payload.get("envelope_version", payload.get("envelopeVersion", 1))
    try:
        env = int(env)
    except (TypeError, ValueError):
        env = 1

    msg_type = payload.get("type", "message")
    is_chat_frame = msg_type in ("message", "new_message", "chat")

    if family_chat_require_e2ee() and is_chat_frame and env != 2:
        raise FamilyChatV2Error("plaintext chat forbidden when FAMILY_CHAT_REQUIRE_E2EE=true")

    if env == 2:
        if payload.get("message"):
            raise FamilyChatV2Error("plaintext message forbidden for envelope_version=2")
        if not payload.get("ciphertext"):
            raise FamilyChatV2Error("ciphertext required for envelope_version=2")

    outbound: Dict[str, Any] = {
        "type": msg_type,
        "family_id": payload.get("family_id"),
        "user_id": payload.get("user_id"),
        "typing": bool(payload.get("typing", False)),
        "envelope_version": env,
    }
    if payload.get("message_id"):
        outbound["message_id"] = payload.get("message_id")
    if payload.get("timestamp"):
        outbound["timestamp"] = payload.get("timestamp")

    if env == 2:
        outbound["ciphertext"] = payload.get("ciphertext")
        outbound["sender_device_id"] = payload.get("sender_device_id") or payload.get("senderDeviceId")
        outbound["message_type"] = payload.get("message_type") or payload.get("messageType") or "text"
        if payload.get("mediaCiphertextUrl") or payload.get("media_ciphertext_url"):
            outbound["media_ciphertext_url"] = payload.get("media_ciphertext_url") or payload.get(
                "mediaCiphertextUrl"
            )
    elif is_chat_frame:
        outbound["message"] = payload.get("message")
    return outbound


def build_ws_new_message_payload(
    *,
    message_id: str,
    family_id: str,
    user_id: int,
    insert_params: Dict[str, Any],
) -> dict:
    env = int(insert_params.get("envelope_version") or 1)
    raw = {
        "type": "new_message",
        "family_id": family_id,
        "user_id": user_id,
        "message_id": message_id,
        "timestamp": insert_params.get("timestamp"),
        "envelope_version": env,
    }
    if env == 2:
        raw["ciphertext"] = _b64encode(insert_params.get("ciphertext"))
        raw["sender_device_id"] = insert_params.get("sender_device_id")
        raw["message_type"] = insert_params.get("message_type") or "text"
        if insert_params.get("media_ciphertext_url"):
            raw["media_ciphertext_url"] = insert_params.get("media_ciphertext_url")
    else:
        raw["message"] = insert_params.get("text")
    return sanitize_ws_payload(raw)
