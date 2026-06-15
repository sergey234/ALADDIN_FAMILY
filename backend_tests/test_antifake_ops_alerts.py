"""P-01 / P-02 — antifake ops alerts unit tests (no DB/Redis)."""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_SPEC = importlib.util.spec_from_file_location(
    "antifake_ops_alerts",
    os.path.join(ROOT, "scripts", "antifake_ops_alerts.py"),
)
alerts = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(alerts)


class AntifakeOpsAlertsTests(unittest.TestCase):
    def test_job_failure_ok_below_threshold(self):
        with patch.object(
            alerts,
            "_job_failure_stats",
            return_value={
                "failed": 1,
                "completed": 99,
                "total": 100,
                "failure_rate": 0.01,
                "window_min": 60,
                "threshold": 0.05,
                "min_sample": 20,
            },
        ):
            ok, msg, stats = alerts.check_job_failure_rate()
        self.assertTrue(ok)
        self.assertIn("OK", msg)
        self.assertEqual(stats["total"], 100)

    def test_job_failure_alert_above_threshold(self):
        with patch.object(
            alerts,
            "_job_failure_stats",
            return_value={
                "failed": 10,
                "completed": 90,
                "total": 100,
                "failure_rate": 0.1,
                "window_min": 60,
                "threshold": 0.05,
                "min_sample": 20,
            },
        ):
            ok, msg, _stats = alerts.check_job_failure_rate()
        self.assertFalse(ok)
        self.assertIn("ALERT", msg)

    def test_job_failure_small_sample_ok(self):
        with patch.object(
            alerts,
            "_job_failure_stats",
            return_value={
                "failed": 5,
                "completed": 0,
                "total": 5,
                "failure_rate": 1.0,
                "window_min": 60,
                "threshold": 0.05,
                "min_sample": 20,
            },
        ):
            ok, msg, _stats = alerts.check_job_failure_rate()
        self.assertTrue(ok)
        self.assertIn("sample too small", msg)

    @patch.object(alerts, "_queue_depth", return_value={"enabled": False, "depth": 0, "queue": "test"})
    def test_queue_disabled_ok(self, _depth):
        ok, msg, info = alerts.check_queue_depth()
        self.assertTrue(ok)
        self.assertFalse(info["enabled"])
        self.assertIn("disabled", msg)

    @patch.object(
        alerts,
        "_queue_depth",
        return_value={"enabled": True, "depth": 75, "queue": "aladdin-antifake"},
    )
    def test_queue_depth_alert(self, _depth):
        ok, msg, info = alerts.check_queue_depth()
        self.assertFalse(ok)
        self.assertEqual(info["depth"], 75)
        self.assertIn("ALERT", msg)


if __name__ == "__main__":
    unittest.main()
