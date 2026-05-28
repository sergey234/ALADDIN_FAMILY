"""
Prometheus-метрики для aladdin-shop-vpn-api (vpn-15).

GET /metrics — текстовый exposition; HTTP — Histogram + Counter; vpn.db — Gauges при scrape.
Не публикуйте /metrics в открытый интернет без ACL (см. deploy/VPN15_OBSERVABILITY_RUNBOOK.md).
"""

from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path
from typing import Callable

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_HTTP_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0, 30.0)

http_request_duration_seconds = Histogram(
    "aladdin_shop_vpn_http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "route"],
    buckets=_HTTP_BUCKETS,
)

http_requests_total = Counter(
    "aladdin_shop_vpn_http_requests_total",
    "HTTP requests",
    ["method", "route", "status_class"],
)


def _status_class(code: int) -> str:
    if 200 <= code < 300:
        return "2xx"
    if 300 <= code < 400:
        return "3xx"
    if 400 <= code < 500:
        return "4xx"
    return "5xx"


def normalize_route(path: str) -> str:
    if path == "/metrics":
        return "/metrics"
    if path.startswith("/sub/"):
        return "/sub/*"
    if path.startswith("/internal/v1/"):
        return path.split("?", 1)[0].rstrip("/") or "/internal/v1"
    if path.startswith("/v1/legal/"):
        return path.split("?", 1)[0].rstrip("/") or "/v1/legal"
    if path in ("/health", "/ready", "/docs", "/redoc", "/openapi.json"):
        return path
    return path or "/"


# --- vpn.db gauges (обновляются при каждом scrape /metrics) ---

gauge_jobs_pending = Gauge("aladdin_shop_vpn_jobs_pending", "Jobs with status pending")
gauge_jobs_processing = Gauge("aladdin_shop_vpn_jobs_processing", "Jobs with status processing")
gauge_jobs_failed = Gauge("aladdin_shop_vpn_jobs_failed", "Jobs with status failed")
gauge_jobs_done = Gauge("aladdin_shop_vpn_jobs_done", "Jobs with status done")
gauge_accounts_active = Gauge("aladdin_shop_vpn_accounts_vpn_active", "Accounts status=vpn_active")
gauge_accounts_provisioning = Gauge(
    "aladdin_shop_vpn_accounts_vpn_provisioning",
    "Accounts status=vpn_provisioning",
)
gauge_accounts_expired = Gauge("aladdin_shop_vpn_accounts_vpn_expired", "Accounts status=vpn_expired")
gauge_accounts_failed = Gauge("aladdin_shop_vpn_accounts_vpn_failed", "Accounts status=vpn_failed")
gauge_accounts_manual = Gauge(
    "aladdin_shop_vpn_accounts_vpn_manual_override",
    "Accounts status=vpn_manual_override",
)


def refresh_db_gauges(db_path: Path | None) -> None:
    """Синхронное чтение vpn.db; при ошибке — нули (кроме уже выставленных значений)."""
    if db_path is None or not Path(db_path).is_file():
        for g in (
            gauge_jobs_pending,
            gauge_jobs_processing,
            gauge_jobs_failed,
            gauge_jobs_done,
            gauge_accounts_active,
            gauge_accounts_provisioning,
            gauge_accounts_expired,
            gauge_accounts_failed,
            gauge_accounts_manual,
        ):
            g.set(0)
        return
    try:
        conn = sqlite3.connect(str(db_path), timeout=2.0)
        try:
            gauge_jobs_pending.set(0)
            gauge_jobs_processing.set(0)
            gauge_jobs_failed.set(0)
            gauge_jobs_done.set(0)
            gauge_accounts_active.set(0)
            gauge_accounts_provisioning.set(0)
            gauge_accounts_expired.set(0)
            gauge_accounts_failed.set(0)
            gauge_accounts_manual.set(0)

            cur = conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            pending = processing = failed = done = 0
            for st, n in cur.fetchall():
                raw = str(st or "")
                c = int(n or 0)
                if raw == "pending":
                    pending = c
                elif raw == "processing":
                    processing = c
                elif raw == "failed":
                    failed = c
                elif raw == "done":
                    done = c
            gauge_jobs_pending.set(pending)
            gauge_jobs_processing.set(processing)
            gauge_jobs_failed.set(failed)
            gauge_jobs_done.set(done)

            cur2 = conn.execute("SELECT status, COUNT(*) FROM vpn_accounts GROUP BY status")
            a_act = a_prov = a_exp = a_fail = a_man = 0
            for st, n in cur2.fetchall():
                raw = str(st or "")
                c = int(n or 0)
                if raw == "vpn_active":
                    a_act = c
                elif raw == "vpn_provisioning":
                    a_prov = c
                elif raw == "vpn_expired":
                    a_exp = c
                elif raw == "vpn_failed":
                    a_fail = c
                elif raw == "vpn_manual_override":
                    a_man = c
            gauge_accounts_active.set(a_act)
            gauge_accounts_provisioning.set(a_prov)
            gauge_accounts_expired.set(a_exp)
            gauge_accounts_failed.set(a_fail)
            gauge_accounts_manual.set(a_man)
        finally:
            conn.close()
    except Exception:
        logger.exception("refresh_db_gauges failed db=%s", db_path)


def metrics_response(settings_getter: Callable[[], object]) -> Response:
    settings = settings_getter()
    dbp = getattr(settings, "vpn_db_path", None)
    refresh_db_gauges(Path(dbp) if dbp is not None else None)
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


async def prometheus_http_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
    route = normalize_route(request.url.path)
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    try:
        code = int(getattr(response, "status_code", 500))
    except (TypeError, ValueError):
        code = 500
    method = (request.method or "GET").upper()
    http_request_duration_seconds.labels(method=method, route=route).observe(elapsed)
    http_requests_total.labels(method=method, route=route, status_class=_status_class(code)).inc()
    return response


def install_middleware(app) -> None:
    app.middleware("http")(prometheus_http_middleware)
