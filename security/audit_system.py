# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Audit System
Система аудита и логирования всех операций

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import hashlib
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase


class AuditLevel(Enum):
    """Уровни аудита"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class AuditEvent:
    """Событие аудита"""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        user: str,
        operation: str,
        level: AuditLevel,
        details: Dict[str, Any],
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.user = user
        self.operation = operation
        self.level = level
        self.details = details
        self.timestamp = datetime.now()
        self.ip_address = details.get("ip_address", "unknown")
        self.user_agent = details.get("user_agent", "unknown")
        self.session_id = details.get("session_id", "unknown")
        self.success = details.get("success", True)
        self.error_message = details.get("error_message", None)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "user": self.user,
            "operation": self.operation,
            "level": self.level.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "success": self.success,
            "error_message": self.error_message,
        }


class AuditSystem(SecurityBase):
    """Система аудита и логирования"""

    def __init__(self, name: str = "AuditSystem", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация аудита
        self.audit_retention_days = config.get("audit_retention_days", 365) if config else 365
        self.max_events_in_memory = config.get("max_events_in_memory", 10000) if config else 10000
        self.enable_real_time_audit = config.get("enable_real_time_audit", True) if config else True
        self.audit_sensitive_data = config.get("audit_sensitive_data", False) if config else False

        # Хранилище событий аудита
        self.audit_events = {}
        self.audit_history = []
        self.user_audit_trail = {}
        self.operation_audit_trail = {}

        # Статистика аудита
        self.total_events = 0
        self.events_by_level = {level.value: 0 for level in AuditLevel}
        self.events_by_user = {}
        self.events_by_operation = {}
        self.failed_operations = 0
        self.successful_operations = 0

        # Блокировки
        self.audit_lock = threading.Lock()
        self.cleanup_thread = None
        self.stop_cleanup = False

    def initialize(self) -> bool:
        """Инициализация системы аудита"""
        try:
            self.log_activity(f"Инициализация системы аудита {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Настройка уровней аудита
            self._setup_audit_levels()

            # Инициализация хранилища
            self._initialize_audit_storage()

            # Запуск очистки старых событий
            self._start_cleanup_thread()

            # Запуск аудита в реальном времени
            if self.enable_real_time_audit:
                self._start_real_time_audit()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Система аудита {self.name} успешно инициализирована")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации системы аудита: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def _setup_audit_levels(self):
        """Настройка уровней аудита"""
        self.audit_levels = {
            AuditLevel.INFO: {
                "log_to_file": True,
                "log_to_database": False,
                "alert": False,
            },
            AuditLevel.WARNING: {
                "log_to_file": True,
                "log_to_database": True,
                "alert": False,
            },
            AuditLevel.ERROR: {
                "log_to_file": True,
                "log_to_database": True,
                "alert": True,
            },
            AuditLevel.CRITICAL: {
                "log_to_file": True,
                "log_to_database": True,
                "alert": True,
                "immediate_notification": True,
            },
            AuditLevel.SECURITY: {
                "log_to_file": True,
                "log_to_database": True,
                "alert": True,
                "immediate_notification": True,
                "security_team_notification": True,
            },
        }

    def _initialize_audit_storage(self):
        """Инициализация хранилища аудита"""
        self.audit_events = {}
        self.audit_history = []
        self.user_audit_trail = {}
        self.operation_audit_trail = {}

    def _start_cleanup_thread(self):
        """Запуск потока очистки старых событий"""
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_events, daemon=True)
        self.cleanup_thread.start()

    def _cleanup_old_events(self):
        """Очистка старых событий аудита"""
        while not self.stop_cleanup:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(days=self.audit_retention_days)

                with self.audit_lock:
                    # Очистка событий старше retention_days
                    events_to_remove = []
                    for event_id, event in self.audit_events.items():
                        if event.timestamp < cutoff_time:
                            events_to_remove.append(event_id)

                    for event_id in events_to_remove:
                        del self.audit_events[event_id]

                    # Очистка истории
                    self.audit_history = [
                        event
                        for event in self.audit_history
                        if event.get("timestamp", datetime.min) > cutoff_time.isoformat()
                    ]

                if events_to_remove:
                    self.log_activity(f"Очищено {len(events_to_remove)} старых событий аудита")

                # Ожидание 24 часа до следующей очистки
                time.sleep(24 * 3600)

            except Exception as e:
                self.log_activity(f"Ошибка очистки событий аудита: {e}", "error")
                time.sleep(3600)  # Повтор через час при ошибке

    def _start_real_time_audit(self):
        """Запуск аудита в реальном времени"""
        self.log_activity("Запуск аудита в реальном времени")

    def log_audit_event(
        self,
        event_type: str,
        user: str,
        operation: str,
        level: AuditLevel,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Логирование события аудита

        Args:
            event_type: Тип события
            user: Пользователь
            operation: Операция
            level: Уровень аудита
            details: Дополнительные детали

        Returns:
            str: ID события аудита
        """
        try:
            with self.audit_lock:
                # Генерация ID события
                event_id = self._generate_audit_event_id(event_type, user, operation)

                # Создание события аудита
                audit_event = AuditEvent(
                    event_id=event_id,
                    event_type=event_type,
                    user=user,
                    operation=operation,
                    level=level,
                    details=details or {},
                )

                # Сохранение события
                self.audit_events[event_id] = audit_event
                self.audit_history.append(audit_event.to_dict())

                # Обновление статистики
                self._update_audit_statistics(audit_event)

                # Обработка по уровню
                self._process_audit_event(audit_event)

                # Ограничение размера в памяти
                if len(self.audit_events) > self.max_events_in_memory:
                    self._cleanup_oldest_events()

                return event_id

        except Exception as e:
            self.log_activity(f"Ошибка логирования события аудита: {e}", "error")
            return ""

    def _generate_audit_event_id(self, event_type: str, user: str, operation: str) -> str:
        """Генерация ID события аудита"""
        timestamp = int(time.time() * 1000)
        data = f"{event_type}_{user}_{operation}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def _update_audit_statistics(self, event: AuditEvent):
        """Обновление статистики аудита"""
        self.total_events += 1
        self.events_by_level[event.level.value] += 1

        # Статистика по пользователям
        if event.user not in self.events_by_user:
            self.events_by_user[event.user] = 0
        self.events_by_user[event.user] += 1

        # Статистика по операциям
        if event.operation not in self.events_by_operation:
            self.events_by_operation[event.operation] = 0
        self.events_by_operation[event.operation] += 1

        # Статистика успешности
        if event.success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1

    def _process_audit_event(self, event: AuditEvent):
        """Обработка события аудита по уровню"""
        level_config = self.audit_levels.get(event.level, {})

        # Логирование в файл
        if level_config.get("log_to_file", True):
            self._log_to_file(event)

        # Логирование в базу данных
        if level_config.get("log_to_database", False):
            self._log_to_database(event)

        # Уведомления
        if level_config.get("alert", False):
            self._send_alert(event)

        # Немедленные уведомления
        if level_config.get("immediate_notification", False):
            self._send_immediate_notification(event)

        # Уведомления команды безопасности
        if level_config.get("security_team_notification", False):
            self._send_security_team_notification(event)

    def _log_to_file(self, event: AuditEvent):
        """Логирование в файл"""
        log_message = (
            f"[{event.timestamp.isoformat()}] {event.level.value.upper()}: "
            f"{event.event_type} - {event.operation} by {event.user}"
        )
        if event.error_message:
            log_message += f" - ERROR: {event.error_message}"

        self.log_activity(log_message, event.level.value)

    def _log_to_database(self, event: AuditEvent):
        """Логирование в базу данных"""
        # Здесь можно добавить логику сохранения в БД

    def _send_alert(self, event: AuditEvent):
        """Отправка уведомления"""
        alert_message = f"Событие аудита: {event.event_type} - {event.operation} by {event.user} ({event.level.value})"
        self.log_activity(f"ALERT: {alert_message}", "warning")

    def _send_immediate_notification(self, event: AuditEvent):
        """Отправка немедленного уведомления"""
        notification = f"КРИТИЧЕСКОЕ СОБЫТИЕ: {event.event_type} - {event.operation} by {event.user}"
        self.log_activity(f"IMMEDIATE NOTIFICATION: {notification}", "critical")

    def _send_security_team_notification(self, event: AuditEvent):
        """Уведомление команды безопасности"""
        security_notification = f"СОБЫТИЕ БЕЗОПАСНОСТИ: {event.event_type} - {event.operation} by {event.user}"
        self.log_activity(f"SECURITY TEAM NOTIFICATION: {security_notification}", "security")

    def _cleanup_oldest_events(self):
        """Очистка самых старых событий из памяти"""
        if len(self.audit_events) > self.max_events_in_memory:
            # Сортируем события по времени и удаляем самые старые
            sorted_events = sorted(self.audit_events.items(), key=lambda x: x[1].timestamp)
            events_to_remove = len(self.audit_events) - self.max_events_in_memory

            for i in range(events_to_remove):
                event_id = sorted_events[i][0]
                del self.audit_events[event_id]

    def get_audit_events(
        self,
        user: Optional[str] = None,
        operation: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Получение событий аудита с фильтрацией

        Args:
            user: Фильтр по пользователю
            operation: Фильтр по операции
            level: Фильтр по уровню
            limit: Лимит результатов

        Returns:
            List[Dict[str, Any]]: Список событий аудита
        """
        try:
            events = list(self.audit_events.values())

            # Фильтрация
            if user:
                events = [e for e in events if e.user == user]
            if operation:
                events = [e for e in events if e.operation == operation]
            if level:
                events = [e for e in events if e.level == level]

            # Сортировка по времени (новые сначала)
            events.sort(key=lambda x: x.timestamp, reverse=True)

            # Ограничение результатов
            return [event.to_dict() for event in events[:limit]]

        except Exception as e:
            self.log_activity(f"Ошибка получения событий аудита: {e}", "error")
            return []

    def get_user_audit_trail(self, user: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение аудиторского следа пользователя"""
        return self.get_audit_events(user=user, limit=limit)

    def get_operation_audit_trail(self, operation: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение аудиторского следа операции"""
        return self.get_audit_events(operation=operation, limit=limit)

    def get_audit_statistics(self) -> Dict[str, Any]:
        """Получение статистики аудита"""
        return {
            "total_events": self.total_events,
            "events_by_level": self.events_by_level,
            "events_by_user": self.events_by_user,
            "events_by_operation": self.events_by_operation,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": ((self.successful_operations / self.total_events * 100) if self.total_events > 0 else 0),
            "active_events_in_memory": len(self.audit_events),
            "retention_days": self.audit_retention_days,
        }

    def generate_audit_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Генерация отчета по аудиту"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Фильтрация событий по дате
            filtered_events = []
            for event in self.audit_events.values():
                if start_date <= event.timestamp <= end_date:
                    filtered_events.append(event)

            # Анализ событий
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "total_events": len(filtered_events),
                "events_by_level": {},
                "events_by_user": {},
                "events_by_operation": {},
                "failed_operations": 0,
                "successful_operations": 0,
                "critical_events": [],
                "security_events": [],
            }

            # Подсчет статистики
            for event in filtered_events:
                # По уровням
                level = event.level.value
                if level not in report["events_by_level"]:
                    report["events_by_level"][level] = 0
                report["events_by_level"][level] += 1

                # По пользователям
                if event.user not in report["events_by_user"]:
                    report["events_by_user"][event.user] = 0
                report["events_by_user"][event.user] += 1

                # По операциям
                if event.operation not in report["events_by_operation"]:
                    report["events_by_operation"][event.operation] = 0
                report["events_by_operation"][event.operation] += 1

                # Успешность
                if event.success:
                    report["successful_operations"] += 1
                else:
                    report["failed_operations"] += 1

                # Критические события
                if event.level == AuditLevel.CRITICAL:
                    report["critical_events"].append(event.to_dict())

                # События безопасности
                if event.level == AuditLevel.SECURITY:
                    report["security_events"].append(event.to_dict())

            return report

        except Exception as e:
            self.log_activity(f"Ошибка генерации отчета по аудиту: {e}", "error")
            return {}

    def stop(self):
        """Остановка системы аудита"""
        self.log_activity(f"Остановка системы аудита {self.name}")
        self.stop_cleanup = True

        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)

        self.status = ComponentStatus.STOPPED
        self.log_activity(f"Система аудита {self.name} остановлена")

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы аудита"""
        return {
            "name": self.name,
            "status": self.status.value,
            "real_time_audit": self.enable_real_time_audit,
            "audit_retention_days": self.audit_retention_days,
            "max_events_in_memory": self.max_events_in_memory,
            "statistics": self.get_audit_statistics(),
        }


# Глобальный экземпляр системы аудита
AUDIT_SYSTEM = AuditSystem()
