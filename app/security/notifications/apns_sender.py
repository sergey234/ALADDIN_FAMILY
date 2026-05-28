"""
Отправка alert push через Apple Push Notification service (HTTP/2).
Требует переменные окружения (см. APNSConfig).
Без конфигурации методы безопасно возвращают False и пишут в лог.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import jwt
except ImportError:  # pragma: no cover
    jwt = None  # type: ignore

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore


@dataclass
class APNSConfig:
    team_id: str
    key_id: str
    auth_key_path: str
    topic: str  # bundle id, e.g. family.aladdin.ios
    use_sandbox: bool = True

    @classmethod
    def from_env(cls) -> Optional["APNSConfig"]:
        team = os.getenv("APNS_TEAM_ID", "").strip()
        kid = os.getenv("APNS_KEY_ID", "").strip()
        key_path = os.getenv("APNS_AUTH_KEY_PATH", "").strip()
        topic = os.getenv("APNS_TOPIC", "").strip()
        if not (team and kid and key_path and topic):
            return None
        sandbox = os.getenv("APNS_USE_SANDBOX", "true").lower() in ("1", "true", "yes")
        return cls(
            team_id=team,
            key_id=kid,
            auth_key_path=key_path,
            topic=topic,
            use_sandbox=sandbox,
        )


def _build_provider_token(cfg: APNSConfig) -> Optional[str]:
    if jwt is None:
        logger.error("PyJWT не установлен — невозможна подпись APNS")
        return None
    try:
        with open(cfg.auth_key_path, "r", encoding="utf-8") as f:
            key_data = f.read()
    except OSError as e:
        logger.error("Не удалось прочитать APNS ключ %s: %s", cfg.auth_key_path, e)
        return None

    headers = {"alg": "ES256", "kid": cfg.key_id}
    now = int(time.time())
    claims = {"iss": cfg.team_id, "iat": now}
    try:
        return jwt.encode(claims, key_data, algorithm="ES256", headers=headers)
    except Exception as e:  # pragma: no cover
        logger.error("Ошибка JWT для APNS: %s", e)
        return None


def _apns_host(cfg: APNSConfig) -> str:
    if cfg.use_sandbox:
        return "https://api.sandbox.push.apple.com"
    return "https://api.push.apple.com"


async def send_apns_alert(
    device_token_hex: str,
    title: str,
    body: str,
    *,
    extra: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Отправляет видимое уведомление на одно устройство.
    device_token_hex — 64-символьная hex строка без пробелов.
    """
    if httpx is None:
        logger.warning("httpx не установлен — APNS пропущен")
        return False

    cfg = APNSConfig.from_env()
    if cfg is None:
        logger.debug(
            "APNS не сконфигурирован (задайте APNS_TEAM_ID, APNS_KEY_ID, APNS_AUTH_KEY_PATH, APNS_TOPIC)"
        )
        return False

    bearer = _build_provider_token(cfg)
    if not bearer:
        return False

    url = f"{_apns_host(cfg).rstrip('/')}/3/device/{device_token_hex.strip()}"
    payload: Dict[str, Any] = {
        "aps": {
            "alert": {"title": title, "body": body},
            "sound": "default",
        }
    }
    if extra:
        payload["aladdin"] = extra

    headers = {
        "authorization": f"bearer {bearer}",
        "apns-topic": cfg.topic,
        "apns-push-type": "alert",
        "apns-priority": "10",
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return True
        logger.warning(
            "APNS ошибка %s: %s",
            response.status_code,
            response.text[:500],
        )
        return False
    except Exception as e:  # pragma: no cover
        logger.error("Сбой HTTP при отправке APNS: %s", e)
        return False
