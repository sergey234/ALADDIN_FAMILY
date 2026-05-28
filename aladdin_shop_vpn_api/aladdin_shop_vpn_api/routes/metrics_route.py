from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.responses import Response

from aladdin_shop_vpn_api import prometheus_metrics as pm
from aladdin_shop_vpn_api.deps import get_settings
from aladdin_shop_vpn_api.settings import Settings

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics_scrape(settings: Settings = Depends(get_settings)) -> Response:
    """Prometheus scrape (vpn-15). Не открывать в публичный интернет без ACL."""
    return pm.metrics_response(lambda: settings)
