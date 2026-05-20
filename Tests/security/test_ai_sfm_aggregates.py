# -*- coding: utf-8 -*-
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from security.services.ai_llm_prompt_builder import build_ai_chat_sfm_payload
from security.services.ai_sfm_aggregate_schema import (
    extract_allowed_aggregates,
    strip_forbidden_llm_params,
)


class TestAISFMAggregates(unittest.TestCase):
    def test_extract_allowed_strips_logs_and_long_strings(self):
        raw = {
            "threats_blocked": 47,
            "protection_status": "ACTIVE",
            "logs": ["secret line"],
            "events": [{"url": "http://x", "payload": "big"}],
            "components": [
                {"id": "firewall", "status": "healthy", "uptime": 99.9, "raw_log": "nope"},
            ],
        }
        out = extract_allowed_aggregates(raw)
        self.assertEqual(out["threats_blocked"], 47)
        self.assertNotIn("logs", out)
        self.assertNotIn("events", out)
        self.assertIn("components_summary", out)

    def test_strip_forbidden_llm_params(self):
        payload = {
            "message": "hello",
            "raw_logs": "x",
            "events": [1, 2],
            "sfm_aggregates": {"threats_blocked": 1},
        }
        clean, removed = strip_forbidden_llm_params(payload)
        self.assertIn("raw_logs", removed)
        self.assertIn("events", removed)
        self.assertIn("message", clean)
        self.assertIn("sfm_aggregates", clean)

    def test_build_ai_chat_payload_includes_aggregates(self):
        def fake_execute(func, params=None):
            if func == "get_analytics_overview":
                return True, {"threats_blocked": 10, "protection_status": "ACTIVE"}, None
            if func == "get_components_health":
                return True, {
                    "total_components": 2,
                    "healthy_components": 2,
                    "overall_health": "healthy",
                }, None
            if func == "get_phishing_sensitivity":
                return True, {"sensitivity_level": "high"}, None
            return False, {}, "unknown"

        payload = build_ai_chat_sfm_payload(
            message="Сколько угроз?",
            ui_context="general",
            user_id="u1",
            execute_fn=fake_execute,
        )
        self.assertEqual(payload["llm_context_policy"], "aggregates_only_v1")
        self.assertIn("sfm_aggregates", payload)
        self.assertGreaterEqual(payload["sfm_aggregates"].get("threats_blocked", 0), 10)
        self.assertNotIn("logs", payload)


if __name__ == "__main__":
    unittest.main()
