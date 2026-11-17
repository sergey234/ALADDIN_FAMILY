"""Trial grant gate: server ledger + Apple DeviceCheck bit0 (fail-open)."""

import os
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.app.services import apple_device_check as dc  # noqa: E402
from backend.app.services import subscription_service as svc_mod  # noqa: E402
from backend.app.models.subscription import TrialDeviceRegisterRequest, TrialInfo  # noqa: E402


class ParseQueryResponseTests(unittest.TestCase):
    def test_never_set_means_not_used(self):
        self.assertIs(dc.parse_query_response(200, "Failed to find bit state"), False)

    def test_bit0_true_means_used(self):
        self.assertIs(dc.parse_query_response(200, '{"bit0":true,"bit1":false}'), True)

    def test_bit0_false(self):
        self.assertIs(dc.parse_query_response(200, '{"bit0":false,"bit1":false}'), False)

    def test_apple_error_is_unknown(self):
        self.assertIsNone(dc.parse_query_response(400, "Missing or badly formatted authorization token"))
        self.assertIsNone(dc.parse_query_response(200, "not json"))


class DeviceCheckClientTests(unittest.TestCase):
    def setUp(self):
        dc._cached_jwt = None
        dc._cached_jwt_at = 0.0

    def test_not_configured_is_unknown_and_never_calls_apple(self):
        with mock.patch.dict(os.environ, {"APPLE_DEVICECHECK_KEY_ID": "", "APPLE_DEVICECHECK_KEY_PATH": ""}):
            with mock.patch("httpx.post") as post:
                self.assertIsNone(dc.trial_already_used("tok"))
                self.assertFalse(dc.mark_trial_used("tok"))
                post.assert_not_called()

    def test_missing_token_is_unknown(self):
        self.assertIsNone(dc.trial_already_used(None))
        self.assertIsNone(dc.trial_already_used("  "))

    def test_signed_query_and_update(self):
        import jwt
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        key = ec.generate_private_key(ec.SECP256R1())
        pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        with tempfile.NamedTemporaryFile("wb", suffix=".p8", delete=False) as fh:
            fh.write(pem)
            key_path = fh.name
        calls = []

        def fake_post(url, json=None, headers=None, timeout=None):
            calls.append((url, json, headers))
            body = '{"bit0":true}' if url.endswith("query_two_bits") else ""
            return types.SimpleNamespace(status_code=200, text=body)

        env = {
            "APPLE_DEVICECHECK_KEY_ID": "KEYID12345",
            "APPLE_DEVICECHECK_TEAM_ID": "B3WGHSWL79",
            "APPLE_DEVICECHECK_KEY_PATH": key_path,
            "APPLE_DEVICECHECK_ENV": "development",
        }
        try:
            with mock.patch.dict(os.environ, env), mock.patch("httpx.post", side_effect=fake_post):
                self.assertIs(dc.trial_already_used("tok"), True)
                self.assertTrue(dc.mark_trial_used("tok"))
        finally:
            os.unlink(key_path)

        self.assertEqual(calls[0][0], "https://api.development.devicecheck.apple.com/v1/query_two_bits")
        self.assertEqual(calls[1][1]["bit0"], True)
        bearer = calls[0][2]["Authorization"].split(" ", 1)[1]
        self.assertEqual(jwt.get_unverified_header(bearer)["kid"], "KEYID12345")
        claims = jwt.decode(bearer, key.public_key(), algorithms=["ES256"])
        self.assertEqual(claims["iss"], "B3WGHSWL79")

    def test_network_error_is_unknown(self):
        with mock.patch.object(dc, "_config", return_value={"host": "https://x", "key_id": "k", "team_id": "t", "key_path": "p"}), \
                mock.patch.object(dc, "_auth_jwt", return_value="jwt"), \
                mock.patch("httpx.post", side_effect=OSError("down")):
            self.assertIsNone(dc.trial_already_used("tok"))


class _FakeRepo:
    existing = None

    def __init__(self, db):
        self.created = []

    def get_subscription_by_device(self, device_id):
        return _FakeRepo.existing

    def create_subscription(self, data):
        return types.SimpleNamespace(**data)

    def update_subscription(self, row, data):
        merged = dict(vars(row))
        merged.update(data)
        return types.SimpleNamespace(**merged)


class TrialGrantDecisionTests(unittest.TestCase):
    def _run(self, existing=None, dc_used=None, token="tok"):
        _FakeRepo.existing = existing
        S = svc_mod.SubscriptionService
        marks = []
        self.query = mock.Mock(return_value=dc_used)
        with mock.patch.object(svc_mod, "SubscriptionRepository", _FakeRepo), \
                mock.patch.object(S, "_ensure_user_for_device", return_value="1521"), \
                mock.patch.object(S, "_sync_user_subscription_level"), \
                mock.patch.object(S, "_map_to_payload", side_effect=lambda row: row), \
                mock.patch.object(svc_mod.apple_device_check, "trial_already_used", self.query), \
                mock.patch.object(svc_mod.apple_device_check, "mark_trial_used", side_effect=lambda t: marks.append(t) or True):
            req = TrialDeviceRegisterRequest(
                device_id="DEV-1", trial_info=TrialInfo(duration_days=14), device_check_token=token
            )
            return S.register_device_with_trial(db=mock.MagicMock(), request=req), marks

    def test_new_device_gets_trial_and_bit_is_set(self):
        row, marks = self._run(dc_used=False)
        self.assertEqual(row.level, "trial")
        self.assertEqual(marks, ["tok"])

    def test_devicecheck_bit_denies_trial_and_records_ledger(self):
        row, marks = self._run(dc_used=True)
        self.assertEqual(row.level, "free")
        self.assertIsNotNone(row.trial_end_date)
        self.assertEqual(marks, [])

    def test_apple_unavailable_falls_back_to_ledger_grant(self):
        row, marks = self._run(dc_used=None)
        self.assertEqual(row.level, "trial")
        self.assertEqual(marks, [])

    def test_used_ledger_stays_free_without_asking_apple(self):
        past = types.SimpleNamespace(
            user_id="1521", level="trial", trial_end_date=datetime.utcnow() - timedelta(days=1)
        )
        row, _ = self._run(existing=past, dc_used=False)
        self.query.assert_not_called()
        self.assertEqual(row.level, "free")

    def test_required_token_missing_stays_free_without_ledger_mark(self):
        with mock.patch.object(svc_mod.apple_device_check, "token_required", return_value=True):
            row, marks = self._run(dc_used=None, token=None)
        self.assertEqual(row.level, "free")
        self.assertIsNone(getattr(row, "trial_end_date", None))
        self.assertEqual(marks, [])

    def test_request_accepts_snake_case_token(self):
        req = TrialDeviceRegisterRequest.model_validate(
            {"device_id": "D", "trial_info": {"duration_days": 14}, "device_check_token": "abc"}
        )
        self.assertEqual(req.device_check_token, "abc")


if __name__ == "__main__":
    unittest.main()
