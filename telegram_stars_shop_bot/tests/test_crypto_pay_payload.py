from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services import orders_repo, users_repo
from bot.services.crypto_pay_payload import (
    DecodedCryptoInvoicePayload,
    crypto_invoice_expires_in_seconds,
    decode_crypto_invoice_payload,
    encode_crypto_invoice_payload,
    order_supports_crypto_pay_invoice,
    verify_decoded_payload_against_order,
)


def test_encode_decode_roundtrip() -> None:
    s = encode_crypto_invoice_payload(order_id=42, due_rub=123.45)
    assert s == "SB1|42|12345"
    d = decode_crypto_invoice_payload(s)
    assert d == DecodedCryptoInvoicePayload(version=1, order_id=42, due_kop=12345)
    assert d.due_rub == 123.45


def test_encode_minimum_due() -> None:
    s = encode_crypto_invoice_payload(order_id=1, due_rub=0.01)
    assert decode_crypto_invoice_payload(s).due_kop == 1


def test_encode_decode_99_99_no_float_drift() -> None:
    s = encode_crypto_invoice_payload(order_id=7, due_rub=99.99)
    assert s == "SB1|7|9999"
    assert decode_crypto_invoice_payload(s).due_kop == 9999


def test_encode_rejects_invalid() -> None:
    with pytest.raises(ValueError, match="invalid_order_id"):
        encode_crypto_invoice_payload(order_id=0, due_rub=10.0)
    with pytest.raises(ValueError, match="invalid_due_rub"):
        encode_crypto_invoice_payload(order_id=1, due_rub=0.0)
    with pytest.raises(ValueError, match="invalid_due_rub"):
        encode_crypto_invoice_payload(order_id=1, due_rub=-1.0)


def test_decode_rejects_garbage() -> None:
    with pytest.raises(ValueError, match="invalid_crypto_payload"):
        decode_crypto_invoice_payload("")
    with pytest.raises(ValueError, match="invalid_crypto_payload"):
        decode_crypto_invoice_payload("SB2|1|100")
    with pytest.raises(ValueError, match="invalid_crypto_payload_fields"):
        decode_crypto_invoice_payload("SB1|x|100")


@pytest.mark.asyncio
async def test_verify_full_crypto_order(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8001, username="c", first_name="C")
    oid = await orders_repo.create_order(
        conn,
        user_id=8001,
        product_id="x",
        product_title="X",
        payment_method="crypto",
        usd_base=1.0,
        rub_before=100.0,
        rub_after=99.99,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    row = await orders_repo.get_order(conn, oid)
    assert row is not None
    raw = encode_crypto_invoice_payload(order_id=oid, due_rub=orders_repo.amount_due_external(row))
    dec = decode_crypto_invoice_payload(raw)
    verify_decoded_payload_against_order(dec, row)


@pytest.mark.asyncio
async def test_verify_mix_crypto_due(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8002, username="m", first_name="M")
    oid = await orders_repo.create_order(
        conn,
        user_id=8002,
        product_id="x",
        product_title="X",
        payment_method="mix_crypto",
        usd_base=1.0,
        rub_before=200.0,
        rub_after=200.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
        balance_applied_rub=50.0,
    )
    row = await orders_repo.get_order(conn, oid)
    assert row is not None
    assert orders_repo.amount_due_external(row) == 150.0
    raw = encode_crypto_invoice_payload(order_id=oid, due_rub=150.0)
    verify_decoded_payload_against_order(decode_crypto_invoice_payload(raw), row)


@pytest.mark.asyncio
async def test_verify_wrong_due_fails(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8003, username="w", first_name="W")
    oid = await orders_repo.create_order(
        conn,
        user_id=8003,
        product_id="x",
        product_title="X",
        payment_method="crypto",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    row = await orders_repo.get_order(conn, oid)
    assert row is not None
    bad = decode_crypto_invoice_payload(encode_crypto_invoice_payload(order_id=oid, due_rub=9.99))
    with pytest.raises(ValueError, match="crypto_payload_due_mismatch"):
        verify_decoded_payload_against_order(bad, row)


@pytest.mark.asyncio
async def test_order_supports_flags(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8005, username="s", first_name="S")
    oid_c = await orders_repo.create_order(
        conn,
        user_id=8005,
        product_id="x",
        product_title="X",
        payment_method="crypto",
        usd_base=1.0,
        rub_before=1.0,
        rub_after=1.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    row_c = await orders_repo.get_order(conn, oid_c)
    assert row_c is not None
    assert order_supports_crypto_pay_invoice(row_c) is True
    oid_f = await orders_repo.create_order(
        conn,
        user_id=8005,
        product_id="x",
        product_title="X",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=1.0,
        rub_after=1.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    row_f = await orders_repo.get_order(conn, oid_f)
    assert row_f is not None
    assert order_supports_crypto_pay_invoice(row_f) is False


@pytest.mark.asyncio
async def test_verify_fiat_order_rejected(conn) -> None:
    await users_repo.upsert_user(conn, user_id=8004, username="f", first_name="F")
    oid = await orders_repo.create_order(
        conn,
        user_id=8004,
        product_id="x",
        product_title="X",
        payment_method="fiat",
        usd_base=1.0,
        rub_before=10.0,
        rub_after=10.0,
        referral_discount_rub=0.0,
        wholesale_discount_rub=0.0,
        referrer_id=None,
        commission_rub=0.0,
        user_note="@u",
        status="pending_payment",
    )
    row = await orders_repo.get_order(conn, oid)
    assert row is not None
    dec = decode_crypto_invoice_payload(encode_crypto_invoice_payload(order_id=oid, due_rub=10.0))
    with pytest.raises(ValueError, match="crypto_payload_payment_method"):
        verify_decoded_payload_against_order(dec, row)


def _s(**kwargs: object) -> Settings:
    base: dict[str, object] = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_crypto_invoice_expires_cap_by_order_ttl() -> None:
    s = _s(
        CRYPTO_PAY_INVOICE_EXPIRE_SECONDS=7200,
        ORDER_PENDING_PAYMENT_EXPIRE_MINUTES=60,
    )
    assert crypto_invoice_expires_in_seconds(s) == 3600


def test_crypto_invoice_expires_when_order_ttl_off() -> None:
    s = _s(
        CRYPTO_PAY_INVOICE_EXPIRE_SECONDS=120,
        ORDER_PENDING_PAYMENT_EXPIRE_MINUTES=0,
    )
    assert crypto_invoice_expires_in_seconds(s) == 120


def test_crypto_invoice_expires_minimum_60() -> None:
    s = _s(
        CRYPTO_PAY_INVOICE_EXPIRE_SECONDS=30,
        ORDER_PENDING_PAYMENT_EXPIRE_MINUTES=0,
    )
    assert crypto_invoice_expires_in_seconds(s) == 60