# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Configuration Module
Модуль управления конфигурацией для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import configparser
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .base import ComponentStatus, CoreBase


class ConfigurationManager(CoreBase):
    """Менеджер конфигурации для системы ALADDIN"""

    def __init__(
        self,
        name: str = "ConfigurationManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Конфигурация менеджера
        self.config_dir = config.get(
            "config_dir", "config") if config else "config"
        self.config_file = config.get(
            "config_file",
            "aladdin_config.json") if config else "aladdin_config.json"
        self.backup_config = config.get(
            "backup_config", True) if config else True
        self.auto_reload = config.get("auto_reload", True) if config else True

        # Хранилище конфигураций
        self.configurations: Dict[str, Any] = {}
        self.config_history: List[Dict[str, Any]] = []
        self.config_validators: Dict[str, Any] = {}
        self.config_watchers: Dict[str, Any] = {}

        # Статистика
        self.config_loads = 0
        self.config_saves = 0
        self.config_errors = 0

    def initialize(self) -> bool:
        """Инициализация менеджера конфигурации"""
        try:
            self.log_activity(
                f"Инициализация менеджера конфигурации {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Создание директории конфигураций
            self._create_config_directory()

            # Загрузка базовой конфигурации
            if not self._load_base_configuration():
                raise Exception("Ошибка загрузки базовой конфигурации")

            # Регистрация валидаторов
            self._register_validators()

            # Инициализация наблюдателей
            if self.auto_reload:
                self._setup_config_watchers()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер конфигурации {self.name} успешно инициализирован")
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера конфигурации {self.name}: {e}",
                "error")
            return False

    def _create_config_directory(self):
        """Создание директории конфигураций"""
        try:
            Path(self.config_dir).mkdir(parents=True, exist_ok=True)
            self.log_activity(
                f"Директория конфигураций создана: {self.config_dir}")
        except Exception as e:
            self.log_activity(
                f"Ошибка создания директории конфигураций: {e}", "error")

    def _load_base_configuration(self) -> bool:
        """Загрузка базовой конфигурации"""
        try:
            config_path = os.path.join(self.config_dir, self.config_file)

            if os.path.exists(config_path):
                # Загружаем существующую конфигурацию
                self.load_configuration(config_path)
                self.log_activity(
                    f"Загружена существующая конфигурация: {config_path}")
            else:
                # Создаем базовую конфигурацию
                self._create_default_configuration()
                self.save_configuration(config_path)
                self.log_activity(
                    f"Создана базовая конфигурация: {config_path}")

            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка загрузки базовой конфигурации: {e}", "error")
            return False

    def _create_default_configuration(self):
        """Создание базовой конфигурации по умолчанию"""
        default_config = {
            "system": {
                "name": "ALADDIN Security System",
                "version": "1.0.0",
                "environment": "development",
                "debug": True,
                "log_level": "INFO",
            },
            "security": {
                "encryption_enabled": True,
                "encryption_algorithm": "AES-256",
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "password_min_length": 8,
                "require_mfa": False,
            },
            "database": {
                "type": "sqlite",
                "path": "data/aladdin.db",
                "backup_enabled": True,
                "backup_interval": 24,
                "max_connections": 10,
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "file_path": "logs/aladdin.log",
                "max_file_size": 10485760,
                "backup_count": 5,
            },
            "api": {
                "enabled": True,
                "host": "localhost",
                "port": 8000,
                "ssl_enabled": False,
                "rate_limit": 100,
                "timeout": 30,
            },
            "ai": {
                "enabled": True,
                "model_path": "models/",
                "confidence_threshold": 0.8,
                "max_processing_time": 30,
                "batch_size": 100,
            },
            "monitoring": {
                "enabled": True,
                "metrics_interval": 60,
                "health_check_interval": 30,
                "alert_enabled": True,
                "alert_channels": ["email", "webhook"],
            },
        }

        self.configurations = default_config
        self.log_activity("Создана базовая конфигурация по умолчанию")

    def _register_validators(self):
        """Регистрация валидаторов конфигурации"""
        self.config_validators = {
            "system": self._validate_system_config,
            "security": self._validate_security_config,
            "database": self._validate_database_config,
            "logging": self._validate_logging_config,
            "api": self._validate_api_config,
            "ai": self._validate_ai_config,
            "monitoring": self._validate_monitoring_config,
        }
        self.log_activity("Валидаторы конфигурации зарегистрированы")

    def _setup_config_watchers(self):
        """Настройка наблюдателей за конфигурацией"""
        # Здесь будет логика наблюдения за файлами конфигурации
        self.log_activity("Наблюдатели за конфигурацией настроены")

    def load_configuration(self, config_path: str) -> bool:
        """
        Загрузка конфигурации из файла

        Args:
            config_path: Путь к файлу конфигурации

        Returns:
            bool: True если конфигурация загружена успешно
        """
        try:
            if not os.path.exists(config_path):
                self.log_activity(
                    f"Файл конфигурации не найден: {config_path}", "error")
                return False

            file_extension = Path(config_path).suffix.lower()

            with open(config_path, "r", encoding="utf-8") as file:
                if file_extension == ".json":
                    config_data = json.load(file)
                elif file_extension in [".yml", ".yaml"]:
                    config_data = yaml.safe_load(file)
                elif file_extension == ".ini":
                    config_data = self._load_ini_config(file)
                else:
                    self.log_activity(
                        f"Неподдерживаемый формат файла: {file_extension}", "error")
                    return False

            # Валидация конфигурации
            if not self._validate_configuration(config_data):
                self.log_activity("Конфигурация не прошла валидацию", "error")
                return False

            # Обновление конфигурации
            self.configurations.update(config_data)

            # Сохранение в историю
            self._save_to_history(config_data, f"Загружено из {config_path}")

            self.config_loads += 1
            self.log_activity(f"Конфигурация загружена из: {config_path}")
            return True

        except Exception as e:
            self.config_errors += 1
            self.log_activity(f"Ошибка загрузки конфигурации: {e}", "error")
            return False

    def _load_ini_config(self, file) -> Dict[str, Any]:
        """Загрузка INI конфигурации"""
        config = configparser.ConfigParser()
        config.read_file(file)

        result = {}
        for section in config.sections():
            result[section] = dict(config[section])

        return result

    def save_configuration(self, config_path: str) -> bool:
        """
        Сохранение конфигурации в файл

        Args:
            config_path: Путь к файлу конфигурации

        Returns:
            bool: True если конфигурация сохранена успешно
        """
        try:
            # Создание резервной копии
            if self.backup_config and os.path.exists(config_path):
                self._create_backup(config_path)

            file_extension = Path(config_path).suffix.lower()

            with open(config_path, "w", encoding="utf-8") as file:
                if file_extension == ".json":
                    json.dump(
                        self.configurations,
                        file,
                        indent=2,
                        ensure_ascii=False)
                elif file_extension in [".yml", ".yaml"]:
                    yaml.dump(
                        self.configurations,
                        file,
                        default_flow_style=False,
                        allow_unicode=True,
                    )
                elif file_extension == ".ini":
                    self._save_ini_config(file)
                else:
                    self.log_activity(
                        f"Неподдерживаемый формат файла: {file_extension}", "error")
                    return False

            self.config_saves += 1
            self.log_activity(f"Конфигурация сохранена в: {config_path}")
            return True

        except Exception as e:
            self.config_errors += 1
            self.log_activity(f"Ошибка сохранения конфигурации: {e}", "error")
            return False

    def _save_ini_config(self, file):
        """Сохранение INI конфигурации"""
        config = configparser.ConfigParser()

        for section, values in self.configurations.items():
            config[section] = values

        config.write(file)

    def _create_backup(self, config_path: str):
        """Создание резервной копии конфигурации"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{config_path}.backup_{timestamp}"

            import shutil

            shutil.copy2(config_path, backup_path)

            self.log_activity(f"Создана резервная копия: {backup_path}")
        except Exception as e:
            self.log_activity(f"Ошибка создания резервной копии: {e}", "error")

    def get_config(
            self,
            section: str,
            key: Optional[str] = None,
            default: Optional[Any] = None) -> Any:
        """
        Получение значения конфигурации

        Args:
            section: Секция конфигурации
            key: Ключ конфигурации (если None, возвращается вся секция)
            default: Значение по умолчанию

        Returns:
            Any: Значение конфигурации
        """
        try:
            if section not in self.configurations:
                return default

            if key is None:
                return self.configurations[section]

            return self.configurations[section].get(key, default)

        except Exception as e:
            self.log_activity(f"Ошибка получения конфигурации: {e}", "error")
            return default

    def set_config(self, section: str, key: str, value: Any) -> bool:
        """
        Установка значения конфигурации

        Args:
            section: Секция конфигурации
            key: Ключ конфигурации
            value: Значение конфигурации

        Returns:
            bool: True если значение установлено успешно
        """
        try:
            # Создание секции если не существует
            if section not in self.configurations:
                self.configurations[section] = {}

            # Валидация значения
            if not self._validate_config_value(section, key, value):
                self.log_activity(
                    f"Значение не прошло валидацию: {section}.{key}", "error")
                return False

            # Установка значения
            self.configurations[section][key] = value

            # Сохранение в историю
            self._save_to_history({section: {key: value}},
                                  f"Установлено {section}.{key}")

            self.log_activity(
                f"Установлена конфигурация: {section}.{key} = {value}")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка установки конфигурации: {e}", "error")
            return False

    def _validate_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Валидация конфигурации"""
        try:
            for section, validator in self.config_validators.items():
                if section in config_data:
                    if not validator(config_data[section]):
                        return False
            return True
        except Exception as e:
            self.log_activity(f"Ошибка валидации конфигурации: {e}", "error")
            return False

    def _validate_config_value(
            self,
            section: str,
            key: str,
            value: Any) -> bool:
        """Валидация значения конфигурации"""
        try:
            if section in self.config_validators:
                # Создаем временную секцию для валидации
                temp_section = self.configurations.get(section, {}).copy()
                temp_section[key] = value
                return self.config_validators[section](temp_section)
            return True
        except Exception as e:
            self.log_activity(f"Ошибка валидации значения: {e}", "error")
            return False

    def _validate_system_config(self, config: Dict[str, Any]) -> bool:
        """Валидация системной конфигурации"""
        required_keys = ["name", "version", "environment"]
        return all(key in config for key in required_keys)

    def _validate_security_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации безопасности"""
        if "session_timeout" in config:
            if not isinstance(
                    config["session_timeout"],
                    int) or config["session_timeout"] <= 0:
                return False
        if "max_login_attempts" in config:
            if not isinstance(
                    config["max_login_attempts"],
                    int) or config["max_login_attempts"] <= 0:
                return False
        return True

    def _validate_database_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации базы данных"""
        required_keys = ["type", "path"]
        return all(key in config for key in required_keys)

    def _validate_logging_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации логирования"""
        if "level" in config:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if config["level"] not in valid_levels:
                return False
        return True

    def _validate_api_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации API"""
        if "port" in config:
            if not isinstance(config["port"], int) or config["port"] <= 0:
                return False
        return True

    def _validate_ai_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации AI"""
        if "confidence_threshold" in config:
            if not isinstance(config["confidence_threshold"], (int, float)):
                return False
            if config["confidence_threshold"] < 0 or config["confidence_threshold"] > 1:
                return False
        return True

    def _validate_monitoring_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации мониторинга"""
        if "metrics_interval" in config:
            if not isinstance(
                    config["metrics_interval"],
                    int) or config["metrics_interval"] <= 0:
                return False
        return True

    def _save_to_history(self, config_data: Dict[str, Any], description: str):
        """Сохранение в историю изменений"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "config_data": config_data,
        }
        self.config_history.append(history_entry)

        # Ограничиваем размер истории
        if len(self.config_history) > 100:
            self.config_history.pop(0)

    def get_config_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получение истории изменений конфигурации

        Args:
            limit: Максимальное количество записей

        Returns:
            List[Dict[str, Any]]: История изменений
        """
        return self.config_history[-limit:] if limit > 0 else self.config_history

    def export_configuration(self, format_type: str = "json") -> str:
        """
        Экспорт конфигурации

        Args:
            format_type: Тип формата (json, yaml, ini)

        Returns:
            str: Конфигурация в указанном формате
        """
        try:
            if format_type == "json":
                return json.dumps(
                    self.configurations,
                    indent=2,
                    ensure_ascii=False)
            elif format_type == "yaml":
                return yaml.dump(
                    self.configurations,
                    default_flow_style=False,
                    allow_unicode=True)
            elif format_type == "ini":
                return self._export_ini_config()
            else:
                raise ValueError(f"Неподдерживаемый формат: {format_type}")

        except Exception as e:
            self.log_activity(f"Ошибка экспорта конфигурации: {e}", "error")
            return ""

    def _export_ini_config(self) -> str:
        """Экспорт конфигурации в INI формат"""
        config = configparser.ConfigParser()

        for section, values in self.configurations.items():
            config[section] = values

        from io import StringIO

        output = StringIO()
        config.write(output)
        return output.getvalue()

    def get_configuration_stats(self) -> Dict[str, Any]:
        """
        Получение статистики конфигурации

        Returns:
            Dict[str, Any]: Статистика конфигурации
        """
        return {
            "total_sections": len(
                self.configurations),
            "total_keys": sum(
                len(section) for section in self.configurations.values()),
            "config_loads": self.config_loads,
            "config_saves": self.config_saves,
            "config_errors": self.config_errors,
            "history_entries": len(
                self.config_history),
            "validators_registered": len(
                self.config_validators),
            "watchers_active": len(
                self.config_watchers),
        }

    def start(self) -> bool:
        """Запуск менеджера конфигурации"""
        try:
            self.log_activity(f"Запуск менеджера конфигурации {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер конфигурации {self.name} успешно запущен")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера конфигурации {self.name}: {e}",
                "error")
            return False

    def stop(self) -> bool:
        """Остановка менеджера конфигурации"""
        try:
            self.log_activity(f"Остановка менеджера конфигурации {self.name}")

            # Остановка наблюдателей
            self.config_watchers.clear()

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер конфигурации {self.name} успешно остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера конфигурации {self.name}: {e}",
                "error")
            return False
