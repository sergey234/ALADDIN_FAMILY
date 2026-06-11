"""
IoT API — explicit routers (B1-08 / iot-02). Agent scan + PostgreSQL, no mock.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.iot_service import bootstrap_home, ensure_iot_tables, run_home_scan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iot", tags=["iot"])


class IoTDevice(BaseModel):
    deviceId: str
    name: str
    type: str
    status: str
    lastSeen: str
    threatLevel: int = Field(ge=0, le=5)


class IoTThreat(BaseModel):
    threatId: str
    deviceId: str
    deviceName: str
    threatType: str
    severity: str
    detectedAt: str
    status: str


class IoTStatusResponse(BaseModel):
    homeId: str
    totalDevices: int
    onlineDevices: int
    offlineDevices: int
    threatDevices: int
    lastScan: str
    protectionLevel: int = Field(ge=0, le=5)
    status: str


class IoTDevicesResponse(BaseModel):
    homeId: str
    devices: List[IoTDevice]
    total: int


class IoTThreatsResponse(BaseModel):
    homeId: str
    threats: List[IoTThreat]
    total: int
    active: int
    fixed: int


class IoTScanResponse(BaseModel):
    success: bool
    scanId: str
    homeId: str
    message: str
    startedAt: str
    threatsFound: int = 0
    source: str = "database"
    agent: str = "iot_security_agent"


def _handle_service_error(exc: Exception) -> None:
    if isinstance(exc, ValueError) and str(exc).startswith("mock_"):
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/status/{homeId}", response_model=IoTStatusResponse)
async def get_iot_status(homeId: str = Path(...), db: Session = Depends(get_db)):
    home_id = homeId
    bootstrap_home(home_id)
    ensure_iot_tables()

    row = (
        db.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status IN ('online') THEN 1 ELSE 0 END) AS online,
                    SUM(CASE WHEN status IN ('offline') THEN 1 ELSE 0 END) AS offline,
                    SUM(CASE WHEN threat_level > 0 OR status IN ('warning','danger') THEN 1 ELSE 0 END) AS threat_devices
                FROM iot_devices WHERE home_id = :home_id
                """
            ),
            {"home_id": home_id},
        )
        .mappings()
        .first()
    )
    total = int(row["total"]) if row else 0
    online = int(row["online"] or 0) if row else 0
    offline = int(row["offline"] or 0) if row else 0
    threat_devices = int(row["threat_devices"] or 0) if row else 0

    last_scan_row = (
        db.execute(
            text(
                """
                SELECT started_at FROM iot_scans
                WHERE home_id = :home_id ORDER BY started_at DESC LIMIT 1
                """
            ),
            {"home_id": home_id},
        )
        .mappings()
        .first()
    )
    last_scan = (
        last_scan_row["started_at"].isoformat()
        if last_scan_row and last_scan_row["started_at"]
        else datetime.utcnow().isoformat()
    )

    if total == 0:
        protection_level, status = 0, "warning"
    elif threat_devices == 0:
        protection_level, status = 5, "protected"
    else:
        protection_level = max(1, 5 - min(threat_devices, 4))
        status = "warning"

    return IoTStatusResponse(
        homeId=home_id,
        totalDevices=total,
        onlineDevices=online,
        offlineDevices=offline,
        threatDevices=threat_devices,
        lastScan=last_scan,
        protectionLevel=protection_level,
        status=status,
    )


@router.get("/devices/{homeId}", response_model=IoTDevicesResponse)
async def get_iot_devices(homeId: str = Path(...), db: Session = Depends(get_db)):
    home_id = homeId
    bootstrap_home(home_id)
    rows = (
        db.execute(
            text(
                """
                SELECT device_id, name, type, status, last_seen, threat_level
                FROM iot_devices WHERE home_id = :home_id ORDER BY device_id
                """
            ),
            {"home_id": home_id},
        )
        .mappings()
        .all()
    )
    devices = [
        IoTDevice(
            deviceId=row["device_id"],
            name=row["name"],
            type=row["type"],
            status=row["status"],
            lastSeen=(
                row["last_seen"].isoformat()
                if isinstance(row["last_seen"], datetime)
                else str(row["last_seen"])
            ),
            threatLevel=int(row["threat_level"] or 0),
        )
        for row in rows
    ]
    return IoTDevicesResponse(homeId=home_id, devices=devices, total=len(devices))


@router.get("/threats/{homeId}", response_model=IoTThreatsResponse)
async def get_iot_threats(homeId: str = Path(...), db: Session = Depends(get_db)):
    home_id = homeId
    ensure_iot_tables()
    rows = (
        db.execute(
            text(
                """
                SELECT threat_id, device_id, threat_type, severity, detected_at, status
                FROM iot_threats WHERE home_id = :home_id
                ORDER BY detected_at DESC, id DESC
                """
            ),
            {"home_id": home_id},
        )
        .mappings()
        .all()
    )
    device_names: Dict[str, str] = {}
    if rows:
        dev_rows = (
            db.execute(
                text("SELECT device_id, name FROM iot_devices WHERE home_id = :home_id"),
                {"home_id": home_id},
            )
            .mappings()
            .all()
        )
        device_names = {r["device_id"]: r["name"] for r in dev_rows}

    threats: List[IoTThreat] = []
    active_count = fixed_count = 0
    for row in rows:
        st = row["status"]
        if st == "active":
            active_count += 1
        if st == "fixed":
            fixed_count += 1
        threats.append(
            IoTThreat(
                threatId=row["threat_id"],
                deviceId=row["device_id"],
                deviceName=device_names.get(row["device_id"], row["device_id"]),
                threatType=row["threat_type"],
                severity=row["severity"],
                detectedAt=(
                    row["detected_at"].isoformat()
                    if isinstance(row["detected_at"], datetime)
                    else str(row["detected_at"])
                ),
                status=st,
            )
        )
    return IoTThreatsResponse(
        homeId=home_id,
        threats=threats,
        total=len(threats),
        active=active_count,
        fixed=fixed_count,
    )


@router.post("/device/{deviceId}/block")
async def block_iot_device(deviceId: str = Path(...), db: Session = Depends(get_db)):
    ensure_iot_tables()
    res = db.execute(
        text(
            """
            UPDATE iot_devices SET status = 'blocked', last_seen = NOW()
            WHERE device_id = :device_id
            """
        ),
        {"device_id": deviceId},
    )
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "success": True,
        "data": True,
        "deviceId": deviceId,
        "message": f"Устройство {deviceId} заблокировано",
    }


@router.post("/scan/{homeId}", response_model=IoTScanResponse)
async def start_iot_scan(homeId: str = Path(...)):
    try:
        result = run_home_scan(homeId)
    except Exception as exc:
        _handle_service_error(exc)
    logger.info(
        "iot_scan home=%s scan_id=%s threats=%s source=%s",
        homeId,
        result.get("scanId"),
        result.get("threatsFound"),
        result.get("source"),
    )
    return IoTScanResponse(**result)


@router.post("/fix/{threatId}")
async def fix_iot_threat(threatId: str = Path(...), db: Session = Depends(get_db)):
    ensure_iot_tables()
    res = db.execute(
        text("UPDATE iot_threats SET status = 'fixed' WHERE threat_id = :threat_id"),
        {"threat_id": threatId},
    )
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Threat not found")
    return {
        "success": True,
        "data": True,
        "threatId": threatId,
        "message": f"Угроза {threatId} исправлена",
    }
