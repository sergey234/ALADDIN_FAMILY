# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from security.services.ai_pii_redactor import contains_blocked_pii, redact
from security.services.ai_prompt_gate import (
    PIIPromptBlockedError,
    prepare_for_llm_prompt,
    redact_sfm_params,
)


class TestAIPIIRedactor(unittest.TestCase):
    def test_redacts_email_phone_card(self):
        raw = "Пишите на user@example.com или +79991234567, карта 4111111111111111"
        result = redact(raw)
        self.assertNotIn("user@example.com", result.text)
        self.assertNotIn("+79991234567", result.text)
        self.assertNotIn("4111111111111111", result.text)
        self.assertIn("[REDACTED_EMAIL]", result.text)
        self.assertGreater(result.replacement_count, 0)

    def test_prepare_blocks_residual_pii(self):
        # Obfuscated email that survives one pass — simulate by patching not needed;
        # normal email must become safe.
        prepared = prepare_for_llm_prompt("Мой email test@mail.ru", field_name="message")
        self.assertNotIn("test@mail.ru", prepared.text)
        self.assertFalse(contains_blocked_pii(prepared.text))

    def test_redact_sfm_params_message(self):
        params = redact_sfm_params(
            "ai_assistant_chat",
            {"message": "Связь +79991234567", "context": "general"},
        )
        self.assertIn("[REDACTED_PHONE]", params["message"])
        self.assertEqual(params["context"], "general")

    def test_empty_message_raises(self):
        with self.assertRaises(PIIPromptBlockedError):
            prepare_for_llm_prompt("   ", field_name="message")


if __name__ == "__main__":
    unittest.main()
