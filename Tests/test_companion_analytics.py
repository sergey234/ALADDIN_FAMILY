# -*- coding: utf-8 -*-
"""P1-10 — companion product analytics events."""

import unittest

from security.services.ai_platform.companion_analytics import (
    ALLOWED_EVENTS,
    COMPANION_EVENT_MESSAGE,
    COMPANION_EVENT_OPEN,
    record_companion_product_event,
)


class CompanionAnalyticsTests(unittest.TestCase):
    def test_allowed_events(self):
        self.assertIn(COMPANION_EVENT_OPEN, ALLOWED_EVENTS)
        self.assertIn(COMPANION_EVENT_MESSAGE, ALLOWED_EVENTS)
        self.assertEqual(len(ALLOWED_EVENTS), 6)

    def test_record_does_not_raise_without_db(self):
        try:
            record_companion_product_event(
                user_id="test-user",
                event=COMPANION_EVENT_OPEN,
                character_id="unicorn",
                session_id="sess-1",
            )
        except Exception as exc:
            self.fail(f"unexpected: {exc}")


if __name__ == "__main__":
    unittest.main()
