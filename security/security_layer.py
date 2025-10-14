# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Layer
Многоуровневая система защиты для всех операций

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import hashlib
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Set

from core.base import ComponentStatus, SecurityBase


class OperationType(Enum):
    """Типы операций"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    MODIFY = "modify"
    CREATE = "create"
    UPDATE = "update"


class SecurityRisk(Enum):
    """Уровни риска операций"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent:
    """Событие безопасности"""

    def __init__(
        self,
        event_id: str,
        operation: str,
        user: str,
        risk_level: SecurityRisk,
        details: Dict[str, Any],
    ):
        self.event_id = event_id
        self.operation = operation
        self.user = user
        self.risk_level = risk_level
        self.details = details
        self.timestamp = datetime.now()
        self.approved = False
        self.blocked = False
        self.reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "event_id": self.event_id,
            "operation": self.operation,
            "user": self.user,
            "risk_level": self.risk_level.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "approved": self.approved,
            "blocked": self.blocked,
            "reason": self.reason,
        }


class SecurityLayer(SecurityBase):
    """Многоуровневая система защиты"""

    def __init__(self, name: str = "SecurityLayer", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация безопасности
        self.enable_real_time_protection = config.get("enable_real_time_protection", True) if config else True
        self.auto_block_high_risk = config.get("auto_block_high_risk", True) if config else True
        self.require_approval_for_critical = config.get("require_approval_for_critical", True) if config else True
        self.max_operations_per_minute = config.get("max_operations_per_minute", 100) if config else 100

        # Хранилище данных
        self.security_events: Dict[str, Any] = {}
        self.operation_history: List[Dict[str, Any]] = []
        self.blocked_operations: List[Dict[str, Any]] = []
        self.approved_operations: List[Dict[str, Any]] = []
        self.user_activity: Dict[str, Any] = {}

        # Правила безопасности
        self.security_rules: Dict[str, Any] = {}
        self.risk_assessments: Dict[str, Any] = {}
        self.operation_whitelist: Set[str] = set()
        self.operation_blacklist: Set[str] = set()

        # Статистика
        self.total_operations = 0
        self.blocked_operations_count = 0
        self.approved_operations_count = 0
        self.critical_operations_count = 0

        # Блокировки
        self.operation_lock = threading.Lock()

    def initialize(self) -> bool:
        """Инициализация системы безопасности"""
        try:
            self.log_activity(f"Инициализация системы безопасности {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Создание базовых правил безопасности
            self._create_basic_security_rules()

            # Настройка оценки рисков
            self._setup_risk_assessment()

            # Инициализация мониторинга операций
            self._setup_operation_monitoring()

            # Запуск защиты в реальном времени
            if self.enable_real_time_protection:
                self._start_real_time_protection()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Система безопасности {self.name} успешно инициализирована")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации системы безопасности: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def _create_basic_security_rules(self):
        """Создание базовых правил безопасности"""
        self.security_rules = {
            # Критические операции (требуют одобрения)
            "delete_user": {"risk": SecurityRisk.CRITICAL, "require_approval": True},
            "drop_table": {"risk": SecurityRisk.CRITICAL, "require_approval": True},
            "clear_logs": {"risk": SecurityRisk.HIGH, "require_approval": True},
            "modify_config": {"risk": SecurityRisk.HIGH, "require_approval": True},
            "execute_system_command": {
                "risk": SecurityRisk.CRITICAL,
                "require_approval": True,
            },
            # Высокий риск (автоматическая блокировка)
            "remove_file": {"risk": SecurityRisk.HIGH, "auto_block": True},
            "unlink_file": {"risk": SecurityRisk.HIGH, "auto_block": True},
            "rmdir_directory": {"risk": SecurityRisk.HIGH, "auto_block": True},
            "shutil_rmtree": {"risk": SecurityRisk.CRITICAL, "auto_block": True},
            # Средний риск (мониторинг)
            "update_data": {"risk": SecurityRisk.MEDIUM, "monitor": True},
            "create_backup": {"risk": SecurityRisk.MEDIUM, "monitor": True},
            "install_update": {"risk": SecurityRisk.MEDIUM, "monitor": True},
            # Низкий риск (разрешено)
            "read_data": {"risk": SecurityRisk.LOW, "allowed": True},
            "analyze_data": {"risk": SecurityRisk.LOW, "allowed": True},
            "generate_report": {"risk": SecurityRisk.LOW, "allowed": True},
        }

    def _setup_risk_assessment(self):
        """Настройка оценки рисков"""
        self.risk_assessments = {
            SecurityRisk.LOW: {
                "auto_approve": True,
                "log_level": "info",
                "monitoring": False,
            },
            SecurityRisk.MEDIUM: {
                "auto_approve": False,
                "log_level": "warning",
                "monitoring": True,
            },
            SecurityRisk.HIGH: {
                "auto_approve": False,
                "log_level": "error",
                "monitoring": True,
                "auto_block": True,
            },
            SecurityRisk.CRITICAL: {
                "auto_approve": False,
                "log_level": "critical",
                "monitoring": True,
                "auto_block": True,
                "require_approval": True,
            },
        }

    def _setup_operation_monitoring(self):
        """Настройка мониторинга операций"""
        self.operation_history = []
        self.user_activity = {}

    def _start_real_time_protection(self):
        """Запуск защиты в реальном времени"""
        self.log_activity("Запуск защиты в реальном времени")

    def validate_operation(
        self, operation: str, user: str, params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, SecurityRisk]:
        """
        Валидация операции на безопасность

        Args:
            operation: Название операции
            user: Пользователь, выполняющий операцию
            params: Параметры операции

        Returns:
            Tuple[bool, str, SecurityRisk]: (разрешено, сообщение, уровень риска)
        """
        try:
            # Проверка базовых правил
            if operation in self.operation_blacklist:
                return False, f"Операция {operation} запрещена", SecurityRisk.CRITICAL

            if operation in self.operation_whitelist:
                return True, f"Операция {operation} разрешена", SecurityRisk.LOW

            # Получение правил для операции
            rule = self.security_rules.get(operation, {"risk": SecurityRisk.MEDIUM})
            risk_level = rule.get("risk", SecurityRisk.MEDIUM)

            # Проверка лимитов пользователя
            if not self._check_user_limits(user):
                return False, "Превышен лимит операций пользователя", SecurityRisk.HIGH

            # Проверка критических операций
            if risk_level == SecurityRisk.CRITICAL and self.require_approval_for_critical:
                return (
                    False,
                    f"Критическая операция {operation} требует одобрения",
                    SecurityRisk.CRITICAL,
                )

            # Проверка автоматической блокировки
            if rule.get("auto_block", False) and self.auto_block_high_risk:
                return (
                    False,
                    f"Операция {operation} автоматически заблокирована",
                    SecurityRisk.HIGH,
                )

            # Операция разрешена
            return True, f"Операция {operation} разрешена", risk_level

        except Exception as e:
            self.log_activity(f"Ошибка валидации операции {operation}: {e}", "error")
            return False, f"Ошибка валидации: {e}", SecurityRisk.CRITICAL

    def _check_user_limits(self, user: str) -> bool:
        """Проверка лимитов пользователя"""
        current_time = datetime.now()
        minute_ago = current_time - timedelta(minutes=1)

        # Подсчет операций за последнюю минуту
        user_ops = [
            op
            for op in self.operation_history
            if op.get("user") == user and op.get("timestamp", datetime.min) > minute_ago
        ]

        return len(user_ops) < self.max_operations_per_minute

    def execute_with_protection(
        self,
        operation: str,
        user: str,
        params: Optional[Dict[str, Any]] = None,
        function: Optional[Callable] = None,
    ) -> Tuple[bool, Any, str]:
        """
        Выполнение операции с защитой

        Args:
            operation: Название операции
            user: Пользователь
            params: Параметры
            function: Функция для выполнения

        Returns:
            Tuple[bool, Any, str]: (успех, результат, сообщение)
        """
        try:
            with self.operation_lock:
                # Валидация операции
                allowed, message, risk_level = self.validate_operation(operation, user, params)

                if not allowed:
                    self._log_security_event(
                        operation,
                        user,
                        risk_level,
                        params or {},
                        blocked=True,
                        reason=message,
                    )
                    return False, None, message

                # Создание события безопасности
                event_id = self._generate_event_id(operation, user)
                security_event = SecurityEvent(event_id, operation, user, risk_level, params or {})
                self.security_events[event_id] = security_event

                # Логирование операции
                self._log_operation(operation, user, params or {}, risk_level)

                # Выполнение функции
                if function:
                    start_time = time.time()
                    try:
                        result = function(params or {})
                        execution_time = time.time() - start_time

                        # Успешное выполнение
                        security_event.approved = True
                        self.approved_operations_count += 1
                        self._log_security_event(
                            operation,
                            user,
                            risk_level,
                            params or {},
                            success=True,
                            execution_time=execution_time,
                        )

                        return True, result, "Операция выполнена успешно"

                    except Exception as e:
                        execution_time = time.time() - start_time
                        security_event.blocked = True
                        security_event.reason = str(e)
                        self.blocked_operations_count += 1

                        self._log_security_event(
                            operation,
                            user,
                            risk_level,
                            params or {},
                            error=True,
                            execution_time=execution_time,
                            error_msg=str(e),
                        )

                        return False, None, f"Ошибка выполнения: {e}"
                else:
                    # Операция без функции (только валидация)
                    security_event.approved = True
                    self.approved_operations_count += 1
                    return True, None, "Операция валидирована успешно"

        except Exception as e:
            self.log_activity(f"Ошибка выполнения защищенной операции {operation}: {e}", "error")
            return False, None, f"Системная ошибка: {e}"

    def _generate_event_id(self, operation: str, user: str) -> str:
        """Генерация ID события"""
        timestamp = int(time.time() * 1000)
        data = f"{operation}_{user}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def _log_operation(
        self,
        operation: str,
        user: str,
        params: Dict[str, Any],
        risk_level: SecurityRisk,
    ):
        """Логирование операции"""
        operation_record = {
            "operation": operation,
            "user": user,
            "params": params,
            "risk_level": risk_level.value,
            "timestamp": datetime.now().isoformat(),
        }

        self.operation_history.append(operation_record)
        self.total_operations += 1

        # Обновление активности пользователя
        if user not in self.user_activity:
            self.user_activity[user] = []
        self.user_activity[user].append(operation_record)

    def _log_security_event(
        self,
        operation: str,
        user: str,
        risk_level: SecurityRisk,
        params: Dict[str, Any],
        **kwargs,
    ):
        """Логирование события безопасности"""

        self.log_activity(
            f"Событие безопасности: {operation} от {user} (риск: {risk_level.value})",
            ("warning" if risk_level in [SecurityRisk.MEDIUM, SecurityRisk.HIGH] else "error"),
        )

    def get_security_statistics(self) -> Dict[str, Any]:
        """Получение статистики безопасности"""
        return {
            "total_operations": self.total_operations,
            "blocked_operations": self.blocked_operations_count,
            "approved_operations": self.approved_operations_count,
            "critical_operations": self.critical_operations_count,
            "security_events_count": len(self.security_events),
            "active_users": len(self.user_activity),
            "status": self.status.value,
            "uptime": ((datetime.now() - self.start_time).total_seconds() if self.start_time else 0),
        }

    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение событий безопасности"""
        events = list(self.security_events.values())
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return [event.to_dict() for event in events[:limit]]

    def approve_operation(self, event_id: str, approver: str) -> bool:
        """Одобрение операции"""
        if event_id not in self.security_events:
            return False

        event = self.security_events[event_id]
        event.approved = True
        event.reason = f"Одобрено пользователем {approver}"

        self.log_activity(f"Операция {event.operation} одобрена пользователем {approver}")
        return True

    def block_operation(self, event_id: str, blocker: str, reason: str) -> bool:
        """Блокировка операции"""
        if event_id not in self.security_events:
            return False

        event = self.security_events[event_id]
        event.blocked = True
        event.reason = f"Заблокировано пользователем {blocker}: {reason}"

        self.log_activity(f"Операция {event.operation} заблокирована пользователем {blocker}: {reason}")
        return True

    def add_security_rule(self, operation: str, rule: Dict[str, Any]) -> bool:
        """Добавление правила безопасности"""
        try:
            self.security_rules[operation] = rule
            self.log_activity(f"Добавлено правило безопасности для операции {operation}")
            return True
        except Exception as e:
            self.log_activity(f"Ошибка добавления правила безопасности: {e}", "error")
            return False

    def remove_security_rule(self, operation: str) -> bool:
        """Удаление правила безопасности"""
        try:
            if operation in self.security_rules:
                del self.security_rules[operation]
                self.log_activity(f"Удалено правило безопасности для операции {operation}")
                return True
            return False
        except Exception as e:
            self.log_activity(f"Ошибка удаления правила безопасности: {e}", "error")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы безопасности"""
        return {
            "name": self.name,
            "status": self.status.value,
            "real_time_protection": self.enable_real_time_protection,
            "auto_block_enabled": self.auto_block_high_risk,
            "approval_required": self.require_approval_for_critical,
            "security_rules_count": len(self.security_rules),
            "statistics": self.get_security_statistics(),
        }


# Глобальный экземпляр системы безопасности
SECURITY_LAYER = SecurityLayer()
