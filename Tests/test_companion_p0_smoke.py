# -*- coding: utf-8 -*-
"""P0 smoke tests — companion platform (no live LLM)."""

from __future__ import annotations

import os
import tempfile
import unittest

os.environ.setdefault("JWT_SECRET", "test-secret-companion-p0")
os.environ.setdefault("FEATURE_VOICE_ENABLED", "true")


class CompanionP0SmokeTests(unittest.TestCase):
    def test_jwt_enrich_device_child(self):
        from security.services.ai_platform.jwt_claims import enrich_access_token_data

        data = enrich_access_token_data({"sub": "u1", "type": "device_auth"})
        self.assertEqual(data["age_band"], "child")
        self.assertEqual(data["app_id"], "aladdin_family")
        self.assertIn("subscription", data)
        self.assertIn("max_ai_messages", data["subscription"]["limits"])

    def test_age_policy_child_unicorn_only(self):
        from security.services.ai_platform.age_policy import filter_characters_for_age

        chars = [{"id": "aladdin"}, {"id": "unicorn"}]
        out = filter_characters_for_age(chars, "child", {"companion": True})
        self.assertEqual([c["id"] for c in out], ["unicorn"])

    def test_companion_store_trust_and_usage(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.usage_meters import check_message_allowed, record_message

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            store.set_trust("user-a", "unicorn", 25)
            self.assertEqual(store.get_trust("user-a", "unicorn"), 25)
            record_message("user-a")
            usage = check_message_allowed("user-a", "free", {"max_ai_messages": 50})
            self.assertTrue(usage.allowed)
            self.assertEqual(usage.messages_today, 1)
            companion_store._store = None  # noqa: SLF001

    def test_companion_store_threads(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            store.append_thread_message("user-t", "companion-abc", "user", "Привет!", "unicorn")
            store.append_thread_message("user-t", "companion-abc", "assistant", "Привет, друг!", "unicorn")
            summaries = store.list_thread_summaries("user-t", limit=10)
            self.assertEqual(len(summaries), 1)
            self.assertEqual(summaries[0]["thread_id"], "companion-abc")
            self.assertEqual(summaries[0]["title"], "Привет!")
            msgs = store.get_thread_messages("user-t", "companion-abc")
            self.assertEqual(len(msgs), 2)
            self.assertEqual(msgs[0]["role"], "user")
            companion_store._store = None  # noqa: SLF001

    def test_family_consent_overrides_jwt(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.consent_resolver import (
            family_consent_key,
            resolve_parent_consent,
        )

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            store.set_consent(
                family_consent_key("fam-1"),
                {
                    "child_can_use_companion": False,
                    "memory_enabled": False,
                    "allowed_characters": ["unicorn"],
                },
            )
            merged = resolve_parent_consent(
                "child-device",
                {"child_can_use_companion": True, "memory_enabled": True},
                "fam-1",
                store=store,
            )
            self.assertFalse(merged["child_can_use_companion"])
            companion_store._store = None  # noqa: SLF001

    def test_companion_memory_store(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.consent_resolver import memory_storage_key

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            key = memory_storage_key("parent-1", "fam-mem")
            store.upsert_memory_item(key, "ex-1", "Вопрос: привет — Ответ: здравствуй")
            items = store.list_memory_items(key)
            self.assertEqual(len(items), 1)
            removed = store.delete_all_memory_items(key)
            self.assertEqual(removed, 1)
            self.assertEqual(store.list_memory_items(key), [])
            companion_store._store = None  # noqa: SLF001

    def test_companion_profile_store(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.consent_resolver import memory_storage_key

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            key = memory_storage_key("parent-1", "fam-p")
            store.set_profile(
                key,
                {
                    "custom_instructions": "Говори короче",
                    "personality_preset": "calm",
                },
            )
            loaded = store.get_profile(key)
            self.assertEqual(loaded["personality_preset"], "calm")
            companion_store._store = None  # noqa: SLF001

    def test_companion_stream_cache(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            mid = "msg-stream-1"
            tokens = ["Привет", "друг"]
            meta = {"response": "Привет друг", "trust_score": 12, "emotion": "happy"}
            store.put_stream_cache(mid, "u1", tokens, meta)
            loaded = store.get_stream_cache(mid, user_id="u1")
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["tokens"], tokens)
            self.assertEqual(loaded["meta"]["trust_score"], 12)
            self.assertIsNone(store.get_stream_cache(mid, user_id="other"))
            store.delete_stream_cache(mid)
            self.assertIsNone(store.get_stream_cache(mid))
            companion_store._store = None  # noqa: SLF001

    def test_companion_feedback_store(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.services.ai_platform.consent_resolver import memory_storage_key

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "t.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            key = memory_storage_key("u1", "fam-fb")
            fid = store.record_feedback(
                key, "u1", "unicorn", "up", 5, thread_id="t1", assistant_excerpt="ok"
            )
            self.assertGreater(fid, 0)
            summary = store.feedback_summary(key, "unicorn")
            self.assertEqual(summary["up"], 1)
            companion_store._store = None  # noqa: SLF001

    def test_policy_child_meetup_block(self):
        from security.services.ai_platform.policy_engine import evaluate_request_policy

        d = evaluate_request_policy(
            app_id="aladdin_family",
            message="давай встретимся завтра",
            age_band="child",
        )
        self.assertFalse(d.allowed)
        self.assertEqual(d.blocked_reason, "child_pii_or_meetup")


if __name__ == "__main__":
    unittest.main()
