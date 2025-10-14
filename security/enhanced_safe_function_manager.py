# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Enhanced Safe Function Manager
Расширенный менеджер безопасных функций с поддержкой компонентов

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-09
"""

import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from core.base import ComponentStatus, SecurityBase, SecurityLevel
from security.safe_function_manager import (
    FunctionStatus,
    SafeFunctionManager,
    SecurityFunction,
)


class ComponentMode(Enum):
    """Режимы работы компонентов"""

    PRODUCTION = "production"
    TEST = "test"
    SAFE = "safe"
    MINIMAL = "minimal"


class SecurityComponentFactory:
    """Фабрика для создания компонентов безопасности"""

    @staticmethod
    def create_monitoring_manager(mode: str = "full") -> Any:
        """Создание менеджера мониторинга в зависимости от режима"""
        if mode == "safe":
            from security.safe_security_monitoring import (
                SafeSecurityMonitoringManager,
            )

            return SafeSecurityMonitoringManager()
        elif mode == "advanced":
            from security.advanced_monitoring_manager import (
                AdvancedMonitoringManager,
            )

            return AdvancedMonitoringManager()
        else:
            from security.security_monitoring import SecurityMonitoringManager

            return SecurityMonitoringManager()

    @staticmethod
    def create_integration_manager(mode: str = "production") -> Any:
        """Создание менеджера интеграции в зависимости от режима"""
        if mode == "test":
            from security.simple_security_integration import (
                SimpleSecurityIntegration,
            )

            return SimpleSecurityIntegration()
        elif mode == "minimal":
            from security.minimal_security_integration import (
                MinimalSecurityIntegration,
            )

            return MinimalSecurityIntegration()
        else:
            from security.security_integration import SecurityIntegration

            return SecurityIntegration()

    @staticmethod
    def create_data_manager(type: str = "smart") -> Any:
        """Создание менеджера данных в зависимости от типа"""
        if type == "protected":
            from security.protected_data_manager import ProtectedDataManager

            return ProtectedDataManager()
        else:
            from security.smart_data_manager import SmartDataManager

            return SmartDataManager()


class EnhancedSafeFunctionManager(SafeFunctionManager):
    """Расширенный менеджер безопасных функций с поддержкой компонентов"""

    def __init__(
        self,
        name: str = "EnhancedSafeFunctionManager",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)

        # Дополнительные настройки для компонентов
        self.component_mode = ComponentMode.PRODUCTION
        self.available_modes = [mode.value for mode in ComponentMode]

        # Словарь активных компонентов
        self.active_components: Dict[str, Any] = {}
        self.component_status: Dict[str, ComponentStatus] = {}

        # Статистика компонентов
        self.total_components = 0
        self.active_components_count = 0
        self.failed_components = 0

    def set_component_mode(self, mode: str) -> bool:
        """Установка режима работы компонентов"""
        try:
            if mode not in self.available_modes:
                self.log_activity(
                    f"Неверный режим: {mode}. "
                    f"Доступные: {self.available_modes}",
                    "error",
                )
                return False

            with self.function_lock:
                old_mode = self.component_mode.value
                self.component_mode = ComponentMode(mode)
                self.log_activity(
                    f"Режим компонентов изменен с {old_mode} на {mode}"
                )

                # Переинициализация компонентов при смене режима
                if self.active_components:
                    self._reinitialize_components()

                return True

        except Exception as e:
            self.log_activity(f"Ошибка смены режима компонентов: {e}", "error")
            return False

    def get_component(self, component_type: str, mode: str = None) -> Any:
        """Получение компонента безопасности"""
        try:
            if mode is None:
                mode = self.component_mode.value

            component_key = f"{component_type}_{mode}"

            if component_key not in self.active_components:
                # Создание компонента через фабрику
                if component_type == "monitoring":
                    component = (
                        SecurityComponentFactory.create_monitoring_manager(
                            mode
                        )
                    )
                elif component_type == "integration":
                    component = (
                        SecurityComponentFactory.create_integration_manager(
                            mode
                        )
                    )
                elif component_type == "data":
                    component = SecurityComponentFactory.create_data_manager(
                        mode
                    )
                else:
                    self.log_activity(
                        f"Неизвестный тип компонента: {component_type}",
                        "error",
                    )
                    return None

                if component:
                    self.active_components[component_key] = component
                    self.component_status[component_key] = (
                        ComponentStatus.INITIALIZING
                    )

                    # Инициализация компонента
                    if hasattr(component, "initialize"):
                        success = component.initialize()
                        self.component_status[component_key] = (
                            ComponentStatus.RUNNING
                            if success
                            else ComponentStatus.ERROR
                        )
                        if success:
                            self.active_components_count += 1
                        else:
                            self.failed_components += 1
                    else:
                        self.component_status[component_key] = (
                            ComponentStatus.RUNNING
                        )
                        self.active_components_count += 1

                    self.total_components += 1

            return self.active_components.get(component_key)

        except Exception as e:
            self.log_activity(
                f"Ошибка получения компонента {component_type}: {e}", "error"
            )
            return None

    def get_component_status(self) -> Dict[str, Any]:
        """Получение статуса всех компонентов"""
        try:
            status = {
                "component_mode": self.component_mode.value,
                "total_components": self.total_components,
                "active_components": self.active_components_count,
                "failed_components": self.failed_components,
                "components": {},
            }

            for component_key, component in self.active_components.items():
                try:
                    component_status = self.component_status.get(
                        component_key, ComponentStatus.UNKNOWN
                    )
                    status["components"][component_key] = {
                        "status": component_status.value,
                        "type": type(component).__name__,
                        "has_initialize": hasattr(component, "initialize"),
                        "has_get_status": hasattr(component, "get_status"),
                    }
                except Exception as e:
                    status["components"][component_key] = {
                        "status": "error",
                        "error": str(e),
                    }

            return status

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статуса компонентов: {e}", "error"
            )
            return {"error": str(e)}

    def get_security_dashboard(self) -> Dict[str, Any]:
        """Получение данных для дашборда безопасности"""
        try:
            # Базовые данные от SafeFunctionManager
            function_stats = self.get_safe_function_stats()

            # Данные компонентов
            component_status = self.get_component_status()

            dashboard_data = {
                "functions": function_stats,
                "components": component_status,
                "system_info": {
                    "mode": self.component_mode.value,
                    "status": self.status.value,
                    "uptime": (
                        (datetime.now() - self.start_time).total_seconds()
                        if self.start_time
                        else 0
                    ),
                },
                "timestamp": datetime.now().isoformat(),
            }

            return dashboard_data

        except Exception as e:
            self.log_activity(
                f"Ошибка получения данных дашборда: {e}", "error"
            )
            return {"error": str(e)}

    def _reinitialize_components(self) -> None:
        """Переинициализация компонентов при смене режима"""
        try:
            self.log_activity(
                f"Переинициализация компонентов для режима "
                f"{self.component_mode.value}"
            )

            for component_key, component in self.active_components.items():
                try:
                    if hasattr(component, "initialize"):
                        success = component.initialize()
                        self.component_status[component_key] = (
                            ComponentStatus.RUNNING
                            if success
                            else ComponentStatus.ERROR
                        )
                except Exception as e:
                    self.log_activity(
                        f"Ошибка переинициализации {component_key}: {e}",
                        "error",
                    )
                    self.component_status[component_key] = (
                        ComponentStatus.ERROR
                    )

        except Exception as e:
            self.log_activity(
                f"Ошибка переинициализации компонентов: {e}", "error"
            )

    def get_component_mode(self) -> str:
        """Получение текущего режима компонентов"""
        return self.component_mode.value

    def get_available_modes(self) -> List[str]:
        """Получение списка доступных режимов"""
        return self.available_modes.copy()

    def get_activity_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение журнала активности"""
        try:
            # Возвращаем последние записи из журнала
            if hasattr(self, 'activity_log') and self.activity_log:
                return self.activity_log[-limit:]
            else:
                # Если журнал не существует, возвращаем пустой список
                return []
        except Exception as e:
            self.log_activity(
                f"Ошибка получения журнала активности: {e}", "error"
            )
            return []

    def get_component_info(self, component_key: str = None) -> Dict[str, Any]:
        """Получение информации о компоненте"""
        try:
            if component_key is None:
                # Возвращаем информацию о всех компонентах
                return self.get_component_status()
            else:
                # Возвращаем информацию о конкретном компоненте
                if component_key in self.active_components:
                    component = self.active_components[component_key]
                    status = self.component_status.get(
                        component_key, ComponentStatus.UNKNOWN
                    )
                    return {
                        "key": component_key,
                        "status": status.value,
                        "type": type(component).__name__,
                        "has_initialize": hasattr(component, "initialize"),
                        "has_get_status": hasattr(component, "get_status"),
                    }
                else:
                    return {"error": f"Компонент {component_key} не найден"}
        except Exception as e:
            self.log_activity(
                f"Ошибка получения информации о компоненте: {e}", "error"
            )
            return {"error": str(e)}

    def get_security_level(self) -> str:
        """Получение уровня безопасности менеджера"""
        return SecurityLevel.HIGH.value

    def is_critical(self) -> bool:
        """Проверка критичности менеджера"""
        return True

    def register_component_function(
        self, component_type: str, mode: str = None
    ) -> bool:
        """Регистрация функции для работы с компонентом"""
        try:
            if mode is None:
                mode = self.component_mode.value

            function_id = f"get_{component_type}_manager"
            function_name = f"Get {component_type.title()} Manager"
            description = (
                f"Получение менеджера {component_type} в режиме {mode}"
            )

            success = self.register_function(
                function_id=function_id,
                name=function_name,
                description=description,
                function_type="component",
                security_level=SecurityLevel.HIGH,
                is_critical=True,
                auto_enable=True,
            )

            if success:
                self.log_activity(
                    f"Зарегистрирована функция компонента: {function_name}"
                )

            return success

        except Exception as e:
            self.log_activity(
                f"Ошибка регистрации функции компонента: {e}", "error"
            )
            return False


# Глобальный экземпляр расширенного менеджера
ENHANCED_SAFE_FUNCTION_MANAGER = EnhancedSafeFunctionManager()
