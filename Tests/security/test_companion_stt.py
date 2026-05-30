# -*- coding: utf-8 -*-
"""Companion server STT — OpenAI proxy + geo-block reason codes."""

from __future__ import annotations

import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from security.services.ai_platform.stt_providers import openai_http as stt


class TestCompanionSTTProxy(unittest.TestCase):
    def test_http_error_403_maps_to_geo_blocked(self):
        self.assertEqual(stt.http_error_reason(HTTPError("url", 403, "Forbidden", {}, io.BytesIO(b""))), "server_stt_geo_blocked")
        self.assertEqual(stt.http_error_reason(HTTPError("url", 451, "Unavailable", {}, io.BytesIO(b""))), "server_stt_geo_blocked")
        self.assertEqual(stt.http_error_reason(HTTPError("url", 500, "Error", {}, io.BytesIO(b""))), "server_stt_provider_error")

    @patch.dict("os.environ", {"COMPANION_STT_OPENAI_HTTPS_PROXY": ""}, clear=False)
    @patch("security.services.ai_platform.stt_providers.openai_http.urlopen")
    def test_direct_openai_success(self, mock_urlopen):
        payload = json.dumps({"text": "hello", "segments": []}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = payload
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *a: None
        mock_urlopen.return_value = mock_resp

        raw = stt.post_openai_multipart(b"body", {"Authorization": "Bearer x"})
        self.assertIn(b"hello", raw)

    @patch.dict("os.environ", {"COMPANION_STT_OPENAI_HTTPS_PROXY": "http://eu-proxy:8080"}, clear=False)
    @patch("security.services.ai_platform.stt_providers.openai_http.build_opener")
    def test_http_proxy_used(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_build_opener.return_value = mock_opener
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"text":"ok"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *a: None
        mock_opener.open.return_value = mock_resp

        stt.post_openai_multipart(b"body", {"Authorization": "Bearer x"})
        mock_build_opener.assert_called_once()
        mock_opener.open.assert_called_once()

    @patch.dict("os.environ", {"COMPANION_STT_OPENAI_HTTPS_PROXY": ""}, clear=False)
    @patch("security.services.ai_platform.stt_providers.openai_http.urlopen")
    def test_direct_openai_403_raises_geo_blocked(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            stt.OPENAI_TRANSCRIPTIONS_URL,
            403,
            "Forbidden",
            {},
            io.BytesIO(b'{"error":"unsupported_country"}'),
        )
        with self.assertRaises(ValueError) as ctx:
            stt.post_openai_multipart(b"body", {"Authorization": "Bearer x"})
        self.assertEqual(str(ctx.exception), "server_stt_geo_blocked")

    @patch.dict("os.environ", {"COMPANION_STT_OPENAI_HTTPS_PROXY": "socks5h://127.0.0.1:1080"}, clear=False)
    @patch("requests.post")
    def test_socks_proxy_403_via_requests(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "unsupported_country"
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError) as ctx:
            stt.post_via_proxy(b"body", {}, proxy="socks5h://127.0.0.1:1080", timeout=5)
        self.assertEqual(str(ctx.exception), "server_stt_geo_blocked")
        mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
