from __future__ import annotations

import time

from aladdin_shop_vpn_api import hmac_auth


def test_signature_roundtrip() -> None:
    secret = "s" * 32
    body = b'{"telegram_user_id":1,"order_id":1,"paid_until":"2099-01-01T00:00:00+00:00"}'
    ts = str(int(time.time()))
    nonce = "n-once-1"
    path = "/internal/v1/provision"
    sig = hmac_auth.compute_signature(secret, method="POST", path=path, timestamp=ts, nonce=nonce, body=body)
    ok, err = hmac_auth.verify_signature(
        secret, method="POST", path=path, timestamp=ts, nonce=nonce, body=body, signature_hex=sig
    )
    assert ok and err == ""
