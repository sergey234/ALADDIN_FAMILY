from __future__ import annotations

import pytest

from bot.services.istar_circuit_breaker import (
    istar_circuit_is_open,
    istar_circuit_record_success,
    istar_circuit_record_transient_failure,
)
from bot.services.istar_fulfill_client import IstarFulfillError
from bot.services.istar_fulfill_errors import (
    backoff_minutes_for_transient_count,
    istar_error_counts_as_fulfill_attempt,
    istar_error_is_server_http,
    istar_error_is_transient,
)


def test_istar_error_is_transient_500() -> None:
    exc = IstarFulfillError("istar_http_500", status_code=500)
    assert istar_error_is_transient(exc) is True
    assert istar_error_counts_as_fulfill_attempt(exc) is False


def test_istar_error_is_permanent_404() -> None:
    exc = IstarFulfillError("istar_http_404", status_code=404)
    assert istar_error_is_transient(exc) is False
    assert istar_error_counts_as_fulfill_attempt(exc) is True


def test_istar_error_network_transient() -> None:
    exc = IstarFulfillError("istar_http_error:timeout")
    assert istar_error_is_transient(exc) is True
    assert istar_error_counts_as_fulfill_attempt(exc) is False


def test_backoff_minutes_schedule() -> None:
    assert backoff_minutes_for_transient_count(1) == 2
    assert backoff_minutes_for_transient_count(2) == 5
    assert backoff_minutes_for_transient_count(3) == 15
    assert backoff_minutes_for_transient_count(4) == 30
    assert backoff_minutes_for_transient_count(99) == 30


def test_istar_error_is_server_http_detects_500() -> None:
    exc = IstarFulfillError("istar_http_500", status_code=500, body="Internal Server Error")
    assert istar_error_is_server_http(exc) is True


def test_circuit_breaker_opens_after_three_transient() -> None:
    istar_circuit_record_success()
    assert istar_circuit_is_open() is False
    assert istar_circuit_record_transient_failure() is False
    assert istar_circuit_record_transient_failure() is False
    assert istar_circuit_record_transient_failure() is True
    assert istar_circuit_is_open() is True
    istar_circuit_record_success()
    assert istar_circuit_is_open() is False


@pytest.mark.asyncio
async def test_revert_and_transient_retry(tmp_path) -> None:
    from bot.db.database import connect
    from bot.services import orders_repo, users_repo

    db = tmp_path / "retry.db"
    conn = await connect(db)
    await users_repo.upsert_user(conn, user_id=1, username="u", first_name="U")
    oid = await orders_repo.create_order(
        conn,
        user_id=1,
        product_id="stars_100",
        product_title="100 Stars",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=100.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@testuser",
    )
    await orders_repo.update_status(conn, oid, "paid")
    claimed = await orders_repo.claim_auto_fulfill_attempt_slot(conn, order_id=oid, max_attempts=5)
    assert claimed is not None
    assert int(claimed["fulfillment_attempt_count"]) == 1

    await orders_repo.revert_auto_fulfill_attempt_claim(conn, oid)
    row = await orders_repo.get_order(conn, oid)
    assert int(row["fulfillment_attempt_count"]) == 0

    tc = await orders_repo.schedule_auto_fulfill_transient_retry(
        conn, oid, error_message="istar_http_500", backoff_minutes=2
    )
    assert tc == 1
    row2 = await orders_repo.get_order(conn, oid)
    assert row2["fulfillment_retry_after"] is not None
    assert row2["fulfillment_last_error"] == "istar_http_500"
    await conn.close()
