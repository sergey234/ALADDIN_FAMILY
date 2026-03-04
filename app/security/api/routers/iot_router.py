# -*- coding: utf-8 -*-
"""
IoT API Router
--------------
Endpoints для управления устройствами умного дома и мониторинга угроз IoT.
"""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

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
# Mock данные для тестирования
# ═══════════════════════════════════════════════════════════════

_MOCK_DEVICES = {
    "home_001": [
        IoTDevice(
            deviceId="device_001",
            name="Умная камера гостиная",
            type="camera",
            status="online",
            lastSeen=datetime.utcnow().isoformat(),
            threatLevel=0
        ),
        IoTDevice(
            deviceId="device_002",
            name="Умный термостат",
            type="thermostat",
            status="online",
            lastSeen=datetime.utcnow().isoformat(),
            threatLevel=1
        ),
        IoTDevice(
            deviceId="device_003",
            name="Умный замок",
            type="lock",
            status="warning",
            lastSeen=datetime.utcnow().isoformat(),
            threatLevel=2
        ),
        IoTDevice(
            deviceId="device_004",
            name="Умная розетка кухня",
            type="socket",
            status="offline",
            lastSeen=(datetime.utcnow() - __import__('datetime').timedelta(hours=2)).isoformat(),
            threatLevel=0
        ),
    ],
    "home_002": [
        IoTDevice(
            deviceId="device_005",
            name="Умная камера вход",
            type="camera",
            status="online",
            lastSeen=datetime.utcnow().isoformat(),
            threatLevel=0
        ),
    ]
}

_MOCK_THREATS = {
    "home_001": [
        IoTThreat(
            threatId="threat_001",
            deviceId="device_003",
            deviceName="Умный замок",
            threatType="vulnerability",
            severity="high",
            detectedAt=(datetime.utcnow() - __import__('datetime').timedelta(hours=5)).isoformat(),
            status="active"
        ),
        IoTThreat(
            threatId="threat_002",
            deviceId="device_002",
            deviceName="Умный термостат",
            threatType="unauthorized_access",
            severity="medium",
            detectedAt=(datetime.utcnow() - __import__('datetime').timedelta(days=2)).isoformat(),
            status="fixed"
        ),
    ],
    "home_002": []
}

_MOCK_STATUS = {
    "home_001": IoTStatusResponse(
        homeId="home_001",
        totalDevices=4,
        onlineDevices=3,
        offlineDevices=1,
        threatDevices=1,
        lastScan=datetime.utcnow().isoformat(),
        protectionLevel=3,
        status="warning"
    ),
    "home_002": IoTStatusResponse(
        homeId="home_002",
        totalDevices=1,
        onlineDevices=1,
        offlineDevices=0,
        threatDevices=0,
        lastScan=datetime.utcnow().isoformat(),
        protectionLevel=5,
        status="protected"
    )
}


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
async def get_iot_status(homeId: str = Path(..., description="ID умного дома")):
    """Возвращает общий статус умного дома."""
    home_id = _resolve_home_id(homeId)
    
    if home_id not in _MOCK_STATUS:
        # Создаем дефолтный статус для нового дома
        return IoTStatusResponse(
            homeId=home_id,
            totalDevices=0,
            onlineDevices=0,
            offlineDevices=0,
            threatDevices=0,
            lastScan=datetime.utcnow().isoformat(),
            protectionLevel=0,
            status="warning"
        )
    
    return _MOCK_STATUS[home_id]


@router.get("/devices/{homeId}", response_model=IoTDevicesResponse)
async def get_iot_devices(homeId: str = Path(..., description="ID умного дома")):
    """Возвращает список всех устройств умного дома."""
    home_id = _resolve_home_id(homeId)
    
    devices = _MOCK_DEVICES.get(home_id, [])
    
    return IoTDevicesResponse(
        homeId=home_id,
        devices=devices,
        total=len(devices)
    )


@router.get("/threats/{homeId}", response_model=IoTThreatsResponse)
async def get_iot_threats(homeId: str = Path(..., description="ID умного дома")):
    """Возвращает список угроз для умного дома."""
    home_id = _resolve_home_id(homeId)
    
    threats = _MOCK_THREATS.get(home_id, [])
    active_count = sum(1 for t in threats if t.status == "active")
    fixed_count = sum(1 for t in threats if t.status == "fixed")
    
    return IoTThreatsResponse(
        homeId=home_id,
        threats=threats,
        total=len(threats),
        active=active_count,
        fixed=fixed_count
    )


@router.post("/device/{deviceId}/block", response_model=Dict[str, str])
async def block_iot_device(deviceId: str = Path(..., description="ID устройства для блокировки")):
    """Блокирует IoT устройство."""
    # В реальной реализации здесь должна быть логика блокировки устройства
    return {
        "success": "true",
        "deviceId": deviceId,
        "message": f"Устройство {deviceId} заблокировано",
        "blockedAt": datetime.utcnow().isoformat()
    }


@router.post("/scan/{homeId}", response_model=IoTScanResponse)
async def start_iot_scan(homeId: str = Path(..., description="ID умного дома")):
    """Запускает сканирование умного дома на угрозы."""
    home_id = _resolve_home_id(homeId)
    scan_id = f"scan_{home_id}_{int(datetime.utcnow().timestamp())}"
    
    # В реальной реализации здесь должна быть логика запуска сканирования
    return IoTScanResponse(
        success=True,
        scanId=scan_id,
        homeId=home_id,
        message="Сканирование запущено",
        startedAt=datetime.utcnow().isoformat()
    )


@router.post("/fix/{threatId}", response_model=Dict[str, str])
async def fix_iot_threat(threatId: str = Path(..., description="ID угрозы для исправления")):
    """Исправляет обнаруженную угрозу IoT."""
    # В реальной реализации здесь должна быть логика исправления угрозы
    return {
        "success": "true",
        "threatId": threatId,
        "message": f"Угроза {threatId} исправлена",
        "fixedAt": datetime.utcnow().isoformat()
    }

