"""
Apple DeviceCheck two-bit ledger: "this iPhone already had a trial".

bit0 = trial consumed. Bits are kept by Apple per device + developer team and
survive app deletion, account switch and a full device reset.

Env (secrets live only on the server, never in git):
  APPLE_DEVICECHECK_KEY_ID    Key ID of the .p8 key with DeviceCheck enabled
  APPLE_DEVICECHECK_TEAM_ID   Team ID (default B3WGHSWL79)
  APPLE_DEVICECHECK_KEY_PATH  path to the .p8 file
  APPLE_DEVICECHECK_ENV       production | development (default production)

Every call is fail-open: on missing config / token / Apple error the result is
None ("unknown") and the caller falls back to the server device ledger.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Optional

logger = logging.getLogger("apple_device_check")

_HOSTS = {
    "production": "https://api.devicecheck.apple.com",
    "development": "https://api.development.devicecheck.apple.com",
}
_TIMEOUT_SECONDS = 4.0
_JWT_TTL_SECONDS = 50 * 60

_cached_jwt: Optional[str] = None
_cached_jwt_at: float = 0.0


def _config() -> Optional[dict]:
    key_id = (os.getenv("APPLE_DEVICECHECK_KEY_ID") or "").strip()
    team_id = (os.getenv("APPLE_DEVICECHECK_TEAM_ID") or "B3WGHSWL79").strip()
    key_path = (os.getenv("APPLE_DEVICECHECK_KEY_PATH") or "").strip()
    env = (os.getenv("APPLE_DEVICECHECK_ENV") or "production").strip().lower()
    if not key_id or not team_id or not key_path or not os.path.isfile(key_path):
        return None
    return {
        "key_id": key_id,
        "team_id": team_id,
        "key_path": key_path,
        "host": _HOSTS.get(env, _HOSTS["production"]),
    }


def is_configured() -> bool:
    return _config() is not None


def token_required() -> bool:
    """APPLE_DEVICECHECK_REQUIRE_TOKEN=1: clients without a token (old builds) get no new trial."""
    return os.getenv("APPLE_DEVICECHECK_REQUIRE_TOKEN", "").strip() == "1" and is_configured()


def _auth_jwt(cfg: dict) -> str:
    global _cached_jwt, _cached_jwt_at
    now = time.time()
    if _cached_jwt and now - _cached_jwt_at < _JWT_TTL_SECONDS:
        return _cached_jwt
    import jwt  # PyJWT + cryptography (ES256)

    with open(cfg["key_path"], "r", encoding="utf-8") as fh:
        private_key = fh.read()
    token = jwt.encode(
        {"iss": cfg["team_id"], "iat": int(now)},
        private_key,
        algorithm="ES256",
        headers={"kid": cfg["key_id"]},
    )
    _cached_jwt, _cached_jwt_at = token, now
    return token


def _post(path: str, payload: dict) -> Optional[tuple]:
    cfg = _config()
    if cfg is None:
        return None
    import httpx

    try:
        resp = httpx.post(
            cfg["host"] + path,
            json=payload,
            headers={"Authorization": "Bearer " + _auth_jwt(cfg)},
            timeout=_TIMEOUT_SECONDS,
        )
        return resp.status_code, resp.text
    except Exception as exc:  # network / key / signing
        logger.warning("devicecheck_request_failed path=%s error=%s", path, type(exc).__name__)
        return None


def _base_payload(device_token: str) -> dict:
    return {
        "device_token": device_token,
        "transaction_id": str(uuid.uuid4()),
        "timestamp": int(time.time() * 1000),
    }


def parse_query_response(status_code: int, body: str) -> Optional[bool]:
    """True = trial already consumed on this iPhone, False = never, None = unknown."""
    if status_code != 200:
        return None
    text = (body or "").strip()
    if not text or "failed to find bit state" in text.lower():
        return False
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return bool(data.get("bit0", False))


def trial_already_used(device_token: Optional[str]) -> Optional[bool]:
    token = (device_token or "").strip()
    if not token:
        return None
    result = _post("/v1/query_two_bits", _base_payload(token))
    if result is None:
        return None
    status_code, body = result
    verdict = parse_query_response(status_code, body)
    if verdict is None:
        logger.warning("devicecheck_query_unexpected status=%s", status_code)
    return verdict


def mark_trial_used(device_token: Optional[str]) -> bool:
    token = (device_token or "").strip()
    if not token:
        return False
    payload = _base_payload(token)
    payload.update({"bit0": True, "bit1": False})
    result = _post("/v1/update_two_bits", payload)
    ok = result is not None and result[0] == 200
    if not ok:
        logger.warning("devicecheck_update_failed status=%s", result[0] if result else "error")
    return ok
