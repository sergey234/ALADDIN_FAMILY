# -*- coding: utf-8 -*-
"""
IoT API Router
--------------
Endpoints для управления устройствами умного дома и мониторинга угроз IoT.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db

# ═══════════════════════════════════════════════════════════════
# Модели данных
# ═══════════════════════════════════════════════════════════════


class IoTDevice(BaseModel):
    """Модель IoT устройства."""
    deviceId: str
    name: str
    type: str
    status: str  # "online", "offline", "warning", "danger"
    lastSeen: str
    threatLevel: int = Field(ge=0, le=5)  # 0 = безопасно, 5 = критическая угроза


class IoTThreat(BaseModel):
    """Модель угрозы IoT."""
    threatId: str
    deviceId: str
    deviceName: str
    threatType: str  # "vulnerability", "unauthorized_access", "data_leak", "malware"
    severity: str  # "low", "medium", "high", "critical"
    detectedAt: str
    status: str  # "active", "fixed", "ignored"


class IoTStatusResponse(BaseModel):
    """Ответ со статусом умного дома."""
    homeId: str
    totalDevices: int
    onlineDevices: int
    offlineDevices: int
    threatDevices: int
    lastScan: str
    protectionLevel: int = Field(ge=0, le=5)
    status: str  # "protected", "warning", "danger"


class IoTDevicesResponse(BaseModel):
    """Ответ со списком устройств."""
    homeId: str
    devices: List[IoTDevice]
    total: int


class IoTThreatsResponse(BaseModel):
    """Ответ со списком угроз."""
    homeId: str
    threats: List[IoTThreat]
    total: int
    active: int
    fixed: int


class IoTScanResponse(BaseModel):
    """Ответ на запуск сканирования."""
    success: bool
    scanId: str
    homeId: str
    message: str
    startedAt: str


# ═══════════════════════════════════════════════════════════════
# DB helpers (реализация без mock-структур)
# ═══════════════════════════════════════════════════════════════


def _ensure_iot_tables(db: Session) -> None:
    """Создаёт минимальные таблицы для IoT-домена, если их ещё нет."""
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS iot_devices (
                id BIGSERIAL PRIMARY KEY,
                home_id TEXT NOT NULL,
                device_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'online',
                last_seen TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                threat_level INTEGER NOT NULL DEFAULT 0
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS iot_threats (
                id BIGSERIAL PRIMARY KEY,
                home_id TEXT NOT NULL,
                threat_id TEXT UNIQUE NOT NULL,
                device_id TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                detected_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
                status TEXT NOT NULL DEFAULT 'active'
            )
            """
        )
    )
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS iot_scans (
                id BIGSERIAL PRIMARY KEY,
                scan_id TEXT UNIQUE NOT NULL,
                home_id TEXT NOT NULL,
                started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )


def _bootstrap_home_if_empty(db: Session, home_id: str) -> None:
    """
    Небольшой сид, чтобы новые homeId не были полностью пустыми.
    Только для demo/начала жизни; в реальной системе дом добавлялся бы отдельным онбордингом.
    """
    _ensure_iot_tables(db)
    device_count = (
        db.execute(
            text("SELECT COUNT(*) FROM iot_devices WHERE home_id = :home_id"),
            {"home_id": home_id},
        ).scalar()
        or 0
    )
    if device_count:
        return

    seed_devices = [
        {
            "home_id": home_id,
            "device_id": f"{home_id}_cam_1",
            "name": "Умная камера",
            "type": "camera",
            "status": "online",
            "threat_level": 0,
        },
        {
            "home_id": home_id,
            "device_id": f"{home_id}_thermo_1",
            "name": "Умный термостат",
            "type": "thermostat",
            "status": "online",
            "threat_level": 1,
        },
    ]
    for d in seed_devices:
        db.execute(
            text(
                """
                INSERT INTO iot_devices (home_id, device_id, name, type, status, threat_level)
                VALUES (:home_id, :device_id, :name, :type, :status, :threat_level)
                ON CONFLICT (device_id) DO NOTHING
                """
            ),
            d,
        )
    db.commit()


# ═══════════════════════════════════════════════════════════════
# Роутер
# ═══════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/iot", tags=["IoT"])


def _get_default_home_id() -> str:
    """Возвращает ID умного дома по умолчанию."""
    return "home_001"


def _resolve_home_id(home_id: Optional[str]) -> str:
    """Разрешает ID умного дома (если None, возвращает дефолтный)."""
    return home_id or _get_default_home_id()


@router.get("/status/{homeId}", response_model=IoTStatusResponse)
async def get_iot_status(
    homeId: str = Path(..., description="ID умного дома"),
    db: Session = Depends(get_db),
):
    """Возвращает общий статус умного дома."""
    home_id = _resolve_home_id(homeId)
    _bootstrap_home_if_empty(db, home_id)

    _ensure_iot_tables(db)
    row = (
        db.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status IN ('online') THEN 1 ELSE 0 END) AS online,
                    SUM(CASE WHEN status IN ('offline') THEN 1 ELSE 0 END) AS offline,
                    SUM(CASE WHEN threat_level > 0 OR status IN ('warning','danger') THEN 1 ELSE 0 END) AS threat_devices
                FROM iot_devices
                WHERE home_id = :home_id
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
                SELECT started_at
                FROM iot_scans
                WHERE home_id = :home_id
                ORDER BY started_at DESC
                LIMIT 1
                """
            ),
            {"home_id": home_id},
        )
        .mappings()
        .first()
    )
    last_scan = (
        last_scan_row["started_at"].isoformat() if last_scan_row and last_scan_row["started_at"] else None
    )
    if not last_scan:
        last_scan = datetime.utcnow().isoformat()

    if total == 0:
        protection_level = 0
        status = "warning"
    elif threat_devices == 0:
        protection_level = 5
        status = "protected"
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
async def get_iot_devices(
    homeId: str = Path(..., description="ID умного дома"),
    db: Session = Depends(get_db),
):
    """Возвращает список всех устройств умного дома."""
    home_id = _resolve_home_id(homeId)
    _bootstrap_home_if_empty(db, home_id)

    rows = (
        db.execute(
            text(
                """
                SELECT device_id, name, type, status, last_seen, threat_level
                FROM iot_devices
                WHERE home_id = :home_id
                ORDER BY device_id
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
            lastSeen=(row["last_seen"].isoformat() if isinstance(row["last_seen"], datetime) else str(row["last_seen"])),
            threatLevel=int(row["threat_level"] or 0),
        )
        for row in rows
    ]

    return IoTDevicesResponse(homeId=home_id, devices=devices, total=len(devices))


@router.get("/threats/{homeId}", response_model=IoTThreatsResponse)
async def get_iot_threats(
    homeId: str = Path(..., description="ID умного дома"),
    db: Session = Depends(get_db),
):
    """Возвращает список угроз для умного дома."""
    home_id = _resolve_home_id(homeId)
    _ensure_iot_tables(db)

    rows = (
        db.execute(
            text(
                """
                SELECT threat_id, device_id, threat_type, severity, detected_at, status
                FROM iot_threats
                WHERE home_id = :home_id
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
                text(
                    """
                    SELECT device_id, name
                    FROM iot_devices
                    WHERE home_id = :home_id
                    """
                ),
                {"home_id": home_id},
            )
            .mappings()
            .all()
        )
        device_names = {r["device_id"]: r["name"] for r in dev_rows}

    threats: List[IoTThreat] = []
    active_count = 0
    fixed_count = 0
    for row in rows:
        status = row["status"]
        if status == "active":
            active_count += 1
        if status == "fixed":
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
                status=status,
            )
        )

    return IoTThreatsResponse(
        homeId=home_id,
        threats=threats,
        total=len(threats),
        active=active_count,
        fixed=fixed_count,
    )


@router.post("/device/{deviceId}/block", response_model=Dict[str, str])
async def block_iot_device(
    deviceId: str = Path(..., description="ID устройства для блокировки"),
    db: Session = Depends(get_db),
):
    """Блокирует IoT устройство (меняет статус на 'blocked')."""
    _ensure_iot_tables(db)
    res = db.execute(
        text(
            """
            UPDATE iot_devices
            SET status = 'blocked', last_seen = NOW()
            WHERE device_id = :device_id
            """
        ),
        {"device_id": deviceId},
    )
    db.commit()

    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "success": "true",
        "deviceId": deviceId,
        "message": f"Устройство {deviceId} заблокировано",
        "blockedAt": datetime.utcnow().isoformat()
    }


@router.post("/scan/{homeId}", response_model=IoTScanResponse)
async def start_iot_scan(
    homeId: str = Path(..., description="ID умного дома"),
    db: Session = Depends(get_db),
):
    """Запускает сканирование умного дома на угрозы (записывает scan_id и время)."""
    home_id = _resolve_home_id(homeId)
    _ensure_iot_tables(db)

    scan_id = f"scan_{home_id}_{int(datetime.utcnow().timestamp())}"
    db.execute(
        text(
            """
            INSERT INTO iot_scans (scan_id, home_id, started_at)
            VALUES (:scan_id, :home_id, NOW())
            ON CONFLICT (scan_id) DO NOTHING
            """
        ),
        {"scan_id": scan_id, "home_id": home_id},
    )
    db.commit()

    return IoTScanResponse(
        success=True,
        scanId=scan_id,
        homeId=home_id,
        message="Сканирование запущено",
        startedAt=datetime.utcnow().isoformat()
    )


@router.post("/fix/{threatId}", response_model=Dict[str, str])
async def fix_iot_threat(
    threatId: str = Path(..., description="ID угрозы для исправления"),
    db: Session = Depends(get_db),
):
    """Исправляет обнаруженную угрозу IoT (меняет статус угрозы на 'fixed')."""
    _ensure_iot_tables(db)
    res = db.execute(
        text(
            """
            UPDATE iot_threats
            SET status = 'fixed'
            WHERE threat_id = :threat_id
            """
        ),
        {"threat_id": threatId},
    )
    db.commit()

    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Threat not found")

    return {
        "success": "true",
        "threatId": threatId,
        "message": f"Угроза {threatId} исправлена",
        "fixedAt": datetime.utcnow().isoformat()
    }

