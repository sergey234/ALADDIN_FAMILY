"""afhub-p2-04 — family share verdict unit tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()
sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_family_share as share_mod  # noqa: E402


class FamilyShareVerdictTests(unittest.TestCase):
    @patch.object(share_mod, "resolve_primary_family_id", return_value=None)
    def test_no_family(self, _fid):
        out = share_mod.share_verdict_with_family(
            user_id=1, verdict="likely_fake", confidence=0.9
        )
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "no_family")

    @patch("app.services.antifake_family_notify._send_apns_sync", return_value=True)
    @patch.object(share_mod, "get_push_tokens", return_value=["tok"])
    @patch.object(share_mod, "get_parent_user_ids", return_value=[2])
    @patch("app.services.family_incidents_store.append_incident")
    @patch.object(share_mod, "resolve_primary_family_id", return_value="fam-1")
    def test_share_ok(self, _fid, _inc, _parents, _tokens, _apns):
        out = share_mod.share_verdict_with_family(
            user_id=1,
            verdict="likely_fake",
            confidence=0.88,
            job_id="job-1",
            summary="scam sms",
            lang="en",
        )
        self.assertTrue(out["ok"])
        self.assertEqual(out["family_id"], "fam-1")
        self.assertGreaterEqual(int(out.get("notified") or 0), 1)


if __name__ == "__main__":
    unittest.main()
