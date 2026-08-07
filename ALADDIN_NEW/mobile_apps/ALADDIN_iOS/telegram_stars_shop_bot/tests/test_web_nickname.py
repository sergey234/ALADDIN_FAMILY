"""Nickname validation + set/login (web, no email/password)."""

from __future__ import annotations

import pytest

from bot.db.database import connect
from bot.services import accounts_repo
from bot.services.web_nickname import validate_nickname


@pytest.mark.parametrize(
    "raw,err",
    [
        ("ab", "too_short"),
        ("a" * 25, "too_long"),
        ("user@mail.com", "looks_like_email"),
        ("79001234567", "looks_like_phone"),
        ("+79001234567", "looks_like_phone"),
        ("1bad", "bad_chars"),
        ("ok_Nick1", None),
        ("FamilyHero2024", None),
    ],
)
def test_validate_nickname(raw, err):
    assert validate_nickname(raw) == err


@pytest.mark.asyncio
async def test_set_nickname_and_login(tmp_path):
    db = tmp_path / "nick.db"
    conn = await connect(db)
    try:
        web = await accounts_repo.create_web_account(conn)
        aid = str(web["account_id"])
        nick, code = await accounts_repo.set_nickname_with_access_code(
            conn, account_id=aid, nickname="FamilyHero2024"
        )
        assert nick == "FamilyHero2024"
        assert code and code.startswith("AIM-")
        # locked
        nick2, code2 = await accounts_repo.set_nickname_with_access_code(
            conn, account_id=aid, nickname="FamilyHero2024"
        )
        assert nick2 == "FamilyHero2024"
        assert code2 is None
        with pytest.raises(ValueError, match="nickname_locked"):
            await accounts_repo.set_nickname_with_access_code(
                conn, account_id=aid, nickname="OtherNick"
            )
        acc, secret = await accounts_repo.login_with_nickname_code(
            conn, nickname="familyhero2024", access_code=code
        )
        assert str(acc["account_id"]) == aid
        assert secret
        assert await accounts_repo.verify_session_secret(conn, aid, secret)
        found = await accounts_repo.find_accounts_orders_by_nickname(conn, "FamilyHero2024")
        assert found["account"]["account_id"] == aid
    finally:
        await conn.close()
