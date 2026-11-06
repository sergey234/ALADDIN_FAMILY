"""Step A: recovery-login shield — UX unchanged, rate limit + family exists."""
from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_rate_limit():
    path = ROOT / "app" / "services" / "web_auth_rate_limit.py"
    spec = importlib.util.spec_from_file_location("web_auth_rate_limit_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # FastAPI may be heavy; stub minimal Request/HTTPException if import fails.
    try:
        spec.loader.exec_module(mod)
    except ModuleNotFoundError:
        fastapi = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, status_code=400, detail=None):
                self.status_code = status_code
                self.detail = detail

        class Request:
            pass

        fastapi.HTTPException = HTTPException
        fastapi.Request = Request
        sys.modules["fastapi"] = fastapi
        spec.loader.exec_module(mod)
    return mod


def _load_normalize():
    """Load only normalize helpers without importing full auth_router (jwt/db)."""
    text = (ROOT / "app" / "routers" / "auth_router.py").read_text(encoding="utf-8")
    start = text.index("def _normalize_family_id")
    end = text.index("def _ensure_db_user_for_device")
    ns: dict = {"re": __import__("re")}
    exec(text[start:end], ns)
    return ns["_normalize_family_id"], ns["_compact_invite_value"]


class TestNormalize(unittest.TestCase):
    def test_fam_underscore_and_dash(self):
        norm, compact = _load_normalize()
        self.assertEqual(norm("FAM_ABCD1234EFGH"), "FAM_ABCD1234EFGH")
        self.assertEqual(norm("fam-abcd-1234-efgh"), "FAM_ABCD1234EFGH")
        self.assertEqual(compact("FAM_ABCD1234EFGH"), compact("FAM-ABCD-1234-EFGH"))

    def test_recovery_matches_product_contract(self):
        _, compact = _load_normalize()
        family = "FAM_ABCD1234EFGH"
        # iOS often sends recovery_code == family_id
        self.assertEqual(compact(family), compact(family))
        # Manual invite form still matches compact family (current product UX)
        self.assertEqual(compact(family), compact("FAM-ABCD-1234-EFGH"))
        # Random invite_token must NOT match family compact
        self.assertNotEqual(compact(family), compact("xYz_invite_token_not_family"))


class TestRecoveryRateLimit(unittest.TestCase):
    def setUp(self):
        self.mod = _load_rate_limit()
        self.mod._buckets.clear()

    def _req(self, ip="203.0.113.9"):
        req = MagicMock()
        req.headers = {}
        req.client = MagicMock()
        req.client.host = ip
        return req

    def test_allows_honest_retries(self):
        for _ in range(10):
            n = self.mod.check_recovery_login_ip_limit(self._req(), limit=40)
            self.assertGreaterEqual(n, 1)

    def test_blocks_after_budget(self):
        req = self._req()
        for _ in range(5):
            self.mod.check_recovery_login_ip_limit(req, limit=5)
        with self.assertRaises(Exception) as ctx:
            self.mod.check_recovery_login_ip_limit(req, limit=5)
        exc = ctx.exception
        self.assertEqual(getattr(exc, "status_code", None), 429)
        detail = getattr(exc, "detail", {})
        self.assertEqual(detail.get("bucket"), "recovery_login")
        # RU message for the app / support — not a cryptic error
        self.assertIn("попыток", detail.get("message", ""))

    def test_separate_ips_independent(self):
        self.mod.check_recovery_login_ip_limit(self._req("1.1.1.1"), limit=2)
        self.mod.check_recovery_login_ip_limit(self._req("1.1.1.1"), limit=2)
        # other IP still ok
        self.mod.check_recovery_login_ip_limit(self._req("8.8.8.8"), limit=2)


if __name__ == "__main__":
    unittest.main()
