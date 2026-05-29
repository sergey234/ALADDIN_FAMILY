# -*- coding: utf-8 -*-
"""Sprint 5 — web search, trust decay, family context, attachments, COGS, workspaces."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date, timedelta

os.environ.setdefault("JWT_SECRET", "test-secret-companion-s5")
os.environ["FEATURE_WEB_SEARCH_ENABLED"] = "true"


class CompanionSprint5Tests(unittest.TestCase):
    def test_web_search_intent(self):
        from security.services.ai_platform.companion_web_search import maybe_companion_web_search

        sources, hint = maybe_companion_web_search("что за фильм Интерстеллар", locale="ru")
        self.assertTrue(sources)
        self.assertIn("Web search", hint)

    def test_trust_decay_after_gap(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.companion_trust_decay import apply_trust_visit

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            store.set_trust("u1", "unicorn", 40)
            yesterday = (date.today() - timedelta(days=3)).isoformat()
            store.set_trust_meta(
                "u1",
                "unicorn",
                {"last_active_day": yesterday, "streak_days": 2},
            )
            result = apply_trust_visit(store, "u1", "unicorn")
            self.assertGreater(result["decay_applied"], 0)
            self.assertLess(store.get_trust("u1", "unicorn"), 40)
            companion_store._store = None  # noqa: SLF001

    def test_family_context_hint(self):
        from security.services.ai_platform.companion_family_context import build_family_context_hint

        hint = build_family_context_hint(
            "scope-abc",
            {"age_band": "teen", "family_id": "fam-123", "parent_consent": {}},
            store=type("S", (), {"list_memory_items": lambda *_a, **_k: []})(),
        )
        self.assertIn("age_band=teen", hint)

    def test_attachments_validate(self):
        from security.services.ai_platform.companion_attachments import validate_and_format_attachments

        accepted, hint, errors = validate_and_format_attachments(
            [{"kind": "image", "filename": "a.jpg", "mime_type": "image/jpeg"}],
            age_band="child",
        )
        self.assertEqual(len(accepted), 1)
        self.assertIn("Attachments", hint)
        self.assertEqual(errors, [])

    def test_cogs_record(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_cogs import record_turn_cogs, build_cogs_dashboard
        from security.services.ai_platform.companion_store import CompanionStore

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            record_turn_cogs(store, "u-cogs", input_chars=400, output_chars=800, chat_mode="fast")
            dash = build_cogs_dashboard(store, "u-cogs")
            self.assertGreater(dash["daily_usd"], 0)
            self.assertEqual(dash["turns_today"], 1)
            companion_store._store = None  # noqa: SLF001

    def test_workspaces_create(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.companion_workspaces import create_workspace, list_workspaces

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            row = create_workspace(store, "u-ws", "Школа", character_id="unicorn")
            rows = list_workspaces(store, "u-ws")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["workspace_id"], row["workspace_id"])
            companion_store._store = None  # noqa: SLF001

    def test_long_context_hint_over_threshold(self):
        from security.services.ai_platform.companion_long_context import build_long_context_hint

        class _Store:
            def get_thread_messages(self, _uid, _tid, limit=50):
                return [
                    {"role": "user", "text": f"msg-{i}"}
                    for i in range(30)
                ]

        hint = build_long_context_hint(_Store(), "u1", "t1", threshold=24, keep_recent=8)
        self.assertIn("Long context recap", hint)

    def test_media_gen_disabled_by_default(self):
        from security.services.ai_platform.companion_media_gen import generate_companion_image

        out = generate_companion_image("sunset", age_band="child")
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
