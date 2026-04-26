from __future__ import annotations

from bot.services.fulfillment_recipient import parse_fulfillment_recipient_username


def test_parse_username_strip_at() -> None:
    assert parse_fulfillment_recipient_username("@John_Doe") == "john_doe"


def test_parse_username_plain() -> None:
    assert parse_fulfillment_recipient_username("user1234") == "user1234"


def test_parse_empty() -> None:
    assert parse_fulfillment_recipient_username(None) is None
    assert parse_fulfillment_recipient_username("") is None
    assert parse_fulfillment_recipient_username("   ") is None


def test_parse_invalid() -> None:
    assert parse_fulfillment_recipient_username("ab") is None
    assert parse_fulfillment_recipient_username("bad!name") is None
