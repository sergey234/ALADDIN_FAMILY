from __future__ import annotations

import pytest

from bot.services import acquisition_repo


def test_parse_start_payload_query_style() -> None:
    out = acquisition_repo.parse_start_payload(
        "utm_source=tg_ads&utm_campaign=2026Q2_vpn_ru_acq_speed&utm_content=video_utility_a&product_hint=vpn&positioning_variant=utility"
    )
    assert out["source"] == "tg_ads"
    assert out["campaign"] == "2026Q2_vpn_ru_acq_speed"
    assert out["creative"] == "video_utility_a"
    assert out["product_hint"] == "vpn"
    assert out["positioning_variant"] == "utility"


@pytest.mark.asyncio
async def test_touch_user_acquisition_first_and_last(conn) -> None:
    await acquisition_repo.touch_user_acquisition(
        conn,
        user_id=42,
        source="tg_ads",
        campaign="c1",
        creative="a1",
    )
    await acquisition_repo.touch_user_acquisition(
        conn,
        user_id=42,
        source="partner",
        campaign="c2",
        creative="a2",
    )
    cur = await conn.execute(
        """
        SELECT first_source, first_campaign, first_creative, last_source, last_campaign, last_creative
        FROM user_acquisition WHERE user_id = ?
        """,
        (42,),
    )
    row = await cur.fetchone()
    assert row is not None
    assert row["first_source"] == "tg_ads"
    assert row["first_campaign"] == "c1"
    assert row["first_creative"] == "a1"
    assert row["last_source"] == "partner"
    assert row["last_campaign"] == "c2"
    assert row["last_creative"] == "a2"
