from __future__ import annotations

import pytest

from bot.services import sell_repo


@pytest.mark.asyncio
async def test_sell_pagination(conn) -> None:
    uid = 9001
    for i in range(7):
        await sell_repo.create_sell_request(conn, user_id=uid, stars=100 + i, rub_offer=float(50 + i))
    total = await sell_repo.count_user_sells(conn, uid)
    assert total == 7
    p0 = await sell_repo.list_user_sells_page(conn, uid, limit=5, offset=0)
    p1 = await sell_repo.list_user_sells_page(conn, uid, limit=5, offset=5)
    assert len(p0) == 5
    assert len(p1) == 2
