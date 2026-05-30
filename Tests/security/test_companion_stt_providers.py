# -*- coding: utf-8
"""STT provider router + Yandex SpeechKit."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from security.services.ai_platform.stt_providers import router
from security.services.ai_platform.stt_providers import yandex_speechkit


class TestSTTRouter(unittest.TestCase):
    @patch.dict("os.environ", {"COMPANION_STT_PROVIDER": "yandex"}, clear=False)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.configured", return_value=True)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.transcribe", return_value=("hello", 0.9))
    def test_yandex_provider_direct(self, _transcribe, _configured):
        result = router.transcribe_with_fallback(b"wav", content_type="audio/wav", language="ru")
        self.assertEqual(result["text"], "hello")
        self.assertEqual(result["provider"], "yandex_speechkit")

    @patch.dict(
        "os.environ",
        {
            "COMPANION_STT_PROVIDER": "auto",
            "COMPANION_STT_FALLBACK_PROVIDER": "openai_whisper",
        },
        clear=False,
    )
    @patch("security.services.ai_platform.stt_providers.openai_whisper.configured", return_value=True)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.configured", return_value=True)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.transcribe", side_effect=ValueError("empty_transcript"))
    @patch("security.services.ai_platform.stt_providers.openai_whisper.transcribe", return_value=("backup", 0.8))
    def test_auto_empty_transcript_does_not_fallback(self, _o, _y, _yc, _oc):
        with self.assertRaises(ValueError) as ctx:
            router.transcribe_with_fallback(b"wav", content_type="audio/wav", language="ru")
        self.assertEqual(str(ctx.exception), "empty_transcript")

    @patch.dict(
        "os.environ",
        {
            "COMPANION_STT_PROVIDER": "auto",
            "COMPANION_STT_FALLBACK_PROVIDER": "openai_whisper",
        },
        clear=False,
    )
    @patch("security.services.ai_platform.stt_providers.openai_whisper.configured", return_value=True)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.configured", return_value=True)
    @patch(
        "security.services.ai_platform.stt_providers.yandex_speechkit.transcribe",
        side_effect=ValueError("server_stt_provider_error"),
    )
    @patch("security.services.ai_platform.stt_providers.openai_whisper.transcribe", return_value=("backup", 0.8))
    def test_auto_falls_back_to_openai_on_provider_error(self, _o, _y, _yc, _oc):
        result = router.transcribe_with_fallback(b"wav", content_type="audio/wav", language="ru")
        self.assertEqual(result["text"], "backup")
        self.assertEqual(result["provider"], "openai_whisper")

    @patch.dict("os.environ", {"COMPANION_STT_PROVIDER": "auto"}, clear=False)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.configured", return_value=True)
    @patch("security.services.ai_platform.stt_providers.openai_whisper.configured", return_value=False)
    def test_active_provider_yandex(self, _oc, _yc):
        self.assertEqual(router.active_provider_name(), "yandex_speechkit")


class TestYandexSpeechKit(unittest.TestCase):
    @patch.dict("os.environ", {"YANDEX_SPEECHKIT_API_KEY": "test-key"}, clear=False)
    @patch("security.services.ai_platform.stt_providers.yandex_speechkit.urlopen")
    def test_yandex_json_result(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"result":"privet"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *a: None
        mock_urlopen.return_value = mock_resp

        text, conf = yandex_speechkit.transcribe(b"\x00" * 100, content_type="audio/wav", language="ru")
        self.assertEqual(text, "privet")
        self.assertGreater(conf, 0.5)


if __name__ == "__main__":
    unittest.main()
