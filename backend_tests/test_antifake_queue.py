"""af-3 — antifake queue unit tests (no redis required)."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.services import antifake_queue


class AntifakeQueueTests(unittest.TestCase):
    def test_queue_disabled_when_async_off(self):
        with patch.dict(os.environ, {"ANTIFAKE_ASYNC_MEDIA": "false"}, clear=False):
            self.assertFalse(antifake_queue.queue_enabled())

    def test_enqueue_returns_false_when_disabled(self):
        with patch.dict(os.environ, {"ANTIFAKE_ASYNC_MEDIA": "false"}, clear=False):
            ok = antifake_queue.enqueue_media_job(
                job_id="00000000-0000-0000-0000-000000000001",
                job_type="audio",
                file_path="/tmp/fake.wav",
            )
            self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
