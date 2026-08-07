from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bot.config import load_settings
from bot.services.catalog import load_products
from bot.sentry_util import init_sentry_fastapi
from partner_api.routers import orders as orders_r
from partner_api.routers import crypto_pay_webhook as crypto_pay_r
from partner_api.routers import apifragment_webhook as apifragment_r
from partner_api.routers import ckassa_webhook as ckassa_r
from partner_api.routers import cardlink_webhook as cardlink_r
from partner_api.routers import lava_webhook as lava_r
from partner_api.routers import payment_pages as payment_pages_r
from partner_api.routers import payment_provider as payment_r
from partner_api.routers import xrocket_webhook as xrocket_r
from partner_api.routers import profile as profile_r
from partner_api.routers import topups as topups_r
from partner_api.routers import legal_pages as legal_r
from partner_api.routers import webhooks_partner as webhooks_r
from partner_api.routers import vpn_ref_landing as vpn_ref_landing_r
from partner_api.routers import web_checkout as web_checkout_r
from partner_api.rate_limit_middleware import PartnerRateLimitMiddleware
from partner_api.rate_limit_store import build_rate_limit_store

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    if not (settings.api_key_pepper or "").strip():
        logger.error("API_KEY_PEPPER is empty — Partner API will not start")
        raise RuntimeError("API_KEY_PEPPER must be set for partner_api")
    app.state.settings = settings
    app.state.products = load_products(settings.products_path)
    init_sentry_fastapi(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment or None,
        traces_sample_rate=settings.sentry_traces_sample_rate,
    )
    logger.info("Partner API started: %d products loaded", len(app.state.products))
    st = app.state.settings
    if bool(getattr(st, "ckassa_enabled", False)) and bool(getattr(st, "ckassa_test_mode", False)):
        logger.warning(
            "CKASSA_TEST_MODE=true: демо-шлюз Ckassa, не для боя. Прод: CKASSA_TEST_MODE=false и боевые ключи."
        )
    yield


def create_app() -> FastAPI:
    settings = load_settings()
    cors_raw = (settings.partner_api_cors_origins or "").strip()
    origins = [o.strip() for o in cors_raw.split(",") if o.strip()]

    app = FastAPI(
        title="ALADDIN Shop Partner API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(PartnerRateLimitMiddleware, store=build_rate_limit_store(settings))

    v1 = "/v1"
    app.include_router(legal_r.router, prefix=v1)
    app.include_router(payment_pages_r.router, prefix=v1)
    app.include_router(vpn_ref_landing_r.router)
    app.include_router(web_checkout_r.router, prefix=v1)
    app.include_router(web_checkout_r.public_router)
    app.include_router(profile_r.router, prefix=v1)
    app.include_router(orders_r.router, prefix=v1)
    app.include_router(topups_r.router, prefix=v1)
    app.include_router(payment_r.router, prefix=v1)
    app.include_router(lava_r.router, prefix=v1)
    app.include_router(cardlink_r.router, prefix=v1)
    app.include_router(ckassa_r.router, prefix=v1)
    app.include_router(crypto_pay_r.router, prefix=v1)
    app.include_router(xrocket_r.router, prefix=v1)
    app.include_router(apifragment_r.router, prefix=v1)
    app.include_router(webhooks_r.router, prefix=v1)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "partner_api.main:app",
        host="0.0.0.0",
        port=8090,
        reload=False,
    )


if __name__ == "__main__":
    main()
