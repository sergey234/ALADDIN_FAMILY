"""l360 stage 4 — server location history: retention by plan, viewer rules, purge."""
from __future__ import annotations

import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

import app.services.family_location_history as hist


class _Result:
    def __init__(self, one=None, many=None, rowcount=0):
        self._one = one
        self._many = many or []
        self.rowcount = rowcount

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
def _plain_sql(monkeypatch):
    monkeypatch.setattr(hist, "text", lambda sql: sql)
    monkeypatch.setattr(hist, "_index_ready", True)
    monkeypatch.setattr(hist, "_last_global_purge", float("inf"))


def _stub_levels(monkeypatch, levels):
    stub = types.ModuleType("app.services.antifake_web_premium")
    stub.subscription_trial_snapshot_from_db = lambda db, uid: levels.get(uid, ("free", None, None))
    monkeypatch.setitem(sys.modules, "app.services.antifake_web_premium", stub)


def test_hours_per_plan():
    assert hist.retention_hours_for_level("free") == 24
    assert hist.retention_hours_for_level("personal") == 24
    assert hist.retention_hours_for_level("trial") == 7 * 24
    assert hist.retention_hours_for_level("family") == 7 * 24
    assert hist.retention_hours_for_level("premium") == 30 * 24
    assert hist.retention_hours_for_level("premium_6m") == 30 * 24
    assert hist.retention_hours_for_level("weird") == 24
    assert hist.retention_hours_for_level(None) == 24


def test_free_member_gets_owner_family_window(monkeypatch):
    _stub_levels(monkeypatch, {1: ("family", "family", None)})
    db = _FakeDB([_Result(many=[(1,)])])
    assert hist.retention_hours_for_user(db, 2) == 7 * 24


def test_personal_owner_does_not_extend_family(monkeypatch):
    _stub_levels(monkeypatch, {1: ("personal", "personal", None)})
    db = _FakeDB([_Result(many=[(1,)])])
    assert hist.retention_hours_for_user(db, 2) == 24


def test_own_premium_wins_over_free_owner(monkeypatch):
    _stub_levels(monkeypatch, {2: ("premium", "premium", None)})
    db = _FakeDB([_Result(many=[(1,)])])
    assert hist.retention_hours_for_user(db, 2) == 30 * 24


def test_purge_user_uses_cutoff():
    now = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)
    db = _FakeDB([_Result(rowcount=5)])
    assert hist.purge_user(db, 7, 24, now=now) == 5
    sql, params = db.statements[0]
    assert sql.startswith("DELETE FROM location_history WHERE user_id = :uid")
    assert params == {"uid": 7, "cutoff": now - timedelta(hours=24)}


def test_purge_all_caps_at_30_days_then_applies_plan(monkeypatch):
    _stub_levels(monkeypatch, {})
    now = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)
    db = _FakeDB([
        _Result(rowcount=3),            # over 30 days
        _Result(many=[(9,)]),           # users with points older than 24 h
        _Result(many=[]),               # user 9 has no family owner
        _Result(rowcount=4),            # user 9 free → 24 h
    ])
    stats = hist.purge_all(db, now=now)
    assert stats == {"over_max": 3, "by_plan": 4, "users_checked": 1}
    assert db.statements[0][1] == {"cutoff": now - timedelta(days=30)}
    assert db.statements[3][1] == {"uid": 9, "cutoff": now - timedelta(hours=24)}
    assert db.commits == 1


def test_enforce_after_write_never_raises(monkeypatch):
    def boom(db, uid):
        raise RuntimeError("db down")

    monkeypatch.setattr(hist, "retention_hours_for_user", boom)
    db = _FakeDB([])
    hist.enforce_after_write(db, 1)
    assert db.rollbacks == 1


def test_child_sees_self_and_parents_only():
    assert hist.viewer_may_see("parent", "1", "5", ["1"])
    assert hist.viewer_may_see(None, "1", "5", [])
    assert hist.viewer_may_see("child", "3", "3", ["1"])
    assert hist.viewer_may_see("teenager", "3", "1", ["1"])
    assert not hist.viewer_may_see("child", "3", "4", ["1"])


def test_thin_keeps_ends_and_limit():
    pts = [{"i": i} for i in range(1000)]
    out = hist.thin(pts, limit=10)
    assert len(out) == 10
    assert out[0]["i"] == 0 and out[-1]["i"] == 999
    assert hist.thin(pts[:5], limit=10) == pts[:5]
    assert hist.thin(pts, limit=1) == [pts[-1]]
    assert hist.thin(pts, limit=0) == []
