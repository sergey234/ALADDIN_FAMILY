import pytest

from app.routers.family_chat_moderation import ModerationValidationError
from scripts.family_chat_moderation_admin import decide_report


class FakeResult:
    def __init__(self, row=None, rowcount=1):
        self.row = row
        self.rowcount = rowcount

    def mappings(self):
        return self

    def first(self):
        return self.row


class FakeConnection:
    def __init__(self, report):
        self.report = report
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}
        self.executions.append((sql, params))
        if "FROM family_chat_reports" in sql and "FOR UPDATE" in sql:
            return FakeResult(self.report)
        return FakeResult(rowcount=1)


class FakeEngine:
    def __init__(self, report):
        self.connection = FakeConnection(report)

    def begin(self):
        return self.connection


def report(status="pending"):
    return {
        "id": "RPT_1",
        "family_id": "FAMILY_A",
        "reported_user_id": 22,
        "message_id": "MSG_1",
        "status": status,
    }


def test_operator_can_restrict_member_without_persisting_free_text(capsys):
    engine = FakeEngine(report())

    result = decide_report(
        engine,
        report_id="RPT_1",
        decision="actioned",
        action="restrict_member",
        resolution="member_restricted",
        moderator_id=9001,
    )

    assert result == 0
    restriction = next(
        (sql, params)
        for sql, params in engine.connection.executions
        if "INSERT INTO family_chat_restrictions" in sql
    )
    assert "reason" not in restriction[0].lower()
    assert "reason" not in restriction[1]
    assert restriction[1]["moderator_id"] == 9001
    assert any(
        params.get("action") == "moderator_actioned:restrict_member"
        for _, params in engine.connection.executions
    )
    assert '"status": "actioned"' in capsys.readouterr().out


def test_operator_cannot_reopen_final_report():
    engine = FakeEngine(report(status="dismissed"))

    with pytest.raises(ModerationValidationError):
        decide_report(
            engine,
            report_id="RPT_1",
            decision="actioned",
            action="remove_message",
            resolution="content_removed",
            moderator_id=9001,
        )

    assert len(engine.connection.executions) == 1


def test_non_actioned_decision_cannot_mutate_chat():
    engine = FakeEngine(report())

    with pytest.raises(ModerationValidationError):
        decide_report(
            engine,
            report_id="RPT_1",
            decision="reviewed",
            action="restrict_member",
            resolution="member_restricted",
            moderator_id=9001,
        )

    assert engine.connection.executions == []
