# -*- coding: utf-8 -*-
"""
ALADDIN Security System - DeviceSecurity
Безопасность устройств - КРИТИЧНО

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import datetime
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Путь к файлу конфигурации безопасности устройств
DEVICE_SECURITY_CONFIG = "data/devices/security_policies.json"


class DeviceType(Enum):
    """Типы устройств"""

    MOBILE = "mobile"
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    TABLET = "tablet"
    SERVER = "server"
    IOT = "iot"
    UNKNOWN = "unknown"


class SecurityLevel(Enum):
    """Уровни безопасности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeviceStatus(Enum):
    """Статус устройства"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPROMISED = "compromised"
    QUARANTINED = "quarantined"
    MAINTENANCE = "maintenance"


class ThreatType(Enum):
    """Типы угроз для устройств"""

    MALWARE = "malware"
    VULNERABILITY = "vulnerability"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    NETWORK_ATTACK = "network_attack"
    PHYSICAL_THEFT = "physical_theft"
    UNKNOWN = "unknown"


@dataclass
class Device:
    """
    Представляет устройство в системе.
    """

    device_id: str
    name: str
    device_type: DeviceType
    os: str
    os_version: str
    hardware_info: Dict[str, Any]
    security_level: SecurityLevel
    status: DeviceStatus
    owner_id: Optional[str] = None
    location: Optional[str] = None
    last_seen: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    security_score: float = 0.0
    compliance_status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type.value,
            "os": self.os,
            "os_version": self.os_version,
            "hardware_info": self.hardware_info,
            "security_level": self.security_level.value,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "location": self.location,
            "last_seen": self.last_seen,
            "created_at": self.created_at,
            "security_score": self.security_score,
            "compliance_status": self.compliance_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        return cls(
            device_id=data["device_id"],
            name=data["name"],
            device_type=DeviceType(data["device_type"]),
            os=data["os"],
            os_version=data["os_version"],
            hardware_info=data["hardware_info"],
            security_level=SecurityLevel(data["security_level"]),
            status=DeviceStatus(data["status"]),
            owner_id=data.get("owner_id"),
            location=data.get("location"),
            last_seen=data.get(
                "last_seen", datetime.datetime.now().isoformat()
            ),
            created_at=data.get(
                "created_at", datetime.datetime.now().isoformat()
            ),
            security_score=data.get("security_score", 0.0),
            compliance_status=data.get("compliance_status", "unknown"),
        )


@dataclass
class SecurityPolicy:
    """
    Политика безопасности для устройства.
    """

    policy_id: str
    name: str
    device_types: List[DeviceType]
    requirements: List[str]
    restrictions: List[str]
    security_level: SecurityLevel
    enabled: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "device_types": [dt.value for dt in self.device_types],
            "requirements": self.requirements,
            "restrictions": self.restrictions,
            "security_level": self.security_level.value,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityPolicy":
        return cls(
            policy_id=data["policy_id"],
            name=data["name"],
            device_types=[DeviceType(dt) for dt in data["device_types"]],
            requirements=data["requirements"],
            restrictions=data["restrictions"],
            security_level=SecurityLevel(data["security_level"]),
            enabled=data.get("enabled", True),
            created_at=data.get(
                "created_at", datetime.datetime.now().isoformat()
            ),
        )


@dataclass
class SecurityThreat:
    """
    Угроза безопасности устройства.
    """

    threat_id: str
    device_id: str
    threat_type: ThreatType
    severity: SecurityLevel
    description: str
    detected_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    resolved_at: Optional[str] = None
    mitigation_actions: List[str] = field(default_factory=list)
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_id": self.threat_id,
            "device_id": self.device_id,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "detected_at": self.detected_at,
            "resolved_at": self.resolved_at,
            "mitigation_actions": self.mitigation_actions,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityThreat":
        return cls(
            threat_id=data["threat_id"],
            device_id=data["device_id"],
            threat_type=ThreatType(data["threat_type"]),
            severity=SecurityLevel(data["severity"]),
            description=data["description"],
            detected_at=data.get(
                "detected_at", datetime.datetime.now().isoformat()
            ),
            resolved_at=data.get("resolved_at"),
            mitigation_actions=data.get("mitigation_actions", []),
            status=data.get("status", "active"),
        )


class DeviceSecurityMetrics:
    """
    Метрики безопасности устройств.
    """

    def __init__(self):
        self.total_devices = 0
        self.active_devices = 0
        self.compromised_devices = 0
        self.avg_security_score = 0.0
        self.threats_detected = 0
        self.threats_resolved = 0
        self.compliance_rate = 0.0
        self.last_updated = datetime.datetime.now().isoformat()

    def update_metrics(
        self, devices: List[Device], threats: List[SecurityThreat]
    ):
        """Обновляет метрики на основе текущего состояния."""
        self.total_devices = len(devices)
        self.active_devices = len(
            [d for d in devices if d.status == DeviceStatus.ACTIVE]
        )
        self.compromised_devices = len(
            [d for d in devices if d.status == DeviceStatus.COMPROMISED]
        )

        if devices:
            self.avg_security_score = sum(
                d.security_score for d in devices
            ) / len(devices)
            compliant_devices = len(
                [d for d in devices if d.compliance_status == "compliant"]
            )
            self.compliance_rate = compliant_devices / len(devices) * 100

        self.threats_detected = len(threats)
        self.threats_resolved = len(
            [t for t in threats if t.status == "resolved"]
        )
        self.last_updated = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_devices": self.total_devices,
            "active_devices": self.active_devices,
            "compromised_devices": self.compromised_devices,
            "avg_security_score": self.avg_security_score,
            "threats_detected": self.threats_detected,
            "threats_resolved": self.threats_resolved,
            "compliance_rate": self.compliance_rate,
            "last_updated": self.last_updated,
        }


class DeviceSecurity:
    """
    Модуль безопасности устройств.
    """

    def __init__(self, config_path: str = DEVICE_SECURITY_CONFIG):
        self.config_path = config_path
        self.devices: List[Device] = []
        self.policies: List[SecurityPolicy] = self._load_policies()
        self.threats: List[SecurityThreat] = []
        self.metrics = DeviceSecurityMetrics()

    def _load_policies(self) -> List[SecurityPolicy]:
        """Загружает политики безопасности из файла."""
        if not os.path.exists(self.config_path):
            return self._create_default_policies()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [
                    SecurityPolicy.from_dict(p)
                    for p in data.get("policies", [])
                ]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки политик безопасности: {e}")
            return self._create_default_policies()

    def _create_default_policies(self) -> List[SecurityPolicy]:
        """Создает набор политик безопасности по умолчанию."""
        default_policies = [
            SecurityPolicy(
                policy_id="mobile_security",
                name="Мобильная безопасность",
                device_types=[DeviceType.MOBILE, DeviceType.TABLET],
                requirements=[
                    "Антивирус установлен",
                    "Шифрование данных включено",
                    "Блокировка экрана настроена",
                    "Автоматические обновления включены",
                ],
                restrictions=[
                    "Запрет установки приложений из неизвестных источников",
                    "Запрет root/jailbreak",
                    "Ограничение доступа к корпоративным данным",
                ],
                security_level=SecurityLevel.HIGH,
            ),
            SecurityPolicy(
                policy_id="desktop_security",
                name="Безопасность рабочего стола",
                device_types=[DeviceType.DESKTOP, DeviceType.LAPTOP],
                requirements=[
                    "Антивирус с актуальными сигнатурами",
                    "Файрвол настроен",
                    "Шифрование диска включено",
                    "Регулярные резервные копии",
                ],
                restrictions=[
                    "Запрет установки неавторизованного ПО",
                    "Ограничение доступа к USB",
                    "Мониторинг сетевого трафика",
                ],
                security_level=SecurityLevel.CRITICAL,
            ),
        ]
        self._save_policies(default_policies)
        return default_policies

    def _save_policies(self, policies: List[SecurityPolicy]):
        """Сохраняет политики в файл."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(
                {"policies": [p.to_dict() for p in policies]},
                f,
                indent=4,
                ensure_ascii=False,
            )

    def register_device(self, device: Device) -> bool:
        """Регистрирует новое устройство в системе."""
        if any(d.device_id == device.device_id for d in self.devices):
            print(f"Устройство {device.device_id} уже зарегистрировано.")
            return False

        self.devices.append(device)
        print(
            f"Устройство {device.name} ({device.device_id}) зарегистрировано."
        )
        self._update_metrics()
        return True

    def update_device(self, device_id: str, updates: Dict[str, Any]) -> bool:
        """Обновляет информацию об устройстве."""
        for i, device in enumerate(self.devices):
            if device.device_id == device_id:
                updated_device = Device.from_dict(
                    {**device.to_dict(), **updates}
                )
                self.devices[i] = updated_device
                print(f"Устройство {device_id} обновлено.")
                self._update_metrics()
                return True
        print(f"Устройство {device_id} не найдено.")
        return False

    def remove_device(self, device_id: str) -> bool:
        """Удаляет устройство из системы."""
        initial_len = len(self.devices)
        self.devices = [d for d in self.devices if d.device_id != device_id]
        if len(self.devices) < initial_len:
            print(f"Устройство {device_id} удалено.")
            self._update_metrics()
            return True
        print(f"Устройство {device_id} не найдено.")
        return False

    def assess_device_security(
        self, device_id: str
    ) -> Tuple[float, List[str]]:
        """
        Оценивает уровень безопасности устройства.
        Возвращает оценку (0-100) и список рекомендаций.
        """
        device = next(
            (d for d in self.devices if d.device_id == device_id), None
        )
        if not device:
            return 0.0, ["Устройство не найдено"]

        score = 0.0
        recommendations = []

        # Проверяем соответствие политикам безопасности
        applicable_policies = [
            p
            for p in self.policies
            if device.device_type in p.device_types and p.enabled
        ]

        for policy in applicable_policies:
            policy_score = 0.0
            total_requirements = len(policy.requirements)

            # Простая проверка требований (в реальной системе здесь была бы
            # детальная проверка)
            for requirement in policy.requirements:
                if self._check_requirement(device, requirement):
                    policy_score += 1.0
                else:
                    recommendations.append(f"Требуется: {requirement}")

            if total_requirements > 0:
                policy_score = (policy_score / total_requirements) * 100
                score += policy_score

        if applicable_policies:
            score = score / len(applicable_policies)

        # Обновляем оценку безопасности устройства
        device.security_score = score
        device.last_seen = datetime.datetime.now().isoformat()

        return score, recommendations

    def _check_requirement(self, device: Device, requirement: str) -> bool:
        """Проверяет выполнение конкретного требования безопасности."""
        # Упрощенная проверка (в реальной системе здесь была бы
        # детальная проверка)
        requirement_lower = requirement.lower()

        if "антивирус" in requirement_lower:
            return device.hardware_info.get("antivirus_installed", False)
        elif "шифрование" in requirement_lower:
            return device.hardware_info.get("encryption_enabled", False)
        elif "обновления" in requirement_lower:
            return device.hardware_info.get("auto_updates_enabled", False)
        elif "блокировка" in requirement_lower:
            return device.hardware_info.get("screen_lock_enabled", False)

        return True  # По умолчанию считаем, что требование выполнено

    def detect_threat(
        self,
        device_id: str,
        threat_type: ThreatType,
        severity: SecurityLevel,
        description: str,
    ) -> str:
        """Обнаруживает угрозу безопасности для устройства."""
        threat_id = f"threat_{int(time.time())}_{len(self.threats)}"

        threat = SecurityThreat(
            threat_id=threat_id,
            device_id=device_id,
            threat_type=threat_type,
            severity=severity,
            description=description,
        )

        self.threats.append(threat)

        # Обновляем статус устройства
        device = next(
            (d for d in self.devices if d.device_id == device_id), None
        )
        if device:
            device.status = DeviceStatus.COMPROMISED
            device.security_score = max(
                0, device.security_score - 20
            )  # Снижаем оценку

        print(
            f"Обнаружена угроза {threat_type.value} для устройства "
            f"{device_id}: {description}"
        )
        self._update_metrics()

        return threat_id

    def resolve_threat(
        self, threat_id: str, mitigation_actions: List[str]
    ) -> bool:
        """Разрешает угрозу безопасности."""
        for threat in self.threats:
            if threat.threat_id == threat_id:
                threat.status = "resolved"
                threat.resolved_at = datetime.datetime.now().isoformat()
                threat.mitigation_actions = mitigation_actions

                # Восстанавливаем статус устройства
                device = next(
                    (
                        d
                        for d in self.devices
                        if d.device_id == threat.device_id
                    ),
                    None,
                )
                if device:
                    device.status = DeviceStatus.ACTIVE
                    device.security_score = min(
                        100, device.security_score + 10
                    )  # Повышаем оценку

                print(f"Угроза {threat_id} разрешена.")
                self._update_metrics()
                return True

        print(f"Угроза {threat_id} не найдена.")
        return False

    def get_device_threats(self, device_id: str) -> List[SecurityThreat]:
        """Возвращает список угроз для конкретного устройства."""
        return [t for t in self.threats if t.device_id == device_id]

    def get_devices_by_status(self, status: DeviceStatus) -> List[Device]:
        """Возвращает устройства по статусу."""
        return [d for d in self.devices if d.status == status]

    def get_devices_by_security_level(
        self, level: SecurityLevel
    ) -> List[Device]:
        """Возвращает устройства по уровню безопасности."""
        return [d for d in self.devices if d.security_level == level]

    def quarantine_device(self, device_id: str, reason: str) -> bool:
        """Переводит устройство в карантин."""
        device = next(
            (d for d in self.devices if d.device_id == device_id), None
        )
        if device:
            device.status = DeviceStatus.QUARANTINED
            print(f"Устройство {device_id} переведено в карантин: {reason}")
            self._update_metrics()
            return True
        print(f"Устройство {device_id} не найдено.")
        return False

    def release_from_quarantine(self, device_id: str) -> bool:
        """Выпускает устройство из карантина."""
        device = next(
            (d for d in self.devices if d.device_id == device_id), None
        )
        if device and device.status == DeviceStatus.QUARANTINED:
            device.status = DeviceStatus.ACTIVE
            print(f"Устройство {device_id} выпущено из карантина.")
            self._update_metrics()
            return True
        print(f"Устройство {device_id} не найдено или не в карантине.")
        return False

    def _update_metrics(self):
        """Обновляет метрики безопасности."""
        self.metrics.update_metrics(self.devices, self.threats)

    def get_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики безопасности устройств."""
        return self.metrics.to_dict()

    def export_device_report(self, file_path: str):
        """Экспортирует отчет по устройствам."""
        report = {
            "devices": [d.to_dict() for d in self.devices],
            "threats": [t.to_dict() for t in self.threats],
            "metrics": self.metrics.to_dict(),
            "generated_at": datetime.datetime.now().isoformat(),
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        print(f"Отчет по устройствам экспортирован в: {file_path}")

    def get_status(self) -> str:
        """Получение статуса DeviceSecurity"""
        try:
            if hasattr(self, 'is_running') and self.is_running:
                return "running"
            else:
                return "stopped"
        except Exception:
            return "unknown"

    def start_security(self) -> bool:
        """Запуск системы безопасности устройств"""
        try:
            self.is_running = True
            print("Система безопасности устройств запущена")
            return True
        except Exception as e:
            print(f"Ошибка запуска системы безопасности устройств: {e}")
            return False

    def stop_security(self) -> bool:
        """Остановка системы безопасности устройств"""
        try:
            self.is_running = False
            print("Система безопасности устройств остановлена")
            return True
        except Exception as e:
            print(f"Ошибка остановки системы безопасности устройств: {e}")
            return False

    def get_security_info(self) -> Dict[str, Any]:
        """Получение информации о системе безопасности устройств"""
        try:
            return {
                "is_running": getattr(self, 'is_running', False),
                "devices_count": len(self.devices),
                "threats_count": len(self.threats),
                "device_types": len(DeviceType),
                "device_statuses": len(DeviceStatus),
                "security_levels": len(SecurityLevel),
                "threat_types": len(ThreatType),
                "quarantined_devices": len([d for d in self.devices if d.status == DeviceStatus.QUARANTINED]),
                "active_threats": len([t for t in self.threats if not t.resolved]),
            }
        except Exception as e:
            print(f"Ошибка получения информации о системе безопасности устройств: {e}")
            return {
                "is_running": False,
                "devices_count": 0,
                "threats_count": 0,
                "device_types": 0,
                "device_statuses": 0,
                "security_levels": 0,
                "threat_types": 0,
                "quarantined_devices": 0,
                "active_threats": 0,
                "error": str(e),
            }
