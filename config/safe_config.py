# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Safe Configuration
Безопасная конфигурация системы без деструктивных функций

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

from enum import Enum
from typing import Any, Dict, Optional, Tuple


class SecurityMode(Enum):
    """Режимы безопасности"""

    SAFE = "safe"  # Только чтение, без изменений
    MONITOR = "monitor"  # Мониторинг без действий
    READONLY = "readonly"  # Только чтение данных


class SafeConfiguration:
    """Безопасная конфигурация системы ALADDIN"""

    def __init__(self):
        # Основные настройки безопасности
        self.security_mode = SecurityMode.SAFE
        self.enable_destructive_operations = False
        self.enable_file_operations = False
        self.enable_system_commands = False
        self.enable_network_operations = False

        # Разрешенные операции
        self.allowed_operations = {
            "read": True,
            "monitor": True,
            "log": True,
            "analyze": True,
            "report": True,
            "authenticate": True,
            "validate": True,
            "test": True,
        }

        # Запрещенные операции
        self.forbidden_operations = {
            "delete": True,
            "remove": True,
            "unlink": True,
            "rmdir": True,
            "rmtree": True,
            "clear": True,
            "clean": True,
            "purge": True,
            "destroy": True,
            "wipe": True,
            "modify": True,
            "write": True,
            "create": True,
            "update": True,
            "execute": True,
            "run": True,
            "system": True,
            "subprocess": True,
            "eval": True,
            "exec": True,
        }

        # Безопасные модули (только чтение и анализ)
        self.safe_modules = {
            "core.base": True,
            "core.service_base": True,
            "core.security_base": True,
            "core.database": False,  # Отключен - может изменять данные
            "core.configuration": False,  # Отключен - может изменять конфиг
            "core.logging_module": True,
            "security.authentication": True,
            # Отключен - может выполнять функции
            "security.safe_function_manager": False,
            "security.threat_intelligence": True,
            # Отключен - может выполнять действия
            "security.incident_response": False,
            "security.compliance_manager": True,
            "security.security_analytics": True,
            "security.security_monitoring": True,  # Только мониторинг
            "security.safe_security_monitoring": True,  # Безопасный мониторинг
            "security.security_reporting": True,
            "security.security_audit": True,
            "security.security_policy": True,
        }

        # Безопасные функции мониторинга
        self.safe_monitoring_functions = {
            "monitor_threats": True,
            "analyze_logs": True,
            "generate_reports": True,
            "check_compliance": True,
            "audit_security": True,
            "detect_anomalies": True,
            "track_metrics": True,
            "validate_configuration": True,
        }

        # Запрещенные функции мониторинга
        self.forbidden_monitoring_functions = {
            "remove_rule": True,
            "delete_alert": True,
            "clear_logs": True,
            "purge_data": True,
            "cleanup_files": True,
            "execute_action": True,
            "modify_config": True,
            "update_policy": True,
            "delete_backup": True,
            "remove_service": True,
        }

        # Настройки логирования (только запись логов)
        self.logging_config = {
            "enable_logging": True,
            "log_level": "INFO",
            "log_file_rotation": True,
            "max_log_size": "10MB",
            "log_retention_days": 30,
            "enable_audit_trail": True,
            "audit_retention_days": 90,
        }

        # Настройки базы данных (только чтение)
        self.database_config = {
            "enable_database": False,  # Отключена - может изменять данные
            "read_only_mode": True,
            "enable_backups": False,  # Отключены - могут удалять файлы
            "enable_cleanup": False,  # Отключена - может удалять данные
            "enable_migrations": False,  # Отключены - могут изменять схему
        }

        # Настройки сети (отключены)
        self.network_config = {
            "enable_network": False,
            "enable_external_apis": False,
            "enable_webhooks": False,
            "enable_remote_commands": False,
        }

        # Настройки файловой системы (только чтение)
        self.filesystem_config = {
            "enable_file_operations": False,
            "read_only_mode": True,
            "enable_backups": False,
            "enable_cleanup": False,
            "enable_temp_files": False,
        }

    def is_operation_allowed(self, operation: str) -> bool:
        """Проверка разрешения операции"""
        if self.security_mode == SecurityMode.SAFE:
            return self.allowed_operations.get(operation, False)
        elif self.security_mode == SecurityMode.MONITOR:
            return operation in ["read", "monitor", "log", "analyze", "report"]
        elif self.security_mode == SecurityMode.READONLY:
            return operation in ["read", "analyze", "report"]
        return False

    def is_operation_forbidden(self, operation: str) -> bool:
        """Проверка запрета операции"""
        return self.forbidden_operations.get(operation, False)

    def is_module_safe(self, module_name: str) -> bool:
        """Проверка безопасности модуля"""
        return self.safe_modules.get(module_name, False)

    def is_monitoring_function_safe(self, function_name: str) -> bool:
        """Проверка безопасности функции мониторинга"""
        if self.forbidden_monitoring_functions.get(function_name, False):
            return False
        return self.safe_monitoring_functions.get(function_name, False)

    def get_safe_config(self) -> Dict[str, Any]:
        """Получение безопасной конфигурации"""
        return {
            "security_mode": self.security_mode.value,
            "enable_destructive_operations": (
                self.enable_destructive_operations
            ),
            "enable_file_operations": self.enable_file_operations,
            "enable_system_commands": self.enable_system_commands,
            "enable_network_operations": self.enable_network_operations,
            "allowed_operations": self.allowed_operations,
            "forbidden_operations": self.forbidden_operations,
            "safe_modules": self.safe_modules,
            "safe_monitoring_functions": (
                self.safe_monitoring_functions
            ),
            "forbidden_monitoring_functions": (
                self.forbidden_monitoring_functions
            ),
            "logging_config": self.logging_config,
            "database_config": self.database_config,
            "network_config": self.network_config,
            "filesystem_config": self.filesystem_config,
        }

    def validate_operation(self,
                           operation: str,
                           module: Optional[str] = None,
                           function: Optional[str] = None) -> Tuple[bool,
                                                                    str]:
        """Валидация операции на безопасность"""
        # Проверка запрещенных операций
        if self.is_operation_forbidden(operation):
            return False, f"Операция '{operation}' запрещена в безопасном режиме"

        # Проверка разрешенных операций
        if not self.is_operation_allowed(operation):
            return False, f"Операция '{operation}' не разрешена в текущем режиме безопасности"

        # Проверка модуля
        if module and not self.is_module_safe(module):
            return False, f"Модуль '{module}' отключен в безопасном режиме"

        # Проверка функции мониторинга
        if function and not self.is_monitoring_function_safe(function):
            return False, f"Функция '{function}' запрещена в безопасном режиме"

        return True, "Операция разрешена"


# Глобальная безопасная конфигурация
SAFE_CONFIG = SafeConfiguration()

# Экспорт безопасных настроек
SAFE_SETTINGS = SAFE_CONFIG.get_safe_config()
