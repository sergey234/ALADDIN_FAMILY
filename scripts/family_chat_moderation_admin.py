#!/usr/bin/env python3
"""Metadata-only operator CLI for family-chat moderation.

Requires DATABASE_URL. It never prints message plaintext, ciphertext, tokens,
free-form report notes, or credentials.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import sys
import uuid

from sqlalchemy import create_engine, text

from app.routers.family_chat_moderation import (
    ModerationValidationError,
    can_transition_report_status,
    normalize_moderation_decision,
)


ALLOWED_ACTIONS = {"none", "restrict_member", "remove_message"}
ALLOWED_RESOLUTIONS = {
    "no_violation",
    "warning_issued",
    "member_restricted",
    "content_removed",
    "escalated",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def required_database_url() -> str:
    value = os.environ.get("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def list_reports(engine, status: str, limit: int) -> int:
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                """
                SELECT id, family_id, reporter_user_id, reported_user_id,
                       message_id, message_envelope_version, category,
                       status, created_at, reviewed_at, resolution
                FROM family_chat_reports
                WHERE status = :status
                ORDER BY created_at ASC
                LIMIT :limit
                """
            ),
            {"status": status, "limit": limit},
        ).mappings()
        for row in rows:
            print(json.dumps(dict(row), ensure_ascii=False, default=str))
    return 0


def decide_report(
    engine,
    *,
    report_id: str,
    decision: str,
    action: str,
    resolution: str,
    moderator_id: int,
) -> int:
    decision = normalize_moderation_decision(decision)
    if action not in ALLOWED_ACTIONS:
        raise ModerationValidationError("Invalid moderation action")
    if resolution not in ALLOWED_RESOLUTIONS:
        raise ModerationValidationError("Invalid resolution code")
    if decision != "actioned" and action != "none":
        raise ModerationValidationError("Only actioned reports may change chat state")

    now = utc_now()
    with engine.begin() as connection:
        report = connection.execute(
            text(
                """
                SELECT id, family_id, reported_user_id, message_id, status
                FROM family_chat_reports
                WHERE id = :report_id
                FOR UPDATE
                """
            ),
            {"report_id": report_id},
        ).mappings().first()
        if not report:
            raise RuntimeError("Report not found")
        if not can_transition_report_status(str(report["status"]), decision):
            raise ModerationValidationError("Invalid report status transition")

        if action == "restrict_member":
            connection.execute(
                text(
                    """
                    INSERT INTO family_chat_restrictions (
                        family_id, target_user_id, restricted_by_user_id,
                        is_active, created_at, updated_at
                    ) VALUES (
                        :family_id, :target_user_id, :moderator_id,
                        TRUE, :created_at, :updated_at
                    )
                    ON CONFLICT (family_id, target_user_id) DO UPDATE SET
                        restricted_by_user_id = EXCLUDED.restricted_by_user_id,
                        is_active = TRUE,
                        updated_at = EXCLUDED.updated_at
                    """
                ),
                {
                    "family_id": report["family_id"],
                    "target_user_id": report["reported_user_id"],
                    "moderator_id": moderator_id,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        elif action == "remove_message":
            connection.execute(
                text("DELETE FROM family_chat_reactions WHERE message_id = :message_id"),
                {"message_id": report["message_id"]},
            )
            connection.execute(
                text("DELETE FROM family_chat_messages WHERE id = :message_id AND family_id = :family_id"),
                {"message_id": report["message_id"], "family_id": report["family_id"]},
            )

        updated = connection.execute(
            text(
                """
                UPDATE family_chat_reports
                SET status = :decision, reviewed_at = :reviewed_at, resolution = :resolution
                WHERE id = :report_id AND status = :previous_status
                """
            ),
            {
                "decision": decision,
                "reviewed_at": now,
                "resolution": resolution,
                "report_id": report_id,
                "previous_status": report["status"],
            },
        )
        if getattr(updated, "rowcount", 0) != 1:
            raise RuntimeError("Concurrent report update")

        connection.execute(
            text(
                """
                INSERT INTO family_chat_moderation_audit (
                    id, family_id, report_id, actor_user_id,
                    target_user_id, target_message_id, action, created_at
                ) VALUES (
                    :id, :family_id, :report_id, :actor_user_id,
                    :target_user_id, :target_message_id, :action, :created_at
                )
                """
            ),
            {
                "id": f"AUD_{uuid.uuid4().hex[:16].upper()}",
                "family_id": report["family_id"],
                "report_id": report_id,
                "actor_user_id": moderator_id,
                "target_user_id": report["reported_user_id"],
                "target_message_id": report["message_id"],
                "action": f"moderator_{decision}:{action}",
                "created_at": now,
            },
        )

    print(json.dumps({"reportId": report_id, "status": decision, "action": action}))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    listing = sub.add_parser("list", help="List metadata-only moderation reports")
    listing.add_argument("--status", choices=["pending", "reviewed", "actioned", "dismissed"], default="pending")
    listing.add_argument("--limit", type=int, choices=range(1, 201), default=50)

    decision = sub.add_parser("decide", help="Apply one transactional moderation decision")
    decision.add_argument("report_id")
    decision.add_argument("--decision", required=True, choices=sorted({"reviewed", "actioned", "dismissed"}))
    decision.add_argument("--action", choices=sorted(ALLOWED_ACTIONS), default="none")
    decision.add_argument("--resolution", required=True, choices=sorted(ALLOWED_RESOLUTIONS))
    decision.add_argument(
        "--moderator-id",
        type=int,
        default=int(os.environ.get("ALADDIN_MODERATOR_ID", "0")),
        help="Non-secret internal operator ID",
    )
    return root


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "moderator_id", 1) <= 0:
        raise RuntimeError("A positive moderator ID is required")
    engine = create_engine(required_database_url(), pool_pre_ping=True)
    if args.command == "list":
        return list_reports(engine, args.status, args.limit)
    return decide_report(
        engine,
        report_id=args.report_id,
        decision=args.decision,
        action=args.action,
        resolution=args.resolution,
        moderator_id=args.moderator_id,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ModerationValidationError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
