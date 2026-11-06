"""Incident 2026-11-06 regression: media jobs silently dead for 21 days (worker without env)."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from app.services.antifake_job_staleness import (
    PROCESSING_GRACE_SEC,
    QUEUED_STALE_SEC,
    sla_seconds,
    stale_failure_reason,
)
from app.services.antifake_pipeline_health import evaluate

_WATCHDOG = Path(__file__).resolve().parents[1] / "scripts" / "ops" / "main_antifake_watchdog.py"
_spec = importlib.util.spec_from_file_location("main_antifake_watchdog", _WATCHDOG)
watchdog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(watchdog)


class JobStalenessTests(unittest.TestCase):
    def test_fresh_queued_job_is_not_failed(self):
        self.assertIsNone(stale_failure_reason("queued", "audio", QUEUED_STALE_SEC - 1))

    def test_queued_job_nobody_picked_up_fails_as_worker_unavailable(self):
        self.assertEqual(
            stale_failure_reason("queued", "video", QUEUED_STALE_SEC + 1),
            "worker_unavailable",
        )

    def test_processing_video_within_sla_keeps_running(self):
        self.assertIsNone(stale_failure_reason("processing", "video", sla_seconds("video")))

    def test_processing_past_sla_and_grace_fails_as_worker_timeout(self):
        age = sla_seconds("call") + PROCESSING_GRACE_SEC + 1
        self.assertEqual(stale_failure_reason("processing", "call", age), "worker_timeout")

    def test_terminal_statuses_are_never_rewritten(self):
        for status in ("completed", "failed"):
            self.assertIsNone(stale_failure_reason(status, "audio", 10_000))


class PipelineHealthTests(unittest.TestCase):
    def _eval(self, **overrides):
        base = dict(queue_enabled=True, workers=1, failed=0, completed=4, stale_queued=0, smoke_age_h=1.0)
        base.update(overrides)
        return evaluate(**base)

    def test_healthy_pipeline_is_ok(self):
        self.assertEqual(self._eval(), {"status": "ok", "problems": []})

    def test_incident_shape_worker_up_but_every_job_fails_is_degraded(self):
        result = self._eval(failed=355, completed=0)
        self.assertEqual(result["status"], "degraded")
        self.assertIn("all_media_jobs_failing", result["problems"])

    def test_single_bad_upload_is_not_an_outage(self):
        self.assertEqual(self._eval(failed=1, completed=0)["status"], "ok")

    def test_no_registered_worker_is_degraded(self):
        self.assertIn("worker_not_registered", self._eval(workers=0)["problems"])

    def test_sync_fallback_mode_does_not_require_worker(self):
        self.assertEqual(self._eval(queue_enabled=False, workers=None)["status"], "ok")

    def test_missing_or_old_smoke_is_degraded(self):
        self.assertIn("smoke_stale", self._eval(smoke_age_h=None)["problems"])
        self.assertIn("smoke_stale", self._eval(smoke_age_h=48.0)["problems"])

    def test_stuck_queue_is_degraded(self):
        self.assertIn("jobs_stuck_in_queue", self._eval(stale_queued=2)["problems"])


class WatchdogStateTests(unittest.TestCase):
    def test_single_blip_does_not_alert(self):
        state, msg = watchdog.step({"fails": 0, "alerted_at": 0.0, "alerting": False}, ["api_health_down"], 1000.0)
        self.assertEqual(msg, "")
        self.assertEqual(state["fails"], 1)

    def test_second_consecutive_failure_alerts(self):
        state, msg = watchdog.step({"fails": 1, "alerted_at": 0.0, "alerting": False}, ["smoke_stale"], 1000.0)
        self.assertIn("smoke_stale", msg)
        self.assertTrue(state["alerting"])

    def test_no_spam_within_realert_window(self):
        prev = {"fails": 5, "alerted_at": 1000.0, "alerting": True}
        _, msg = watchdog.step(prev, ["smoke_stale"], 1000.0 + watchdog.REALERT_SEC - 1)
        self.assertEqual(msg, "")

    def test_realert_after_window(self):
        prev = {"fails": 5, "alerted_at": 1000.0, "alerting": True}
        _, msg = watchdog.step(prev, ["smoke_stale"], 1000.0 + watchdog.REALERT_SEC)
        self.assertNotEqual(msg, "")

    def test_alerts_never_use_aimonkey_shop_bot_keys(self):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as fh:
            fh.write("ALERT_TELEGRAM_BOT_TOKEN=shop\nALERT_TELEGRAM_CHAT_ID=1\nBOT_TOKEN=shop\n")
        original = watchdog.ENV_FILE
        watchdog.ENV_FILE = Path(fh.name)
        try:
            self.assertFalse(watchdog.notify("x"))
        finally:
            watchdog.ENV_FILE = original
            Path(fh.name).unlink()
        self.assertEqual(watchdog.TOKEN_KEY, "ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN")

    def test_recovery_message_once_then_silent(self):
        state, msg = watchdog.step({"fails": 3, "alerted_at": 1.0, "alerting": True}, [], 2000.0)
        self.assertIn("восстановлен", msg)
        _, msg2 = watchdog.step(state, [], 2300.0)
        self.assertEqual(msg2, "")


if __name__ == "__main__":
    unittest.main()
