"""M-03 / M-04 security tests for antifake."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.antifake_security import (
    AntifakeSecurityError,
    assert_upload_path_under_root,
    redact_text_for_log,
    validate_check_url,
    validate_media_upload,
)


class AntifakeSecurityTests(unittest.TestCase):
    def test_blocks_private_url(self):
        with self.assertRaises(AntifakeSecurityError):
            validate_check_url("http://127.0.0.1/admin")
        with self.assertRaises(AntifakeSecurityError):
            validate_check_url("http://169.254.169.254/latest/meta-data")

    def test_blocks_file_scheme(self):
        with self.assertRaises(AntifakeSecurityError):
            validate_check_url("file:///etc/passwd")

    def test_allows_public_https(self):
        self.assertTrue(validate_check_url("https://example.com/path").startswith("https://"))

    def test_redact_text_never_contains_raw(self):
        secret = "переведите деньги срочно 12345"
        redacted = redact_text_for_log(secret)
        self.assertNotIn(secret, redacted)
        self.assertIn("sha256:", redacted)

    def test_upload_path_escape_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "uploads"
            root.mkdir()
            outside = Path(tmp) / "evil.bin"
            outside.write_bytes(b"x")
            with self.assertRaises(AntifakeSecurityError):
                assert_upload_path_under_root(outside, root)

    def test_media_upload_rejects_traversal_name(self):
        with self.assertRaises(AntifakeSecurityError):
            validate_media_upload(
                job_type="audio",
                file_name="../etc/passwd.wav",
                file_bytes=b"RIFF",
                content_type="audio/wav",
            )


if __name__ == "__main__":
    unittest.main()
