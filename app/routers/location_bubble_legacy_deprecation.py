"""
SEC-P2-03: legacy /api/location/bubble/* → explicit /api/location-bubble/*.
Registered only when explicit location_bubble router is active.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/location/bubble", tags=["location-bubble-deprecated"])


def _gone() -> JSONResponse:
    return JSONResponse(
        status_code=410,
        content={
            "detail": "Deprecated. Use /api/location-bubble/generate, /stats, /settings",
            "canonical_prefix": "/api/location-bubble",
        },
    )


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def location_bubble_legacy_gone(request: Request, path: str = ""):
    return _gone()


@router.api_route("", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def location_bubble_legacy_root(request: Request):
    return _gone()
