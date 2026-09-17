"""T3-03 — video ensemble tests."""
from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sqlalchemy_mock = MagicMock()
    sys.modules["sqlalchemy"] = sqlalchemy_mock
    sys.modules["sqlalchemy.text"] = MagicMock()

sys.modules.setdefault("app.database.database", MagicMock())

from app.security.ml_lazy_loader import probe_video_bytes  # noqa: E402
from app.services.antifake_service import FORBIDDEN_SOURCES, check_media  # noqa: E402
from app.services.antifake_video_ensemble import (  # noqa: E402
    VIDEO_MODEL_CARD,
    ensemble_check_video,
)
from app.services.antifake_video_metadata import analyze_video_metadata  # noqa: E402

_FAKE_MP4 = b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00" + b"moov" + b"\x00" * 64 + b"mdat" + b"\x00" * 128


class AntifakeVideoEnsembleTests(unittest.TestCase):
    def test_metadata_ftyp_isom(self):
        reasons, score = analyze_video_metadata(_FAKE_MP4, file_name="clip.mp4")
        self.assertIn("ftyp_isom", reasons)
        self.assertGreater(score, 0.0)

    def test_metadata_jpeg_mismatch(self):
        jpeg = b"\xff\xd8\xff" + b"\x00" * 512
        reasons, score = analyze_video_metadata(jpeg, file_name="fake.mp4")
        self.assertIn("jpeg_not_video_container", reasons)
        self.assertIn("extension_container_mismatch", reasons)

    def test_probe_never_likely_fake(self):
        probe = probe_video_bytes(b"\xff\xd8\xff" + b"\x00" * 512)
        self.assertEqual(probe["verdict"], "uncertain")

    @patch("app.services.antifake_service._sfm_execute")
    def test_video_offline_ensemble_source(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        out = check_media(media_type="video", file_name="x.mp4", file_bytes=_FAKE_MP4)
        self.assertEqual(out["source"], "ensemble_video")
        self.assertNotIn(out.get("source"), FORBIDDEN_SOURCES)
        channels = {row["channel"] for row in out.get("sources") or []}
        self.assertIn("deepfake", channels)
        self.assertIn("metadata", channels)
        self.assertIn("probe", channels)
        self.assertNotEqual(out["verdict"], "likely_fake")

    @patch("app.services.antifake_service._sfm_execute")
    def test_probe_blocked_without_deepfake_fake(self, mock_sfm):
        mock_sfm.return_value = {"success": False, "error": "offline"}
        jpeg = b"\xff\xd8\xff" + b"\x00" * 600
        out = ensemble_check_video(file_name="v.mp4", file_bytes=jpeg)
        self.assertEqual(out["source"], "ensemble_video")
        self.assertNotEqual(out["verdict"], "likely_fake")
        self.assertLessEqual(float(out["confidence"]), 0.69)

    @patch("app.services.antifake_video_ensemble.analyze_video_metadata")
    def test_deepfake_local_likely_fake_when_strong_signal(self, mock_meta):
        # RH-F01: no SFM DPS — local metadata channel can still emit likely_fake
        mock_meta.return_value = (["extension_container_mismatch", "jpeg_not_video_container"], 0.72)
        out = ensemble_check_video(file_name="x.mp4", file_bytes=_FAKE_MP4)
        self.assertEqual(out["verdict"], "likely_fake")
        self.assertLessEqual(float(out["confidence"]), 0.78)  # RH-F04 ceiling

    def test_model_card_contract(self):
        self.assertEqual(VIDEO_MODEL_CARD["ensemble_version"], "antifake_video_v2")
        self.assertTrue(VIDEO_MODEL_CARD["channels"]["probe"]["never_likely_fake"])
        self.assertEqual(VIDEO_MODEL_CARD["channels"]["deepfake"]["tier"], "local_ml")
        self.assertEqual(VIDEO_MODEL_CARD["channels"]["onnx"].get("default"), "on")


if __name__ == "__main__":
    unittest.main()
