"""
Parental monitoring API — explicit FastAPI only (B1-10 / pc-01). No wildcard mock.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.database.database import get_db
from app.services.parental_monitoring_service import get_monitoring_detail
from security.api.routers.parental_control_router import (
    MonitoringIngestRequest,
    ParentalMonitoringDetailResponse,
    ingest_parental_monitoring_events,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/parental-control", tags=["parental-monitoring"])


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError) and str(exc).startswith("mock_"):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    raise


@router.get("/monitoring/detail", response_model=ParentalMonitoringDetailResponse)
async def parental_monitoring_detail(
    childId: Optional[str] = Query(None, alias="childId"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """GET /api/parental-control/monitoring/detail — iOS ParentalMonitoringDetailResponse."""
    try:
        return get_monitoring_detail(db, child_id=childId, current_user=current_user)
    except ValueError as exc:
        _handle_service_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/monitoring/events")
async def parental_monitoring_events_ingest(
    payload: MonitoringIngestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """POST /api/parental-control/monitoring/events — child device ingest."""
    try:
        return await ingest_parental_monitoring_events(payload, db, current_user)
    except HTTPException:
        raise
    except ValueError as exc:
        _handle_service_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
