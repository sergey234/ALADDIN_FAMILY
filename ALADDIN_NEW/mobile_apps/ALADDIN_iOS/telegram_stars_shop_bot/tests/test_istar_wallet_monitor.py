from __future__ import annotations

import pytest

from bot.services.istar_wallet_monitor import istar_error_looks_like_insufficient_funds


@pytest.mark.parametrize(
    "msg",
    [
        "insufficient funds on wallet",
        "Not enough TON balance",
        "balance too low",
        "недостаточно средств",
    ],
)
def test_insufficient_funds_detection(msg: str) -> None:
    assert istar_error_looks_like_insufficient_funds(Exception(msg)) is True


def test_insufficient_funds_negative() -> None:
    assert istar_error_looks_like_insufficient_funds(Exception("invalid username")) is False
