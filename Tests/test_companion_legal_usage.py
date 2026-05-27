# -*- coding: utf-8 -*-
"""P1-09 legal + P1-11 usage snapshot tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

if "jwt" not in sys.modules:
    sys.modules["jwt"] = MagicMock()

os.environ.setdefault("JWT_SECRET", "test-companion-legal")


class CompanionLegalUsageTests(unittest.TestCase):
    def test_usage_snapshot_warn_at_80(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.companion_usage import build_usage_snapshot

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "u.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            for _ in range(42):
                store.increment_messages("warn-user")
            snap = build_usage_snapshot("warn-user", "free", {"max_ai_messages": 50})
            self.assertEqual(snap["messages_today"], 42)
            self.assertGreaterEqual(snap["messages_usage_percent"], 80)
            self.assertTrue(snap["should_warn_messages"])
            self.assertFalse(snap["message_limit_reached"])
            companion_store._store = None  # noqa: SLF001

    def test_legal_endpoint_sections(self):
        from security.api.routers.ai_companion_router import companion_legal
        import asyncio

        resp = asyncio.run(companion_legal(locale="ru"))
        ids = {s.id for s in resp.sections}
        self.assertIn("ai_disclosure", ids)
        self.assertIn("coppa_152fz", ids)
        self.assertIn("store_disclosure", ids)


if __name__ == "__main__":
    unittest.main()
