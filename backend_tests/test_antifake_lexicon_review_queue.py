"""afhub-p3-01 — lexicon review queue tests (no live lexicon mutation)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.antifake_lexicon_review_queue import (
    enqueue_from_feedback,
    extract_lexicon_candidates,
    list_pending,
    mark_status,
)


class LexiconReviewQueueTests(unittest.TestCase):
    def test_extract_skips_known_and_short(self):
        known = {"срочно переведите", "банк"}
        out = extract_lexicon_candidates(
            "Срочно переведите на крипто-кошелёк сейчас",
            existing=known,
            max_candidates=5,
        )
        self.assertTrue(out)
        self.assertNotIn("срочно переведите", out)
        self.assertTrue(any("крипто" in p or "кошел" in p for p in out))

    def test_enqueue_and_hit_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.jsonl"
            note = "Переведите на криптокошелёк через сбп прямо сейчас"
            a = enqueue_from_feedback(
                note=note,
                feedback_id="fb1",
                feedback="was_scam",
                queue_path=path,
            )
            self.assertTrue(a["queued"])
            self.assertGreaterEqual(a["count"], 1)
            b = enqueue_from_feedback(
                note=note,
                feedback_id="fb2",
                feedback="was_scam",
                queue_path=path,
            )
            pending = list_pending(queue_path=path)
            self.assertTrue(pending)
            self.assertGreaterEqual(int(pending[0].get("hit_count") or 1), 2)
            self.assertEqual(b.get("count"), 0)  # merged into hits

    def test_mark_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.jsonl"
            enqueue_from_feedback(
                note="новый скам-фрагмент для теста очереди",
                feedback="was_scam",
                queue_path=path,
            )
            pending = list_pending(queue_path=path)
            self.assertTrue(pending)
            for row in pending:
                self.assertTrue(mark_status(str(row["id"]), status="rejected", queue_path=path))
            self.assertEqual(list_pending(queue_path=path), [])


if __name__ == "__main__":
    unittest.main()
