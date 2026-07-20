# -*- coding: utf-8 -*-
"""psych-02 — SSOT guide mode ids: JSON ↔ wellness_guide_role (Swift mirror documented)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from security.services.ai_platform.wellness_guide_role import (
    GUIDE_MODE_BLIND,
    GUIDE_MODE_DEEP,
    GUIDE_MODE_ONE_Q,
    GUIDE_MODE_PRESENCE,
    GUIDE_MODE_STRUCTURED,
    _MODE_INSTRUCTIONS,
)

_ROOT = Path(__file__).resolve().parents[1]
_JSON = (
    _ROOT
    / "security"
    / "services"
    / "ai_platform"
    / "wellness_i18n"
    / "reflective_modes_v1.json"
)

# Must match WellnessGuideSessionStore.ssotModeIds / allModes order-independent set.
_SWIFT_SSOT_IDS = frozenset(
    {
        "presence",
        "structured_view",
        "deep_explore",
        "blind_spots",
        "single_question",
    }
)


class WellnessGuideModesSSOTTests(unittest.TestCase):
    def test_json_ids_match_python_and_swift_ssot(self):
        data = json.loads(_JSON.read_text(encoding="utf-8"))
        modes = data.get("modes") or []
        json_ids = {str(m.get("id")) for m in modes if isinstance(m, dict)}
        self.assertEqual(json_ids, _SWIFT_SSOT_IDS)
        py_ids = set(_MODE_INSTRUCTIONS.keys())
        self.assertEqual(py_ids, _SWIFT_SSOT_IDS)
        self.assertEqual(
            py_ids,
            {
                GUIDE_MODE_PRESENCE,
                GUIDE_MODE_STRUCTURED,
                GUIDE_MODE_DEEP,
                GUIDE_MODE_BLIND,
                GUIDE_MODE_ONE_Q,
            },
        )

    def test_json_pillar_field_is_hint_only_documented(self):
        """pillar in JSON must not be required for Guide overlay (mode ≠ pillar switch)."""
        data = json.loads(_JSON.read_text(encoding="utf-8"))
        for mode in data.get("modes") or []:
            self.assertIn("id", mode)
            # pillar may exist as deep-link hint — Guide path must ignore it
            self.assertTrue(mode.get("id"))


if __name__ == "__main__":
    unittest.main()
