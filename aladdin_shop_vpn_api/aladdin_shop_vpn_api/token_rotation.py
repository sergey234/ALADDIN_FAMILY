"""Ротация opaque_token при истечении подписки (P2 anti-abuse)."""

from __future__ import annotations

import secrets

import aiosqlite


def new_opaque_token() -> str:
    return secrets.token_urlsafe(24)


async def rotate_opaque_token_for_account(
    conn: aiosqlite.Connection,
    *,
    telegram_user_id: int,
    now_iso: str,
) -> str:
    """Новый токен для /sub/; старая ссылка → 404. Возвращает новый opaque_token."""
    tok = new_opaque_token()
    await conn.execute(
        """
        UPDATE vpn_accounts
        SET opaque_token = ?, updated_at = ?
        WHERE telegram_user_id = ?
        """,
        (tok, now_iso, int(telegram_user_id)),
    )
    return tok
