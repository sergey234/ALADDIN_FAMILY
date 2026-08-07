"""Тесты вывода реф-бонуса: карта / крипта (ручные заявки)."""

from __future__ import annotations

import pytest

from bot.db.database import connect
from bot.services import ref_withdraw_repo


@pytest.mark.asyncio
async def test_withdraw_card_and_crypto(tmp_path) -> None:
    db = tmp_path / "wd.db"
    conn = await connect(db)
    await conn.execute(
        "INSERT INTO users (user_id, username, referrer_id, first_order_completed, ref_balance_rub) "
        "VALUES (7001, 'u', NULL, 0, 1500)"
    )
    await conn.commit()

    rid = await ref_withdraw_repo.create_withdraw_request(
        conn, user_id=7001, amount_rub=1500, method="card"
    )
    assert rid > 0
    assert await ref_withdraw_repo.has_pending_withdraw(conn, 7001)

    with pytest.raises(ValueError, match="pending_exists"):
        await ref_withdraw_repo.create_withdraw_request(
            conn,
            user_id=7001,
            amount_rub=1500,
            method="crypto",
            crypto_channel="usdt_trc20",
            payout_target="TXyzabcdefghijklmnopqrstuvwxyz012345",  # invalid len hopefully
        )

    await ref_withdraw_repo.set_withdraw_status(conn, request_id=rid, status="paid")
    assert not await ref_withdraw_repo.has_pending_withdraw(conn, 7001)

    # valid-looking TRC20 (34 chars)
    addr = "T" + ("A" * 33)
    rid2 = await ref_withdraw_repo.create_withdraw_request(
        conn,
        user_id=7001,
        amount_rub=1500,
        method="crypto",
        crypto_channel="usdt_trc20",
        payout_target=addr,
    )
    row = await ref_withdraw_repo.get_withdraw(conn, rid2)
    assert row is not None
    assert row["method"] == "crypto"
    assert row["crypto_channel"] == "usdt_trc20"
    assert row["payout_target"] == addr
    assert ref_withdraw_repo.format_withdraw_method_label(row) == "crypto/trc20"
    await conn.close()


@pytest.mark.asyncio
async def test_withdraw_cryptobot_and_validation(tmp_path) -> None:
    db = tmp_path / "wd2.db"
    conn = await connect(db)
    await conn.execute(
        "INSERT INTO users (user_id, username, referrer_id, first_order_completed, ref_balance_rub) "
        "VALUES (7002, 'u2', NULL, 0, 1500)"
    )
    await conn.commit()

    with pytest.raises(ValueError, match="bad_trc20"):
        await ref_withdraw_repo.create_withdraw_request(
            conn,
            user_id=7002,
            amount_rub=1500,
            method="crypto",
            crypto_channel="usdt_trc20",
            payout_target="not-an-address",
        )

    with pytest.raises(ValueError, match="bad_cryptobot"):
        await ref_withdraw_repo.create_withdraw_request(
            conn,
            user_id=7002,
            amount_rub=1500,
            method="crypto",
            crypto_channel="cryptobot",
            payout_target="@@bad",
        )

    rid = await ref_withdraw_repo.create_withdraw_request(
        conn,
        user_id=7002,
        amount_rub=1500,
        method="crypto",
        crypto_channel="cryptobot",
        payout_target="friend_user",
    )
    row = await ref_withdraw_repo.get_withdraw(conn, rid)
    assert row["payout_target"] == "@friend_user"
    assert ref_withdraw_repo.format_withdraw_method_label(row) == "crypto/cryptobot"
    await conn.close()


def test_normalize_helpers() -> None:
    assert (
        ref_withdraw_repo.normalize_payout_target(
            method="card", crypto_channel=None, raw=""
        )
        == "card_payout_request"
    )
    addr = "T" + ("B" * 33)
    assert (
        ref_withdraw_repo.normalize_payout_target(
            method="crypto", crypto_channel="usdt_trc20", raw=addr
        )
        == addr
    )
