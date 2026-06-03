# -*- coding: utf-8 -*-
"""hero-x-64 — persona metrics events."""

import unittest

from security.services.ai_platform.companion_analytics import (
    COMPANION_EVENT_GUARD_TRIGGERED,
    COMPANION_EVENT_HUMOR_INJECTED,
    COMPANION_EVENT_WISDOM_USED,
    ALLOWED_EVENTS,
)


class CompanionMetricsTests(unittest.TestCase):
    def test_hero_events_registered(self):
        for ev in (
            COMPANION_EVENT_HUMOR_INJECTED,
            COMPANION_EVENT_WISDOM_USED,
            COMPANION_EVENT_GUARD_TRIGGERED,
        ):
            self.assertIn(ev, ALLOWED_EVENTS)


if __name__ == "__main__":
    unittest.main()
