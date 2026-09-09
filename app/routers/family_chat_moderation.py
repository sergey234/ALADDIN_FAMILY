"""Pure validation policy for family-chat moderation."""

from typing import Optional


REPORT_CATEGORIES = frozenset(
    {"spam", "harassment", "inappropriate", "threat", "other"}
)
MODERATION_DECISIONS = frozenset({"reviewed", "actioned", "dismissed"})
MAX_REPORT_NOTE_LENGTH = 500


class ModerationValidationError(ValueError):
    """Raised when untrusted moderation input violates the public contract."""


def normalize_report_category(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in REPORT_CATEGORIES:
        raise ModerationValidationError("Invalid report category")
    return normalized


def normalize_report_note(value: Optional[str]) -> Optional[str]:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    if len(normalized) > MAX_REPORT_NOTE_LENGTH:
        raise ModerationValidationError(
            f"Report note exceeds {MAX_REPORT_NOTE_LENGTH} characters"
        )
    return normalized


def normalize_moderation_decision(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in MODERATION_DECISIONS:
        raise ModerationValidationError("Invalid moderation decision")
    return normalized


def can_transition_report_status(current: str, new: str) -> bool:
    current_status = str(current or "").strip().lower()
    new_status = str(new or "").strip().lower()
    if new_status not in MODERATION_DECISIONS:
        return False
    if current_status == "pending":
        return True
    return current_status == "reviewed" and new_status in {"actioned", "dismissed"}


def can_report_chat_message(
    *,
    reporter_user_id: int,
    reported_user_id: int,
    reporter_belongs_to_family: bool,
) -> bool:
    return reporter_belongs_to_family and reporter_user_id != reported_user_id


def can_restrict_chat_member(
    *,
    actor_user_id: int,
    target_user_id: int,
    target_role: str,
    actor_can_manage: bool,
) -> bool:
    if not actor_can_manage or actor_user_id == target_user_id:
        return False
    return str(target_role or "").strip().lower() != "parent"
