from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiosqlite


@dataclass(frozen=True)
class SpendRow:
    spend_date: str
    source: str
    campaign: str
    spend_rub: float
    clicks: int
    impressions: int
    meta: dict[str, Any] | None = None


def _norm_date(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        raise ValueError("spend_date is required")
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"invalid spend_date: {raw}") from exc


def _norm_source(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not s:
        raise ValueError("source is required")
    allowed = {"tg_ads", "tg_channel", "referral", "partner", "organic", "meta", "google", "unknown"}
    return s if s in allowed else "unknown"


def _norm_campaign(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        raise ValueError("campaign is required")
    return s[:96]


def _row_payload(meta: dict[str, Any] | None) -> str | None:
    if not meta:
        return None
    return json.dumps(meta, ensure_ascii=False)


async def upsert_daily_spend(
    conn: aiosqlite.Connection,
    *,
    spend_date: str,
    source: str,
    campaign: str,
    spend_rub: float,
    clicks: int,
    impressions: int,
    meta: dict[str, Any] | None = None,
) -> None:
    d = _norm_date(spend_date)
    src = _norm_source(source)
    cmp = _norm_campaign(campaign)
    await conn.execute(
        """
        INSERT INTO marketing_spend_daily (
            spend_date, source, campaign, spend_rub, clicks, impressions, meta_json, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(spend_date, source, campaign) DO UPDATE SET
            spend_rub = excluded.spend_rub,
            clicks = excluded.clicks,
            impressions = excluded.impressions,
            meta_json = excluded.meta_json,
            updated_at = datetime('now')
        """,
        (
            d,
            src,
            cmp,
            float(spend_rub),
            int(clicks),
            int(impressions),
            _row_payload(meta),
        ),
    )
    await conn.commit()


async def bulk_upsert_daily_spend(conn: aiosqlite.Connection, rows: list[SpendRow]) -> int:
    if not rows:
        return 0
    for r in rows:
        await upsert_daily_spend(
            conn,
            spend_date=r.spend_date,
            source=r.source,
            campaign=r.campaign,
            spend_rub=r.spend_rub,
            clicks=r.clicks,
            impressions=r.impressions,
            meta=r.meta,
        )
    return len(rows)
