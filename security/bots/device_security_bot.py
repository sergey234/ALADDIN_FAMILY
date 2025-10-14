#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
function_100: DeviceSecurityBot - Бот безопасности устройств
Интеллектуальный бот для защиты устройств от угроз
"""

import asyncio
import json
import logging
import platform
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Уровни угроз"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeviceAction(Enum):
    """Действия с устройством"""

    BLOCK = "block"
    ALLOW = "allow"
    QUARANTINE = "quarantine"
    UPDATE = "update"
    RESTART = "restart"
    ALERT = "alert"


class DeviceType(Enum):
    """Типы устройств"""

    DESKTOP = "desktop"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    TABLET = "tablet"
    SERVER = "server"
    IOT = "iot"
    ROUTER = "router"
    CAMERA = "camera"


class ThreatType(Enum):
    """Типы угроз"""

    MALWARE = "malware"
    VIRUS = "virus"
    TROJAN = "trojan"
    RANSOMWARE = "ransomware"
    SPYWARE = "spyware"
    ROOTKIT = "rootkit"
    KEYLOGGER = "keylogger"
    BACKDOOR = "backdoor"
    VULNERABILITY = "vulnerability"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


@dataclass
class DeviceThreat:
    """Угроза устройства"""

    threat_id: str
    threat_type: ThreatType
    device_id: str
    file_path: str
    threat_level: ThreatLevel
    description: str
    detection_time: datetime
    file_size: int
    file_hash: str
    process_id: Optional[int]
    mitigation: str


@dataclass
class DeviceInfo:
    """Информация об устройстве"""

    device_id: str
    device_type: DeviceType
    os_name: str
    os_version: str
    hardware_info: Dict[str, Any]
    installed_software: List[str]
    running_processes: List[str]
    network_interfaces: List[str]
    security_status: str
    last_scan: datetime


@dataclass
class DeviceResponse:
    """Ответ устройства"""

    action: DeviceAction
    threat_level: ThreatLevel
    message: str
    blocked_files: List[str]
    quarantined_files: List[str]
    updated_software: List[str]
    security_recommendations: List[str]
    device_metrics: Dict[str, Any]


class DeviceSecurityBot:
    """Бот безопасности устройств"""

    def __init__(self, name: str = "DeviceSecurityBot"):
        self.name = name
        self.running = False
        self.config = self._load_config()
        self.db_path = "device_security.db"
        self.stats = {
            "devices_scanned": 0,
            "threats_detected": 0,
            "files_quarantined": 0,
            "software_updated": 0,
            "devices_restarted": 0,
            "security_score_avg": 0.0,
            "performance_score_avg": 0.0,
        }
        self.registered_devices = {}
        self.threat_database = self._load_threat_database()
        self.scanning_threads = []
        self._init_database()

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        return {
            "enabled_features": [
                "malware_detection",
                "vulnerability_scanning",
                "software_updates",
                "process_monitoring",
                "network_monitoring",
                "file_integrity_checking",
            ],
            "scan_settings": {
                "scan_interval_minutes": 60,
                "deep_scan_interval_hours": 24,
                "quarantine_suspicious": True,
                "auto_update_software": True,
                "monitor_critical_files": True,
            },
            "security_policies": {
                "block_unsigned_software": True,
                "require_antivirus": True,
                "enable_firewall": True,
                "encrypt_sensitive_data": True,
                "monitor_usb_devices": True,
            },
            "threat_detection": {
                "malware_signatures": [],
                "suspicious_processes": [
                    "cmd.exe",
                    "powershell.exe",
                    "wscript.exe",
                    "cscript.exe",
                    "rundll32.exe",
                ],
                "suspicious_files": [
                    "*.exe",
                    "*.bat",
                    "*.cmd",
                    "*.scr",
                    "*.pif",
                    "*.vbs",
                    "*.js",
                    "*.jar",
                    "*.com",
                ],
                "suspicious_registry_keys": [
                    "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\"
                    "CurrentVersion\\Run",
                    "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\"
                    "CurrentVersion\\Run",
                ],
            },
            "device_types": {
                "desktop": {"scan_priority": 1, "security_level": "high"},
                "laptop": {"scan_priority": 2, "security_level": "high"},
                "mobile": {"scan_priority": 3, "security_level": "medium"},
                "tablet": {"scan_priority": 4, "security_level": "medium"},
                "server": {"scan_priority": 1, "security_level": "critical"},
                "iot": {"scan_priority": 5, "security_level": "low"},
            },
        }

    def _load_threat_database(self) -> Dict[str, Any]:
        """Загрузка базы данных угроз"""
        return {
            "malware_signatures": [
                "4D5A90000300000004000000FFFF0000",  # PE header
                "504B0304140000000800",  # ZIP with executable
                "7F454C460101010000000000",  # ELF executable
            ],
            "suspicious_processes": [
                "cmd.exe",
                "powershell.exe",
                "wscript.exe",
                "cscript.exe",
                "rundll32.exe",
                "regsvr32.exe",
            ],
            "suspicious_files": [
                "*.exe",
                "*.bat",
                "*.cmd",
                "*.scr",
                "*.pif",
                "*.vbs",
                "*.js",
                "*.jar",
                "*.com",
                "*.pif",
            ],
            "vulnerability_patterns": [
                r"MS\d{2}-\d{3}",  # Microsoft security bulletins
                r"CVE-\d{4}-\d{4,7}",  # CVE identifiers
                r"Buffer overflow",  # Common vulnerability type
                r"SQL injection",  # Web vulnerability
                r"Cross-site scripting",  # XSS vulnerability
            ],
        }

    def _init_database(self):
        """Инициализация базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Таблица устройств
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    device_type TEXT NOT NULL,
                    os_name TEXT NOT NULL,
                    os_version TEXT NOT NULL,
                    hardware_info TEXT,
                    installed_software TEXT,
                    running_processes TEXT,
                    network_interfaces TEXT,
                    security_status TEXT,
                    last_scan TEXT,
                    registration_time TEXT NOT NULL
                )
            """
            )

            # Таблица угроз устройств
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS device_threats (
                    threat_id TEXT PRIMARY KEY,
                    threat_type TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    file_path TEXT,
                    threat_level TEXT NOT NULL,
                    description TEXT,
                    detection_time TEXT NOT NULL,
                    file_size INTEGER,
                    file_hash TEXT,
                    process_id INTEGER,
                    mitigation TEXT
                )
            """
            )

            # Таблица карантина
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quarantined_files (
                    file_path TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT,
                    threat_level TEXT,
                    quarantine_time TEXT NOT NULL,
                    original_location TEXT
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("База данных безопасности устройств инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")

    async def start(self) -> bool:
        """Запуск бота"""
        try:
            self.running = True
            # Запуск сканирования в отдельном потоке
            scanning_thread = threading.Thread(target=self._start_scanning)
            scanning_thread.daemon = True
            scanning_thread.start()
            self.scanning_threads.append(scanning_thread)

            logger.info(f"Бот {self.name} запущен")
            return True
        except Exception as e:
            logger.error(f"Ошибка запуска бота {self.name}: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота"""
        try:
            self.running = False
            # Остановка всех потоков сканирования
            for thread in self.scanning_threads:
                if thread.is_alive():
                    thread.join(timeout=1)

            logger.info(f"Бот {self.name} остановлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка остановки бота {self.name}: {e}")
            return False

    def _start_scanning(self):
        """Запуск сканирования устройств"""
        while self.running:
            try:
                # Сканирование зарегистрированных устройств
                for device_id in self.registered_devices:
                    self._scan_device(device_id)

                # Ожидание до следующего сканирования
                time.sleep(
                    self.config["scan_settings"]["scan_interval_minutes"] * 60
                )

            except Exception as e:
                logger.error(f"Ошибка сканирования: {e}")
                time.sleep(60)  # Ожидание 1 минуту при ошибке

    def _scan_device(self, device_id: str):
        """Сканирование устройства"""
        try:
            if device_id not in self.registered_devices:
                return

            device = self.registered_devices[device_id]

            # Сканирование процессов
            self._scan_processes(device_id)

            # Сканирование файлов
            self._scan_files(device_id)

            # Проверка уязвимостей
            self._scan_vulnerabilities(device_id)

            # Обновление времени последнего сканирования
            device.last_scan = datetime.utcnow()

            logger.info(f"Устройство {device_id} просканировано")

        except Exception as e:
            logger.error(f"Ошибка сканирования устройства {device_id}: {e}")

    def _scan_processes(self, device_id: str):
        """Сканирование процессов"""
        try:
            for proc in psutil.process_iter(["pid", "name", "exe"]):
                try:
                    process_name = proc.info["name"]
                    if (
                        process_name
                        in self.threat_database["suspicious_processes"]
                    ):
                        self._create_threat(
                            ThreatType.MALWARE,
                            device_id,
                            f"Process: {process_name}",
                            ThreatLevel.MEDIUM,
                            f"Подозрительный процесс: {process_name}",
                            process_id=proc.info["pid"],
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Ошибка сканирования процессов: {e}")

    def _scan_files(self, device_id: str):
        """Сканирование файлов"""
        try:
            # Упрощенное сканирование файлов
            # В реальной системе здесь будет полное сканирование файловой
            # системы
            pass
        except Exception as e:
            logger.error(f"Ошибка сканирования файлов: {e}")

    def _scan_vulnerabilities(self, device_id: str):
        """Сканирование уязвимостей"""
        try:
            # Упрощенное сканирование уязвимостей
            # В реальной системе здесь будет проверка CVE баз
            pass
        except Exception as e:
            logger.error(f"Ошибка сканирования уязвимостей: {e}")

    def _create_threat(
        self,
        threat_type: ThreatType,
        device_id: str,
        file_path: str,
        threat_level: ThreatLevel,
        description: str,
        process_id: Optional[int] = None,
    ):
        """Создание записи об угрозе"""
        threat = DeviceThreat(
            threat_id=f"{threat_type.value}_{int(time.time())}",
            threat_type=threat_type,
            device_id=device_id,
            file_path=file_path,
            threat_level=threat_level,
            description=description,
            detection_time=datetime.utcnow(),
            file_size=0,
            file_hash="",
            process_id=process_id,
            mitigation=self._get_mitigation(threat_type),
        )

        # Сохранение в базу данных
        self._save_threat(threat)

        # Обновление статистики
        self.stats["threats_detected"] += 1

        # Карантин файла если необходимо
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._quarantine_file(device_id, file_path, threat_level)

    def _get_mitigation(self, threat_type: ThreatType) -> str:
        """Получение рекомендаций по устранению угрозы"""
        mitigations = {
            ThreatType.MALWARE: "Удалить файл и запустить полное сканирование",
            ThreatType.VIRUS: "Обновить антивирус и запустить сканирование",
            ThreatType.TROJAN: "Удалить файл и проверить систему",
            ThreatType.RANSOMWARE: (
                "Немедленно отключить устройство и восстановить "
                "из резервной копии"
            ),
            ThreatType.SPYWARE: "Удалить программу и изменить пароли",
            ThreatType.ROOTKIT: "Переустановить операционную систему",
            ThreatType.KEYLOGGER: "Удалить программу и изменить все пароли",
            ThreatType.BACKDOOR: "Закрыть порты и обновить систему",
            ThreatType.VULNERABILITY: "Установить обновления безопасности",
            ThreatType.UNAUTHORIZED_ACCESS: "Изменить пароли и включить 2FA",
        }
        return mitigations.get(threat_type, "Мониторить и анализировать")

    def _save_threat(self, threat: DeviceThreat):
        """Сохранение угрозы в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO device_threats
                (threat_id, threat_type, device_id, file_path, "
                "threat_level, description, detection_time, file_size, "
                "file_hash, process_id, mitigation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    threat.threat_id,
                    threat.threat_type.value,
                    threat.device_id,
                    threat.file_path,
                    threat.threat_level.value,
                    threat.description,
                    threat.detection_time.isoformat(),
                    threat.file_size,
                    threat.file_hash,
                    threat.process_id,
                    threat.mitigation,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Ошибка сохранения угрозы: {e}")

    def _quarantine_file(
        self, device_id: str, file_path: str, threat_level: ThreatLevel
    ):
        """Помещение файла в карантин"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            file_name = (
                file_path.split("/")[-1] if "/" in file_path else file_path
            )
            file_type = (
                file_name.split(".")[-1] if "." in file_name else "unknown"
            )

            cursor.execute(
                """
                INSERT OR REPLACE INTO quarantined_files
                (file_path, device_id, file_name, file_type, threat_level,
                 quarantine_time, original_location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    device_id,
                    file_name,
                    file_type,
                    threat_level.value,
                    datetime.utcnow().isoformat(),
                    file_path,
                ),
            )

            conn.commit()
            conn.close()

            self.stats["files_quarantined"] += 1
            logger.info(f"Файл {file_path} помещен в карантин")

        except Exception as e:
            logger.error(f"Ошибка помещения файла в карантин {file_path}: {e}")

    async def register_device(
        self, device_id: str, device_type: DeviceType
    ) -> bool:
        """Регистрация устройства"""
        try:
            # Получение информации об устройстве
            device_info = self._get_device_info(device_id, device_type)

            # Сохранение в базу данных
            await self._save_device(device_info)

            # Добавление в зарегистрированные устройства
            self.registered_devices[device_id] = device_info

            self.stats["devices_scanned"] += 1
            logger.info(f"Устройство {device_id} зарегистрировано")
            return True

        except Exception as e:
            logger.error(f"Ошибка регистрации устройства {device_id}: {e}")
            return False

    def _get_device_info(
        self, device_id: str, device_type: DeviceType
    ) -> DeviceInfo:
        """Получение информации об устройстве"""
        try:
            # Получение информации об ОС
            os_name = platform.system()
            os_version = platform.version()

            # Получение информации об оборудовании
            hardware_info = {
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "machine": platform.machine(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": (
                    psutil.disk_usage("/").total
                    if os_name != "Windows"
                    else psutil.disk_usage("C:").total
                ),
            }

            # Получение установленного ПО (упрощенная версия)
            installed_software = self._get_installed_software()

            # Получение запущенных процессов
            running_processes = [
                proc.info["name"]
                for proc in psutil.process_iter(["name"])
                if proc.info["name"]
            ]

            # Получение сетевых интерфейсов
            network_interfaces = list(psutil.net_if_addrs().keys())

            return DeviceInfo(
                device_id=device_id,
                device_type=device_type,
                os_name=os_name,
                os_version=os_version,
                hardware_info=hardware_info,
                installed_software=installed_software,
                running_processes=running_processes,
                network_interfaces=network_interfaces,
                security_status="registered",
                last_scan=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Ошибка получения информации об устройстве: {e}")
            return DeviceInfo(
                device_id=device_id,
                device_type=device_type,
                os_name="unknown",
                os_version="unknown",
                hardware_info={},
                installed_software=[],
                running_processes=[],
                network_interfaces=[],
                security_status="error",
                last_scan=datetime.utcnow(),
            )

    def _get_installed_software(self) -> List[str]:
        """Получение списка установленного ПО"""
        try:
            # Упрощенная версия получения установленного ПО
            # В реальной системе здесь будет полное сканирование
            return ["python", "nodejs", "git", "docker"]
        except Exception as e:
            logger.error(f"Ошибка получения установленного ПО: {e}")
            return []

    async def _save_device(self, device_info: DeviceInfo):
        """Сохранение устройства в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO devices
                (device_id, device_type, os_name, os_version, hardware_info,
                 installed_software, running_processes, network_interfaces,
                 security_status, last_scan, registration_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    device_info.device_id,
                    device_info.device_type.value,
                    device_info.os_name,
                    device_info.os_version,
                    json.dumps(device_info.hardware_info),
                    json.dumps(device_info.installed_software),
                    json.dumps(device_info.running_processes),
                    json.dumps(device_info.network_interfaces),
                    device_info.security_status,
                    device_info.last_scan.isoformat(),
                    datetime.utcnow().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Ошибка сохранения устройства: {e}")

    async def analyze_device(self, device_id: str) -> DeviceResponse:
        """Анализ устройства на предмет угроз"""
        try:
            if device_id not in self.registered_devices:
                return DeviceResponse(
                    action=DeviceAction.ALERT,
                    threat_level=ThreatLevel.HIGH,
                    message="Устройство не зарегистрировано",
                    blocked_files=[],
                    quarantined_files=[],
                    updated_software=[],
                    security_recommendations=["Зарегистрируйте устройство"],
                    device_metrics={},
                )

            # Сканирование устройства
            self._scan_device(device_id)

            # Определение уровня угрозы
            threat_level = self._calculate_device_threat_level(device_id)

            # Определение действия
            action = self._determine_device_action(threat_level)

            # Создание ответа
            response = DeviceResponse(
                action=action,
                threat_level=threat_level,
                message=self._generate_device_message(action, threat_level),
                blocked_files=self._get_blocked_files(device_id),
                quarantined_files=self._get_quarantined_files(device_id),
                updated_software=self._get_updated_software(device_id),
                security_recommendations=self._generate_device_recommendations(
                    device_id
                ),
                device_metrics=self._get_device_metrics(device_id),
            )

            return response

        except Exception as e:
            logger.error(f"Ошибка анализа устройства {device_id}: {e}")
            return DeviceResponse(
                action=DeviceAction.ALERT,
                threat_level=ThreatLevel.HIGH,
                message=f"Ошибка анализа: {str(e)}",
                blocked_files=[],
                quarantined_files=[],
                updated_software=[],
                security_recommendations=["Проверьте подключение устройства"],
                device_metrics={},
            )

    def _calculate_device_threat_level(self, device_id: str) -> ThreatLevel:
        """Расчет уровня угрозы устройства"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT threat_level FROM device_threats
                WHERE device_id = ? AND detection_time > "
                "datetime('now', '-1 hour')
                ORDER BY detection_time DESC
            """,
                (device_id,),
            )

            recent_threats = cursor.fetchall()
            conn.close()

            if not recent_threats:
                return ThreatLevel.LOW

            # Определение максимального уровня угрозы
            max_level = ThreatLevel.LOW
            for threat_level in recent_threats:
                level = ThreatLevel(threat_level[0])
                if level.value > max_level.value:
                    max_level = level

            return max_level

        except Exception as e:
            logger.error(f"Ошибка расчета уровня угрозы: {e}")
            return ThreatLevel.MEDIUM

    def _determine_device_action(
        self, threat_level: ThreatLevel
    ) -> DeviceAction:
        """Определение действия с устройством"""
        if threat_level == ThreatLevel.CRITICAL:
            return DeviceAction.RESTART
        elif threat_level == ThreatLevel.HIGH:
            return DeviceAction.QUARANTINE
        elif threat_level == ThreatLevel.MEDIUM:
            return DeviceAction.UPDATE
        else:
            return DeviceAction.ALLOW

    def _generate_device_message(
        self, action: DeviceAction, threat_level: ThreatLevel
    ) -> str:
        """Генерация сообщения для пользователя"""
        if action == DeviceAction.RESTART:
            return (
                f"🔄 Устройство требует перезагрузки: "
                f"{threat_level.value.upper()} уровень угрозы"
            )
        elif action == DeviceAction.QUARANTINE:
            return (
                f"⚠️ Устройство помещено в карантин: "
                f"{threat_level.value.upper()} уровень угрозы"
            )
        elif action == DeviceAction.UPDATE:
            return (
                f"📦 Требуется обновление: "
                f"{threat_level.value.upper()} уровень угрозы"
            )
        else:
            return "✅ Устройство безопасно"

    def _get_blocked_files(self, device_id: str) -> List[str]:
        """Получение заблокированных файлов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT file_path FROM device_threats
                WHERE device_id = ? AND threat_level IN ('high', 'critical')
            """,
                (device_id,),
            )

            blocked_files = [row[0] for row in cursor.fetchall()]
            conn.close()

            return blocked_files

        except Exception as e:
            logger.error(f"Ошибка получения заблокированных файлов: {e}")
            return []

    def _get_quarantined_files(self, device_id: str) -> List[str]:
        """Получение файлов в карантине"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT file_path FROM quarantined_files
                WHERE device_id = ?
            """,
                (device_id,),
            )

            quarantined_files = [row[0] for row in cursor.fetchall()]
            conn.close()

            return quarantined_files

        except Exception as e:
            logger.error(f"Ошибка получения файлов в карантине: {e}")
            return []

    def _get_updated_software(self, device_id: str) -> List[str]:
        """Получение обновленного ПО"""
        # Упрощенная версия
        return ["security_update_1", "antivirus_update_2"]

    def _generate_device_recommendations(self, device_id: str) -> List[str]:
        """Генерация рекомендаций по безопасности устройства"""
        recommendations = []

        if device_id in self.registered_devices:
            device = self.registered_devices[device_id]

            if device.os_name == "Windows":
                recommendations.append(
                    "Включите Windows Defender и обновите систему"
                )
            elif device.os_name == "Linux":
                recommendations.append("Обновите пакеты и включите firewall")
            elif device.os_name == "Darwin":  # macOS
                recommendations.append("Включите Gatekeeper и обновите macOS")

            recommendations.append("Установите антивирусное ПО")
            recommendations.append("Включите автоматические обновления")
            recommendations.append("Используйте сильные пароли")
            recommendations.append("Включите двухфакторную аутентификацию")

        return recommendations

    def _get_device_metrics(self, device_id: str) -> Dict[str, Any]:
        """Получение метрик устройства"""
        try:
            if device_id in self.registered_devices:
                device = self.registered_devices[device_id]
                return {
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": (
                        psutil.disk_usage("/").percent
                        if device.os_name != "Windows"
                        else psutil.disk_usage("C:").percent
                    ),
                    "network_io": psutil.net_io_counters()._asdict(),
                    "process_count": len(psutil.pids()),
                    "uptime": time.time() - psutil.boot_time(),
                }
            else:
                return {}
        except Exception as e:
            logger.error(f"Ошибка получения метрик устройства: {e}")
            return {}

    async def get_security_report(self) -> Dict[str, Any]:
        """Получение отчета по безопасности"""
        return {
            "bot_name": self.name,
            "status": "running" if self.running else "stopped",
            "stats": self.stats,
            "registered_devices": len(self.registered_devices),
            "config": self.config,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        return {
            "name": self.name,
            "running": self.running,
            "registered_devices": len(self.registered_devices),
            "stats": self.stats,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Пример использования
async def main():
    """Пример использования DeviceSecurityBot"""
    bot = DeviceSecurityBot("TestDeviceBot")

    # Запуск бота
    await bot.start()

    # Регистрация устройства
    device_registered = await bot.register_device(
        "device_123", DeviceType.DESKTOP
    )
    print(f"Устройство зарегистрировано: {device_registered}")

    # Анализ устройства
    response = await bot.analyze_device("device_123")
    print(f"Результат анализа: {response.message}")

    # Получение отчета
    report = await bot.get_security_report()
    print(f"Отчет: {report}")

    # Остановка бота
    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
