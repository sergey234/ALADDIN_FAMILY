# -*- coding: utf-8 -*-
"""Handbook must not answer with chat UI status strings."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.services.kb_rag_service import (  # noqa: E402
    chunk_is_ui_chrome,
    try_kb_rag_answer,
)

SCREENSHOT_CHUNK = {
    "chunk_id": "family_chat_e2ee_e2ee_en__c00",
    "parent_id": "family_chat_e2ee_e2ee_en",
    "topic": "e2ee",
    "title": "family_chat_e2ee",
    "source": "LocalizationManager",
    "score": 0.91,
    "text": (
        "### family_chat_e2ee_decrypt_failed\n"
        "Could not decrypt. Refresh keys or wait for a resend.\n\n"
        "### family_chat_e2ee_not_ready\n"
        "Secure chat is not set up on this phone yet.\n\n"
        "### family_chat_e2ee_setup\n"
        "Setting up end-to-end encryption…"
    ),
}

GOOD_E2EE = {
    "chunk_id": "family_chat_e2ee_e2ee_en__c00",
    "parent_id": "family_chat_e2ee_e2ee_en",
    "topic": "e2ee",
    "title": "Family chat encryption",
    "source": "curated",
    "score": 0.8,
    "text": (
        "If a family message won’t open: wait a few seconds and try again, "
        "or open Family Chat on another family phone so keys can sync."
    ),
}

GOOD_FAQ = {
    "chunk_id": "faq_accidental_purchases_en__c00",
    "parent_id": "faq_accidental_purchases_en",
    "topic": "security_faq",
    "title": "Accidental purchases",
    "source": "UnifiedFAQCatalog",
    "score": 0.77,
    "text": "ALADDIN asks a parent to confirm a purchase before a child can buy.",
}


def test_screenshot_chunk_is_ui_chrome() -> None:
    assert chunk_is_ui_chrome(SCREENSHOT_CHUNK)


def test_general_question_does_not_dump_screenshot(monkeypatch) -> None:
    monkeypatch.setattr(
        "security.services.kb_rag_service.hermes_available", lambda: False
    )
    monkeypatch.setattr(
        "security.services.kb_rag_service.kb_search_chunks",
        lambda *args, **kwargs: [SCREENSHOT_CHUNK],
    )
    result = try_kb_rag_answer(
        question="What is my protection status?",
        intent_id="general",
        kb_only=False,
        locale="en",
    )
    assert result is None


def test_e2ee_howto_uses_curated_not_status_lines(monkeypatch) -> None:
    monkeypatch.setattr(
        "security.services.kb_rag_service.hermes_available", lambda: False
    )
    monkeypatch.setattr(
        "security.services.kb_rag_service.kb_search_chunks",
        lambda *args, **kwargs: [SCREENSHOT_CHUNK, GOOD_E2EE],
    )
    result = try_kb_rag_answer(
        question="How does family chat encryption work?",
        intent_id="e2ee_howto",
        kb_only=True,
        locale="en",
    )
    assert result is not None
    assert "Could not decrypt" not in result.response_text
    assert "### family_chat" not in result.response_text
    assert "From the ALADDIN knowledge base:" in result.response_text
    assert "another family phone" in result.response_text


def test_open_chat_does_not_extract_faq_when_model_is_down(monkeypatch) -> None:
    monkeypatch.setattr(
        "security.services.kb_rag_service.hermes_available", lambda: False
    )
    monkeypatch.setattr(
        "security.services.kb_rag_service.kb_search_chunks",
        lambda *args, **kwargs: [GOOD_FAQ],
    )
    result = try_kb_rag_answer(
        question="Hi",
        intent_id="general",
        kb_only=False,
        locale="en",
    )
    assert result is None


def test_russian_status_line_is_chrome() -> None:
    assert chunk_is_ui_chrome(
        {"text": "Не удалось расшифровать. Обновите ключи или дождитесь повторной отправки."}
    )
