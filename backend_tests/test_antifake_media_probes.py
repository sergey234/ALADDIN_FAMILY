"""F-02 / F-11 — media probe must not emit likely_fake without ML source."""
from __future__ import annotations

import unittest

from app.security.ml_lazy_loader import probe_audio_bytes, probe_video_bytes
from app.services.antifake_service import _merge_probe_into_verdict


class AntifakeMediaProbeTests(unittest.TestCase):
    def test_audio_probe_never_likely_fake(self):
        wav = (
            b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        )
        probe = probe_audio_bytes(wav)
        self.assertEqual(probe["verdict"], "uncertain")
        self.assertEqual(probe["source"], "audio_probe")
        self.assertIn("wav_container", probe["reasons"])

    def test_video_probe_never_likely_fake(self):
        probe = probe_video_bytes(b"\xff\xd8\xff" + b"\x00" * 512)
        self.assertEqual(probe["verdict"], "uncertain")
        self.assertEqual(probe["source"], "video_probe")
        self.assertLessEqual(float(probe["confidence"]), 0.69)

    def test_merge_probe_does_not_escalate_rule_engine(self):
        base = {
            "verdict": "uncertain",
            "confidence": 0.25,
            "reasons": ["audio_agent_unavailable"],
            "source": "rule_engine",
            "agent": "heuristic_audio",
        }
        probe = probe_audio_bytes(b"RIFF" + b"\x00" * 200)
        merged = _merge_probe_into_verdict(base, probe)
        self.assertNotEqual(merged["verdict"], "likely_fake")
        self.assertIn("audio_probe", merged["source"])
        self.assertLessEqual(float(merged["confidence"]), 0.69)

    def test_merge_probe_preserves_ml_likely_fake(self):
        base = {
            "verdict": "likely_fake",
            "confidence": 0.91,
            "reasons": ["bert_scam"],
            "source": "real_agent",
            "agent": "fake_news_detection_agent",
        }
        probe = probe_video_bytes(b"\xff\xd8\xff" + b"\x00" * 100)
        merged = _merge_probe_into_verdict(base, probe)
        self.assertEqual(merged["verdict"], "likely_fake")
        self.assertIn("real_agent", merged["source"])


if __name__ == "__main__":
    unittest.main()
