# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Logging Module
Модуль логирования для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import hashlib
import json
import logging
import logging.handlers
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import ComponentStatus, CoreBase


class LogLevel(Enum):
    """Уровни логирования"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry:
    """Класс для представления записи лога"""

    def __init__(
        self,
        level: str,
        message: str,
        component: str,
        timestamp: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        self.level = level
        self.message = message
        self.component = component
        self.timestamp = timestamp or datetime.now()
        self.extra_data = extra_data or {}
        self.id = self._generate_log_id()

    def _generate_log_id(self) -> str:
        """Генерация уникального ID записи лога"""
        data = f"{self.level}{self.component}{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "level": self.level,
            "message": self.message,
            "component": self.component,
            "timestamp": self.timestamp.isoformat(),
            "extra_data": self.extra_data,
        }

    def to_json(self) -> str:
        """Преобразование в JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class LoggingManager(CoreBase):
    """Менеджер логирования для системы ALADDIN"""

    def __init__(self, name: str = "LoggingManager",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация логирования
        self.log_dir = config.get("log_dir", "logs") if config else "logs"
        self.log_file = config.get("log_file",
                                   "aladdin.log") if config else "aladdin.log"
        self.max_file_size = config.get(
            "max_file_size", 10485760) if config else 10485760  # 10MB
        self.backup_count = config.get("backup_count", 5) if config else 5
        self.log_level = config.get("log_level", "INFO") if config else "INFO"
        self.enable_console = config.get(
            "enable_console", True) if config else True
        self.enable_file = config.get("enable_file", True) if config else True

        # Хранилище логов
        self.log_entries: List[LogEntry] = []
        self.log_filters: Dict[str, Any] = {}
        self.log_formatters: Dict[str, Any] = {}
        self.log_handlers: Dict[str, Any] = {}

        # Статистика
        self.total_logs = 0
        self.logs_by_level: Dict[str, int] = {}
        self.logs_by_component: Dict[str, int] = {}
        self.log_errors = 0

    def initialize(self) -> bool:
        """Инициализация менеджера логирования"""
        try:
            self.log_activity(
                f"Инициализация менеджера логирования {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Создание директории логов
            self._create_log_directory()

            # Настройка логирования
            if not self._setup_logging():
                raise Exception("Ошибка настройки логирования")

            # Регистрация форматтеров
            self._register_formatters()

            # Регистрация фильтров
            self._register_filters()

            # Инициализация статистики
            self._initialize_statistics()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер логирования {self.name} успешно инициализирован")
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера логирования {self.name}: {e}",
                "error")
            return False

    def _create_log_directory(self):
        """Создание директории логов"""
        try:
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            self.log_activity(f"Директория логов создана: {self.log_dir}")
        except Exception as e:
            self.log_activity(
                f"Ошибка создания директории логов: {e}", "error")

    def _setup_logging(self) -> bool:
        """Настройка логирования"""
        try:
            # Настройка корневого логгера
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, self.log_level))

            # Очистка существующих обработчиков
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Создание форматтера
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

            # Консольный обработчик
            if self.enable_console:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(getattr(logging, self.log_level))
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)
                self.log_handlers["console"] = console_handler

            # Файловый обработчик
            if self.enable_file:
                log_path = os.path.join(self.log_dir, self.log_file)
                file_handler = logging.handlers.RotatingFileHandler(
                    log_path,
                    maxBytes=self.max_file_size,
                    backupCount=self.backup_count,
                    encoding="utf-8",
                )
                file_handler.setLevel(getattr(logging, self.log_level))
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                self.log_handlers["file"] = file_handler

            self.log_activity("Логирование настроено")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка настройки логирования: {e}", "error")
            return False

    def _register_formatters(self):
        """Регистрация форматтеров логов"""
        self.log_formatters = {
            "default": logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "detailed": logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(funcName)s:%(lineno)d - %(message)s"),
            "json": self._json_formatter,
            "simple": logging.Formatter("%(levelname)s - %(message)s"),
        }
        self.log_activity("Форматтеры логов зарегистрированы")

    def _json_formatter(self, record):
        """JSON форматтер для логов"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False)

    def _register_filters(self):
        """Регистрация фильтров логов"""
        self.log_filters = {
            "security_only": self._security_filter,
            "error_only": self._error_filter,
            "component_filter": self._component_filter,
        }
        self.log_activity("Фильтры логов зарегистрированы")

    def _security_filter(self, record):
        """Фильтр для логов безопасности"""
        return "security" in record.name.lower() or "auth" in record.name.lower()

    def _error_filter(self, record):
        """Фильтр для логов ошибок"""
        return record.levelno >= logging.ERROR

    def _component_filter(self, record):
        """Фильтр по компонентам"""
        # Здесь будет логика фильтрации по компонентам
        return True

    def _initialize_statistics(self):
        """Инициализация статистики"""
        self.logs_by_level = {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0,
        }
        self.logs_by_component = {}

    def log(
        self,
        level: str,
        message: str,
        component: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Запись лога

        Args:
            level: Уровень логирования
            message: Сообщение лога
            component: Компонент системы
            extra_data: Дополнительные данные

        Returns:
            bool: True если лог записан успешно
        """
        try:
            # Создание записи лога
            log_entry = LogEntry(
                level,
                message,
                component or self.name,
                extra_data=extra_data)

            # Добавление в хранилище
            self.log_entries.append(log_entry)

            # Обновление статистики
            self._update_statistics(log_entry)

            # Запись через стандартный логгер
            logger = logging.getLogger(component or self.name)
            log_method = getattr(logger, level.lower(), logger.info)

            if extra_data:
                log_method(f"{message} | Extra: {extra_data}")
            else:
                log_method(message)

            self.total_logs += 1
            return True

        except Exception as e:
            self.log_errors += 1
            self.log_activity(f"Ошибка записи лога: {e}", "error")
            return False

    def _update_statistics(self, log_entry: LogEntry):
        """Обновление статистики логов"""
        # Статистика по уровням
        if log_entry.level in self.logs_by_level:
            self.logs_by_level[log_entry.level] += 1

        # Статистика по компонентам
        if log_entry.component not in self.logs_by_component:
            self.logs_by_component[log_entry.component] = 0
        self.logs_by_component[log_entry.component] += 1

    def debug(self,
              message: str,
              component: Optional[str] = None,
              extra_data: Optional[Dict[str,
                                        Any]] = None) -> bool:
        """Запись отладочного лога"""
        return self.log("DEBUG", message, component, extra_data)

    def info(self,
             message: str,
             component: Optional[str] = None,
             extra_data: Optional[Dict[str,
                                       Any]] = None) -> bool:
        """Запись информационного лога"""
        return self.log("INFO", message, component, extra_data)

    def warning(self,
                message: str,
                component: Optional[str] = None,
                extra_data: Optional[Dict[str,
                                          Any]] = None) -> bool:
        """Запись предупреждения"""
        return self.log("WARNING", message, component, extra_data)

    def error(self,
              message: str,
              component: Optional[str] = None,
              extra_data: Optional[Dict[str,
                                        Any]] = None) -> bool:
        """Запись ошибки"""
        return self.log("ERROR", message, component, extra_data)

    def critical(self,
                 message: str,
                 component: Optional[str] = None,
                 extra_data: Optional[Dict[str,
                                           Any]] = None) -> bool:
        """Запись критической ошибки"""
        return self.log("CRITICAL", message, component, extra_data)

    def get_logs(
        self,
        level: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """
        Получение логов с фильтрацией

        Args:
            level: Фильтр по уровню
            component: Фильтр по компоненту
            start_time: Начальное время
            end_time: Конечное время
            limit: Максимальное количество записей

        Returns:
            List[LogEntry]: Список записей логов
        """
        try:
            filtered_logs = self.log_entries.copy()

            # Фильтрация по уровню
            if level:
                filtered_logs = [
                    log for log in filtered_logs if log.level == level]

            # Фильтрация по компоненту
            if component:
                filtered_logs = [
                    log for log in filtered_logs if log.component == component]

            # Фильтрация по времени
            if start_time:
                filtered_logs = [
                    log for log in filtered_logs if log.timestamp >= start_time]

            if end_time:
                filtered_logs = [
                    log for log in filtered_logs if log.timestamp <= end_time]

            # Ограничение количества
            if limit > 0:
                filtered_logs = filtered_logs[-limit:]

            return filtered_logs

        except Exception as e:
            self.log_activity(f"Ошибка получения логов: {e}", "error")
            return []

    def get_logs_by_level(
            self,
            level: str,
            limit: int = 100) -> List[LogEntry]:
        """
        Получение логов по уровню

        Args:
            level: Уровень логирования
            limit: Максимальное количество записей

        Returns:
            List[LogEntry]: Список записей логов
        """
        return self.get_logs(level=level, limit=limit)

    def get_logs_by_component(
            self,
            component: str,
            limit: int = 100) -> List[LogEntry]:
        """
        Получение логов по компоненту

        Args:
            component: Компонент системы
            limit: Максимальное количество записей

        Returns:
            List[LogEntry]: Список записей логов
        """
        return self.get_logs(component=component, limit=limit)

    def get_error_logs(self, limit: int = 100) -> List[LogEntry]:
        """
        Получение логов ошибок

        Args:
            limit: Максимальное количество записей

        Returns:
            List[LogEntry]: Список записей ошибок
        """
        return self.get_logs_by_level("ERROR", limit)

    def get_security_logs(self, limit: int = 100) -> List[LogEntry]:
        """
        Получение логов безопасности

        Args:
            limit: Максимальное количество записей

        Returns:
            List[LogEntry]: Список записей безопасности
        """
        try:
            security_logs = []
            for log_entry in self.log_entries:
                if (
                    "security" in log_entry.component.lower()
                    or "auth" in log_entry.component.lower()
                    or "security" in log_entry.message.lower()
                ):
                    security_logs.append(log_entry)

            return security_logs[-limit:] if limit > 0 else security_logs

        except Exception as e:
            self.log_activity(
                f"Ошибка получения логов безопасности: {e}", "error")
            return []

    def export_logs(self, format_type: str = "json", **kwargs) -> str:
        """
        Экспорт логов

        Args:
            format_type: Тип формата (json, csv, txt)
            **kwargs: Параметры фильтрации

        Returns:
            str: Логи в указанном формате
        """
        try:
            logs = self.get_logs(**kwargs)

            if format_type == "json":
                return json.dumps([log.to_dict()
                                  for log in logs], indent=2, ensure_ascii=False)
            elif format_type == "csv":
                return self._export_csv(logs)
            elif format_type == "txt":
                return self._export_txt(logs)
            else:
                raise ValueError(f"Неподдерживаемый формат: {format_type}")

        except Exception as e:
            self.log_activity(f"Ошибка экспорта логов: {e}", "error")
            return ""

    def _export_csv(self, logs: List[LogEntry]) -> str:
        """Экспорт логов в CSV формат"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(
            ["Timestamp", "Level", "Component", "Message", "Extra Data"])

        # Данные
        for log in logs:
            writer.writerow(
                [
                    log.timestamp.isoformat(),
                    log.level,
                    log.component,
                    log.message,
                    json.dumps(log.extra_data, ensure_ascii=False),
                ]
            )

        return output.getvalue()

    def _export_txt(self, logs: List[LogEntry]) -> str:
        """Экспорт логов в текстовый формат"""
        lines = []
        for log in logs:
            line = f"[{log.timestamp.isoformat()}] {log.level} - " f"{log.component}: {log.message}"
            if log.extra_data:
                line += f" | Extra: {log.extra_data}"
            lines.append(line)

        return "\n".join(lines)

    def clear_logs(self, older_than: Optional[datetime] = None) -> bool:
        """
        Очистка логов

        Args:
            older_than: Удалить логи старше указанной даты

        Returns:
            bool: True если логи очищены успешно
        """
        try:
            if older_than:
                self.log_entries = [
                    log for log in self.log_entries if log.timestamp > older_than]
                self.log_activity(
                    f"Очищены логи старше {older_than.isoformat()}")
            else:
                self.log_entries.clear()
                self.log_activity("Все логи очищены")

            return True

        except Exception as e:
            self.log_activity(f"Ошибка очистки логов: {e}", "error")
            return False

    def get_logging_stats(self) -> Dict[str, Any]:
        """
        Получение статистики логирования

        Returns:
            Dict[str, Any]: Статистика логирования
        """
        return {
            "total_logs": self.total_logs,
            "logs_by_level": self.logs_by_level.copy(),
            "logs_by_component": self.logs_by_component.copy(),
            "log_errors": self.log_errors,
            "active_handlers": len(self.log_handlers),
            "active_filters": len(self.log_filters),
            "active_formatters": len(self.log_formatters),
            "log_file_size": self._get_log_file_size(),
            "oldest_log": (self.log_entries[0].timestamp.isoformat() if self.log_entries else None),
            "newest_log": (self.log_entries[-1].timestamp.isoformat() if self.log_entries else None),
        }

    def _get_log_file_size(self) -> int:
        """Получение размера файла логов"""
        try:
            log_path = os.path.join(self.log_dir, self.log_file)
            if os.path.exists(log_path):
                return os.path.getsize(log_path)
            return 0
        except Exception:
            return 0

    def rotate_logs(self) -> bool:
        """
        Ротация логов

        Returns:
            bool: True если ротация выполнена успешно
        """
        try:
            for handler in self.log_handlers.values():
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()

            self.log_activity("Ротация логов выполнена")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка ротации логов: {e}", "error")
            return False

    def start(self) -> bool:
        """Запуск менеджера логирования"""
        try:
            self.log_activity(f"Запуск менеджера логирования {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер логирования {self.name} успешно запущен")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера логирования {self.name}: {e}",
                "error")
            return False

    def stop(self) -> bool:
        """Остановка менеджера логирования"""
        try:
            self.log_activity(f"Остановка менеджера логирования {self.name}")

            # Закрытие обработчиков
            for handler in self.log_handlers.values():
                handler.close()

            self.log_handlers.clear()

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер логирования {self.name} успешно остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера логирования {self.name}: {e}",
                "error")
            return False
