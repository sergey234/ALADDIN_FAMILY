"""KB build from SSOT marketing / VPN copy + keyword retrieve."""

from __future__ import annotations

import hashlib
import logging
import re
from html.parser import HTMLParser

import aiosqlite

from bot.assistant import repo as as_repo
from bot.config import Settings

logger = logging.getLogger(__name__)


class _HTMLToText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def text(self) -> str:
        raw = " ".join(self._parts)
        return re.sub(r"\s+", " ", raw).strip()


def html_to_plain(html: str) -> str:
    p = _HTMLToText()
    try:
        p.feed(html or "")
        p.close()
        return p.text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html or "")


def _hash_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:40]


def _captcha_kb_plain() -> str:
    return (
        "Капча при оформлении заказа: выберите правильный эмодзи в кнопках. "
        "После успешной капчи оформление продолжается автоматически. "
        "Если ошибка — попробуйте снова. Нельзя обойти капчу. "
        "Во время капчи/оплаты не пишите в Помощника — сначала завершите или отмените оплату."
    )


def _brand_kb_plain(settings: Settings) -> str:
    if not bool(getattr(settings, "assistant_brand_voice_enabled", True)):
        return "Тон: коротко по-русски. Факты — из базы бота."
    from bot.assistant.brand_gold_answers import brand_kb_plain

    return brand_kb_plain()


def catalog_kb_plain(settings: Settings) -> str:
    """Prices/titles only from products.yaml — never invent RUB/USD."""
    from bot.services.catalog import load_products

    path = getattr(settings, "products_path", None)
    if path is None:
        return "Каталог недоступен. Цены смотрите в меню бота."
    try:
        products = load_products(path)
    except Exception as e:
        logger.warning("assistant_catalog_kb_load_failed: %s", e)
        return "Каталог временно недоступен. Цены смотрите в меню бота при оформлении."

    lines = [
        "Каталог AiMonkey (источник: products.yaml). Не выдумывать цены вне этого списка.",
        "Точную сумму к оплате всегда сверяйте с экраном оформления в боте.",
        "Запрещено: «100% uptime», гарантии скорости VPN, «всегда одна цена» без меню.",
        "",
        "Фиксированные ₽ в каталоге (price_rub):",
    ]
    fixed = [p for p in products if p.price_rub is not None and p.price_rub > 0]
    fx = [p for p in products if p not in fixed and float(p.price_usd or 0) > 0]
    if not fixed:
        lines.append("— (нет позиций с price_rub)")
    for p in fixed:
        hide = " [скрыт в меню]" if p.hide_from_menu else ""
        lines.append(f"• {p.title}: {int(p.price_rub) if p.price_rub == int(p.price_rub) else p.price_rub} ₽ ({p.id}){hide}")
    lines.append("")
    lines.append(
        "Stars/Premium и прочее без фиксированных ₽: витрина = price_usd × курс магазина "
        "(USD_RUB_RATE). Называйте пакет по title/id; ₽ — только из меню бота, не из памяти."
    )
    for p in fx:
        hide = " [скрыт в меню]" if p.hide_from_menu else ""
        extra = ""
        if p.kind == "stars" and p.stars:
            extra = f", {p.stars}⭐"
        elif p.kind == "premium" and p.duration_months:
            extra = f", {p.duration_months} мес."
        lines.append(f"• {p.title} ({p.id}, {p.price_usd} USD{extra}){hide}")
    return "\n".join(lines)


def _collect_sources(settings: Settings) -> list[tuple[str, str, str]]:
    from bot.services import marketing
    from bot.services.vpn_connect_copy import (
        vpn_happ_android_steps_html,
        vpn_happ_plus_steps_html,
        vpn_happ_stub_troubleshoot_html,
    )

    return [
        ("kb.happ.android", "happ", html_to_plain(vpn_happ_android_steps_html())),
        ("kb.happ.ios", "happ", html_to_plain(vpn_happ_plus_steps_html())),
        ("kb.vpn.help", "vpn", html_to_plain(vpn_happ_stub_troubleshoot_html())),
        ("kb.pay", "pay", html_to_plain(marketing.payment_faq_html(settings))),
        ("kb.refund", "refund", html_to_plain(marketing.refund_policy_blurb_html(settings))),
        ("kb.faq", "faq", html_to_plain(marketing.faq_comprehensive_html(settings))),
        ("kb.ref", "ref", html_to_plain(marketing.referral_faq_html(settings))),
        ("kb.privacy", "privacy", html_to_plain(marketing.privacy_screen_html(settings))),
        ("kb.captcha", "captcha", _captcha_kb_plain()),
        ("kb.catalog", "catalog", catalog_kb_plain(settings)),
        ("kb.brand", "brand", _brand_kb_plain(settings)),
    ]


async def build_kb(conn: aiosqlite.Connection, settings: Settings) -> int:
    """Rebuild changed chunks from SSOT. Returns number upserted."""
    existing = await as_repo.get_kb_hash_map(conn)
    n = 0
    for chunk_id, topic, plain in _collect_sources(settings):
        h = _hash_text(plain)
        if existing.get(chunk_id) == h:
            continue
        await as_repo.upsert_kb_chunk(
            conn,
            chunk_id=chunk_id,
            topic=topic,
            text_plain=plain[:12000],
            source_hash=h,
        )
        n += 1
    if n:
        await as_repo.commit_kb(conn)
        logger.info("assistant_kb_rebuilt chunks=%s", n)
    return n


_TOKEN_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9]{3,}")


def _score(query: str, text: str) -> int:
    q = set(_TOKEN_RE.findall((query or "").lower()))
    if not q:
        return 0
    t = (text or "").lower()
    return sum(1 for w in q if w in t)


async def retrieve_kb(
    conn: aiosqlite.Connection,
    query: str,
    *,
    topic_hint_ids: list[str] | None = None,
    limit: int = 3,
) -> list[dict[str, str]]:
    preferred: list[dict[str, str]] = []
    if topic_hint_ids:
        preferred = await as_repo.get_kb_chunks(conn, chunk_ids=topic_hint_ids)

    all_chunks = await as_repo.get_kb_chunks(conn)
    ranked = sorted(all_chunks, key=lambda c: _score(query, c["text_plain"]), reverse=True)
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for c in preferred + ranked:
        cid = c["id"]
        if cid in seen:
            continue
        if preferred and c in preferred:
            out.append(c)
            seen.add(cid)
            continue
        if _score(query, c["text_plain"]) <= 0 and cid not in (topic_hint_ids or []):
            continue
        out.append(c)
        seen.add(cid)
        if len(out) >= limit:
            break
    if not out and preferred:
        return preferred[:limit]
    if not out and all_chunks:
        # Soft fallback: top faq
        for c in all_chunks:
            if c["id"] == "kb.faq":
                return [c]
    return out[:limit]
