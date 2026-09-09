import asyncio
import inspect
import os

import pytest

os.environ.setdefault("JWT_SECRET", "test-only-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5432/test_database",
)

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.routers import family


class FakeResult:
    def __init__(self, row=None, rowcount=1):
        self._row = row
        self.rowcount = rowcount

    def fetchone(self):
        return self._row


class FakeDB:
    def __init__(
        self,
        *,
        message_row=("FAMILY_A", 22, 2),
        existing_report=None,
        target_role=("child",),
    ):
        self.message_row = message_row
        self.existing_report = existing_report
        self.target_role = target_role
        self.executions = []
        self.commits = 0

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}
        self.executions.append((sql, params))
        if "SELECT family_id, sender_user_id, COALESCE(envelope_version, 1)" in sql:
            return FakeResult(self.message_row)
        if "SELECT family_id, sender_user_id FROM family_chat_messages" in sql:
            return FakeResult(self.message_row[:2])
        if "SELECT role FROM family_members" in sql:
            return FakeResult(self.target_role)
        if "SELECT 1 FROM families" in sql:
            return FakeResult(None)
        if "SELECT id FROM family_chat_reports" in sql:
            return FakeResult(self.existing_report)
        return FakeResult()

    def commit(self):
        self.commits += 1


def install_database(monkeypatch, db):
    def generator():
        yield db

    monkeypatch.setattr(family, "get_postgres_db", generator)
    monkeypatch.setattr(family, "_ensure_family_chat_table", lambda _: None)
    monkeypatch.setattr(family, "_ensure_family_chat_moderation_tables", lambda _: None)


def endpoint(function):
    return inspect.unwrap(function)


def test_report_endpoint_queues_metadata_and_audit(monkeypatch):
    db = FakeDB()
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_belongs_to_family", lambda *_: True)

    response = asyncio.run(
        endpoint(family.family_chat_report_message)(
            request=None,
            payload=family.ReportFamilyChatMessageRequest(
                messageId="MSG_1",
                category="harassment",
                note="validated but never persisted",
            ),
            current_user={"user_id": 11},
        )
    )

    assert response.success is True
    assert response.actionId.startswith("RPT_")
    assert db.commits == 1
    report_insert = next(
        item for item in db.executions if "INSERT INTO family_chat_reports" in item[0]
    )
    assert report_insert[1]["reporter_user_id"] == 11
    assert report_insert[1]["reported_user_id"] == 22
    assert "note" not in report_insert[0].lower()
    assert any(
        "INSERT INTO family_chat_moderation_audit" in sql
        for sql, _ in db.executions
    )


def test_report_endpoint_rejects_cross_family_idor_without_writes(monkeypatch):
    db = FakeDB()
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_belongs_to_family", lambda *_: False)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            endpoint(family.family_chat_report_message)(
                request=None,
                payload=family.ReportFamilyChatMessageRequest(
                    messageId="MSG_OTHER_FAMILY",
                    category="spam",
                ),
                current_user={"user_id": 11},
            )
        )

    assert error.value.status_code == 403
    assert db.commits == 0
    assert not any(sql.startswith("INSERT") for sql, _ in db.executions)


def test_report_endpoint_rejects_reporting_own_message(monkeypatch):
    db = FakeDB(message_row=("FAMILY_A", 11, 2))
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_belongs_to_family", lambda *_: True)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            endpoint(family.family_chat_report_message)(
                request=None,
                payload=family.ReportFamilyChatMessageRequest(
                    messageId="MSG_OWN",
                    category="other",
                ),
                current_user={"user_id": 11},
            )
        )

    assert error.value.status_code == 400
    assert db.commits == 0


def test_parent_can_restrict_child_and_reason_is_not_persisted(monkeypatch):
    db = FakeDB()
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_can_manage_family_roster", lambda *_: True)

    response = asyncio.run(
        endpoint(family.family_chat_restrict_member)(
            request=None,
            payload=family.RestrictFamilyChatMemberRequest(
                messageId="MSG_1",
                restricted=True,
                reason="free-form text must not reach storage",
            ),
            current_user={"user_id": 11},
        )
    )

    assert response.success is True
    assert response.actionId.startswith("RST_")
    restriction_insert = next(
        item
        for item in db.executions
        if "INSERT INTO family_chat_restrictions" in item[0]
    )
    assert "reason" not in restriction_insert[0].lower()
    assert "reason" not in restriction_insert[1]
    assert restriction_insert[1]["target_user_id"] == 22
    assert any(
        params.get("action") == "member_restricted"
        for _, params in db.executions
    )


def test_non_manager_cannot_restrict_member(monkeypatch):
    db = FakeDB()
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_can_manage_family_roster", lambda *_: False)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            endpoint(family.family_chat_restrict_member)(
                request=None,
                payload=family.RestrictFamilyChatMemberRequest(
                    messageId="MSG_1",
                    restricted=True,
                ),
                current_user={"user_id": 11},
            )
        )

    assert error.value.status_code == 403
    assert db.commits == 0
    assert not any(
        "INSERT INTO family_chat_restrictions" in sql
        for sql, _ in db.executions
    )


def test_manager_cannot_restrict_departed_member(monkeypatch):
    db = FakeDB(target_role=None)
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_can_manage_family_roster", lambda *_: True)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            endpoint(family.family_chat_restrict_member)(
                request=None,
                payload=family.RestrictFamilyChatMemberRequest(messageId="MSG_1"),
                current_user={"user_id": 11},
            )
        )

    assert error.value.status_code == 404
    assert db.commits == 0


def test_report_endpoint_returns_rate_limit_after_ten_requests(monkeypatch):
    db = FakeDB()
    install_database(monkeypatch, db)
    monkeypatch.setattr(family, "_actor_belongs_to_family", lambda *_: True)
    app = FastAPI()
    app.state.limiter = family.limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.include_router(family.router)
    app.dependency_overrides[family.get_current_user] = lambda: {"user_id": 11}
    client = TestClient(app)
    payload = {"messageId": "MSG_RATE_LIMIT", "category": "spam"}

    family.limiter.reset()
    try:
        for _ in range(10):
            response = client.post("/api/family/chat/moderation/report", json=payload)
            assert response.status_code == 200

        limited = client.post("/api/family/chat/moderation/report", json=payload)
        assert limited.status_code == 429
        assert limited.json()["error"] == "Rate limit exceeded: 10 per 1 minute"
    finally:
        family.limiter.reset()
