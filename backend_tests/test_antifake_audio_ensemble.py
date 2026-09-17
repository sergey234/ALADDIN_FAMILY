"""T3-02 / afhub-p2-01 — audio/call ensemble tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.services.antifake_audio_ensemble import (  # noqa: E402
    AUDIO_MODEL_CARD,
    ensemble_check_audio,
)
from app.services.antifake_service import FORBIDDEN_SOURCES, check_media  # noqa: E402

_WAV = (
    b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
    b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
)


class AntifakeAudioEnsembleTests(unittest.TestCase):
    @patch("app.services.antifake_service._sfm_execute")
    def test_audio_offline_ensemble_source(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        out = check_media(media_type="audio", file_name="x.wav", file_bytes=_WAV)
        self.assertEqual(out["source"], "ensemble_audio")
        self.assertNotIn(out.get("source"), FORBIDDEN_SOURCES)
        channels = {row["channel"] for row in out.get("sources") or []}
        self.assertIn("deepfake", channels)
        self.assertIn("probe", channels)
        self.assertIn("stt_text", channels)
        self.assertIn("model_card", out)

    @patch("app.services.antifake_service._sfm_execute")
    def test_call_spoof_elevates_ensemble(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        out = ensemble_check_audio(
            media_type="call",
            file_name="call.wav",
            file_bytes=_WAV,
            extra={"caller_id": "+7 916 123-45-67", "display_name": "Сбербанк"},
        )
        self.assertEqual(out["source"], "ensemble_audio")
        channels = {row["channel"] for row in out.get("sources") or []}
        self.assertIn("spoof", channels)
        self.assertGreaterEqual(float(out["confidence"]), 0.35)

    @patch("app.services.antifake_service._sfm_execute")
    def test_stt_scam_transcript_veto(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        scam = "Срочно переведи деньги на карту"
        out = ensemble_check_audio(
            media_type="audio",
            file_name="v.wav",
            file_bytes=_WAV,
            extra={"stt_transcript": scam, "stt_lang": "ru"},
        )
        channels = {row["channel"] for row in out.get("sources") or []}
        self.assertIn("stt_text", channels)
        self.assertEqual(out["verdict"], "likely_fake")
        self.assertGreaterEqual(float(out["confidence"]), 0.72)

    @patch("app.services.antifake_service._sfm_execute")
    def test_stt_en_scam_transcript(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        out = ensemble_check_audio(
            media_type="audio",
            file_name="en.wav",
            file_bytes=_WAV,
            extra={
                "stt_transcript": "Send me money urgently to my card",
                "stt_lang": "en",
            },
        )
        self.assertEqual(out["verdict"], "likely_fake")

    @patch("app.services.antifake_service._sfm_execute")
    def test_stt_unavailable_not_green_alone(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        with patch(
            "app.services.antifake_audio_ensemble.try_transcript",
            return_value=(None, "unknown"),
        ):
            out = ensemble_check_audio(
                media_type="audio",
                file_name="v.wav",
                file_bytes=_WAV,
                extra={},
            )
        blob = " ".join(out.get("reasons") or [])
        self.assertIn("stt_unavailable", blob)
        self.assertNotEqual(out.get("verdict"), "likely_real")

    def test_model_card_contract(self):
        self.assertEqual(AUDIO_MODEL_CARD["ensemble_version"], "antifake_audio_v2")
        self.assertIn("deepfake", AUDIO_MODEL_CARD["channels"])
        self.assertIn("stt_text", AUDIO_MODEL_CARD["channels"])


if __name__ == "__main__":
    unittest.main()
