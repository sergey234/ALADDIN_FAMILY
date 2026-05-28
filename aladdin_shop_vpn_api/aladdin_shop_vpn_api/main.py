from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from aladdin_shop_vpn_api.db import init_schema
from aladdin_shop_vpn_api import sentry_util
from aladdin_shop_vpn_api import prometheus_metrics as prom_metrics
from aladdin_shop_vpn_api.routes import health as health_r
from aladdin_shop_vpn_api.routes import internal as internal_r
from aladdin_shop_vpn_api.routes import legal as legal_r
from aladdin_shop_vpn_api.routes import metrics_route as metrics_r
from aladdin_shop_vpn_api.settings import load_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    sentry_util.init_sentry_fastapi(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment or None,
        traces_sample_rate=settings.sentry_traces_sample_rate,
    )
    await init_schema(settings.vpn_db_path)
    app.state.settings = settings
    logger.info("aladdin_shop_vpn_api started, db=%s", settings.vpn_db_path)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ALADDIN Shop VPN API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    prom_metrics.install_middleware(app)
    app.include_router(health_r.router)
    app.include_router(legal_r.router)
    app.include_router(internal_r.router)
    app.include_router(metrics_r.router)
    return app


app = create_app()
