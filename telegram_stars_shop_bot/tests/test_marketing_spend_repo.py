from __future__ import annotations

import pytest

from bot.services import marketing_spend_repo


@pytest.mark.asyncio
async def test_upsert_daily_spend_is_idempotent(conn) -> None:
    await marketing_spend_repo.upsert_daily_spend(
        conn,
        spend_date="2026-06-02",
        source="tg_ads",
        campaign="2026Q2_vpn_ru_acq_speed",
        spend_rub=1200.50,
        clicks=34,
        impressions=12000,
    )
    await marketing_spend_repo.upsert_daily_spend(
        conn,
        spend_date="2026-06-02",
        source="tg_ads",
        campaign="2026Q2_vpn_ru_acq_speed",
        spend_rub=2000.00,
        clicks=50,
        impressions=15000,
    )
    cur = await conn.execute(
        """
        SELECT COUNT(*) AS c, SUM(spend_rub) AS spend, SUM(clicks) AS clicks, SUM(impressions) AS impr
        FROM marketing_spend_daily
        WHERE spend_date = '2026-06-02' AND source = 'tg_ads' AND campaign = '2026Q2_vpn_ru_acq_speed'
        """
    )
    row = await cur.fetchone()
    assert int(row["c"]) == 1
    assert float(row["spend"]) == pytest.approx(2000.00)
    assert int(row["clicks"]) == 50
    assert int(row["impr"]) == 15000


@pytest.mark.asyncio
async def test_bulk_upsert_daily_spend_multiple_rows(conn) -> None:
    rows = [
        marketing_spend_repo.SpendRow(
            spend_date="2026-06-01",
            source="partner",
            campaign="2026Q2_shop_ru_partner_launch",
            spend_rub=500.0,
            clicks=10,
            impressions=4000,
        ),
        marketing_spend_repo.SpendRow(
            spend_date="2026-06-01",
            source="tg_channel",
            campaign="2026Q2_shop_ru_channel_post1",
            spend_rub=300.0,
            clicks=6,
            impressions=2500,
        ),
    ]
    n = await marketing_spend_repo.bulk_upsert_daily_spend(conn, rows)
    assert n == 2
    cur = await conn.execute("SELECT COUNT(*) AS c FROM marketing_spend_daily")
    row = await cur.fetchone()
    assert int(row["c"]) == 2
