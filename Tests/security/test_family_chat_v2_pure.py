# -*- coding: utf-8 -*-
"""E1.3 — unit tests for family chat v2 pure helpers."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.routers.family_chat_v2_pure import (  # noqa: E402
    FamilyChatV2Error,
    build_send_insert_params,
    build_ws_new_message_payload,
    row_to_api_message,
    sanitize_ws_payload,
)


def test_v2_send_params_no_plaintext() -> None:
    os.environ["FAMILY_CHAT_REQUIRE_E2EE"] = "true"
    p = SimpleNamespace(
        envelopeVersion=2,
        ciphertext="SGVsbG8=",
        senderDeviceId="dev-1",
        messageType="text",
        message=None,
    )
    params = build_send_insert_params(
        p,
        message_id="MSG1",
        family_id="fam1",
        user_id=1,
        sender_name="A",
        timestamp="2026-05-20T12:00:00Z",
    )
    assert params["text"] is None
    assert params["envelope_version"] == 2
    assert params["ciphertext"] == b"Hello"


def test_v1_send_rejected_when_require_e2ee() -> None:
    os.environ["FAMILY_CHAT_REQUIRE_E2EE"] = "true"
    p = SimpleNamespace(envelopeVersion=1, message="hello", messageType="text")
    try:
        build_send_insert_params(
            p,
            message_id="MSG2",
            family_id="fam1",
            user_id=1,
            sender_name="A",
            timestamp="2026-05-20T12:00:00Z",
        )
        raise AssertionError("expected FamilyChatV2Error")
    except FamilyChatV2Error as exc:
        assert "envelope_version=2" in str(exc)


def test_row_to_api_message_v2_hides_text() -> None:
    row = (
        "MSG1",
        "Alice",
        "should-not-leak",
        "2026-05-20T12:00:00Z",
        "text",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "sent",
        None,
        2,
        "dev-1",
        b"\x01\x02",
        0,
        42,
        None,
        None,
    )
    api = row_to_api_message(row, {"user_id": 99})
    assert api["text"] is None
    assert api["ciphertext"]
    assert api["envelopeVersion"] == 2


def test_ws_sanitize_v2_strips_message() -> None:
    os.environ["FAMILY_CHAT_REQUIRE_E2EE"] = "true"
    out = sanitize_ws_payload(
        {
            "type": "new_message",
            "envelope_version": 2,
            "ciphertext": "abc",
            "sender_device_id": "dev-1",
            "family_id": "fam1",
        }
    )
    assert "message" not in out
    assert out["ciphertext"] == "abc"


def test_build_ws_new_message_from_insert() -> None:
    os.environ["FAMILY_CHAT_REQUIRE_E2EE"] = "true"
    insert = {
        "envelope_version": 2,
        "timestamp": "2026-05-20T12:00:00Z",
        "ciphertext": b"cipher",
        "sender_device_id": "dev-1",
        "message_type": "text",
        "text": None,
    }
    ws = build_ws_new_message_payload(
        message_id="MSG9",
        family_id="fam1",
        user_id=7,
        insert_params=insert,
    )
    assert ws["type"] == "new_message"
    assert ws["ciphertext"]
    assert "message" not in ws


if __name__ == "__main__":
    test_v2_send_params_no_plaintext()
    test_v1_send_rejected_when_require_e2ee()
    test_row_to_api_message_v2_hides_text()
    test_ws_sanitize_v2_strips_message()
    test_build_ws_new_message_from_insert()
    print("OK: test_family_chat_v2_pure")
