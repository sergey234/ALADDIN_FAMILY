# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Device Security Service
Система безопасности устройств для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import logging
import platform
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from core.base import SecurityBase


class DeviceType(Enum):
    """Типы устройств"""

    DESKTOP = "desktop"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    IOT = "iot"
    ROUTER = "router"
    PRINTER = "printer"
    CAMERA = "camera"
    UNKNOWN = "unknown"


class SecurityStatus(Enum):
    """Статусы безопасности"""

    SECURE = "secure"
    WARNING = "warning"
    VULNERABLE = "vulnerable"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Уровни угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Действия безопасности"""

    SCAN = "scan"
    UPDATE = "update"
    QUARANTINE = "quarantine"
    BLOCK = "block"
    ALERT = "alert"
    NOTIFY_PARENT = "notify_parent"
    NOTIFY_ADMIN = "notify_admin"
    ISOLATE = "isolate"
    PATCH = "patch"
    RESET = "reset"


@dataclass
class DeviceProfile:
    """Профиль устройства"""

    device_id: str
    device_name: str
    device_type: DeviceType
    operating_system: str
    os_version: str
    hardware_info: Dict[str, Any]
    network_interfaces: List[str]
    installed_software: List[str]
    security_status: SecurityStatus
    last_scan: Optional[datetime] = None
    vulnerabilities: List[str] = field(default_factory=list)
    security_score: float = 0.0
    user_id: Optional[str] = None
    family_role: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityVulnerability:
    """Уязвимость безопасности"""

    vulnerability_id: str
    device_id: str
    vulnerability_type: str
    severity: ThreatLevel
    description: str
    cve_id: Optional[str] = None
    affected_software: Optional[str] = None
    detection_date: datetime = field(default_factory=datetime.now)
    remediation: Optional[str] = None
    status: str = "detected"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityRule:
    """Правило безопасности устройства"""

    rule_id: str
    name: str
    description: str
    device_type: DeviceType
    conditions: Dict[str, Any]
    actions: List[SecurityAction]
    enabled: bool = True
    family_specific: bool = False
    age_group: Optional[str] = None
    priority: int = 1


@dataclass
class DeviceSecurityReport:
    """Отчет о безопасности устройства"""

    device_id: str
    scan_date: datetime
    security_score: float
    vulnerabilities_found: int
    vulnerabilities_critical: int
    vulnerabilities_high: int
    vulnerabilities_medium: int
    vulnerabilities_low: int
    recommendations: List[str]
    compliance_status: str
    family_protection_status: Dict[str, Any]


class DeviceSecurityService(SecurityBase):
    """Сервис безопасности устройств для семей"""

    def __init__(
        self,
        name: str = "DeviceSecurity",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)
        self.logger = logging.getLogger(__name__)
        # Хранилища данных
        self.device_profiles: Dict[str, DeviceProfile] = {}
        self.security_vulnerabilities: Dict[str, SecurityVulnerability] = {}
        self.security_rules: Dict[str, SecurityRule] = {}
        self.quarantined_devices: Set[str] = set()
        self.blocked_devices: Set[str] = set()
        self.family_device_history: Dict[str, List[str]] = (
            {}
        )  # user_id -> device_ids
        # Настройки безопасности
        self.security_scanning_enabled = True
        self.automatic_updates = True
        self.family_protection_enabled = True
        self.child_device_monitoring = True
        self.elderly_device_monitoring = True
        self.real_time_monitoring = True
        # Пороги для обнаружения угроз
        self.threat_thresholds = {
            ThreatLevel.LOW: 0.3,
            ThreatLevel.MEDIUM: 0.5,
            ThreatLevel.HIGH: 0.7,
            ThreatLevel.CRITICAL: 0.9,
        }
        # Инициализация
        self._initialize_security_rules()
        self._setup_family_protection()
        self._scan_system_devices()

    def _initialize_security_rules(self):
        """Инициализация правил безопасности"""
        rules = [
            SecurityRule(
                rule_id="scan_malware",
                name="Сканирование на вредоносное ПО",
                description="Регулярное сканирование устройств на наличие "
                "вредоносного ПО",
                device_type=DeviceType.DESKTOP,
                conditions={"scan_required": True},
                actions=[SecurityAction.SCAN, SecurityAction.ALERT],
                family_specific=True,
            ),
            SecurityRule(
                rule_id="update_software",
                name="Обновление программного обеспечения",
                description="Автоматическое обновление программного "
                "обеспечения",
                device_type=DeviceType.DESKTOP,
                conditions={"updates_available": True},
                actions=[SecurityAction.UPDATE, SecurityAction.NOTIFY_PARENT],
                family_specific=True,
            ),
            SecurityRule(
                rule_id="child_device_control",
                name="Контроль детских устройств",
                description="Специальный контроль устройств детей",
                device_type=DeviceType.MOBILE,
                conditions={
                    "age_group": "child",
                    "inappropriate_content": True,
                },
                actions=[
                    SecurityAction.BLOCK,
                    SecurityAction.NOTIFY_PARENT,
                    SecurityAction.QUARANTINE,
                ],
                family_specific=True,
                age_group="child",
            ),
            SecurityRule(
                rule_id="elderly_device_protection",
                name="Защита устройств пожилых",
                description="Специальная защита устройств пожилых людей",
                device_type=DeviceType.DESKTOP,
                conditions={
                    "age_group": "elderly",
                    "suspicious_activity": True,
                },
                actions=[
                    SecurityAction.ALERT,
                    SecurityAction.NOTIFY_ADMIN,
                    SecurityAction.ISOLATE,
                ],
                family_specific=True,
                age_group="elderly",
            ),
            SecurityRule(
                rule_id="iot_device_security",
                name="Безопасность IoT устройств",
                description="Контроль безопасности умных устройств",
                device_type=DeviceType.IOT,
                conditions={
                    "default_password": True,
                    "unencrypted_communication": True,
                },
                actions=[
                    SecurityAction.PATCH,
                    SecurityAction.ALERT,
                    SecurityAction.ISOLATE,
                ],
                family_specific=True,
            ),
            SecurityRule(
                rule_id="network_device_monitoring",
                name="Мониторинг сетевых устройств",
                description="Контроль безопасности роутеров и сетевого "
                "оборудования",
                device_type=DeviceType.ROUTER,
                conditions={
                    "firmware_outdated": True,
                    "weak_encryption": True,
                },
                actions=[
                    SecurityAction.UPDATE,
                    SecurityAction.ALERT,
                    SecurityAction.PATCH,
                ],
                family_specific=True,
            ),
            SecurityRule(
                rule_id="mobile_device_security",
                name="Безопасность мобильных устройств",
                description="Контроль безопасности смартфонов и планшетов",
                device_type=DeviceType.MOBILE,
                conditions={"jailbroken": True, "untrusted_apps": True},
                actions=[
                    SecurityAction.ALERT,
                    SecurityAction.QUARANTINE,
                    SecurityAction.NOTIFY_PARENT,
                ],
                family_specific=True,
            ),
            SecurityRule(
                rule_id="critical_vulnerability",
                name="Критические уязвимости",
                description="Немедленная реакция на критические уязвимости",
                device_type=DeviceType.DESKTOP,
                conditions={"critical_vulnerability": True},
                actions=[
                    SecurityAction.PATCH,
                    SecurityAction.ALERT,
                    SecurityAction.ISOLATE,
                ],
                family_specific=True,
            ),
        ]
        for rule in rules:
            self.security_rules[rule.rule_id] = rule
        self.log_activity(
            f"Инициализировано {len(rules)} правил безопасности устройств"
        )

    def _setup_family_protection(self):
        """Настройка семейной защиты"""
        self.family_protection_settings = {
            "child_protection": {
                "enabled": True,
                "app_control": True,
                "content_filtering": True,
                "screen_time_limits": True,
                "location_tracking": True,
                "parent_notifications": True,
            },
            "elderly_protection": {
                "enabled": True,
                "fraud_detection": True,
                "phishing_protection": True,
                "family_notifications": True,
                "suspicious_activity_alerts": True,
                "simplified_interface": True,
            },
            "general_family": {
                "unified_security": True,
                "shared_device_policies": True,
                "family_aware_blocking": True,
                "real_time_monitoring": True,
                "automatic_updates": True,
            },
        }
        self.log_activity("Настроена семейная защита устройств")

    def _scan_system_devices(self):
        """Сканирование системных устройств"""
        try:
            # Получаем информацию о текущем устройстве
            device_info = self._get_system_device_info()
            # Создаем профиль устройства
            device_profile = DeviceProfile(
                device_id=device_info["device_id"],
                device_name=device_info["device_name"],
                device_type=device_info["device_type"],
                operating_system=device_info["os"],
                os_version=device_info["os_version"],
                hardware_info=device_info["hardware"],
                network_interfaces=device_info["network_interfaces"],
                installed_software=device_info["software"],
                security_status=SecurityStatus.SECURE,
                security_score=0.8,  # Начальный балл
                metadata=device_info,
            )
            # Добавляем в профили
            self.device_profiles[
                device_profile.device_id
            ] = device_profile
            self.log_activity(
                f"Обнаружено системное устройство: "
                f"{device_profile.device_name}"
            )
        except Exception as e:
            self.logger.error(f"Ошибка сканирования системных устройств: {e}")

    def _get_system_device_info(self) -> Dict[str, Any]:
        """Получение информации о системном устройстве"""
        try:
            device_info = {
                "device_id": self._generate_device_id(),
                "device_name": platform.node(),
                "device_type": self._detect_device_type(),
                "os": platform.system(),
                "os_version": platform.version(),
                "hardware": {
                    "processor": platform.processor(),
                    "architecture": platform.architecture()[0],
                    "machine": platform.machine(),
                },
                "network_interfaces": self._get_network_interfaces(),
                "software": self._get_installed_software(),
            }
            return device_info
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о системе: {e}")
            return {}

    def _detect_device_type(self) -> DeviceType:
        """Определение типа устройства"""
        try:
            system = platform.system().lower()
            # machine = platform.machine()  # Не используется.lower()
            if "darwin" in system:
                return DeviceType.DESKTOP  # macOS
            elif "linux" in system:
                return DeviceType.DESKTOP  # Linux
            elif "windows" in system:
                return DeviceType.DESKTOP  # Windows
            else:
                return DeviceType.UNKNOWN
        except Exception:
            return DeviceType.UNKNOWN

    def _get_network_interfaces(self) -> List[str]:
        """Получение сетевых интерфейсов"""
        try:
            # Упрощенная реализация
            return ["eth0", "wlan0", "lo"]
        except Exception:
            return []

    def _get_installed_software(self) -> List[str]:
        """Получение списка установленного ПО"""
        try:
            # Упрощенная реализация
            return ["python3", "git", "vim", "curl", "wget"]
        except Exception:
            return []

    def register_device(
        self,
        device_name: str,
        device_type: DeviceType,
        operating_system: str,
        os_version: str,
        user_id: Optional[str] = None,
        family_role: Optional[str] = None,
    ) -> DeviceProfile:
        """Регистрация нового устройства"""
        try:
            device_id = self._generate_device_id()
            device_profile = DeviceProfile(
                device_id=device_id,
                device_name=device_name,
                device_type=device_type,
                operating_system=operating_system,
                os_version=os_version,
                hardware_info={},
                network_interfaces=[],
                installed_software=[],
                security_status=SecurityStatus.UNKNOWN,
                security_score=0.5,  # Начальный балл для новых устройств
                user_id=user_id,
                family_role=family_role,
                metadata={
                    "registration_date": datetime.now().isoformat(),
                    "family_protection_enabled": True,
                },
            )
            # Добавляем в профили
            self.device_profiles[device_id] = device_profile
            # Добавляем в семейную историю
            if user_id:
                if user_id not in self.family_device_history:
                    self.family_device_history[user_id] = []
                self.family_device_history[user_id].append(
                    device_id
                )
            # Проверяем правила безопасности
            self._check_security_rules(device_profile)
            # Добавляем событие безопасности
            self.add_security_event(
                event_type="device_registered",
                severity="info",
                description=f"Зарегистрировано новое устройство: "
                f"{device_name}",
                source="DeviceSecurity",
                metadata={
                    "device_id": device_id,
                    "device_name": device_name,
                    "device_type": device_type.value,
                    "operating_system": operating_system,
                    "user_id": user_id,
                    "family_role": family_role,
                },
            )
            return device_profile
        except Exception as e:
            self.logger.error(f"Ошибка регистрации устройства: {e}")
            return None

    def scan_device_security(self, device_id: str) -> DeviceSecurityReport:
        """Сканирование безопасности устройства"""
        try:
            if device_id not in self.device_profiles:
                raise ValueError(f"Устройство {device_id} не найдено")
            device_profile = self.device_profiles[device_id]
            # Выполняем сканирование
            vulnerabilities = self._perform_security_scan(device_profile)
            # Обновляем профиль устройства
            device_profile.vulnerabilities = [
                v.vulnerability_id for v in vulnerabilities
            ]
            device_profile.last_scan = datetime.now()
            device_profile.security_score = self._calculate_security_score(
                device_profile, vulnerabilities
            )
            # Создаем отчет
            report = DeviceSecurityReport(
                device_id=device_id,
                scan_date=datetime.now(),
                security_score=device_profile.security_score,
                vulnerabilities_found=len(vulnerabilities),
                vulnerabilities_critical=len(
                    [
                        v
                        for v in vulnerabilities
                        if v.severity == ThreatLevel.CRITICAL
                    ]
                ),
                vulnerabilities_high=len(
                    [
                        v
                        for v in vulnerabilities
                        if v.severity == ThreatLevel.HIGH
                    ]
                ),
                vulnerabilities_medium=len(
                    [
                        v
                        for v in vulnerabilities
                        if v.severity == ThreatLevel.MEDIUM
                    ]
                ),
                vulnerabilities_low=len(
                    [
                        v
                        for v in vulnerabilities
                        if v.severity == ThreatLevel.LOW
                    ]
                ),
                recommendations=self._generate_recommendations(
                    device_profile, vulnerabilities
                ),
                compliance_status=self._check_compliance_status(
                    device_profile
                ),
                family_protection_status=self._get_family_protection_status(
                    device_profile
                ),
            )
            # Добавляем событие безопасности
            self.add_security_event(
                event_type="device_scan_completed",
                severity="info",
                description=f"Завершено сканирование безопасности устройства: "
                f"{device_profile.device_name}",
                source="DeviceSecurity",
                metadata={
                    "device_id": device_id,
                    "security_score": device_profile.security_score,
                    "vulnerabilities_found": len(vulnerabilities),
                    "vulnerabilities_critical": (
                        report.vulnerabilities_critical
                    ),
                    "user_id": device_profile.user_id,
                },
            )
            return report
        except Exception as e:
            self.logger.error(
                f"Ошибка сканирования безопасности устройства: {e}"
            )
            return None

    def _perform_security_scan(
        self, device_profile: DeviceProfile
    ) -> List[SecurityVulnerability]:
        """Выполнение сканирования безопасности"""
        vulnerabilities = []
        try:
            # Проверяем различные типы уязвимостей
            vulnerabilities.extend(
                self._check_software_vulnerabilities(device_profile)
            )
            vulnerabilities.extend(
                self._check_network_vulnerabilities(device_profile)
            )
            vulnerabilities.extend(
                self._check_configuration_vulnerabilities(device_profile)
            )
            vulnerabilities.extend(
                self._check_family_specific_vulnerabilities(device_profile)
            )
            # Добавляем уязвимости в хранилище
            for vulnerability in vulnerabilities:
                self.security_vulnerabilities[
                    vulnerability.vulnerability_id
                ] = vulnerability
            return vulnerabilities
        except Exception as e:
            self.logger.error(
                f"Ошибка выполнения сканирования безопасности: {e}"
            )
            return []

    def _check_software_vulnerabilities(
        self, device_profile: DeviceProfile
    ) -> List[SecurityVulnerability]:
        """Проверка уязвимостей программного обеспечения"""
        vulnerabilities = []
        try:
            # Проверяем устаревшее ПО
            for software in device_profile.installed_software:
                if self._is_software_outdated(software):
                    vulnerability = SecurityVulnerability(
                        vulnerability_id=self._generate_vulnerability_id(),
                        device_id=device_profile.device_id,
                        vulnerability_type="outdated_software",
                        severity=ThreatLevel.MEDIUM,
                        description=f"Устаревшее программное обеспечение: "
                        f"{software}",
                        affected_software=software,
                        remediation=f"Обновить {software} до последней "
                        f"версии",
                    )
                    vulnerabilities.append(vulnerability)
            # Проверяем отсутствие антивируса
            if not self._has_antivirus_installed(
                device_profile
            ):
                vulnerability = SecurityVulnerability(
                    vulnerability_id=self._generate_vulnerability_id(),
                    device_id=device_profile.device_id,
                    vulnerability_type="missing_antivirus",
                    severity=ThreatLevel.HIGH,
                    description="Отсутствует антивирусное программное "
                    "обеспечение",
                    remediation="Установить антивирусное программное "
                    "обеспечение",
                )
                vulnerabilities.append(vulnerability)
            return vulnerabilities
        except Exception as e:
            self.logger.error(f"Ошибка проверки уязвимостей ПО: {e}")
            return []

    def _check_network_vulnerabilities(
        self, device_profile: DeviceProfile
    ) -> List[SecurityVulnerability]:
        """Проверка сетевых уязвимостей"""
        vulnerabilities = []
        try:
            # Проверяем открытые порты
            for interface in device_profile.network_interfaces:
                if self._has_open_ports(interface):
                    vulnerability = SecurityVulnerability(
                        vulnerability_id=self._generate_vulnerability_id(),
                        device_id=device_profile.device_id,
                        vulnerability_type="open_ports",
                        severity=ThreatLevel.MEDIUM,
                        description=f"Открытые порты на интерфейсе "
                        f"{interface}",
                        remediation="Закрыть неиспользуемые порты",
                    )
                    vulnerabilities.append(vulnerability)
            return vulnerabilities
        except Exception as e:
            self.logger.error(f"Ошибка проверки сетевых уязвимостей: {e}")
            return []

    def _check_configuration_vulnerabilities(
        self, device_profile: DeviceProfile
    ) -> List[SecurityVulnerability]:
        """Проверка уязвимостей конфигурации"""
        vulnerabilities = []
        try:
            # Проверяем слабые пароли
            if self._has_weak_passwords(device_profile):
                vulnerability = SecurityVulnerability(
                    vulnerability_id=self._generate_vulnerability_id(),
                    device_id=device_profile.device_id,
                    vulnerability_type="weak_passwords",
                    severity=ThreatLevel.HIGH,
                    description="Обнаружены слабые пароли",
                    remediation="Изменить пароли на более сложные",
                )
                vulnerabilities.append(vulnerability)
            # Проверяем отключенный файрвол
            if not self._is_firewall_enabled(device_profile):
                vulnerability = SecurityVulnerability(
                    vulnerability_id=self._generate_vulnerability_id(),
                    device_id=device_profile.device_id,
                    vulnerability_type="disabled_firewall",
                    severity=ThreatLevel.HIGH,
                    description="Файрвол отключен",
                    remediation="Включить файрвол",
                )
                vulnerabilities.append(vulnerability)
            return vulnerabilities
        except Exception as e:
            self.logger.error(f"Ошибка проверки уязвимостей конфигурации: {e}")
            return []

    def _check_family_specific_vulnerabilities(
        self, device_profile: DeviceProfile
    ) -> List[SecurityVulnerability]:
        """Проверка семейных уязвимостей"""
        vulnerabilities = []
        try:
            # Проверяем детские устройства
            if device_profile.family_role == "child":
                if self._has_inappropriate_content(
                    device_profile
                ):
                    vulnerability = SecurityVulnerability(
                        vulnerability_id=self._generate_vulnerability_id(),
                        device_id=device_profile.device_id,
                        vulnerability_type="inappropriate_content",
                        severity=ThreatLevel.CRITICAL,
                        description="Обнаружен неподходящий контент на "
                        "детском устройстве",
                        remediation="Удалить неподходящий контент и усилить "
                        "фильтрацию",
                    )
                    vulnerabilities.append(vulnerability)
            # Проверяем устройства пожилых
            elif device_profile.family_role == "elderly":
                if self._has_suspicious_activity(
                    device_profile
                ):
                    vulnerability = SecurityVulnerability(
                        vulnerability_id=self._generate_vulnerability_id(),
                        device_id=device_profile.device_id,
                        vulnerability_type="suspicious_activity",
                        severity=ThreatLevel.HIGH,
                        description="Подозрительная активность на устройстве "
                        "пожилого человека",
                        remediation="Проверить активность и усилить "
                        "мониторинг",
                    )
                    vulnerabilities.append(vulnerability)
            return vulnerabilities
        except Exception as e:
            self.logger.error(f"Ошибка проверки семейных уязвимостей: {e}")
            return []

    def _check_security_rules(self, device_profile: DeviceProfile):
        """Проверка правил безопасности"""
        try:
            for rule in self.security_rules.values():
                if not rule.enabled:
                    continue
                if self._evaluate_rule_conditions(device_profile, rule):
                    self._apply_rule_actions(device_profile, rule)
        except Exception as e:
            self.logger.error(f"Ошибка проверки правил безопасности: {e}")

    def _evaluate_rule_conditions(
        self, device_profile: DeviceProfile, rule: SecurityRule
    ) -> bool:
        """Оценка условий правила"""
        try:
            conditions = rule.conditions
            # Проверка типа устройства
            if rule.device_type != device_profile.device_type:
                return False
            # Проверка семейных условий
            if rule.family_specific:
                if (
                    rule.age_group == "child"
                    and device_profile.family_role != "child"
                ):
                    return False
                elif (
                    rule.age_group == "elderly"
                    and device_profile.family_role != "elderly"
                ):
                    return False
            # Проверка условий сканирования
            if "scan_required" in conditions and conditions["scan_required"]:
                return True
            # Проверка доступных обновлений
            if (
                "updates_available" in conditions
                and conditions["updates_available"]
            ):
                return self._has_available_updates(device_profile)
            # Проверка неподходящего контента
            if (
                "inappropriate_content" in conditions
                and conditions["inappropriate_content"]
            ):
                return self._has_inappropriate_content(device_profile)
            # Проверка подозрительной активности
            if (
                "suspicious_activity" in conditions
                and conditions["suspicious_activity"]
            ):
                return self._has_suspicious_activity(device_profile)
            # Проверка критических уязвимостей
            if (
                "critical_vulnerability" in conditions
                and conditions["critical_vulnerability"]
            ):
                return self._has_critical_vulnerabilities(device_profile)
            return False
        except Exception as e:
            self.logger.error(f"Ошибка оценки условий правила: {e}")
            return False

    def _apply_rule_actions(
        self, device_profile: DeviceProfile, rule: SecurityRule
    ):
        """Применение действий правила"""
        try:
            for action in rule.actions:
                if action == SecurityAction.SCAN:
                    self.scan_device_security(device_profile.device_id)
                elif action == SecurityAction.UPDATE:
                    self.log_activity(
                        f"Обновление устройства: "
                        f"{device_profile.device_name}"
                    )
                elif action == SecurityAction.QUARANTINE:
                    self.quarantined_devices.add(device_profile.device_id)
                    self.log_activity(
                        f"Устройство помещено в карантин: "
                        f"{device_profile.device_name}"
                    )
                elif action == SecurityAction.BLOCK:
                    self.blocked_devices.add(
                        device_profile.device_id
                    )
                    self.log_activity(
                        f"Устройство заблокировано: "
                        f"{device_profile.device_name}"
                    )
                elif action == SecurityAction.ALERT:
                    self.log_activity(
                        f"Алерт безопасности: {rule.name} - "
                        f"{device_profile.device_name}"
                    )
                elif action == SecurityAction.NOTIFY_PARENT:
                    self.log_activity(f"Уведомление родителям: {rule.name}")
                elif action == SecurityAction.NOTIFY_ADMIN:
                    self.log_activity(
                        f"Уведомление администратору: {rule.name}"
                    )
                elif action == SecurityAction.ISOLATE:
                    self.log_activity(
                        f"Изоляция устройства: {device_profile.device_name}"
                    )
                elif action == SecurityAction.PATCH:
                    self.log_activity(
                        f"Установка патча: {device_profile.device_name}"
                    )
                elif action == SecurityAction.RESET:
                    self.log_activity(
                        f"Сброс устройства: {device_profile.device_name}"
                    )
        except Exception as e:
            self.logger.error(f"Ошибка применения действий правила: {e}")

    def _calculate_security_score(
        self,
        device_profile: DeviceProfile,
        vulnerabilities: List[SecurityVulnerability],
    ) -> float:
        """Расчет балла безопасности"""
        try:
            base_score = 1.0
            # Снижаем балл за уязвимости
            for vulnerability in vulnerabilities:
                if vulnerability.severity == ThreatLevel.CRITICAL:
                    base_score -= 0.3
                elif vulnerability.severity == ThreatLevel.HIGH:
                    base_score -= 0.2
                elif vulnerability.severity == ThreatLevel.MEDIUM:
                    base_score -= 0.1
                elif vulnerability.severity == ThreatLevel.LOW:
                    base_score -= 0.05
            # Дополнительные факторы
            if device_profile.family_role == "child":
                base_score += 0.1  # Дополнительная защита для детей
            elif device_profile.family_role == "elderly":
                base_score += 0.05  # Дополнительная защита для пожилых
            return max(0.0, min(1.0, base_score))
        except Exception as e:
            self.logger.error(f"Ошибка расчета балла безопасности: {e}")
            return 0.5

    def _generate_recommendations(
        self,
        device_profile: DeviceProfile,
        vulnerabilities: List[SecurityVulnerability],
    ) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        try:
            # Рекомендации на основе уязвимостей
            for vulnerability in vulnerabilities:
                if vulnerability.remediation:
                    recommendations.append(vulnerability.remediation)
            # Общие рекомендации
            if device_profile.security_score < 0.7:
                recommendations.append("Усилить общую безопасность устройства")
            if device_profile.family_role == "child":
                recommendations.append("Включить родительский контроль")
                recommendations.append("Настроить фильтрацию контента")
            elif device_profile.family_role == "elderly":
                recommendations.append("Включить защиту от мошенничества")
                recommendations.append("Упростить интерфейс")
            return recommendations
        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")
            return []

    def _check_compliance_status(self, device_profile: DeviceProfile) -> str:
        """Проверка статуса соответствия"""
        try:
            if device_profile.security_score >= 0.9:
                return "compliant"
            elif device_profile.security_score >= 0.7:
                return "mostly_compliant"
            elif device_profile.security_score >= 0.5:
                return "partially_compliant"
            else:
                return "non_compliant"
        except Exception as e:
            self.logger.error(f"Ошибка проверки соответствия: {e}")
            return "unknown"

    def _get_family_protection_status(
        self, device_profile: DeviceProfile
    ) -> Dict[str, Any]:
        """Получение статуса семейной защиты"""
        try:
            status = {
                "family_protection_enabled": True,
                "user_id": device_profile.user_id,
                "family_role": device_profile.family_role,
                "child_protection": device_profile.family_role == "child",
                "elderly_protection": device_profile.family_role == "elderly",
                "security_score": device_profile.security_score,
                "last_scan": (
                    device_profile.last_scan.isoformat()
                    if device_profile.last_scan
                    else None
                ),
            }
            return status
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса семейной защиты: {e}")
            return {}

    def get_device_security_summary(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение сводки по безопасности устройств"""
        try:
            if user_id:
                # Сводка для конкретного пользователя
                user_devices = [
                    device
                    for device in self.device_profiles.values()
                    if device.user_id == user_id
                ]
            else:
                # Общая сводка
                user_devices = list(self.device_profiles.values())
            summary = {
                "total_devices": len(user_devices),
                "secure_devices": len(
                    [
                        d
                        for d in user_devices
                        if d.security_status == SecurityStatus.SECURE
                    ]
                ),
                "vulnerable_devices": len(
                    [
                        d
                        for d in user_devices
                        if d.security_status == SecurityStatus.VULNERABLE
                    ]
                ),
                "quarantined_devices": len(
                    [
                        d
                        for d in user_devices
                        if d.device_id in self.quarantined_devices
                    ]
                ),
                "blocked_devices": len(
                    [
                        d
                        for d in user_devices
                        if d.device_id in self.blocked_devices
                    ]
                ),
                "average_security_score": (
                    sum(d.security_score for d in user_devices)
                    / len(user_devices)
                    if user_devices
                    else 0
                ),
                "by_device_type": {
                    device_type.value: len(
                        [
                            d
                            for d in user_devices
                            if d.device_type == device_type
                        ]
                    )
                    for device_type in DeviceType
                },
                "by_security_status": {
                    status.value: len(
                        [
                            d
                            for d in user_devices
                            if d.security_status == status
                        ]
                    )
                    for status in SecurityStatus
                },
                "recent_scans": [
                    {
                        "device_id": device.device_id,
                        "device_name": device.device_name,
                        "security_score": device.security_score,
                        "last_scan": (
                            device.last_scan.isoformat()
                            if device.last_scan
                            else None
                        ),
                        "vulnerabilities_count": len(device.vulnerabilities),
                    }
                    for device in sorted(
                        user_devices,
                        key=lambda x: x.last_scan or datetime.min,
                        reverse=True,
                    )[:10]
                ],
            }
            return summary
        except Exception as e:
            self.logger.error(
                f"Ошибка получения сводки по безопасности устройств: {e}"
            )
            return {}

    def get_family_device_status(self) -> Dict[str, Any]:
        """Получение статуса семейных устройств"""
        try:
            status = {
                "security_scanning_enabled": self.security_scanning_enabled,
                "automatic_updates": self.automatic_updates,
                "family_protection_enabled": self.family_protection_enabled,
                "child_device_monitoring": self.child_device_monitoring,
                "elderly_device_monitoring": self.elderly_device_monitoring,
                "real_time_monitoring": self.real_time_monitoring,
                "active_rules": len(
                    [
                        r for r in self.security_rules.values()
                        if r.enabled
                    ]
                ),
                "family_specific_rules": len(
                    [
                        r
                        for r in self.security_rules.values()
                        if r.family_specific
                    ]
                ),
                "total_devices": len(self.device_profiles),
                "quarantined_devices_count": len(
                    self.quarantined_devices
                ),
                "blocked_devices_count": len(self.blocked_devices),
                "total_vulnerabilities": len(self.security_vulnerabilities),
                "protection_settings": self.family_protection_settings,
                "family_history": {
                    user_id: len(device_ids)
                    for user_id, device_ids in (
                        self.family_device_history.items()
                    )
                },
            }
            return status
        except Exception as e:
            self.logger.error(
                f"Ошибка получения статуса семейных устройств: {e}"
            )
            return {}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса сервиса"""
        try:
            return {
                "service_name": self.name,
                "status": self.status.value,
                "security_rules": len(self.security_rules),
                "device_profiles": len(self.device_profiles),
                "security_vulnerabilities": len(self.security_vulnerabilities),
                "quarantined_devices": len(self.quarantined_devices),
                "blocked_devices": len(self.blocked_devices),
                "family_protection_enabled": self.family_protection_enabled,
                "security_scanning_enabled": self.security_scanning_enabled,
                "uptime": (
                    (datetime.now() - self.start_time).total_seconds()
                    if hasattr(self, "start_time") and self.start_time
                    else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {}

    # Вспомогательные методы для проверок

    def _is_software_outdated(self, software: str) -> bool:
        """Проверка устаревшего ПО"""
        # Упрощенная реализация
        outdated_software = ["python2", "java8", "flash"]
        return software.lower() in outdated_software

    def _has_antivirus_installed(self, device_profile: DeviceProfile) -> bool:
        """Проверка наличия антивируса"""
        # Упрощенная реализация
        antivirus_software = ["avast", "norton", "kaspersky", "bitdefender"]
        return any(
            av in device_profile.installed_software
            for av in antivirus_software
        )

    def _has_open_ports(self, interface: str) -> bool:
        """Проверка открытых портов"""
        # Упрощенная реализация
        return interface in ["eth0", "wlan0"]

    def _has_weak_passwords(self, device_profile: DeviceProfile) -> bool:
        """Проверка слабых паролей"""
        # Упрощенная реализация
        return device_profile.device_name in ["admin", "user", "test"]

    def _is_firewall_enabled(self, device_profile: DeviceProfile) -> bool:
        """Проверка включенного файрвола"""
        # Упрощенная реализация
        return device_profile.device_name not in ["unprotected"]

    def _has_inappropriate_content(
        self, device_profile: DeviceProfile
    ) -> bool:
        """Проверка неподходящего контента"""
        # Упрощенная реализация
        return device_profile.device_name in ["child_device_with_bad_content"]

    def _has_suspicious_activity(self, device_profile: DeviceProfile) -> bool:
        """Проверка подозрительной активности"""
        # Упрощенная реализация
        return device_profile.device_name in ["elderly_device_suspicious"]

    def _has_available_updates(self, device_profile: DeviceProfile) -> bool:
        """Проверка доступных обновлений"""
        # Упрощенная реализация
        return device_profile.device_name in ["device_needs_update"]

    def _has_critical_vulnerabilities(
        self, device_profile: DeviceProfile
    ) -> bool:
        """Проверка критических уязвимостей"""
        # Упрощенная реализация
        return device_profile.device_name in ["device_critical_vuln"]

    def _generate_device_id(self) -> str:
        """Генерация ID устройства"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(timestamp))[-8:]
        return f"device_{timestamp}_{random_part}"

    def _generate_vulnerability_id(self) -> str:
        """Генерация ID уязвимости"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(timestamp))[-8:]
        return f"vuln_{timestamp}_{random_part}"
