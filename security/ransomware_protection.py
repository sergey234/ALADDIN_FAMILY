"""
Система защиты от Ransomware для ALADDIN Security System
Автоматическое резервное копирование и мониторинг подозрительной активности
"""

import hashlib
import json
import logging
import os
import shutil
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set


# Кастомные исключения
class RansomwareProtectionError(Exception):
    """Базовое исключение для системы защиты от ransomware"""

    pass


class ConfigurationError(RansomwareProtectionError):
    """Ошибка конфигурации системы"""

    pass


class MonitoringError(RansomwareProtectionError):
    """Ошибка мониторинга файловой системы"""

    pass


class BackupError(RansomwareProtectionError):
    """Ошибка создания резервной копии"""

    pass


class ValidationError(RansomwareProtectionError):
    """Ошибка валидации данных"""

    pass


# Упрощенная реализация без внешних зависимостей
class FileSystemEventHandler:
    """Упрощенный обработчик событий файловой системы"""

    def __init__(
        self, protection_system: "RansomwareProtectionSystem"
    ) -> None:
        self.protection_system: "RansomwareProtectionSystem" = (
            protection_system
        )

    def on_modified(self, event: object) -> None:
        """Обработка изменения файла"""
        pass

    def on_created(self, event: object) -> None:
        """Обработка создания файла"""
        pass

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"FileSystemEventHandler(protection_system="
            f"{self.protection_system.name})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"FileSystemEventHandler(protection_system="
            f"{repr(self.protection_system)})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, FileSystemEventHandler):
            return False
        return self.protection_system is other.protection_system


class Observer:
    """Упрощенный наблюдатель файловой системы"""

    def __init__(self) -> None:
        self.handlers: List[tuple] = []

    def schedule(
        self,
        handler: FileSystemEventHandler,
        path: str,
        recursive: bool = True,
    ) -> None:
        """Планирование обработчика для мониторинга пути"""
        self.handlers.append((handler, path, recursive))

    def start(self) -> None:
        """Запуск наблюдения"""
        pass

    def stop(self) -> None:
        """Остановка наблюдения"""
        pass

    def join(self) -> None:
        """Ожидание завершения наблюдения"""
        pass

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return f"Observer(handlers_count={len(self.handlers)})"

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return f"Observer(handlers={len(self.handlers)})"

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, Observer):
            return False
        return self.handlers == other.handlers


@dataclass
class RansomwareSignature:
    """Сигнатура ransomware атаки"""

    name: str
    file_extensions: Set[str]
    suspicious_patterns: List[str]
    behavior_indicators: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"RansomwareSignature(name='{self.name}', "
            f"risk_level='{self.risk_level}')"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"RansomwareSignature(name='{self.name}', "
            f"file_extensions={self.file_extensions}, "
            f"risk_level='{self.risk_level}')"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, RansomwareSignature):
            return False
        return (
            self.name == other.name
            and self.file_extensions == other.file_extensions
            and self.risk_level == other.risk_level
        )

    def __lt__(self, other) -> bool:
        """Сравнение по уровню риска"""
        if not isinstance(other, RansomwareSignature):
            return NotImplemented
        risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        return risk_levels.get(self.risk_level, 0) < risk_levels.get(
            other.risk_level, 0
        )

    def __le__(self, other) -> bool:
        """Сравнение по уровню риска (меньше или равно)"""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        """Сравнение по уровню риска (больше)"""
        return not self.__le__(other)

    def __ge__(self, other) -> bool:
        """Сравнение по уровню риска (больше или равно)"""
        return not self.__lt__(other)


@dataclass
class BackupInfo:
    """Информация о резервной копии"""

    backup_id: str
    timestamp: datetime
    file_path: str
    file_hash: str
    file_size: int
    backup_location: str
    is_encrypted: bool = False

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"BackupInfo(id='{self.backup_id}', size={self.file_size} bytes)"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"BackupInfo(backup_id='{self.backup_id}', "
            f"file_path='{self.file_path}', "
            f"file_size={self.file_size})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, BackupInfo):
            return False
        return (
            self.backup_id == other.backup_id
            and self.file_path == other.file_path
            and self.file_hash == other.file_hash
        )

    def __lt__(self, other) -> bool:
        """Сравнение по времени создания"""
        if not isinstance(other, BackupInfo):
            return NotImplemented
        return self.timestamp < other.timestamp

    def __le__(self, other) -> bool:
        """Сравнение по времени создания (меньше или равно)"""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        """Сравнение по времени создания (больше)"""
        return not self.__le__(other)

    def __ge__(self, other) -> bool:
        """Сравнение по времени создания (больше или равно)"""
        return not self.__lt__(other)


@dataclass
class RansomwareAlert:
    """Алерт о подозрительной активности"""

    alert_id: str
    timestamp: datetime
    alert_type: str
    severity: str
    description: str
    affected_files: List[str]
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"RansomwareAlert(id='{self.alert_id}', "
            f"severity='{self.severity}')"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"RansomwareAlert(alert_id='{self.alert_id}', "
            f"alert_type='{self.alert_type}', "
            f"severity='{self.severity}')"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, RansomwareAlert):
            return False
        return (
            self.alert_id == other.alert_id
            and self.alert_type == other.alert_type
            and self.severity == other.severity
        )

    def __lt__(self, other) -> bool:
        """Сравнение по уровню серьезности"""
        if not isinstance(other, RansomwareAlert):
            return NotImplemented
        severity_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        return severity_levels.get(self.severity, 0) < severity_levels.get(
            other.severity, 0
        )

    def __le__(self, other) -> bool:
        """Сравнение по уровню серьезности (меньше или равно)"""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        """Сравнение по уровню серьезности (больше)"""
        return not self.__le__(other)

    def __ge__(self, other) -> bool:
        """Сравнение по уровню серьезности (больше или равно)"""
        return not self.__lt__(other)


class RansomwareProtectionSystem:
    """
    Система защиты от Ransomware
    Мониторинг, резервное копирование и блокировка подозрительной активности
    """

    def __init__(self, name: str = "RansomwareProtection") -> None:
        # Валидация входных параметров
        if not name or not isinstance(name, str):
            raise ValidationError("Имя системы должно быть непустой строкой")

        self.name: str = name
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.is_running: bool = False
        self.monitored_directories: Set[str] = set()
        self.backup_directory: str = "backups/ransomware_protection"
        self.alert_threshold: int = (
            10  # Количество подозрительных файлов для алерта
        )
        self.backup_interval: int = 300  # 5 минут
        self.max_backups: int = 100  # Максимальное количество резервных копий

        # Валидация конфигурации
        if self.alert_threshold <= 0:
            raise ConfigurationError(
                "Порог алертов должен быть положительным числом"
            )
        if self.backup_interval <= 0:
            raise ConfigurationError(
                "Интервал резервного копирования должен быть "
                "положительным числом"
            )
        if self.max_backups <= 0:
            raise ConfigurationError(
                "Максимальное количество резервных копий должно быть "
                "положительным числом"
            )

        # Сигнатуры ransomware
        self.ransomware_signatures: List[RansomwareSignature] = (
            self._load_ransomware_signatures()
        )

        # Мониторинг файлов
        self.file_hashes: Dict[str, str] = {}
        self.suspicious_files: Set[str] = set()
        self.encrypted_files: Set[str] = set()

        # Статистика
        self.stats: Dict[str, any] = {
            "files_monitored": 0,
            "backups_created": 0,
            "alerts_generated": 0,
            "threats_blocked": 0,
            "last_backup": None,
            "last_scan": None,
        }

        # Создаем директорию для резервных копий
        os.makedirs(self.backup_directory, exist_ok=True)

    @property
    def status_info(self) -> Dict[str, any]:
        """Получение информации о статусе системы"""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "monitored_directories_count": len(self.monitored_directories),
            "suspicious_files_count": len(self.suspicious_files),
            "backups_created": self.stats["backups_created"],
            "alerts_generated": self.stats["alerts_generated"],
        }

    @property
    def is_healthy(self) -> bool:
        """Проверка здоровья системы"""
        return (
            self.is_running
            and len(self.monitored_directories) > 0
            and self.stats["threats_blocked"] >= 0
        )

    @staticmethod
    def get_supported_extensions() -> Set[str]:
        """Получение поддерживаемых расширений файлов"""
        return {
            ".txt",
            ".doc",
            ".docx",
            ".pdf",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".jpg",
            ".png",
            ".gif",
            ".mp4",
            ".avi",
            ".zip",
            ".rar",
            ".7z",
        }

    @classmethod
    def create_with_custom_config(
        cls, name: str, backup_dir: str, alert_threshold: int
    ) -> "RansomwareProtectionSystem":
        """Создание системы с пользовательской конфигурацией"""
        # Валидация параметров
        if not backup_dir or not isinstance(backup_dir, str):
            raise ValidationError(
                "Директория резервных копий должна быть непустой строкой"
            )
        if not isinstance(alert_threshold, int) or alert_threshold <= 0:
            raise ValidationError(
                "Порог алертов должен быть положительным целым числом"
            )

        instance = cls(name)
        instance.backup_directory = backup_dir
        instance.alert_threshold = alert_threshold

        # Создаем директорию для резервных копий
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except OSError as e:
            raise ConfigurationError(
                f"Не удалось создать директорию {backup_dir}: {e}"
            )

        return instance

    def _load_ransomware_signatures(self) -> List[RansomwareSignature]:
        """Загрузка сигнатур ransomware"""
        signatures = [
            RansomwareSignature(
                name="WannaCry",
                file_extensions={".wncry", ".wannacry", ".locked"},
                suspicious_patterns=[
                    "WannaCry",
                    "Wanna Decrypt0r",
                    "Wanna Decryptor",
                ],
                behavior_indicators=[
                    "mass_file_encryption",
                    "bitcoin_demand",
                    "timer_display",
                ],
                risk_level="CRITICAL",
            ),
            RansomwareSignature(
                name="Locky",
                file_extensions={".locky", ".zepto", ".odin", ".thor"},
                suspicious_patterns=["Locky", "Zepto", "Odin", "Thor"],
                behavior_indicators=["mass_file_encryption", "ransom_note"],
                risk_level="HIGH",
            ),
            RansomwareSignature(
                name="CryptoLocker",
                file_extensions={".cryptolocker", ".encrypted"},
                suspicious_patterns=[
                    "CryptoLocker",
                    "Your files are encrypted",
                ],
                behavior_indicators=[
                    "mass_file_encryption",
                    "bitcoin_payment",
                ],
                risk_level="HIGH",
            ),
            RansomwareSignature(
                name="Cerber",
                file_extensions={".cerber", ".cerber3", ".cerber4"},
                suspicious_patterns=["Cerber", "Cerber3", "Cerber4"],
                behavior_indicators=["mass_file_encryption", "tor_payment"],
                risk_level="HIGH",
            ),
            RansomwareSignature(
                name="GenericRansomware",
                file_extensions={
                    ".encrypted",
                    ".locked",
                    ".crypted",
                    ".crypto",
                },
                suspicious_patterns=[
                    "encrypted",
                    "locked",
                    "crypted",
                    "crypto",
                ],
                behavior_indicators=["mass_file_encryption", "ransom_note"],
                risk_level="MEDIUM",
            ),
        ]
        return signatures

    def start_monitoring(self, directories: List[str]) -> bool:
        """Запуск мониторинга директорий"""
        try:
            self.monitored_directories.update(directories)
            self.is_running = True

            # Запускаем мониторинг файловой системы
            self._start_file_monitoring()

            # Запускаем автоматическое резервное копирование
            self._start_backup_scheduler()

            # Запускаем периодическое сканирование
            self._start_periodic_scanning()

            self.logger.info(
                f"Защита от ransomware запущена для "
                f"{len(directories)} директорий"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска защиты от ransomware: {e}")
            return False

    def _start_file_monitoring(self):
        """Запуск мониторинга файловой системы"""
        self.observer = Observer()

        for directory in self.monitored_directories:
            if os.path.exists(directory):
                event_handler = RansomwareFileHandler(self)
                self.observer.schedule(
                    event_handler, directory, recursive=True
                )

        self.observer.start()

    def _start_backup_scheduler(self):
        """Запуск планировщика резервного копирования"""

        def backup_scheduler():
            while self.is_running:
                try:
                    self._create_automatic_backup()
                    time.sleep(self.backup_interval)
                except Exception as e:
                    self.logger.error(
                        f"Ошибка в планировщике резервного копирования: {e}"
                    )
                    time.sleep(60)  # Ждем минуту при ошибке

        backup_thread = threading.Thread(target=backup_scheduler, daemon=True)
        backup_thread.start()

    def _start_periodic_scanning(self):
        """Запуск периодического сканирования"""

        def periodic_scanner():
            while self.is_running:
                try:
                    self._scan_for_ransomware()
                    time.sleep(60)  # Сканируем каждую минуту
                except Exception as e:
                    self.logger.error(
                        f"Ошибка в периодическом сканировании: {e}"
                    )
                    time.sleep(60)

        scan_thread = threading.Thread(target=periodic_scanner, daemon=True)
        scan_thread.start()

    def _create_automatic_backup(self) -> bool:
        """Создание автоматической резервной копии"""
        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"auto_backup_{backup_timestamp}"

            # Создаем резервную копию для каждой мониторируемой директории
            for directory in self.monitored_directories:
                if os.path.exists(directory):
                    backup_path = os.path.join(
                        self.backup_directory,
                        backup_id,
                        os.path.basename(directory),
                    )
                    os.makedirs(backup_path, exist_ok=True)

                    # Копируем файлы
                    shutil.copytree(directory, backup_path, dirs_exist_ok=True)

                    # Создаем манифест резервной копии
                    self._create_backup_manifest(backup_path, backup_id)

            self.stats["backups_created"] += 1
            self.stats["last_backup"] = datetime.now()

            # Очищаем старые резервные копии
            self._cleanup_old_backups()

            self.logger.info(
                f"Автоматическая резервная копия создана: {backup_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            return False

    def _create_backup_manifest(self, backup_path: str, backup_id: str):
        """Создание манифеста резервной копии"""
        manifest = {
            "backup_id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "backup_path": backup_path,
            "files": [],
            "total_size": 0,
        }

        total_size = 0
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_hash = self._calculate_file_hash(file_path)

                manifest["files"].append(
                    {
                        "path": file_path,
                        "size": file_size,
                        "hash": file_hash,
                        "timestamp": os.path.getmtime(file_path),
                    }
                )

                total_size += file_size

        manifest["total_size"] = total_size

        # Сохраняем манифест
        manifest_path = os.path.join(backup_path, "backup_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def _cleanup_old_backups(self):
        """Очистка старых резервных копий"""
        try:
            backup_dirs = [
                d
                for d in os.listdir(self.backup_directory)
                if os.path.isdir(os.path.join(self.backup_directory, d))
            ]

            if len(backup_dirs) > self.max_backups:
                # Сортируем по времени создания
                backup_dirs.sort(
                    key=lambda x: os.path.getctime(
                        os.path.join(self.backup_directory, x)
                    )
                )

                # Удаляем самые старые
                for old_backup in backup_dirs[: -self.max_backups]:
                    old_path = os.path.join(self.backup_directory, old_backup)
                    shutil.rmtree(old_path)
                    self.logger.info(
                        f"Удалена старая резервная копия: {old_backup}"
                    )

        except Exception as e:
            self.logger.error(f"Ошибка очистки старых резервных копий: {e}")

    def _scan_for_ransomware(self):
        """Сканирование на наличие ransomware"""
        try:
            suspicious_count = 0
            new_suspicious_files = set()

            for directory in self.monitored_directories:
                if not os.path.exists(directory):
                    continue

                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)

                        # Проверяем расширение файла
                        if self._is_suspicious_file(file_path):
                            new_suspicious_files.add(file_path)
                            suspicious_count += 1

                        # Проверяем содержимое файла
                        if self._contains_ransomware_patterns(file_path):
                            new_suspicious_files.add(file_path)
                            suspicious_count += 1

            # Обновляем список подозрительных файлов
            self.suspicious_files.update(new_suspicious_files)

            # Генерируем алерт при превышении порога
            if suspicious_count >= self.alert_threshold:
                self._generate_ransomware_alert(
                    suspicious_count, new_suspicious_files
                )

            self.stats["last_scan"] = datetime.now()

        except Exception as e:
            self.logger.error(f"Ошибка сканирования на ransomware: {e}")

    def _is_suspicious_file(self, file_path: str) -> bool:
        """Проверка файла на подозрительность по расширению"""
        file_ext = os.path.splitext(file_path)[1].lower()

        for signature in self.ransomware_signatures:
            if file_ext in signature.file_extensions:
                return True

        return False

    def _contains_ransomware_patterns(self, file_path: str) -> bool:
        """Проверка файла на наличие паттернов ransomware"""
        try:
            if (
                not os.path.exists(file_path)
                or os.path.getsize(file_path) > 10 * 1024 * 1024
            ):  # 10MB
                return False

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(1024)  # Читаем первые 1024 символа

                for signature in self.ransomware_signatures:
                    for pattern in signature.suspicious_patterns:
                        if pattern.lower() in content.lower():
                            return True

        except Exception:
            pass  # Игнорируем ошибки чтения файла

        return False

    def _generate_ransomware_alert(
        self, suspicious_count: int, suspicious_files: List[str]
    ):
        """Генерация алерта о ransomware"""
        alert = RansomwareAlert(
            alert_id=f"ransomware_alert_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type="RANSOMWARE_DETECTED",
            severity="CRITICAL",
            description=(
                f"Обнаружено {suspicious_count} подозрительных файлов, "
                f"возможна ransomware атака"
            ),
            affected_files=list(suspicious_files),
        )

        # Сохраняем алерт
        self._save_alert(alert)

        # Блокируем подозрительные файлы
        self._block_suspicious_files(suspicious_files)

        self.stats["alerts_generated"] += 1
        self.logger.critical(f"RANSOMWARE АЛЕРТ: {alert.description}")

    def _save_alert(self, alert: RansomwareAlert):
        """Сохранение алерта"""
        try:
            alert_file = os.path.join(
                self.backup_directory, f"alert_{alert.alert_id}.json"
            )

            alert_data = {
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "description": alert.description,
                "affected_files": alert.affected_files,
                "source_ip": alert.source_ip,
                "user_agent": alert.user_agent,
            }

            with open(alert_file, "w", encoding="utf-8") as f:
                json.dump(alert_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Ошибка сохранения алерта: {e}")

    def _block_suspicious_files(self, suspicious_files: List[str]):
        """Блокировка подозрительных файлов"""
        try:
            for file_path in suspicious_files:
                # Перемещаем файл в карантин
                quarantine_dir = os.path.join(
                    self.backup_directory, "quarantine"
                )
                os.makedirs(quarantine_dir, exist_ok=True)

                filename = os.path.basename(file_path)
                quarantine_path = os.path.join(
                    quarantine_dir,
                    f"quarantined_{int(time.time())}_{filename}",
                )

                shutil.move(file_path, quarantine_path)
                self.logger.warning(
                    f"Файл перемещен в карантин: {file_path} -> "
                    f"{quarantine_path}"
                )

        except Exception as e:
            self.logger.error(f"Ошибка блокировки подозрительных файлов: {e}")

    def _calculate_file_hash(self, file_path: str) -> str:
        """Вычисление хеша файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def get_status(self) -> Dict[str, any]:
        """Получение статуса системы защиты от ransomware"""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "monitored_directories": list(self.monitored_directories),
            "suspicious_files_count": len(self.suspicious_files),
            "encrypted_files_count": len(self.encrypted_files),
            "stats": self.stats,
            "backup_directory": self.backup_directory,
            "alert_threshold": self.alert_threshold,
            "max_backups": self.max_backups,
        }

    def stop(self):
        """Остановка системы защиты от ransomware"""
        self.is_running = False
        if hasattr(self, "observer"):
            self.observer.stop()
            self.observer.join()
        self.logger.info("Защита от ransomware остановлена")

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"RansomwareProtectionSystem(name='{self.name}', "
            f"running={self.is_running}, "
            f"monitored_dirs={len(self.monitored_directories)})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"RansomwareProtectionSystem(name='{self.name}', "
            f"is_running={self.is_running}, "
            f"backup_directory='{self.backup_directory}')"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, RansomwareProtectionSystem):
            return False
        return (
            self.name == other.name
            and self.backup_directory == other.backup_directory
        )

    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.logger.info(f"Вход в контекст системы защиты: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.logger.info(f"Выход из контекста системы защиты: {self.name}")
        if exc_type is not None:
            self.logger.error(
                f"Ошибка в контексте: {exc_type.__name__}: {exc_val}"
            )
        self.stop()
        return False  # Не подавляем исключения

    def __iter__(self):
        """Итерация по мониторируемым директориям"""
        return iter(self.monitored_directories)

    def __len__(self) -> int:
        """Количество мониторируемых директорий"""
        return len(self.monitored_directories)

    def __contains__(self, item: str) -> bool:
        """Проверка наличия директории в мониторинге"""
        return item in self.monitored_directories


class RansomwareFileHandler(FileSystemEventHandler):
    """Обработчик событий файловой системы для обнаружения ransomware"""

    def __init__(self, protection_system: RansomwareProtectionSystem) -> None:
        self.protection_system: RansomwareProtectionSystem = protection_system
        self.logger: logging.Logger = logging.getLogger(__name__)

    def on_modified(self, event: object) -> None:
        """Обработка изменения файла"""
        if not event.is_directory:
            self._check_file(event.src_path)

    def on_created(self, event: object) -> None:
        """Обработка создания файла"""
        if not event.is_directory:
            self._check_file(event.src_path)

    def _check_file(self, file_path: str) -> None:
        """Проверка файла на подозрительность"""
        try:
            if self.protection_system._is_suspicious_file(file_path):
                self.protection_system.suspicious_files.add(file_path)
                self.logger.warning(
                    f"Обнаружен подозрительный файл: {file_path}"
                )

                # Немедленно создаем резервную копию
                self.protection_system._create_automatic_backup()

        except Exception as e:
            self.logger.error(f"Ошибка проверки файла {file_path}: {e}")

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"RansomwareFileHandler(protection_system="
            f"{self.protection_system.name})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"RansomwareFileHandler(protection_system="
            f"{repr(self.protection_system)})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение объектов на равенство"""
        if not isinstance(other, RansomwareFileHandler):
            return False
        return self.protection_system is other.protection_system


# Пример использования
if __name__ == "__main__":
    # Создаем систему защиты от ransomware
    ransomware_protection = RansomwareProtectionSystem()

    # Запускаем мониторинг
    directories_to_monitor = [
        "ALADDIN_NEW/security",
        "ALADDIN_NEW/core",
        "ALADDIN_NEW/tests",
    ]

    if ransomware_protection.start_monitoring(directories_to_monitor):
        print("✅ Защита от ransomware запущена")

        # Получаем статус
        status = ransomware_protection.get_status()
        print(f"📊 Статус: {status['is_running']}")
        print(
            f"📁 Мониторируемые директории: "
            f"{len(status['monitored_directories'])}"
        )
        print(f"⚠️ Подозрительные файлы: {status['suspicious_files_count']}")

        # Останавливаем через 60 секунд (для демонстрации)
        time.sleep(60)
        ransomware_protection.stop()
        print("🛑 Защита от ransomware остановлена")
    else:
        print("❌ Ошибка запуска защиты от ransomware")
