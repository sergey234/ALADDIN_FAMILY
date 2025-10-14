# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Protected Data Manager
Система защиты критических данных и кода проекта

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import fnmatch
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.base import SecurityBase


class ProtectionLevel(Enum):
    """Уровни защиты данных"""

    ABSOLUTE = "absolute"  # Абсолютная защита - НИКОГДА не удалять
    CRITICAL = "critical"  # Критическая защита - только архивирование
    HIGH = "high"  # Высокая защита - долгое хранение
    MEDIUM = "medium"  # Средняя защита - обычное хранение
    LOW = "low"  # Низкая защита - краткое хранение


class ProtectedDataManager(SecurityBase):
    """Менеджер защищенных данных"""

    def __init__(
        self,
        name: str = "ProtectedDataManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Защищенные директории и файлы
        self.protected_directories = set()
        self.protected_files = set()
        self.protected_patterns = set()

        # Инициализация защиты
        self._initialize_protection()

        # Статистика защиты
        self.protection_stats = {
            "protected_directories": 0,
            "protected_files": 0,
            "protected_patterns": 0,
            "last_scan": None,
        }

    def _initialize_protection(self):
        """Инициализация системы защиты"""
        try:
            # 1. ЗАЩИТА ВСЕХ ФАЙЛОВ ПРОЕКТА ALADDIN
            self._protect_project_files()

            # 2. ЗАЩИТА КРИТИЧЕСКИХ ДАННЫХ БЕЗОПАСНОСТИ
            self._protect_security_data()

            # 3. ЗАЩИТА КОНФИГУРАЦИОННЫХ ФАЙЛОВ
            self._protect_config_files()

            # 4. ЗАЩИТА ДОКУМЕНТАЦИИ
            self._protect_documentation()

            self.log_activity("Система защиты критических данных инициализирована")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации защиты: {e}", "error")

    def _protect_project_files(self):
        """Защита всех файлов проекта ALADDIN"""

        # АБСОЛЮТНАЯ ЗАЩИТА - НИКОГДА НЕ УДАЛЯТЬ
        absolute_protection = [
            # Основные директории проекта
            "core/",
            "security/",
            "config/",
            "tests/",
            "docs/",
            # Все Python файлы
            "*.py",
            "*.pyc",
            "*.pyo",
            # Конфигурационные файлы
            "*.json",
            "*.yaml",
            "*.yml",
            "*.ini",
            "*.cfg",
            "*.conf",
            # Документация
            "*.md",
            "*.txt",
            "*.rst",
            # Планы и отчеты
            "*PLAN*.md",
            "*REPORT*.md",
            "*SECURITY*.md",
            # Специфичные файлы проекта
            "ALADDIN_*.md",
            "SECURE_*.md",
            "FINAL_*.md",
        ]

        for pattern in absolute_protection:
            self.protected_patterns.add((pattern, ProtectionLevel.ABSOLUTE))

        self.log_activity(f"Защищено {len(absolute_protection)} паттернов файлов проекта")

    def _protect_security_data(self):
        """Защита критических данных безопасности"""

        # КРИТИЧЕСКАЯ ЗАЩИТА - только архивирование
        critical_security_data = [
            # Данные о попытках взлома
            "*hack_attempt*",
            "*security_breach*",
            "*unauthorized_access*",
            # Данные об удалении правил
            "*rule_deletion*",
            "*monitoring_rule*",
            "*security_rule*",
            # Критические инциденты
            "*critical_incident*",
            "*security_alert*",
            "*threat_detected*",
            # Данные о блокировках
            "*blocked_operation*",
            "*access_denied*",
            "*permission_denied*",
        ]

        for pattern in critical_security_data:
            self.protected_patterns.add((pattern, ProtectionLevel.CRITICAL))

        self.log_activity(f"Защищено {len(critical_security_data)} типов критических данных безопасности")

    def _protect_config_files(self):
        """Защита конфигурационных файлов"""

        # ВЫСОКАЯ ЗАЩИТА - долгое хранение
        config_files = [
            # Конфигурации безопасности
            "*security_config*",
            "*access_control*",
            "*user_roles*",
            # Системные конфигурации
            "*system_config*",
            "*database_config*",
            "*network_config*",
            # Настройки мониторинга
            "*monitoring_config*",
            "*alert_config*",
            "*log_config*",
        ]

        for pattern in config_files:
            self.protected_patterns.add((pattern, ProtectionLevel.HIGH))

        self.log_activity(f"Защищено {len(config_files)} типов конфигурационных файлов")

    def _protect_documentation(self):
        """Защита документации"""

        # ВЫСОКАЯ ЗАЩИТА - долгое хранение
        documentation_files = [
            # Документация проекта
            "*README*",
            "*INSTALL*",
            "*SETUP*",
            "*GUIDE*",
            # Документация безопасности
            "*SECURITY*",
            "*AUDIT*",
            "*COMPLIANCE*",
            # Техническая документация
            "*API*",
            "*ARCHITECTURE*",
            "*DESIGN*",
        ]

        for pattern in documentation_files:
            self.protected_patterns.add((pattern, ProtectionLevel.HIGH))

        self.log_activity(f"Защищено {len(documentation_files)} типов документации")

    def is_protected(self, file_path: str) -> Optional[ProtectionLevel]:
        """
        Проверка, защищен ли файл

        Args:
            file_path: Путь к файлу

        Returns:
            Optional[ProtectionLevel]: Уровень защиты или None
        """
        try:
            # Нормализация пути
            normalized_path = os.path.normpath(file_path)
            filename = os.path.basename(normalized_path)

            # Проверка защищенных директорий
            for protected_dir in self.protected_directories:
                if normalized_path.startswith(protected_dir):
                    return ProtectionLevel.ABSOLUTE

            # Проверка защищенных файлов
            if normalized_path in self.protected_files:
                return ProtectionLevel.ABSOLUTE

            # Проверка паттернов
            for pattern, protection_level in self.protected_patterns:
                if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(normalized_path, pattern):
                    return protection_level

            return None

        except Exception as e:
            self.log_activity(f"Ошибка проверки защиты файла {file_path}: {e}", "error")
            return ProtectionLevel.ABSOLUTE  # В случае ошибки - защищаем

    def can_delete(self, file_path: str) -> bool:
        """
        Проверка, можно ли удалить файл

        Args:
            file_path: Путь к файлу

        Returns:
            bool: True если можно удалить, False если защищен
        """
        protection_level = self.is_protected(file_path)

        if protection_level is None:
            return True  # Не защищен - можно удалить

        if protection_level == ProtectionLevel.ABSOLUTE:
            # Абсолютная защита - НИКОГДА не удалять
            self.log_activity(
                f"ФАЙЛ ЗАЩИЩЕН ОТ УДАЛЕНИЯ: {file_path} (уровень: {protection_level.value})",
                "warning",
            )
            return False

        # Для других уровней - можно удалять по политике
        return True

    def can_archive(self, file_path: str) -> bool:
        """
        Проверка, можно ли архивировать файл

        Args:
            file_path: Путь к файлу

        Returns:
            bool: True если можно архивировать, False если нельзя
        """
        protection_level = self.is_protected(file_path)

        if protection_level is None:
            return True  # Не защищен - можно архивировать

        if protection_level in [ProtectionLevel.ABSOLUTE, ProtectionLevel.CRITICAL]:
            # Абсолютная и критическая защита - можно архивировать
            return True

        return True  # Остальные уровни - можно архивировать

    def add_protection(self, file_path: str, protection_level: ProtectionLevel):
        """
        Добавление защиты для файла

        Args:
            file_path: Путь к файлу
            protection_level: Уровень защиты
        """
        try:
            if os.path.isdir(file_path):
                self.protected_directories.add(file_path)
                self.log_activity(f"Защищена директория: {file_path} (уровень: {protection_level.value})")
            else:
                self.protected_files.add(file_path)
                self.log_activity(f"Защищен файл: {file_path} (уровень: {protection_level.value})")

        except Exception as e:
            self.log_activity(f"Ошибка добавления защиты для {file_path}: {e}", "error")

    def remove_protection(self, file_path: str) -> bool:
        """
        Удаление защиты с файла (ОСТОРОЖНО!)

        Args:
            file_path: Путь к файлу

        Returns:
            bool: Успешность удаления защиты
        """
        try:
            # Проверка, что это не критический файл проекта
            if self._is_critical_project_file(file_path):
                self.log_activity(
                    f"НЕВОЗМОЖНО УДАЛИТЬ ЗАЩИТУ: {file_path} - критический файл проекта",
                    "error",
                )
                return False

            removed = False
            if file_path in self.protected_directories:
                self.protected_directories.remove(file_path)
                removed = True
            if file_path in self.protected_files:
                self.protected_files.remove(file_path)
                removed = True

            if removed:
                self.log_activity(f"Защита удалена: {file_path}", "warning")

            return removed

        except Exception as e:
            self.log_activity(f"Ошибка удаления защиты для {file_path}: {e}", "error")
            return False

    def _is_critical_project_file(self, file_path: str) -> bool:
        """Проверка, является ли файл критическим для проекта"""
        critical_patterns = [
            "*.py",
            "ALADDIN_*",
            "*SECURITY*",
            "*PLAN*",
            "core/",
            "security/",
            "config/",
        ]

        for pattern in critical_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True

        return False

    def scan_and_protect(self, directory: str = ".") -> Dict[str, Any]:
        """
        Сканирование и автоматическая защита файлов проекта

        Args:
            directory: Директория для сканирования

        Returns:
            Dict[str, Any]: Результат сканирования
        """
        try:
            scan_results = {
                "scanned_files": 0,
                "protected_files": 0,
                "already_protected": 0,
                "errors": 0,
                "start_time": datetime.now().isoformat(),
            }

            for root, dirs, files in os.walk(directory):
                # Пропускаем служебные директории
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]

                for file in files:
                    file_path = os.path.join(root, file)
                    scan_results["scanned_files"] += 1

                    # Проверка, нужно ли защитить
                    if self._should_auto_protect(file_path):
                        if self.is_protected(file_path) is None:
                            self.add_protection(file_path, ProtectionLevel.ABSOLUTE)
                            scan_results["protected_files"] += 1
                        else:
                            scan_results["already_protected"] += 1

            scan_results["end_time"] = datetime.now().isoformat()
            scan_results["duration_seconds"] = (
                datetime.fromisoformat(scan_results["end_time"]) - datetime.fromisoformat(scan_results["start_time"])
            ).total_seconds()

            self.log_activity(f"Сканирование завершено: {scan_results}")
            return scan_results

        except Exception as e:
            self.log_activity(f"Ошибка сканирования: {e}", "error")
            return {"error": str(e)}

    def _should_auto_protect(self, file_path: str) -> bool:
        """Определение, нужно ли автоматически защитить файл"""
        auto_protect_patterns = [
            "*.py",
            "*.md",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.ini",
            "*.cfg",
            "ALADDIN_*",
            "*SECURITY*",
            "*PLAN*",
            "*REPORT*",
        ]

        for pattern in auto_protect_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True

        return False

    def get_protection_statistics(self) -> Dict[str, Any]:
        """Получение статистики защиты"""
        return {
            "protected_directories": len(self.protected_directories),
            "protected_files": len(self.protected_files),
            "protected_patterns": len(self.protected_patterns),
            "protection_levels": {
                level.value: sum(1 for _, pl in self.protected_patterns if pl == level) for level in ProtectionLevel
            },
            "last_scan": self.protection_stats["last_scan"],
        }

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы защиты"""
        return {
            "name": self.name,
            "status": self.status.value,
            "protection_statistics": self.get_protection_statistics(),
            "protection_enabled": True,
            "auto_protection": True,
        }


# Глобальный экземпляр системы защиты
PROTECTED_DATA_MANAGER = ProtectedDataManager()
