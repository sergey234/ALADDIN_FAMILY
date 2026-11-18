"""l360 1Б.3 — Personal monthly cap on heavy Antifake checks; 1Б.6 — family owner sharing."""
from __future__ import annotations

import sys
import types
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

import app.services.antifake_family_entitlement as share
import app.services.antifake_personal_quota as quota


class _Result:
    def __init__(self, one=None, many=None):
        self._one = one
        self._many = many or []

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._many


class _FakeDB:
    def __init__(self, results):
        self._results = list(results)
        self.statements = []
        self.commits = 0
        self.rollbacks = 0

    def execute(self, stmt, params=None):
        self.statements.append((str(stmt), params or {}))
        return self._results.pop(0) if self._results else _Result()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


@pytest.fixture(autouse=True)
def _table_ready(monkeypatch):
    # Other backend_tests replace sys.modules["sqlalchemy"] with a MagicMock; keep SQL as plain strings.
    monkeypatch.setattr(quota, "text", lambda sql: sql)
    monkeypatch.setattr(share, "text", lambda sql: sql)
    monkeypatch.setattr(quota, "_table_ready", True)
    monkeypatch.delenv("ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT", raising=False)


def _stub_levels(monkeypatch, levels):
    stub = types.ModuleType("app.services.antifake_web_premium")
    stub.subscription_trial_snapshot_from_db = lambda db, uid: levels.get(uid, ("free", None, None))
    monkeypatch.setitem(sys.modules, "app.services.antifake_web_premium", stub)


def test_month_key_uses_moscow_time():
    late_utc = datetime(2026, 11, 30, 22, 0, tzinfo=timezone.utc)
    assert quota.month_key(late_utc) == "2026-12"
    assert quota.month_key(datetime(2026, 11, 30, 20, 0, tzinfo=timezone.utc)) == "2026-11"


def test_resets_at_rolls_year():
    assert quota.resets_at(datetime(2026, 12, 10, tzinfo=timezone.utc)) == "2027-01-01"
    assert quota.resets_at(datetime(2026, 11, 10, tzinfo=timezone.utc)) == "2026-12-01"


def test_limit_env(monkeypatch):
    assert quota.personal_monthly_limit() == 30
    monkeypatch.setenv("ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT", "0")
    assert quota.personal_monthly_limit() == 0
    monkeypatch.setenv("ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT", "oops")
    assert quota.personal_monthly_limit() == 30


def test_text_checks_never_counted(monkeypatch):
    monkeypatch.setattr(quota, "is_quota_limited", lambda user, db: True)
    db = _FakeDB([])
    assert quota.consume_heavy_check({"id": 7}, db, "text") is False
    assert db.statements == []


def test_unlimited_plan_not_counted(monkeypatch):
    monkeypatch.setattr(quota, "is_quota_limited", lambda user, db: False)
    db = _FakeDB([])
    assert quota.consume_heavy_check({"id": 7}, db, "video") is False
    assert db.statements == []


def test_personal_heavy_counted(monkeypatch):
    monkeypatch.setattr(quota, "is_quota_limited", lambda user, db: True)
    db = _FakeDB([_Result(one=(5,))])
    assert quota.consume_heavy_check({"id": 7}, db, "audio") is True
    sql, params = db.statements[0]
    assert "ON CONFLICT" in sql and params["lim"] == 30 and params["uid"] == 7


def test_personal_over_limit_gets_429(monkeypatch):
    monkeypatch.setattr(quota, "is_quota_limited", lambda user, db: True)
    db = _FakeDB([_Result(one=None)])
    with pytest.raises(HTTPException) as exc:
        quota.consume_heavy_check({"id": 7}, db, "call", now=datetime(2026, 11, 18, tzinfo=timezone.utc))
    assert exc.value.status_code == 429
    assert exc.value.detail == {
        "error": "monthly_quota_exceeded",
        "limit": 30,
        "used": 30,
        "resets_at": "2026-12-01",
    }


def test_is_quota_limited_only_for_own_personal(monkeypatch):
    monkeypatch.setattr(share, "family_owner_grants_antifake", lambda db, uid: False)
    _stub_levels(monkeypatch, {1: ("personal", None, None), 2: ("family", None, None), 3: ("premium", None, None)})
    db = _FakeDB([])
    assert quota.is_quota_limited({"id": 1}, db) is True
    assert quota.is_quota_limited({"id": 2}, db) is False
    assert quota.is_quota_limited({"id": 3}, db) is False


def test_personal_in_family_owner_plan_is_unlimited(monkeypatch):
    monkeypatch.setattr(share, "family_owner_grants_antifake", lambda db, uid: True)
    _stub_levels(monkeypatch, {1: ("personal", None, None)})
    assert quota.is_quota_limited({"id": 1}, _FakeDB([])) is False


def test_quota_disabled_by_env(monkeypatch):
    monkeypatch.setenv("ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT", "0")
    assert quota.is_quota_limited({"id": 1}, _FakeDB([])) is False


def test_sharing_levels():
    for level in ("family", "premium", "trial", "Trial_Premium", "premium_3m"):
        assert share.level_shares_with_family(level) is True
    for level in ("personal", "free", "", None):
        assert share.level_shares_with_family(level) is False


def test_member_of_family_owner_grants(monkeypatch):
    _stub_levels(monkeypatch, {100: ("family", None, None)})
    db = _FakeDB([_Result(many=[("fam-1",)]), _Result(one=(100,))])
    assert share.family_owner_grants_antifake(db, 5) is True


def test_member_of_personal_owner_denied(monkeypatch):
    _stub_levels(monkeypatch, {100: ("personal", None, None)})
    db = _FakeDB([_Result(many=[("fam-1",)]), _Result(one=(100,))])
    assert share.family_owner_grants_antifake(db, 5) is False


def test_owner_own_family_does_not_self_grant(monkeypatch):
    _stub_levels(monkeypatch, {5: ("family", None, None)})
    db = _FakeDB([_Result(many=[("fam-1",)]), _Result(one=(5,))])
    assert share.family_owner_grants_antifake(db, 5) is False


def test_family_lookup_failure_rolls_back(monkeypatch):
    _stub_levels(monkeypatch, {})

    class _Boom(_FakeDB):
        def execute(self, stmt, params=None):
            raise RuntimeError("db down")

    db = _Boom([])
    assert share.family_owner_grants_antifake(db, 5) is False
    assert db.rollbacks == 1
