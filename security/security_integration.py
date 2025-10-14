# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Integration
Интеграция системы безопасности с существующими модулями

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from core.base import ComponentStatus, SecurityBase
from security.access_control import ACCESS_CONTROL
from security.audit_system import AUDIT_SYSTEM
from security.secure_wrapper import SECURE_WRAPPERS, create_secure_wrapper
from security.security_layer import SECURITY_LAYER


class SecurityIntegration(SecurityBase):
    """Интеграция системы безопасности"""

    def __init__(self, name: str = "SecurityIntegration", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Интегрированные модули
        self.integrated_modules = {}
        self.secure_wrappers = {}
        self.module_security_status = {}

        # Статистика интеграции
        self.total_modules = 0
        self.secured_modules = 0
        self.integration_errors = 0

        # Конфигурация интеграции
        self.auto_integrate = config.get("auto_integrate", True) if config else True
        self.enable_wrappers = config.get("enable_wrappers", True) if config else True
        self.strict_mode = config.get("strict_mode", True) if config else True

    def initialize(self) -> bool:
        """Инициализация интеграции безопасности"""
        try:
            self.log_activity(f"Инициализация интеграции безопасности {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Инициализация компонентов безопасности
            self._initialize_security_components()

            # Интеграция существующих модулей
            if self.auto_integrate:
                self._integrate_existing_modules()

            # Создание безопасных оберток
            if self.enable_wrappers:
                self._create_secure_wrappers()

            # Валидация интеграции
            self._validate_integration()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(f"Интеграция безопасности {self.name} успешно инициализирована")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации интеграции безопасности: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def _initialize_security_components(self):
        """Инициализация компонентов безопасности"""
        try:
            # Инициализация SecurityLayer
            if not SECURITY_LAYER.initialize():
                raise Exception("Ошибка инициализации SecurityLayer")

            # Инициализация AuditSystem
            if not AUDIT_SYSTEM.initialize():
                raise Exception("Ошибка инициализации AuditSystem")

            # Инициализация AccessControl
            if not ACCESS_CONTROL.initialize():
                raise Exception("Ошибка инициализации AccessControl")

            self.log_activity("Все компоненты безопасности инициализированы")

        except Exception as e:
            self.log_activity(f"Ошибка инициализации компонентов безопасности: {e}", "error")
            raise

    def _integrate_existing_modules(self):
        """Интеграция существующих модулей"""
        try:
            # Список модулей для интеграции (только те, которые точно
            # существуют)
            modules_to_integrate = [
                "core.logging_module",
                "security.safe_function_manager",
            ]

            for module_name in modules_to_integrate:
                try:
                    self._integrate_module(module_name)
                    self.secured_modules += 1
                except Exception as e:
                    self.integration_errors += 1
                    self.log_activity(f"Ошибка интеграции модуля {module_name}: {e}", "warning")

            self.total_modules = len(modules_to_integrate)
            self.log_activity(f"Интегрировано {self.secured_modules} из {self.total_modules} модулей")

        except Exception as e:
            self.log_activity(f"Ошибка интеграции модулей: {e}", "error")
            raise

    def _integrate_module(self, module_name: str):
        """Интеграция отдельного модуля"""
        try:
            # Импорт модуля
            module = self._import_module(module_name)
            if not module:
                raise Exception(f"Модуль {module_name} не найден")

            # Создание безопасной обертки
            if self.enable_wrappers:
                wrapper = create_secure_wrapper(module, module_name.split(".")[-1])
                self.secure_wrappers[module_name] = wrapper
                SECURE_WRAPPERS[module_name] = wrapper

            # Регистрация модуля
            self.integrated_modules[module_name] = {
                "module": module,
                "wrapper": self.secure_wrappers.get(module_name),
                "integrated_at": datetime.now(),
                "security_status": "secured",
            }

            # Логирование интеграции
            AUDIT_SYSTEM.log_audit_event(
                event_type="module_integration",
                user="system",
                operation="integrate_module",
                level=AUDIT_SYSTEM.AuditLevel.INFO,
                details={
                    "module_name": module_name,
                    "integration_method": ("secure_wrapper" if self.enable_wrappers else "direct"),
                },
            )

            self.log_activity(f"Модуль {module_name} успешно интегрирован")

        except Exception as e:
            self.log_activity(f"Ошибка интеграции модуля {module_name}: {e}", "error")
            raise

    def _import_module(self, module_name: str):
        """Импорт модуля"""
        try:
            # Попытка импорта модуля (только существующие)
            if module_name == "core.logging_module":
                from core.logging_module import LoggingModule

                return LoggingModule()
            elif module_name == "security.safe_function_manager":
                from security.safe_function_manager import SafeFunctionManager

                return SafeFunctionManager()
            else:
                return None

        except ImportError as e:
            self.log_activity(f"Ошибка импорта модуля {module_name}: {e}", "warning")
            return None
        except Exception as e:
            self.log_activity(f"Ошибка создания экземпляра модуля {module_name}: {e}", "warning")
            return None

    def _create_secure_wrappers(self):
        """Создание безопасных оберток"""
        try:
            for module_name, module_info in self.integrated_modules.items():
                if module_info["module"] and not module_info["wrapper"]:
                    wrapper = create_secure_wrapper(module_info["module"], module_name.split(".")[-1])
                    self.secure_wrappers[module_name] = wrapper
                    module_info["wrapper"] = wrapper

                    self.log_activity(f"Создана безопасная обертка для {module_name}")

        except Exception as e:
            self.log_activity(f"Ошибка создания безопасных оберток: {e}", "error")

    def _validate_integration(self):
        """Валидация интеграции"""
        try:
            validation_results = {
                "security_layer": SECURITY_LAYER.status == ComponentStatus.RUNNING,
                "audit_system": AUDIT_SYSTEM.status == ComponentStatus.RUNNING,
                "access_control": ACCESS_CONTROL.status == ComponentStatus.RUNNING,
                "integrated_modules": len(self.integrated_modules),
                "secure_wrappers": len(self.secure_wrappers),
            }

            all_valid = all(validation_results.values())

            if not all_valid:
                failed_components = [k for k, v in validation_results.items() if not v]
                raise Exception(f"Валидация не пройдена для компонентов: {failed_components}")

            self.log_activity("Валидация интеграции пройдена успешно")

        except Exception as e:
            self.log_activity(f"Ошибка валидации интеграции: {e}", "error")
            raise

    def get_secure_module(self, module_name: str, user: str = "system"):
        """
        Получение безопасного модуля

        Args:
            module_name: Название модуля
            user: Пользователь

        Returns:
            Безопасная обертка модуля или None
        """
        try:
            if module_name in self.secure_wrappers:
                # Логирование доступа к модулю
                AUDIT_SYSTEM.log_audit_event(
                    event_type="module_access",
                    user=user,
                    operation="get_secure_module",
                    level=AUDIT_SYSTEM.AuditLevel.INFO,
                    details={"module_name": module_name},
                )

                return self.secure_wrappers[module_name]
            else:
                self.log_activity(f"Модуль {module_name} не найден в безопасных обертках", "warning")
                return None

        except Exception as e:
            self.log_activity(f"Ошибка получения безопасного модуля {module_name}: {e}", "error")
            return None

    def execute_secure_operation(
        self, module_name: str, operation: str, user: str, params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Any, str]:
        """
        Выполнение безопасной операции

        Args:
            module_name: Название модуля
            operation: Операция
            user: Пользователь
            params: Параметры

        Returns:
            Tuple[bool, Any, str]: (успех, результат, сообщение)
        """
        try:
            secure_module = self.get_secure_module(module_name, user)
            if not secure_module:
                return False, None, f"Модуль {module_name} не доступен"

            return secure_module.execute_secure_operation(operation=operation, user=user, params=params)

        except Exception as e:
            self.log_activity(f"Ошибка выполнения безопасной операции: {e}", "error")
            return False, None, f"Ошибка выполнения операции: {e}"

    def get_integration_status(self) -> Dict[str, Any]:
        """Получение статуса интеграции"""
        return {
            "total_modules": self.total_modules,
            "secured_modules": self.secured_modules,
            "integration_errors": self.integration_errors,
            "integration_success_rate": (
                (self.secured_modules / self.total_modules * 100) if self.total_modules > 0 else 0
            ),
            "integrated_modules": list(self.integrated_modules.keys()),
            "secure_wrappers": list(self.secure_wrappers.keys()),
            "security_components": {
                "security_layer": SECURITY_LAYER.status.value,
                "audit_system": AUDIT_SYSTEM.status.value,
                "access_control": ACCESS_CONTROL.status.value,
            },
        }

    def get_security_statistics(self) -> Dict[str, Any]:
        """Получение статистики безопасности"""
        return {
            "security_layer": SECURITY_LAYER.get_security_statistics(),
            "audit_system": AUDIT_SYSTEM.get_audit_statistics(),
            "access_control": ACCESS_CONTROL.get_access_statistics(),
            "integration": self.get_integration_status(),
        }

    def generate_security_report(self) -> Dict[str, Any]:
        """Генерация отчета по безопасности"""
        return {
            "report_id": f"security_integration_report_{int(datetime.now().timestamp())}",
            "generated_at": datetime.now().isoformat(),
            "integration_status": self.get_integration_status(),
            "security_statistics": self.get_security_statistics(),
            "component_status": {
                "security_layer": SECURITY_LAYER.get_status(),
                "audit_system": AUDIT_SYSTEM.get_status(),
                "access_control": ACCESS_CONTROL.get_status(),
            },
            "summary": {
                "total_modules": self.total_modules,
                "secured_modules": self.secured_modules,
                "security_level": ("HIGH" if self.secured_modules == self.total_modules else "MEDIUM"),
                "integration_complete": self.secured_modules == self.total_modules,
            },
        }

    def stop(self):
        """Остановка интеграции безопасности"""
        self.log_activity(f"Остановка интеграции безопасности {self.name}")

        # Остановка компонентов безопасности
        try:
            SECURITY_LAYER.stop()
            AUDIT_SYSTEM.stop()
            ACCESS_CONTROL.stop()
        except Exception as e:
            self.log_activity(f"Ошибка остановки компонентов безопасности: {e}", "error")

        self.status = ComponentStatus.STOPPED
        self.log_activity(f"Интеграция безопасности {self.name} остановлена")

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса интеграции безопасности"""
        return {
            "name": self.name,
            "status": self.status.value,
            "auto_integrate": self.auto_integrate,
            "enable_wrappers": self.enable_wrappers,
            "strict_mode": self.strict_mode,
            "integration_status": self.get_integration_status(),
        }


# Глобальный экземпляр интеграции безопасности
SECURITY_INTEGRATION = SecurityIntegration()
