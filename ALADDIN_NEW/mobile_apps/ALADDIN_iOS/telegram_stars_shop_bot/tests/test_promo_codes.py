from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from bot.db.database import connect
from bot.services import promo_repo, users_repo
from bot.services.pricing import PriceQuote, apply_promo_to_quote, quote_product
from bot.config import Settings


async def _db():
    td = tempfile.TemporaryDirectory()
    conn = await connect(Path(td.name) / "t.db")
    return td, conn


@pytest.mark.asyncio
async def test_promo_activate_and_once_per_user() -> None:
    td, conn = await _db()
    try:
        await users_repo.upsert_user(conn, user_id=101, username="u", first_name="U")
        await promo_repo.create_promo(
            conn,
            code="SUMMER10",
            title="Summer",
            discount_type="percent",
            discount_value=10,
            scope="all",
            max_activations=100,
        )
        st, offer = await promo_repo.activate_promo(conn, user_id=101, code="summer10")
        assert st == "ok"
        assert offer.code == "SUMMER10"
        st2, fail = await promo_repo.activate_promo(conn, user_id=101, code="SUMMER10")
        assert st2 == "fail"
        assert fail == "already_used"
    finally:
        await conn.close()
        td.cleanup()


@pytest.mark.asyncio
async def test_promo_limit_and_personal() -> None:
    td, conn = await _db()
    try:
        await users_repo.upsert_user(conn, user_id=1, username="a", first_name="A")
        await users_repo.upsert_user(conn, user_id=2, username="b", first_name="B")
        await promo_repo.create_promo(
            conn,
            code="ONE",
            title="one",
            discount_type="fixed_rub",
            discount_value=50,
            scope="vpn",
            max_activations=1,
            allowed_user_ids="1",
        )
        st, _ = await promo_repo.activate_promo(conn, user_id=2, code="ONE")
        assert st == "fail"
        st, _ = await promo_repo.activate_promo(conn, user_id=1, code="ONE")
        assert st == "ok"
        await users_repo.upsert_user(conn, user_id=3, username="c", first_name="C")
        st, fail = await promo_repo.activate_promo(conn, user_id=3, code="ONE")
        assert st == "fail"
        assert fail == "limit"
    finally:
        await conn.close()
        td.cleanup()


def test_apply_promo_scope_and_percent() -> None:
    q = PriceQuote(
        usd=1.0,
        rub_list=1000.0,
        rub_referral_discount=0.0,
        rub_wholesale_discount=0.0,
        rub_final=1000.0,
    )
    offer = promo_repo.PromoOffer(
        promo_id=1,
        activation_id=1,
        code="X",
        discount_type="percent",
        discount_value=10,
        scope="stars",
    )
    q2 = apply_promo_to_quote(q, product_kind="vpn", promo=offer)
    assert q2.rub_promo_discount == 0.0
    assert q2.rub_final == 1000.0
    q3 = apply_promo_to_quote(q, product_kind="stars", promo=offer)
    assert q3.rub_promo_discount == 100.0
    assert q3.rub_final == 900.0


def test_promo_button_in_cabinet_kb() -> None:
    from bot.keyboards.shop_kb import profile_inline_kb_rows_prefix

    labels = [b.text for row in profile_inline_kb_rows_prefix(None) for b in row]
    assert "🎁 Промокод" in labels


def test_hero_start_path_mentions_schedule_strip() -> None:
    from pathlib import Path

    src = Path("bot/handlers/common.py").read_text(encoding="utf-8")
    assert "_schedule_strip_sticky_reply_keyboard" in src
    assert "_start_side_effects" in src
