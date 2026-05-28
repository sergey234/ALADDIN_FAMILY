from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _scrub_headers(headers: dict[str, Any]) -> None:
    for k in list(headers.keys()):
        lk = k.lower()
        if lk in ("x-api-key", "authorization", "x-payment-signature", "x-partner-signature", "x-signature"):
            headers[k] = "[Filtered]"


def scrub_sentry_event(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    try:
        req = event.get("request")
        if isinstance(req, dict):
            h = req.get("headers")
            if isinstance(h, dict):
                _scrub_headers(h)
        if "extra" in event and isinstance(event["extra"], dict):
            for k in list(event["extra"].keys()):
                if "token" in k.lower() or "secret" in k.lower() or "key" in k.lower():
                    event["extra"][k] = "[Filtered]"
    except Exception:
        logger.debug("sentry scrub failed", exc_info=True)
    return event


def init_sentry_fastapi(*, dsn: str, environment: str | None, traces_sample_rate: float) -> None:
    if not (dsn or "").strip():
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        logger.warning("sentry-sdk not installed; skip Sentry init for vpn-api")
        return

    sentry_sdk.init(
        dsn=dsn.strip(),
        environment=(environment or "").strip() or None,
        traces_sample_rate=max(0.0, min(1.0, traces_sample_rate)),
        integrations=[
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            FastApiIntegration(),
        ],
        before_send=scrub_sentry_event,
    )
