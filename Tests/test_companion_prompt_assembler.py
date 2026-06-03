# -*- coding: utf-8
"""hero-x-09 — companion prompt assembler."""

from __future__ import annotations

import unittest

from security.services.ai_platform.companion_prompt_assembler import (
    PromptLayer,
    assemble_companion_prompt_layers,
)


class CompanionPromptAssemblerTests(unittest.TestCase):
    def test_keeps_high_priority_layers(self):
        layers = [
            PromptLayer("persona", "A" * 100, priority=50, droppable=True),
            PromptLayer("wellness", "[WELLNESS v1] pillar=cognitive", priority=10, droppable=True),
            PromptLayer("humor", "B" * 100, priority=40, droppable=True),
        ]
        result = assemble_companion_prompt_layers(layers, char_budget=5000, user_message="hi")
        joined = "".join(result.parts)
        self.assertIn("[WELLNESS v1]", joined)

    def test_drops_low_priority_when_over_budget(self):
        layers = [
            PromptLayer("wellness", "[WELLNESS v1] x", priority=10, droppable=True),
            PromptLayer("humor", "H" * 8000, priority=50, droppable=True),
        ]
        result = assemble_companion_prompt_layers(layers, char_budget=200, user_message="")
        self.assertIn("humor", result.dropped)


if __name__ == "__main__":
    unittest.main()
