#!/usr/bin/env python3
"""Static gate for Apple UGC moderation requirements."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    family_router = read("app/routers/family.py")
    main_backend = read("main.py")
    migration = read("app/database/migrations/create_family_chat_moderation.sql")
    api_service = read("Core/Network/APIService.swift")
    chat_screen = read("Screens/23_FamilyChatScreen.swift")
    context_menu = read("Shared/Components/Chat/MessageActionsMenu.swift")
    localization = read("Core/Localization/LocalizationManager.swift")
    operator_cli = read("scripts/family_chat_moderation_admin.py")

    checks = [
        (
            '@router.post("/chat/moderation/report"' in family_router,
            "backend report endpoint is missing",
        ),
        (
            '@router.post("/chat/moderation/restrict"' in family_router,
            "backend restrict endpoint is missing",
        ),
        (
            "family_chat_reports" in family_router,
            "moderation queue storage is missing",
        ),
        (
            "family_chat_restrictions" in family_router,
            "member restriction storage is missing",
        ),
        (
            "family_chat_moderation_audit" in family_router
            and "family_chat_moderation_audit" in migration,
            "durable metadata-only moderation audit is missing",
        ),
        (
            "note TEXT" not in migration
            and "reason TEXT" not in migration
            and "CHECK (status IN ('pending', 'reviewed', 'actioned', 'dismissed'))" in migration,
            "moderation schema must forbid free-text leakage and invalid statuses",
        ),
        (
            "@limiter.limit(" in family_router,
            "moderation endpoints need rate limits",
        ),
        (
            '@router.post("/chat/send", response_model=SendFamilyChatMessageResponse)\n@limiter.limit("60/minute")'
            in family_router,
            "chat send rate limit is missing",
        ),
        (
            '@router.post("/chat/upload-media")\n@limiter.limit("10/minute")'
            in family_router
            and '@router.post("/chat/upload-media-ciphertext")\n@limiter.limit("10/minute")'
            in family_router,
            "chat upload rate limits are missing",
        ),
        (
            "await request.body()" not in family_router
            and "async for chunk in request.stream()" in family_router,
            "ciphertext upload must use bounded streaming",
        ),
        (
            "family_chat_media_files" in family_router
            and "current_user: dict = Depends(get_current_user)" in family_router,
            "chat media must be mapped to a family and authenticated",
        ),
        (
            "Not a member of this message's family" in family_router,
            "cross-family reaction/report access checks are missing",
        ),
        (
            "reportFamilyChatMessage" in api_service,
            "iOS report API method is missing",
        ),
        (
            "restrictFamilyChatMember" in api_service,
            "iOS restrict API method is missing",
        ),
        (
            "reportMessage(" in chat_screen,
            "chat report action is missing",
        ),
        (
            "restrictMessageSender(" in chat_screen,
            "parent restrict action is missing",
        ),
        (
            "onReport" in context_menu and "onRestrictSender" in context_menu,
            "message actions do not expose report/restrict",
        ),
        (
            "deleteFamilyChatMessage" in api_service and "deleteMessage(" in chat_screen,
            "delete-own-message behavior is missing",
        ),
        (
            'websocket.headers.get("authorization")' in main_backend
            and "_actor_belongs_to_family" in main_backend
            and '"user_id": str(user_id)' in main_backend,
            "family WebSocket must authenticate and derive its room actor server-side",
        ),
        (
            "_is_family_chat_restricted" in main_backend
            and "refresh_restriction_status" in main_backend
            and 'code": "chat_restricted"' in main_backend,
            "family WebSocket must refresh and enforce chat restrictions",
        ),
        (
            "frame_times = deque()" in main_backend and "len(frame_times) >= 60" in main_backend,
            "family WebSocket frame rate limit is missing",
        ),
        (
            family_router.find("if getattr(deleted, \"rowcount\", 0) == 0:")
            < family_router.find('DELETE FROM family_chat_reactions WHERE message_id = :message_id'),
            "failed delete-own attempts must not remove another message's reactions",
        ),
        (
            "Target is not a current family member" in family_router,
            "restriction endpoint must reject departed family members",
        ),
        (
            "FOR UPDATE" in operator_cli
            and "ALLOWED_ACTIONS" in operator_cli
            and "family_chat_moderation_audit" in operator_cli,
            "transactional metadata-only operator workflow is missing",
        ),
        (
            all(
                key in localization
                for key in (
                    "family_chat_report",
                    "family_chat_report_other",
                    "family_chat_restrict_sender",
                    "family_chat_moderation_success_title",
                )
            ),
            "RU/EN moderation localization is incomplete",
        ),
    ]

    for condition, message in checks:
        if not condition:
            failures.append(message)

    if failures:
        print("UGC MODERATION: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("UGC MODERATION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
