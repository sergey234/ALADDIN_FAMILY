"""B2-10 — ml_lazy_loader import isolation tests (no torch/cv2 required at import)."""
from __future__ import annotations

import importlib
import sys
import unittest


class AntifakeMlLazyLoaderTests(unittest.TestCase):
    def test_fake_news_agent_imports_without_eager_torch(self):
        module = importlib.import_module("security.ai_agents.fake_news_detection_agent")
        agent_cls = module.FakeNewsDetectionAgent
        agent = agent_cls()
        self.assertFalse(agent._pipeline_ready)

    def test_fake_documents_agent_imports_without_eager_cv2(self):
        module = importlib.import_module("security.ai_agents.fake_documents_agent")
        self.assertTrue(hasattr(module, "FakeDocumentsAgent"))

    def test_ai_agents_package_import_is_resilient(self):
        importlib.import_module("security.ai_agents")


if __name__ == "__main__":
    unittest.main()
