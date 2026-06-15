"""B-09: antifake per-bucket rate limits return HTTP 429."""
from __future__ import annotations

import unittest

from fastapi import HTTPException

from app.services.antifake_rate_limit import check_rate_limit


class AntifakeRateLimitTests(unittest.TestCase):
    def setUp(self) -> None:
        import app.services.antifake_rate_limit as rl

        rl._buckets.clear()

    def test_allows_under_limit(self) -> None:
        for _ in range(3):
            check_rate_limit(user_id=9001, bucket="text_url_test", limit=5, window_sec=60)

    def test_blocks_at_limit(self) -> None:
        uid = 9002
        bucket = "media_test"
        for _ in range(2):
            check_rate_limit(user_id=uid, bucket=bucket, limit=2, window_sec=3600)
        with self.assertRaises(HTTPException) as ctx:
            check_rate_limit(user_id=uid, bucket=bucket, limit=2, window_sec=3600)
        self.assertEqual(ctx.exception.status_code, 429)
        detail = ctx.exception.detail
        self.assertIsInstance(detail, dict)
        self.assertEqual(detail.get("error"), "rate_limit")
        self.assertEqual(detail.get("bucket"), bucket)


if __name__ == "__main__":
    unittest.main()
