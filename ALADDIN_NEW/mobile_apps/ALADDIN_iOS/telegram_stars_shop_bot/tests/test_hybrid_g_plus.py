from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services import orders_repo, users_repo
from bot.services.auto_fulfill_runner import notify_ops_auto_fulfill_create_failed
from bot.services.stuck_orders_monitor import run_stuck_processing_check


def _settings_db(path: str, **kwargs: object) -> Settings:
    base = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        DATABASE_PATH=path,
        ALERTS_ENABLED=True,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_list_order_ids_stuck_processing_only(conn, temp_db_path) -> None:
    await users_repo.upsert_user(conn, user_id=601, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=601,
        product_id="s",
        product_title="S",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@x",
        status="processing",
    )
    await conn.execute(
        "UPDATE orders SET updated_at = datetime('now', '-90 minutes') WHERE id = ?",
        (oid,),
    )
    await conn.commit()

    stuck = await orders_repo.list_order_ids_stuck_processing_only(
        conn, minutes_without_update=45, limit=50
    )
    assert oid in stuck

    fresh = await orders_repo.list_order_ids_stuck_processing_only(
        conn, minutes_without_update=500, limit=50
    )
    assert oid not in fresh


@pytest.mark.asyncio
async def test_list_orders_operator_attention_queue(conn) -> None:
    await users_repo.upsert_user(conn, user_id=602, username="u2", first_name="U")
    oid_err = await orders_repo.create_order(
        conn,
        user_id=602,
        product_id="s",
        product_title="ErrProduct",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@a",
        status="paid",
    )
    await orders_repo.set_fulfillment_last_error(conn, oid_err, "missing_recipient_username")

    oid_proc = await orders_repo.create_order(
        conn,
        user_id=602,
        product_id="s",
        product_title="ProcProduct",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@b",
        status="processing",
    )
    await conn.execute(
        "UPDATE orders SET updated_at = datetime('now', '-120 minutes') WHERE id = ?",
        (oid_proc,),
    )
    await conn.commit()

    q = await orders_repo.list_orders_operator_attention_queue(
        conn, processing_idle_minutes=30, limit=20
    )
    ids = {int(r["id"]) for r in q}
    assert oid_err in ids
    assert oid_proc in ids


@pytest.mark.asyncio
async def test_run_stuck_processing_check_sends_alert(conn, temp_db_path, monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[dict[str, object]] = []

    async def fake_send_alert(settings: Settings, severity: str, title: str, body: str, dedupe_key: str) -> bool:
        sent.append(
            {"severity": severity, "title": title, "body": body, "dedupe_key": dedupe_key}
        )
        return True

    monkeypatch.setattr("bot.services.stuck_orders_monitor.send_alert", fake_send_alert)

    await users_repo.upsert_user(conn, user_id=603, username="u3", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=603,
        product_id="s",
        product_title="P",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@z",
        status="processing",
    )
    await conn.execute(
        "UPDATE orders SET updated_at = datetime('now', '-200 minutes') WHERE id = ?",
        (oid,),
    )
    await conn.commit()

    settings = _settings_db(
        str(temp_db_path),
        STUCK_PROCESSING_ALERT_MINUTES=60,
    )
    await run_stuck_processing_check(settings)
    assert len(sent) == 1
    assert "stuck processing" in str(sent[0]["title"]).lower()
    assert str(oid) in str(sent[0]["body"])


@pytest.mark.asyncio
async def test_notify_ops_auto_fulfill_create_failed_respects_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[object] = []

    async def fake_send_alert(*_a: object, **_k: object) -> bool:
        called.append(True)
        return True

    monkeypatch.setattr("bot.services.auto_fulfill_runner.send_alert", fake_send_alert)
    s = Settings(  # type: ignore[arg-type]
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        AUTO_FULFILL_FAILURE_ALERTS_ENABLED=False,
    )
    await notify_ops_auto_fulfill_create_failed(
        s, order_id=1, username="bob", exc=Exception("fail")
    )
    assert called == []

    s2 = Settings(  # type: ignore[arg-type]
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        AUTO_FULFILL_FAILURE_ALERTS_ENABLED=True,
    )
    await notify_ops_auto_fulfill_create_failed(
        s2, order_id=7, username="ann", exc=Exception("boom")
    )
    assert len(called) == 1
