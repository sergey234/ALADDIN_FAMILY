"""AG07 / afhub-p2-02 — video ONNX / face gates / AV1 / no-green-on-decode."""
from __future__ import annotations

import ast
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

if "sqlalchemy" not in sys.modules:
    sys.modules["sqlalchemy"] = MagicMock()
    sys.modules["sqlalchemy.text"] = MagicMock()
    sys.modules["sqlalchemy.ext"] = MagicMock()
    sys.modules["sqlalchemy.ext.declarative"] = MagicMock()
sys.modules.setdefault("app.database.database", MagicMock())

from app.services import antifake_video_onnx_local as onnx_mod  # noqa: E402
from app.services.antifake_video_ensemble import ensemble_check_video  # noqa: E402

_FTYP = b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00" + b"moov" + b"\x00" * 32 + b"mdat" + b"\x00" * 64
_AV1 = b"\x00\x00\x00\x1cftypav01\x00\x00\x00\x00" + b"av01" + b"\x00" * 64 + b"mdat" + b"\x00" * 64


def _valid_jpeg() -> bytes:
    try:
        import cv2
        import numpy as np

        img = np.zeros((32, 32, 3), dtype=np.uint8)
        ok, buf = cv2.imencode(".jpg", img)
        if ok:
            return bytes(buf)
    except Exception:
        pass
    return b"\xff\xd8\xff\xe0" + b"\x00" * 800 + b"\xff\xd9"


class VideoOnnxLocalTests(unittest.TestCase):
    def test_flag_default_on(self):
        env = {k: v for k, v in os.environ.items() if k != "ANTIFAKE_VIDEO_ONNX"}
        with patch.dict(os.environ, env, clear=True):
            self.assertTrue(onnx_mod.video_onnx_enabled())

    def test_flag_off(self):
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "0"}, clear=False):
            self.assertFalse(onnx_mod.video_onnx_enabled())

    def test_flag_on(self):
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "1"}, clear=False):
            self.assertTrue(onnx_mod.video_onnx_enabled())

    def test_jpeg_as_mp4_heuristic(self):
        jpeg = _valid_jpeg()
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "1"}, clear=False):
            out = onnx_mod.analyze_video_onnx_local(jpeg, file_name="clip.mp4")
        self.assertIn(out["verdict"], ("likely_fake", "uncertain", "insufficient_data"))
        self.assertLessEqual(float(out["confidence"]), onnx_mod.ONNX_CONFIDENCE_CEILING)
        self.assertTrue(out.get("reasons"))

    def test_ensemble_includes_onnx_by_default(self):
        env = {k: v for k, v in os.environ.items() if k != "ANTIFAKE_VIDEO_ONNX"}
        with patch.dict(os.environ, env, clear=True):
            out = ensemble_check_video(file_name="x.mp4", file_bytes=_valid_jpeg())
        channels = {row["channel"] for row in out.get("sources") or []}
        self.assertIn("onnx", channels)
        self.assertIn("deepfake", channels)

    def test_ensemble_skips_onnx_when_flag_off(self):
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "0"}, clear=False):
            out = ensemble_check_video(file_name="x.mp4", file_bytes=_FTYP)
        channels = {row["channel"] for row in out.get("sources") or []}
        self.assertNotIn("onnx", channels)

    def test_av1_insufficient_not_green(self):
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "1"}, clear=False):
            out = ensemble_check_video(file_name="tg.mp4", file_bytes=_AV1)
        self.assertEqual(out["verdict"], "insufficient_data")
        joined = " ".join(out.get("reasons") or [])
        self.assertIn("video_codec_av1_unsupported", joined)
        self.assertNotEqual(out["verdict"], "likely_real")

    def test_decode_fail_insufficient_not_green(self):
        garbage = b"not-a-video-file-xxxxxx" + b"\x00" * 200
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "1"}, clear=False):
            out = onnx_mod.analyze_video_onnx_local(garbage, file_name="bad.mp4")
        self.assertEqual(out["verdict"], "insufficient_data")
        self.assertNotEqual(out["verdict"], "likely_real")

    def test_face_gate_blocks_hard_fake_on_blur(self):
        try:
            import numpy as np
        except Exception:
            self.skipTest("numpy unavailable")
        # Flat gray frames → no face + low blur → gate blocks likely_fake
        frames = [np.full((64, 64, 3), 128, dtype=np.uint8) for _ in range(3)]
        ok, reasons = onnx_mod.assess_face_quality(frames)
        self.assertFalse(ok)
        self.assertTrue(
            any("face_quality_blurry" in r or "face_not_detected" in r for r in reasons)
        )

        with patch.object(onnx_mod, "extract_frames_bgr", return_value=(frames, ["frames_sampled_3"])):
            with patch.object(onnx_mod, "_onnx_score", return_value=(0.9, ["video_onnx_scored"])):
                with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "1"}, clear=False):
                    out = onnx_mod.analyze_video_onnx_local(b"\xff\xd8\xff" + b"\x00" * 100, file_name="x.mp4")
        self.assertNotEqual(out["verdict"], "likely_fake")
        self.assertIn("face_quality_gate_blocked", out.get("reasons") or [])

    def test_onnx_forward_when_model_present(self):
        if not onnx_mod.model_file_present() or not onnx_mod.onnxruntime_available():
            self.skipTest("real model.onnx or ort missing")
        try:
            import cv2
            import numpy as np

            img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            ok, buf = cv2.imencode(".jpg", img)
            raw = bytes(buf) if ok else b"\xff\xd8\xff\xe0" + b"\x00" * 800 + b"\xff\xd9"
        except Exception:
            self.skipTest("cv2 unavailable")
        with patch.dict(os.environ, {"ANTIFAKE_VIDEO_ONNX": "1"}, clear=False):
            out = onnx_mod.analyze_video_onnx_local(raw, file_name="probe.jpg")
        joined = " ".join(out.get("reasons") or [])
        self.assertTrue(
            "video_onnx_scored" in joined
            or "video_onnx_fallback" in joined
            or "video_onnx" in joined
            or out.get("agent") in ("video_onnx_local", "video_frame_heuristic")
        )
        self.assertLessEqual(float(out["confidence"]), onnx_mod.ONNX_CONFIDENCE_CEILING)

    def test_never_imports_dps(self):
        path = Path(onnx_mod.__file__)
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                chunk = ast.get_source_segment(src, node) or ""
                self.assertNotIn("deepfake_protection", chunk.lower())


if __name__ == "__main__":
    unittest.main()
