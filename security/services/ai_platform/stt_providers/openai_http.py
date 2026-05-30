# -*- coding: utf-8 -*-
"""OpenAI Whisper HTTP client with optional EU proxy."""

from __future__ import annotations

import logging
import os
from typing import Dict
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener, urlopen

logger = logging.getLogger(__name__)

OPENAI_TRANSCRIPTIONS_URL = "https://api.openai.com/v1/audio/transcriptions"


def openai_api_key() -> str:
    for name in ("COMPANION_STT_OPENAI_API_KEY", "OPENAI_API_KEY"):
        val = (os.getenv(name) or "").strip()
        if val:
            return val
    return ""


def openai_https_proxy() -> str:
    for name in ("COMPANION_STT_OPENAI_HTTPS_PROXY", "COMPANION_STT_HTTPS_PROXY"):
        val = (os.getenv(name) or "").strip()
        if val:
            return val
    return ""


def http_error_reason(exc: HTTPError) -> str:
    if exc.code in (403, 451):
        return "server_stt_geo_blocked"
    return "server_stt_provider_error"


def post_openai_multipart(body: bytes, headers: Dict[str, str], *, timeout: float = 45) -> bytes:
    proxy = openai_https_proxy()
    if proxy:
        return post_via_proxy(body, headers, proxy=proxy, timeout=timeout)
    req = Request(OPENAI_TRANSCRIPTIONS_URL, data=body, method="POST", headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        reason = http_error_reason(exc)
        logger.warning(
            "companion_stt_openai_http_error status=%s reason=%s detail=%s",
            exc.code,
            reason,
            detail,
        )
        raise ValueError(reason) from exc
    except URLError as exc:
        logger.warning("companion_stt_openai_network_error error=%s", exc)
        raise ValueError("server_stt_network_error") from exc


def post_via_proxy(
    body: bytes,
    headers: Dict[str, str],
    *,
    proxy: str,
    timeout: float,
) -> bytes:
    proxy_l = proxy.lower()
    if proxy_l.startswith("socks"):
        try:
            import requests
        except ImportError as exc:
            logger.warning("companion_stt_socks_proxy_requires_requests_or_pysocks")
            raise ValueError("server_stt_proxy_unavailable") from exc
        try:
            resp = requests.post(
                OPENAI_TRANSCRIPTIONS_URL,
                data=body,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=timeout,
            )
        except requests.RequestException as exc:
            logger.warning("companion_stt_openai_network_error proxy=%s error=%s", proxy[:32], exc)
            raise ValueError("server_stt_network_error") from exc
        if resp.status_code >= 400:
            reason = (
                "server_stt_geo_blocked"
                if resp.status_code in (403, 451)
                else "server_stt_provider_error"
            )
            logger.warning(
                "companion_stt_openai_http_error status=%s reason=%s detail=%s",
                resp.status_code,
                reason,
                (resp.text or "")[:300],
            )
            raise ValueError(reason)
        return resp.content

    opener = build_opener(ProxyHandler({"http": proxy, "https": proxy}))
    req = Request(OPENAI_TRANSCRIPTIONS_URL, data=body, method="POST", headers=headers)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        reason = http_error_reason(exc)
        logger.warning(
            "companion_stt_openai_http_error status=%s reason=%s proxy=%s detail=%s",
            exc.code,
            reason,
            proxy[:32],
            detail,
        )
        raise ValueError(reason) from exc
    except URLError as exc:
        logger.warning("companion_stt_openai_network_error proxy=%s error=%s", proxy[:32], exc)
        raise ValueError("server_stt_network_error") from exc
