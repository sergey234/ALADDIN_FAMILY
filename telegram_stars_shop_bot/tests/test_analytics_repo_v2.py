from __future__ import annotations

import json

import pytest

from bot.services import analytics_repo


@pytest.mark.asyncio
async def test_log_event_normalizes_meta_schema_v2(conn) -> None:
    await analytics_repo.log_event(
        conn,
        user_id=12345,
        event_type="offer_click",
        meta={
            "product_id": "stars_100",
            "source": "tg_ads",
            "campaign": "2026Q2_vpn_ru_acq_speed",
            "unexpected_field": "kept_under_namespace",
        },
    )
    cur = await conn.execute(
        "SELECT event_type, meta_json FROM analytics_events WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (12345,),
    )
    row = await cur.fetchone()
    assert row is not None
    assert row["event_type"] == "offer_click"
    meta = json.loads(row["meta_json"])
    assert meta["product_id"] == "stars_100"
    assert meta["source"] == "tg_ads"
    assert meta["campaign"] == "2026Q2_vpn_ru_acq_speed"
    assert meta["x_unexpected_field"] == "kept_under_namespace"
    assert meta["schema_version"] == "v2"


@pytest.mark.asyncio
async def test_log_event_truncates_event_type_length(conn) -> None:
    long_event = "x" * 200
    await analytics_repo.log_event(conn, user_id=7, event_type=long_event, meta=None)
    cur = await conn.execute(
        "SELECT event_type, meta_json FROM analytics_events WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (7,),
    )
    row = await cur.fetchone()
    assert row is not None
    assert len(row["event_type"]) == 64
    assert row["meta_json"] is None
