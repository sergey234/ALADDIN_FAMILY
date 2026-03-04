#!/usr/bin/env python3
"""
ALADDIN VPN - Security Audit Logger
Система аудита и структурированного логирования

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType(Enum):
    """Типы событий аудита"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    SECURITY = "security"
    SYSTEM = "system"
    VPN_OPERATION = "vpn_operation"
    ADMIN_ACTION = "admin_action"
    ERROR = "error"
    AUDIT = "audit"


class SecurityLevel(Enum):
    """Уровни безопасности"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Событие аудита"""
    event_id: str
    timestamp: datetime
    event_type: EventType
    security_level: SecurityLevel
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    message: str = ""
    details: Dict[str, Any] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    response_time_ms: Optional[float] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)


@dataclass
class LogRotationConfig:
    """Конфигурация ротации логов"""
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    when: str = "midnight"
    interval: int = 1
    encoding: str = "utf-8"


class SecurityAuditLogger:
    """
    Система аудита безопасности

    Функции:
    - Структурированное логирование (JSON)
    - Ротация логов по размеру и времени
    - Security audit trail
    - SIEM интеграция готовность
    - Алерты при подозрительной активности
    - Корреляция событий
    - Compliance отчеты
    """

    def __init__(self, config_file: str = "config/audit_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

        # Создание директорий
        self.log_dir = Path(self.config.get("log_directory", "logs"))
        self.log_dir.mkdir(exist_ok=True)

        # Настройка логгеров
        self._setup_loggers()

        # Хранилище событий для корреляции
        self.event_buffer: List[AuditEvent] = []
        self.max_buffer_size = self.config.get("max_buffer_size", 1000)

        # Статистика
        self.stats = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_level": {},
            "errors": 0,
            "warnings": 0,
            "last_cleanup": None
        }

        logger.info("Security Audit Logger initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            "log_directory": "logs",
            "max_buffer_size": 1000,
            "rotation": {
                "max_bytes": 10485760,  # 10MB
                "backup_count": 5,
                "when": "midnight",
                "interval": 1
            },
            "siem": {
                "enabled": False,
                "endpoint": "",
                "api_key": "",
                "batch_size": 100,
                "flush_interval": 60
            },
            "alerts": {
                "enabled": True,
                "email": "",
                "webhook": "",
                "thresholds": {
                    "error_rate": 0.1,
                    "failed_logins": 5,
                    "suspicious_activity": 3
                }
            },
            "retention": {
                "days": 30,
                "compress_after_days": 7,
                "delete_after_days": 90
            },
            "correlation": {
                "enabled": True,
                "time_window_minutes": 5,
                "max_events_per_correlation": 100
            }
        }

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self._save_config(default_config)

        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _setup_loggers(self) -> None:
        """Настройка логгеров"""
        # Основной аудит логгер
        self.audit_logger = logging.getLogger("audit")
        self.audit_logger.setLevel(logging.INFO)

        # Очистка существующих хендлеров
        self.audit_logger.handlers.clear()

        # Файловый хендлер с ротацией
        audit_file = self.log_dir / "audit.log"
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_file,
            maxBytes=self.config["rotation"]["max_bytes"],
            backupCount=self.config["rotation"]["backup_count"],
            encoding=self.config["rotation"]["encoding"]
        )

        # JSON форматтер
        audit_formatter = JSONFormatter()
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)

        # Security логгер
        self.security_logger = logging.getLogger("security")
        self.security_logger.setLevel(logging.WARNING)

        security_file = self.log_dir / "security.log"
        security_handler = logging.handlers.RotatingFileHandler(
            security_file,
            maxBytes=self.config["rotation"]["max_bytes"],
            backupCount=self.config["rotation"]["backup_count"],
            encoding=self.config["rotation"]["encoding"]
        )

        security_formatter = JSONFormatter()
        security_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(security_handler)

        # Error логгер
        self.error_logger = logging.getLogger("error")
        self.error_logger.setLevel(logging.ERROR)

        error_file = self.log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=self.config["rotation"]["max_bytes"],
            backupCount=self.config["rotation"]["backup_count"],
            encoding=self.config["rotation"]["encoding"]
        )

        error_formatter = JSONFormatter()
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)

        # Console логгер для критичных событий
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.CRITICAL)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        for logger_name in ["audit", "security", "error"]:
            logger_obj = logging.getLogger(logger_name)
            logger_obj.addHandler(console_handler)

    def _generate_event_id(self) -> str:
        """Генерация уникального ID события"""
        return str(uuid.uuid4())

    def _get_security_level(self, event_type: EventType, message: str) -> SecurityLevel:
        """Определение уровня безопасности события"""
        critical_keywords = ["attack", "breach", "hack", "exploit", "malware", "ddos"]
        high_keywords = ["failed", "unauthorized", "blocked", "suspicious", "anomaly"]
        medium_keywords = ["warning", "error", "timeout", "retry"]

        message_lower = message.lower()

        if any(keyword in message_lower for keyword in critical_keywords):
            return SecurityLevel.CRITICAL
        elif any(keyword in message_lower for keyword in high_keywords):
            return SecurityLevel.HIGH
        elif any(keyword in message_lower for keyword in medium_keywords):
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW

    def log_event(self, event_type: EventType, message: str,
                  user_id: str = None, ip_address: str = None,
                  user_agent: str = None, endpoint: str = None,
                  method: str = None, status_code: int = None,
                  details: Dict[str, Any] = None, session_id: str = None,
                  request_id: str = None, response_time_ms: float = None,
                  bytes_sent: int = None, bytes_received: int = None) -> str:
        """
        Логирование события аудита

        Args:
            event_type: Тип события
            message: Сообщение события
            user_id: ID пользователя
            ip_address: IP адрес
            user_agent: User-Agent
            endpoint: Эндпоинт
            method: HTTP метод
            status_code: HTTP статус код
            details: Дополнительные детали
            session_id: ID сессии
            request_id: ID запроса
            response_time_ms: Время ответа в мс
            bytes_sent: Отправлено байт
            bytes_received: Получено байт

        Returns:
            str: ID события
        """
        try:
            event_id = self._generate_event_id()
            timestamp = datetime.now(timezone.utc)
            security_level = self._get_security_level(event_type, message)

            event = AuditEvent(
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type,
                security_level=security_level,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                message=message,
                details=details or {},
                session_id=session_id,
                request_id=request_id,
                response_time_ms=response_time_ms,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received
            )

            # Добавляем в буфер
            self.event_buffer.append(event)
            if len(self.event_buffer) > self.max_buffer_size:
                self.event_buffer.pop(0)

            # Выбираем логгер
            if security_level in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
                target_logger = self.security_logger
            elif event_type == EventType.ERROR:
                target_logger = self.error_logger
            else:
                target_logger = self.audit_logger

            # Логируем событие
            log_data = asdict(event)
            log_data["timestamp"] = timestamp.isoformat()
            log_data["event_type"] = event_type.value
            log_data["security_level"] = security_level.value

            target_logger.info(json.dumps(log_data, ensure_ascii=False))

            # Обновляем статистику
            self._update_stats(event)

            # Проверяем на подозрительную активность
            if self.config.get("alerts", {}).get("enabled", True):
                self._check_suspicious_activity(event)

            # Корреляция событий
            if self.config.get("correlation", {}).get("enabled", True):
                self._correlate_events(event)

            return event_id

        except Exception as e:
            logger.error(f"Error logging event: {e}")
            return ""

    def _update_stats(self, event: AuditEvent) -> None:
        """Обновление статистики"""
        self.stats["total_events"] += 1

        # По типам событий
        event_type = event.event_type.value
        if event_type not in self.stats["events_by_type"]:
            self.stats["events_by_type"][event_type] = 0
        self.stats["events_by_type"][event_type] += 1

        # По уровням безопасности
        security_level = event.security_level.value
        if security_level not in self.stats["events_by_level"]:
            self.stats["events_by_level"][security_level] = 0
        self.stats["events_by_level"][security_level] += 1

        # Ошибки и предупреждения
        if event.event_type == EventType.ERROR:
            self.stats["errors"] += 1
        elif event.security_level == SecurityLevel.HIGH:
            self.stats["warnings"] += 1

    def _check_suspicious_activity(self, event: AuditEvent) -> None:
        """Проверка подозрительной активности"""
        thresholds = self.config.get("alerts", {}).get("thresholds", {})

        # Проверка неудачных попыток входа
        if (event.event_type == EventType.AUTHENTICATION and
                "failed" in event.message.lower()):
            failed_logins = len([e for e in self.event_buffer
                                if (e.event_type == EventType.AUTHENTICATION and
                                    "failed" in e.message.lower() and
                                    e.ip_address == event.ip_address and
                                    (datetime.now(timezone.utc) - e.timestamp).seconds < 300)])

            if failed_logins >= thresholds.get("failed_logins", 5):
                self._send_alert("Multiple failed login attempts", {
                    "ip_address": event.ip_address,
                    "failed_attempts": failed_logins,
                    "time_window": "5 minutes"
                })

        # Проверка подозрительной активности
        if event.security_level == SecurityLevel.HIGH:
            suspicious_events = len([e for e in self.event_buffer
                                    if (e.security_level == SecurityLevel.HIGH and
                                        e.ip_address == event.ip_address and
                                        (datetime.now(timezone.utc) - e.timestamp).seconds < 300)])

            if suspicious_events >= thresholds.get("suspicious_activity", 3):
                self._send_alert("Suspicious activity detected", {
                    "ip_address": event.ip_address,
                    "suspicious_events": suspicious_events,
                    "time_window": "5 minutes"
                })

    def _correlate_events(self, event: AuditEvent) -> None:
        """Корреляция событий"""
        time_window = self.config.get("correlation", {}).get("time_window_minutes", 5)
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window)

        # Находим связанные события
        related_events = [e for e in self.event_buffer
                          if (e.timestamp > cutoff_time and
                              e.ip_address == event.ip_address and
                              e.event_id != event.event_id)]

        if len(related_events) > 0:
            # Логируем корреляцию
            correlation_id = self._generate_event_id()
            self.log_event(
                EventType.AUDIT,
                f"Event correlation detected: {len(related_events)} related events",
                ip_address=event.ip_address,
                details={
                    "correlation_id": correlation_id,
                    "related_events": [e.event_id for e in related_events],
                    "time_window_minutes": time_window
                }
            )

    def _send_alert(self, message: str, details: Dict[str, Any]) -> None:
        """Отправка алерта"""
        try:
            alert_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": message,
                "details": details,
                "severity": "HIGH"
            }

            # Логируем алерт
            self.security_logger.critical(json.dumps(alert_data, ensure_ascii=False))

            # TODO: Реализовать отправку email/webhook
            logger.warning(f"ALERT: {message} - {details}")

        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    def get_events(self, event_type: EventType = None,
                   security_level: SecurityLevel = None,
                   user_id: str = None, ip_address: str = None,
                   start_time: datetime = None, end_time: datetime = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Получение событий по фильтрам"""
        filtered_events = self.event_buffer.copy()

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        if security_level:
            filtered_events = [e for e in filtered_events if e.security_level == security_level]

        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]

        if ip_address:
            filtered_events = [e for e in filtered_events if e.ip_address == ip_address]

        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]

        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]

        # Сортируем по времени (новые сначала)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)

        # Ограничиваем количество
        filtered_events = filtered_events[:limit]

        # Конвертируем в словари
        return [asdict(event) for event in filtered_events]

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        return {
            **self.stats,
            "buffer_size": len(self.event_buffer),
            "log_files": {
                "audit": str(self.log_dir / "audit.log"),
                "security": str(self.log_dir / "security.log"),
                "error": str(self.log_dir / "error.log")
            }
        }

    def cleanup_old_events(self) -> None:
        """Очистка старых событий"""
        retention_days = self.config.get("retention", {}).get("days", 30)
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # Очищаем буфер
        self.event_buffer = [e for e in self.event_buffer if e.timestamp > cutoff_time]

        self.stats["last_cleanup"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"Cleaned up events older than {retention_days} days")


class JSONFormatter(logging.Formatter):
    """JSON форматтер для логов"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Добавляем исключение если есть
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Добавляем дополнительные поля
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


# Глобальный экземпляр аудит логгера
audit_logger = SecurityAuditLogger()


def log_audit_event(event_type: EventType, message: str, **kwargs) -> str:
    """Глобальная функция логирования событий аудита"""
    return audit_logger.log_event(event_type, message, **kwargs)


def get_audit_events(**filters) -> List[Dict[str, Any]]:
    """Получение событий аудита"""
    return audit_logger.get_events(**filters)


def get_audit_statistics() -> Dict[str, Any]:
    """Получение статистики аудита"""
    return audit_logger.get_statistics()


if __name__ == "__main__":
    # Тестирование системы аудита
    print("🧪 Testing Security Audit Logger...")

    # Тестовые события
    test_events = [
        (EventType.AUTHENTICATION, "User login successful", "user123", "192.168.1.1"),
        (EventType.AUTHENTICATION, "User login failed", "user123", "192.168.1.1"),
        (EventType.VPN_OPERATION, "VPN connection established", "user123", "192.168.1.1"),
        (EventType.SECURITY, "Suspicious activity detected", None, "192.168.1.2"),
        (EventType.ADMIN_ACTION, "Configuration changed", "admin", "192.168.1.10"),
        (EventType.ERROR, "Database connection failed", None, None),
    ]

    for event_type, message, user_id, ip_address in test_events:
        event_id = log_audit_event(
            event_type=event_type,
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            endpoint="/api/v1/test",
            method="POST",
            status_code=200
        )
        print(f"Logged event: {event_id}")

    # Статистика
    stats = get_audit_statistics()
    print(f"\n📊 Statistics: {json.dumps(stats, indent=2)}")

    # Получение событий
    events = get_audit_events(limit=5)
    print(f"\n📋 Recent events: {len(events)} events")

    print("✅ Security Audit Logger test completed")
