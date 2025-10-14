# -*- coding: utf-8 -*-
"""
Расширенный логгер для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import logging
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog


class LogLevel(Enum):
    """Уровни логирования"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Форматы логирования"""

    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"


@dataclass
class LogContext:
    """Контекст логирования"""

    component: str
    operation: str
    child_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)


@dataclass
class LogEntry:
    """Запись лога"""

    timestamp: datetime
    level: LogLevel
    message: str
    context: LogContext
    exception: Optional[str] = None
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "context": self.context.to_dict(),
            "exception": self.exception,
            "stack_trace": self.stack_trace,
        }


class AdvancedLogger:
    """Расширенный логгер с контекстом и структурированием"""

    def __init__(
        self,
        name: str,
        log_level: LogLevel = LogLevel.INFO,
        log_format: LogFormat = LogFormat.JSON,
        log_file: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_metrics: bool = True,
    ):
        self.name = name
        self.log_level = log_level
        self.log_format = log_format
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_metrics = enable_metrics

        # Создание директории для логов
        if self.log_file:
            log_dir = Path(self.log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)

        # Инициализация логгера
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))

        # Очистка существующих обработчиков
        self.logger.handlers.clear()

        # Настройка обработчиков
        self._setup_handlers()

        # Настройка structlog
        self._setup_structlog()

        # Метрики логирования
        self.metrics = {
            "total_logs": 0,
            "logs_by_level": {level.value: 0 for level in LogLevel},
            "logs_by_component": {},
            "error_rate": 0.0,
            "last_error": None,
        }

        # Буфер для батчинга логов
        self.log_buffer: List[LogEntry] = []
        self.buffer_size = 100
        self.buffer_timeout = 5.0  # секунды
        self._buffer_task: Optional[asyncio.Task] = None

    def _setup_handlers(self):
        """Настройка обработчиков логов"""
        # Консольный обработчик
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level.value)

            if self.log_format == LogFormat.JSON:
                console_handler.setFormatter(logging.Formatter("%(message)s"))
            else:
                console_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                )

            self.logger.addHandler(console_handler)

        # Файловый обработчик
        if self.enable_file and self.log_file:
            from logging.handlers import RotatingFileHandler

            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
            )
            file_handler.setLevel(self.log_level.value)

            if self.log_format == LogFormat.JSON:
                file_handler.setFormatter(logging.Formatter("%(message)s"))
            else:
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                )

            self.logger.addHandler(file_handler)

    def _setup_structlog(self):
        """Настройка structlog"""
        try:
            processors = [
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
            ]

            if self.log_format == LogFormat.JSON:
                processors.append(structlog.processors.JSONRenderer())
            else:
                processors.append(structlog.dev.ConsoleRenderer())

            structlog.configure(
                processors=processors,
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

            self.struct_logger = structlog.get_logger(name=self.name)

        except Exception as e:
            # Fallback к стандартному логированию
            self.struct_logger = None
            self.logger.warning(f"Не удалось настроить structlog: {e}")

    def _create_context_logger(self, context: LogContext):
        """Создание контекстного логгера"""
        if self.struct_logger:
            return self.struct_logger.bind(**context.to_dict())
        else:
            return self.logger

    def _log_entry(
        self,
        level: LogLevel,
        message: str,
        context: LogContext,
        exception: Optional[Exception] = None,
    ):
        """Создание записи лога"""
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            context=context,
            exception=str(exception) if exception else None,
            stack_trace=traceback.format_exc() if exception else None,
        )

        # Добавление в буфер
        self.log_buffer.append(log_entry)

        # Обновление метрик
        self._update_metrics(log_entry)

        # Немедленное логирование для критических сообщений
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self._flush_buffer()

        # Проверка размера буфера
        if len(self.log_buffer) >= self.buffer_size:
            asyncio.create_task(self._flush_buffer_async())

    def _update_metrics(self, log_entry: LogEntry):
        """Обновление метрик логирования"""
        self.metrics["total_logs"] += 1
        self.metrics["logs_by_level"][log_entry.level.value] += 1

        component = log_entry.context.component
        if component not in self.metrics["logs_by_component"]:
            self.metrics["logs_by_component"][component] = 0
        self.metrics["logs_by_component"][component] += 1

        if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.metrics["last_error"] = log_entry.timestamp.isoformat()

        # Расчет коэффициента ошибок
        error_count = (
            self.metrics["logs_by_level"][LogLevel.ERROR.value]
            + self.metrics["logs_by_level"][LogLevel.CRITICAL.value]
        )
        self.metrics["error_rate"] = error_count / max(
            1, self.metrics["total_logs"]
        )

    def _flush_buffer(self):
        """Синхронная очистка буфера"""
        if not self.log_buffer:
            return

        for entry in self.log_buffer:
            self._write_log_entry(entry)

        self.log_buffer.clear()

    async def _flush_buffer_async(self):
        """Асинхронная очистка буфера"""
        if not self.log_buffer:
            return

        for entry in self.log_buffer:
            self._write_log_entry(entry)

        self.log_buffer.clear()

    def _write_log_entry(self, entry: LogEntry):
        """Запись записи лога"""
        context_logger = self._create_context_logger(entry.context)

        log_data = {
            "message": entry.message,
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level.value,
            "component": entry.context.component,
            "operation": entry.context.operation,
        }

        # Добавление дополнительного контекста
        if entry.context.child_id:
            log_data["child_id"] = entry.context.child_id
        if entry.context.user_id:
            log_data["user_id"] = entry.context.user_id
        if entry.context.session_id:
            log_data["session_id"] = entry.context.session_id
        if entry.context.request_id:
            log_data["request_id"] = entry.context.request_id
        if entry.context.duration is not None:
            log_data["duration"] = entry.context.duration
        if entry.context.metadata:
            log_data.update(entry.context.metadata)

        # Логирование с соответствующим уровнем
        log_method = getattr(context_logger, entry.level.value.lower())

        if entry.exception:
            log_method(entry.message, exc_info=True, **log_data)
        else:
            log_method(entry.message, **log_data)

    def debug(self, message: str, context: LogContext, **kwargs):
        """Логирование отладочной информации"""
        context.metadata = kwargs
        self._log_entry(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: LogContext, **kwargs):
        """Логирование информационного сообщения"""
        context.metadata = kwargs
        self._log_entry(LogLevel.INFO, message, context)

    def warning(self, message: str, context: LogContext, **kwargs):
        """Логирование предупреждения"""
        context.metadata = kwargs
        self._log_entry(LogLevel.WARNING, message, context)

    def error(
        self,
        message: str,
        context: LogContext,
        exception: Optional[Exception] = None,
        **kwargs,
    ):
        """Логирование ошибки"""
        context.metadata = kwargs
        self._log_entry(LogLevel.ERROR, message, context, exception)

    def critical(
        self,
        message: str,
        context: LogContext,
        exception: Optional[Exception] = None,
        **kwargs,
    ):
        """Логирование критической ошибки"""
        context.metadata = kwargs
        self._log_entry(LogLevel.CRITICAL, message, context, exception)

    def log_operation_start(
        self, operation: str, component: str, **kwargs
    ) -> LogContext:
        """Логирование начала операции"""
        context = LogContext(
            component=component, operation=operation, **kwargs
        )
        self.info(f"Начало операции: {operation}", context)
        return context

    def log_operation_end(
        self, context: LogContext, duration: float, success: bool = True
    ):
        """Логирование завершения операции"""
        context.duration = duration
        if success:
            self.info(f"Операция завершена: {context.operation}", context)
        else:
            self.error(
                f"Операция завершена с ошибкой: {context.operation}", context
            )

    def log_performance(
        self, operation: str, component: str, duration: float, **kwargs
    ):
        """Логирование производительности"""
        context = LogContext(
            component=component, operation=operation, duration=duration
        )
        self.info(f"Производительность: {operation}", context, **kwargs)

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        child_id: Optional[str] = None,
        **kwargs,
    ):
        """Логирование события безопасности"""
        context = LogContext(
            component="security",
            operation="security_event",
            child_id=child_id,
            metadata={
                "event_type": event_type,
                "severity": severity,
                **kwargs,
            },
        )

        if severity in ["high", "critical"]:
            self.critical(f"Событие безопасности: {event_type}", context)
        elif severity == "medium":
            self.warning(f"Событие безопасности: {event_type}", context)
        else:
            self.info(f"Событие безопасности: {event_type}", context)

    def log_user_action(
        self, action: str, child_id: str, user_id: str, **kwargs
    ):
        """Логирование действия пользователя"""
        context = LogContext(
            component="user_action",
            operation=action,
            child_id=child_id,
            user_id=user_id,
            **kwargs,
        )
        self.info(f"Действие пользователя: {action}", context)

    def log_system_event(self, event: str, component: str, **kwargs):
        """Логирование системного события"""
        context = LogContext(
            component=component,
            operation="system_event",
            metadata={"event": event, **kwargs},
        )
        self.info(f"Системное событие: {event}", context)

    async def start_buffer_processor(self):
        """Запуск обработчика буфера"""
        if self._buffer_task is None or self._buffer_task.done():
            self._buffer_task = asyncio.create_task(self._buffer_processor())

    async def stop_buffer_processor(self):
        """Остановка обработчика буфера"""
        if self._buffer_task and not self._buffer_task.done():
            self._buffer_task.cancel()
            try:
                await self._buffer_task
            except asyncio.CancelledError:
                pass

        # Финальная очистка буфера
        await self._flush_buffer_async()

    async def _buffer_processor(self):
        """Обработчик буфера логов"""
        while True:
            try:
                await asyncio.sleep(self.buffer_timeout)
                await self._flush_buffer_async()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Ошибка в обработчике буфера: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик логирования"""
        return {
            "logger_name": self.name,
            "log_level": self.log_level.value,
            "log_format": self.log_format.value,
            "buffer_size": len(self.log_buffer),
            "metrics": self.metrics.copy(),
        }

    def export_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[LogLevel] = None,
        component: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Экспорт логов с фильтрацией"""
        # В реальной реализации здесь был бы запрос к базе данных логов
        # Пока возвращаем пустой список
        return []

    def cleanup_old_logs(self, days: int = 30):
        """Очистка старых логов"""
        if not self.log_file:
            return

        log_path = Path(self.log_file)
        if not log_path.exists():
            return

        # В реальной реализации здесь была бы логика очистки старых файлов
        self.info(
            f"Очистка логов старше {days} дней",
            LogContext(component="logger", operation="cleanup"),
        )

    def set_log_level(self, level: LogLevel):
        """Изменение уровня логирования"""
        self.log_level = level
        self.logger.setLevel(getattr(logging, level.value))

        # Обновление всех обработчиков
        for handler in self.logger.handlers:
            handler.setLevel(level.value)

    def add_custom_handler(self, handler: logging.Handler):
        """Добавление пользовательского обработчика"""
        self.logger.addHandler(handler)

    def remove_handler(self, handler: logging.Handler):
        """Удаление обработчика"""
        if handler in self.logger.handlers:
            self.logger.removeHandler(handler)
            handler.close()


class LoggingManager:
    """Менеджер логирования для всей системы"""

    def __init__(self):
        self.loggers: Dict[str, AdvancedLogger] = {}
        self.global_context: Dict[str, Any] = {}

    def get_logger(self, name: str, **kwargs) -> AdvancedLogger:
        """Получение логгера по имени"""
        if name not in self.loggers:
            self.loggers[name] = AdvancedLogger(name, **kwargs)
        return self.loggers[name]

    def set_global_context(self, **kwargs):
        """Установка глобального контекста"""
        self.global_context.update(kwargs)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Получение метрик всех логгеров"""
        return {
            name: logger.get_metrics() for name, logger in self.loggers.items()
        }

    async def shutdown_all(self):
        """Остановка всех логгеров"""
        for logger in self.loggers.values():
            await logger.stop_buffer_processor()


# Глобальный менеджер логирования
logging_manager = LoggingManager()
