from __future__ import annotations

from urllib.parse import parse_qsl

import aiosqlite


def _sanitize(raw: str | None, *, max_len: int = 96) -> str:
    if raw is None:
        return ""
    return str(raw).strip()[:max_len]


def _normalize_source(raw: str | None) -> str:
    src = _sanitize(raw, max_len=64).lower()
    allowed = {
        "tg_ads",
        "tg_channel",
        "referral",
        "partner",
        "organic",
        "meta",
        "google",
        "unknown",
    }
    return src if src in allowed else ("unknown" if src else "unknown")


def parse_start_payload(payload: str) -> dict[str, str]:
    """
    Поддерживаем:
    - query-string: utm_source=tg_ads&utm_campaign=...&utm_content=...
    - парные токены через ':': src:tg_ads:cmp:launch:cr:a
    """
    p = (payload or "").strip()
    if not p:
        return {
            "source": "unknown",
            "campaign": "",
            "creative": "",
            "product_hint": "",
            "positioning_variant": "",
        }

    source = ""
    campaign = ""
    creative = ""
    product_hint = ""
    positioning_variant = ""

    if "=" in p:
        kv = {k.strip().lower(): v.strip() for k, v in parse_qsl(p, keep_blank_values=True)}
        source = kv.get("utm_source", kv.get("source", ""))
        campaign = kv.get("utm_campaign", kv.get("campaign", ""))
        creative = kv.get("utm_content", kv.get("creative", ""))
        product_hint = kv.get("product_hint", kv.get("product", ""))
        positioning_variant = kv.get("positioning_variant", kv.get("position", ""))
    elif ":" in p:
        parts = [x.strip() for x in p.split(":")]
        for i in range(0, len(parts) - 1, 2):
            k = parts[i].lower()
            v = parts[i + 1]
            if k in ("src", "source"):
                source = v
            elif k in ("cmp", "campaign"):
                campaign = v
            elif k in ("cr", "creative"):
                creative = v
            elif k in ("product", "product_hint"):
                product_hint = v
            elif k in ("pos", "positioning_variant"):
                positioning_variant = v

    return {
        "source": _normalize_source(source),
        "campaign": _sanitize(campaign),
        "creative": _sanitize(creative),
        "product_hint": _sanitize(product_hint, max_len=48),
        "positioning_variant": _sanitize(positioning_variant, max_len=32),
    }


async def touch_user_acquisition(
    conn: aiosqlite.Connection,
    *,
    user_id: int,
    source: str,
    campaign: str,
    creative: str,
) -> None:
    norm_source = _normalize_source(source)
    camp = _sanitize(campaign)
    cr = _sanitize(creative)
    await conn.execute(
        """
        INSERT INTO user_acquisition (
            user_id, first_source, first_campaign, first_creative,
            last_source, last_campaign, last_creative, first_seen_at, last_seen_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            last_source = excluded.last_source,
            last_campaign = excluded.last_campaign,
            last_creative = excluded.last_creative,
            last_seen_at = datetime('now')
        """,
        (int(user_id), norm_source, camp, cr, norm_source, camp, cr),
    )
    await conn.commit()
