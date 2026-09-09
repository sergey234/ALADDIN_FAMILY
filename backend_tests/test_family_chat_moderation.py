import pytest

from app.routers.family_chat_moderation import (
    ModerationValidationError,
    can_report_chat_message,
    can_restrict_chat_member,
    can_transition_report_status,
    normalize_moderation_decision,
    normalize_report_category,
    normalize_report_note,
)


@pytest.mark.parametrize(
    "value",
    ["spam", "harassment", "inappropriate", "threat", "other"],
)
def test_normalize_report_category_accepts_allowlist(value: str) -> None:
    assert normalize_report_category(value.upper()) == value


def test_normalize_report_category_rejects_unknown_value() -> None:
    with pytest.raises(ModerationValidationError):
        normalize_report_category("anything-goes")


def test_normalize_report_note_trims_and_limits_content() -> None:
    assert normalize_report_note("  details  ") == "details"
    with pytest.raises(ModerationValidationError):
        normalize_report_note("x" * 501)


def test_only_family_manager_can_restrict_non_parent_member() -> None:
    assert can_restrict_chat_member(
        actor_user_id=10,
        target_user_id=20,
        target_role="child",
        actor_can_manage=True,
    )
    assert not can_restrict_chat_member(
        actor_user_id=10,
        target_user_id=20,
        target_role="child",
        actor_can_manage=False,
    )


def test_member_restriction_cannot_target_self_or_parent() -> None:
    assert not can_restrict_chat_member(
        actor_user_id=10,
        target_user_id=10,
        target_role="child",
        actor_can_manage=True,
    )
    assert not can_restrict_chat_member(
        actor_user_id=10,
        target_user_id=20,
        target_role="parent",
        actor_can_manage=True,
    )


def test_report_requires_same_family_and_foreign_sender() -> None:
    assert can_report_chat_message(
        reporter_user_id=10,
        reported_user_id=20,
        reporter_belongs_to_family=True,
    )
    assert not can_report_chat_message(
        reporter_user_id=10,
        reported_user_id=20,
        reporter_belongs_to_family=False,
    )
    assert not can_report_chat_message(
        reporter_user_id=10,
        reported_user_id=10,
        reporter_belongs_to_family=True,
    )


@pytest.mark.parametrize("value", ["reviewed", "actioned", "dismissed"])
def test_moderation_decision_uses_closed_allowlist(value: str) -> None:
    assert normalize_moderation_decision(value.upper()) == value


def test_report_status_transition_is_forward_only() -> None:
    assert can_transition_report_status("pending", "reviewed")
    assert can_transition_report_status("pending", "actioned")
    assert can_transition_report_status("reviewed", "actioned")
    assert not can_transition_report_status("actioned", "reviewed")
    assert not can_transition_report_status("dismissed", "actioned")


def test_invalid_moderation_decision_is_rejected() -> None:
    with pytest.raises(ModerationValidationError):
        normalize_moderation_decision("delete_everything")
