from __future__ import annotations

import pytest

from bot.config import Settings
from bot.db.database import connect
from bot.keyboards.shop_kb import admin_order_kb
from bot.services import orders_repo, users_repo
from bot.services.admin_order_ff import (
    AdminOrderFfContext,
    ff_context_from_order_row,
    format_fulfillment_admin_block,
    fulfillment_controls_allowed,
)
from bot.services.auto_fulfill_policy import auto_fulfill_order_eligible


def _dump_callbacks(markup) -> list[str]:
    dumped = markup.model_dump(mode="python", exclude_none=True)
    rows = dumped.get("inline_keyboard") or []
    out: list[str] = []
    for row in rows:
        for btn in row:
            cd = btn.get("callback_data")
            if cd:
                out.append(str(cd))
    return out


def test_ff_context_and_format_block() -> None:
    row = {
        "status": "paid",
        "fulfillment_mode": "manual_only",
        "fulfillment_attempt_count": 2,
        "fulfillment_provider_ref": "uuid-1",
        "fulfillment_last_error": "x" * 600,
    }
    ctx = ff_context_from_order_row(row)
    assert ctx is not None
    assert ctx.has_provider_ref is True
    assert fulfillment_controls_allowed(ctx) is True
    html = format_fulfillment_admin_block(row)
    assert "manual_only" in html
    assert "uuid-1" in html
    assert "Автовыдача" in html


def test_fulfillment_controls_not_for_completed() -> None:
    ctx = AdminOrderFfContext(
        status="completed",
        fulfillment_mode_raw=None,
        attempt_count=0,
        has_provider_ref=False,
    )
    assert fulfillment_controls_allowed(ctx) is False
    assert format_fulfillment_admin_block({"status": "completed"}) == ""


def test_admin_kb_super_sees_reset_and_manual_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:kb")
    monkeypatch.setenv("ADMIN_IDS", "10,20")
    monkeypatch.setenv("SUPER_ADMIN_IDS", "20")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    s = Settings()
    ctx = AdminOrderFfContext(status="paid", fulfillment_mode_raw=None, attempt_count=0, has_provider_ref=False)
    cds = _dump_callbacks(admin_order_kb(99, settings=s, actor_id=20, order_ff=ctx))
    assert any("adm:ffman:99" in c for c in cds)
    assert any("adm:ffrst:99" in c for c in cds)


def test_admin_kb_operator_sees_only_manual(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:kb2")
    monkeypatch.setenv("ADMIN_IDS", "10,20")
    monkeypatch.setenv("SUPER_ADMIN_IDS", "20")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    s = Settings()
    ctx = AdminOrderFfContext(status="paid", fulfillment_mode_raw=None, attempt_count=0, has_provider_ref=False)
    cds = _dump_callbacks(admin_order_kb(7, settings=s, actor_id=10, order_ff=ctx))
    assert any("adm:ffman:7" in c for c in cds)
    assert not any("ffrst" in c for c in cds)
    assert not any("ffauto" in c for c in cds)


def test_admin_kb_manual_shows_auto_for_super(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:kb3")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    s = Settings()
    ctx = AdminOrderFfContext(status="paid", fulfillment_mode_raw="manual_only", attempt_count=1, has_provider_ref=False)
    cds = _dump_callbacks(admin_order_kb(3, settings=s, actor_id=1, order_ff=ctx))
    assert any("adm:ffauto:3" in c for c in cds)


@pytest.mark.asyncio
async def test_set_fulfillment_mode_and_reset(tmp_path) -> None:
    db = tmp_path / "aff.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="S",
        payment_method="t",
        usd_base=1.0,
        rub_before=1.0,
        rub_after=1.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="paid",
    )
    await conn.execute(
        "UPDATE orders SET fulfillment_attempt_count = 2, fulfillment_last_error = 'e', "
        "fulfillment_provider_ref = 'rid' WHERE id = ?",
        (oid,),
    )
    await conn.commit()

    ok = await orders_repo.set_order_fulfillment_mode(conn, oid, mode="manual_only")
    assert ok is True
    row = await orders_repo.get_order(conn, oid)
    assert str(row["fulfillment_mode"]) == "manual_only"

    s = Settings(BOT_TOKEN="9:t", ADMIN_IDS="1", API_KEY_PEPPER="k" * 32, AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=True)  # type: ignore[call-arg]
    order_map = {str(k): row[k] for k in row.keys()}
    ok_elig, reason = auto_fulfill_order_eligible(
        order_map,
        s,
        product_kind="stars",
        stars=100,
    )
    assert ok_elig is False
    assert reason == "manual_only"

    ok2 = await orders_repo.set_order_fulfillment_mode(conn, oid, mode="auto")
    assert ok2 is True

    ok3 = await orders_repo.super_reset_paid_auto_fulfill_fields(conn, oid)
    assert ok3 is True
    row2 = await orders_repo.get_order(conn, oid)
    assert int(row2["fulfillment_attempt_count"] or 0) == 0
    assert row2["fulfillment_last_error"] in (None, "")
    assert row2["fulfillment_provider_ref"] in (None, "")
    await conn.close()


@pytest.mark.asyncio
async def test_invalid_fulfillment_mode_raises(tmp_path) -> None:
    db = tmp_path / "aff2.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="S",
        payment_method="t",
        usd_base=1.0,
        rub_before=1.0,
        rub_after=1.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="paid",
    )
    with pytest.raises(ValueError, match="invalid_fulfillment_mode"):
        await orders_repo.set_order_fulfillment_mode(conn, oid, mode="bogus")
    await conn.close()
