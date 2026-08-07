"""Crypto Pay / xRocket payload для пополнения баланса (отдельно от заказов SB1)."""

from __future__ import annotations

from dataclasses import dataclass

_PAYLOAD_MAGIC = "SB1T"
_PAYLOAD_SEP = "|"
_MAX_PAYLOAD_LEN = 512


@dataclass(frozen=True)
class DecodedTopupCryptoPayload:
    topup_id: int
    due_kop: int

    @property
    def due_rub(self) -> float:
        return self.due_kop / 100.0


def encode_topup_crypto_payload(*, topup_id: int, due_rub: float) -> str:
    if topup_id < 1:
        raise ValueError("invalid_topup_id")
    due = round(max(0.0, float(due_rub)), 2)
    if due < 0.01:
        raise ValueError("invalid_due_rub")
    kop = int(round(due * 100))
    raw = f"{_PAYLOAD_MAGIC}{_PAYLOAD_SEP}{topup_id}{_PAYLOAD_SEP}{kop}"
    if len(raw) > _MAX_PAYLOAD_LEN:
        raise ValueError("payload_too_long")
    return raw


def decode_topup_crypto_payload(raw: str) -> DecodedTopupCryptoPayload:
    s = (raw or "").strip()
    parts = s.split(_PAYLOAD_SEP)
    if len(parts) != 3 or parts[0] != _PAYLOAD_MAGIC:
        raise ValueError("invalid_topup_crypto_payload")
    try:
        tid = int(parts[1], 10)
        kop = int(parts[2], 10)
    except ValueError as exc:
        raise ValueError("invalid_topup_crypto_payload_fields") from exc
    if tid < 1 or kop < 1:
        raise ValueError("invalid_topup_crypto_payload_fields")
    return DecodedTopupCryptoPayload(topup_id=tid, due_kop=kop)


def is_topup_crypto_payload(raw: str) -> bool:
    return (raw or "").strip().startswith(f"{_PAYLOAD_MAGIC}{_PAYLOAD_SEP}")


def verify_decoded_topup_payload(decoded: DecodedTopupCryptoPayload, row: object) -> None:
    """Сверка payload с записью topup_requests."""
    try:
        tid = int(row["id"])  # type: ignore[index]
        amt_rub = float(row["amount_rub"])  # type: ignore[index]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid_topup_row") from exc
    if tid != decoded.topup_id:
        raise ValueError("topup_id_mismatch")
    expected_kop = int(round(amt_rub * 100))
    if decoded.due_kop != expected_kop:
        raise ValueError("amount_mismatch")
