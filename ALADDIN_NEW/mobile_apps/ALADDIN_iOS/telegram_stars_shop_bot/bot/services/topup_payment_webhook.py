"""Обработка webhook/reconcile для оплаты пополнения баланса."""

from __future__ import annotations

import aiosqlite

from bot.config import Settings
from bot.services import balance_repo
from bot.services.provider_mark_topup_paid import MarkTopupPaidResult, mark_topup_paid_idempotent
from bot.services.topup_crypto_payload import DecodedTopupCryptoPayload, verify_decoded_topup_payload
from bot.services.topup_paid_notify import schedule_topup_paid_user_notify


async def mark_topup_paid_from_provider(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    topup_id: int,
    idempotency_key: str,
    expected_amount_rub: float | None = None,
) -> MarkTopupPaidResult:
    """Внутри BEGIN IMMEDIATE. При успехе планирует уведомление пользователю."""
    row = await balance_repo.get_topup(conn, topup_id)
    if row is None:
        return MarkTopupPaidResult("not_found", topup_id)
    if expected_amount_rub is not None:
        if abs(float(row["amount_rub"]) - float(expected_amount_rub)) > 0.05:
            return MarkTopupPaidResult("conflict", topup_id, int(row["user_id"]), float(row["amount_rub"]), str(row["status"]))
    res = await mark_topup_paid_idempotent(conn, topup_id=topup_id, idempotency_key=idempotency_key)
    if res.outcome == "ok" and res.user_id is not None:
        schedule_topup_paid_user_notify(
            settings,
            user_id=res.user_id,
            topup_id=topup_id,
            amount_rub=float(res.amount_rub or row["amount_rub"]),
        )
    return res


async def verify_topup_crypto_payload_row(
    conn: aiosqlite.Connection,
    decoded: DecodedTopupCryptoPayload,
) -> aiosqlite.Row:
    row = await balance_repo.get_topup(conn, decoded.topup_id)
    if row is None:
        raise ValueError("topup_not_found")
    verify_decoded_topup_payload(decoded, row)
    return row
