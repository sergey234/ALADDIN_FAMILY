"""afhub-p2-03 — threat intel freshness unit tests (no DB required)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

if "sqlalchemy" not in sys.modules:
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()
sys.modules.setdefault("app.database.database", MagicMock())

from app.services.antifake_threat_intel_freshness import (  # noqa: E402
    check_threat_intel_freshness,
)


def _write_report(dir_path: Path, *, generated_at: str, uh_ok: bool = True, op_ok: bool = True) -> None:
    payload = {
        "generated_at": generated_at,
        "sources": {
            "urlhaus": {"ok": uh_ok, "rows": 10 if uh_ok else 0},
            "openphish": {"ok": op_ok, "rows": 5 if op_ok else 0},
        },
        "merged_count": 12,
        "ok": uh_ok or op_ok,
        "degraded": not (uh_ok and op_ok),
    }
    (dir_path / "last_fetch_report.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


class ThreatIntelFreshnessTests(unittest.TestCase):
    def test_fresh_report_ok(self):
        now = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            _write_report(d, generated_at=(now - timedelta(hours=2)).isoformat())
            out = check_threat_intel_freshness(
                feed_dir=d, now=now, active_count=200, min_active=50
            )
        self.assertTrue(out["ok"])
        self.assertFalse(out["alert"])
        self.assertAlmostEqual(out["age_hours"], 2.0, places=1)

    def test_stale_report_alerts(self):
        now = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            _write_report(d, generated_at=(now - timedelta(hours=48)).isoformat())
            out = check_threat_intel_freshness(
                feed_dir=d, now=now, max_age_hours=36, active_count=200
            )
        self.assertFalse(out["ok"])
        self.assertTrue(out["alert"])
        self.assertIn("fetch_report_stale", out["alerts"])
        self.assertIn("older than", out["message_en"])

    def test_both_sources_failed(self):
        now = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            _write_report(
                d,
                generated_at=now.isoformat(),
                uh_ok=False,
                op_ok=False,
            )
            out = check_threat_intel_freshness(feed_dir=d, now=now, active_count=200)
        self.assertTrue(out["alert"])
        self.assertIn("both_external_sources_failed", out["alerts"])

    def test_missing_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = check_threat_intel_freshness(
                feed_dir=Path(tmp), active_count=200, min_active=50
            )
        self.assertTrue(out["alert"])
        self.assertIn("missing_last_fetch_report", out["alerts"])

    def test_low_active_count(self):
        now = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            _write_report(d, generated_at=now.isoformat())
            out = check_threat_intel_freshness(
                feed_dir=d, now=now, active_count=10, min_active=50
            )
        self.assertTrue(out["alert"])
        self.assertIn("active_domains_below_min", out["alerts"])


if __name__ == "__main__":
    unittest.main()
