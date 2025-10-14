# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Secure Wrapper
Обертка для безопасного выполнения операций существующих модулей

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import functools
from typing import Any, Callable, Dict, Optional, Tuple

from security.access_control import ACCESS_CONTROL, Permission
from security.audit_system import AUDIT_SYSTEM, AuditLevel
from security.security_layer import SECURITY_LAYER, SecurityRisk

# Создаем алиас для обратной совместимости (перемещаем в конец файла)


def secure_operation(
    operation_name: str,
    required_permission: Optional[Permission] = None,
    risk_level: SecurityRisk = SecurityRisk.MEDIUM,
):
    """
    Декоратор для безопасного выполнения операций

    Args:
        operation_name: Название операции
        required_permission: Требуемое разрешение
        risk_level: Уровень риска операции
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Получение контекста (пользователь, сессия)
            user_context = _get_user_context(args, kwargs)
            user = user_context.get("user", "system")
            session_id = user_context.get("session_id", None)

            # Проверка разрешений
            if required_permission and session_id:
                if not ACCESS_CONTROL.check_permission(session_id, required_permission):
                    AUDIT_SYSTEM.log_audit_event(
                        event_type="access_denied",
                        user=user,
                        operation=operation_name,
                        level=AuditLevel.SECURITY,
                        details={
                            "reason": "insufficient_permissions",
                            "required_permission": required_permission.value,
                            "function": func.__name__,
                        },
                    )
                    raise PermissionError(f"Недостаточно прав для выполнения операции {operation_name}")

            # Выполнение с защитой
            return SECURITY_LAYER.execute_with_protection(
                operation=operation_name,
                user=user,
                params={"args": args, "kwargs": kwargs},
                function=lambda params: func(*params["args"], **params["kwargs"]),
            )

        return wrapper

    return decorator


def _get_user_context(args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Получение контекста пользователя из аргументов"""
    context = {"user": "system", "session_id": None}

    # Поиск пользователя в аргументах
    for arg in args:
        if isinstance(arg, dict) and "user" in arg:
            context["user"] = arg["user"]
        if isinstance(arg, dict) and "session_id" in arg:
            context["session_id"] = arg["session_id"]

    # Поиск в kwargs
    if "user" in kwargs:
        context["user"] = kwargs["user"]
    if "session_id" in kwargs:
        context["session_id"] = kwargs["session_id"]

    return context


class SecureModuleWrapper:
    """Обертка для безопасного выполнения модулей"""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.security_layer = SECURITY_LAYER
        self.audit_system = AUDIT_SYSTEM
        self.access_control = ACCESS_CONTROL

    def execute_secure_operation(
        self,
        operation: str,
        user: str,
        params: Optional[Dict[str, Any]] = None,
        function: Optional[Callable] = None,
        required_permission: Optional[Permission] = None,
    ) -> Tuple[bool, Any, str]:
        """
        Безопасное выполнение операции

        Args:
            operation: Название операции
            user: Пользователь
            params: Параметры
            function: Функция для выполнения
            required_permission: Требуемое разрешение

        Returns:
            Tuple[bool, Any, str]: (успех, результат, сообщение)
        """
        try:
            # Логирование начала операции
            self.audit_system.log_audit_event(
                event_type="operation_start",
                user=user,
                operation=operation,
                level=AuditLevel.INFO,
                details={
                    "module": self.module_name,
                    "params": params,
                    "required_permission": (required_permission.value if required_permission else None),
                },
            )

            # Выполнение с защитой
            success, result, message = self.security_layer.execute_with_protection(
                operation=operation, user=user, params=params, function=function
            )

            # Логирование результата
            audit_level = AuditLevel.INFO if success else AuditLevel.ERROR
            self.audit_system.log_audit_event(
                event_type="operation_complete" if success else "operation_failed",
                user=user,
                operation=operation,
                level=audit_level,
                details={
                    "module": self.module_name,
                    "success": success,
                    "result": str(result) if result else None,
                    "message": message,
                },
            )

            return success, result, message

        except Exception as e:
            # Логирование ошибки
            self.audit_system.log_audit_event(
                event_type="operation_error",
                user=user,
                operation=operation,
                level=AuditLevel.ERROR,
                details={
                    "module": self.module_name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

            return False, None, f"Ошибка выполнения операции: {e}"


class SecureDatabaseWrapper(SecureModuleWrapper):
    """Безопасная обертка для Database модуля"""

    def __init__(self, database_module):
        super().__init__("Database")
        self.database = database_module

    def execute_query(self, user: str, query: str, params: Optional[tuple] = None) -> Tuple[bool, Any, str]:
        """Безопасное выполнение запроса на чтение"""
        return self.execute_secure_operation(
            operation="read_data",
            user=user,
            params={"query": query, "params": params},
            function=lambda p: self.database.execute_query(p["query"], p["params"]),
            required_permission=Permission.READ_DATA,
        )

    def execute_update(self, user: str, query: str, params: Optional[tuple] = None) -> Tuple[bool, Any, str]:
        """Безопасное выполнение запроса на изменение"""
        return self.execute_secure_operation(
            operation="write_data",
            user=user,
            params={"query": query, "params": params},
            function=lambda p: self.database.execute_update(p["query"], p["params"]),
            required_permission=Permission.WRITE_DATA,
        )

    def delete_user(self, user: str, user_id: str) -> Tuple[bool, Any, str]:
        """Безопасное удаление пользователя"""
        return self.execute_secure_operation(
            operation="delete_user",
            user=user,
            params={"user_id": user_id},
            function=lambda p: self.database.delete_user(p["user_id"]),
            required_permission=Permission.DELETE_DATA,
        )


class SecureConfigurationWrapper(SecureModuleWrapper):
    """Безопасная обертка для Configuration модуля"""

    def __init__(self, config_module):
        super().__init__("Configuration")
        self.config = config_module

    def get_config(self, user: str, key: str) -> Tuple[bool, Any, str]:
        """Безопасное получение конфигурации"""
        return self.execute_secure_operation(
            operation="read_config",
            user=user,
            params={"key": key},
            function=lambda p: self.config.get_config(p["key"]),
            required_permission=Permission.READ_CONFIG,
        )

    def set_config(self, user: str, key: str, value: Any) -> Tuple[bool, Any, str]:
        """Безопасное изменение конфигурации"""
        return self.execute_secure_operation(
            operation="modify_config",
            user=user,
            params={"key": key, "value": value},
            function=lambda p: self.config.set_config(p["key"], p["value"]),
            required_permission=Permission.WRITE_CONFIG,
        )


class SecureIncidentResponseWrapper(SecureModuleWrapper):
    """Безопасная обертка для IncidentResponse модуля"""

    def __init__(self, incident_module):
        super().__init__("IncidentResponse")
        self.incident = incident_module

    def analyze_incident(self, user: str, incident_data: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """Безопасный анализ инцидента"""
        return self.execute_secure_operation(
            operation="analyze_incident",
            user=user,
            params={"incident_data": incident_data},
            function=lambda p: self.incident.analyze_incident(p["incident_data"]),
            required_permission=Permission.VIEW_SECURITY_EVENTS,
        )

    def auto_respond(self, user: str, incident_id: str) -> Tuple[bool, Any, str]:
        """Безопасное автоматическое реагирование"""
        return self.execute_secure_operation(
            operation="auto_respond",
            user=user,
            params={"incident_id": incident_id},
            function=lambda p: self.incident.auto_respond(p["incident_id"]),
            required_permission=Permission.EXECUTE_FUNCTIONS,
        )


class SecureFunctionManagerWrapper(SecureModuleWrapper):
    """Безопасная обертка для SafeFunctionManager"""

    def __init__(self, function_manager):
        super().__init__("SafeFunctionManager")
        self.function_manager = function_manager

    def execute_function(
        self, user: str, function_id: str, params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Any, str]:
        """Безопасное выполнение функции"""
        return self.execute_secure_operation(
            operation="execute_function",
            user=user,
            params={"function_id": function_id, "params": params},
            function=lambda p: self.function_manager.execute_function(p["function_id"], p["params"]),
            required_permission=Permission.EXECUTE_FUNCTIONS,
        )

    def register_function(self, user: str, function_id: str, name: str, description: str) -> Tuple[bool, Any, str]:
        """Безопасная регистрация функции"""
        return self.execute_secure_operation(
            operation="register_function",
            user=user,
            params={
                "function_id": function_id,
                "name": name,
                "description": description,
            },
            function=lambda p: self.function_manager.register_function(
                p["function_id"], p["name"], p["description"], "custom"
            ),
            required_permission=Permission.MANAGE_SYSTEM,
        )


# Функция для создания безопасных оберток
def create_secure_wrapper(module, module_name: str) -> SecureModuleWrapper:
    """Создание безопасной обертки для модуля"""
    if module_name == "Database":
        return SecureDatabaseWrapper(module)
    elif module_name == "Configuration":
        return SecureConfigurationWrapper(module)
    elif module_name == "IncidentResponse":
        return SecureIncidentResponseWrapper(module)
    elif module_name == "SafeFunctionManager":
        return SecureFunctionManagerWrapper(module)
    else:
        return SecureModuleWrapper(module_name)


# Глобальные безопасные обертки
SECURE_WRAPPERS = {}

# Создаем алиас для обратной совместимости
SecureWrapper = SecureModuleWrapper
