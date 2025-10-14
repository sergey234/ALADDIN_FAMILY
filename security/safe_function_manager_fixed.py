# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Safe Function Manager
Главный менеджер безопасных функций ALADDIN

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.base import ComponentStatus, SecurityBase, SecurityLevel


class FunctionStatus(Enum):
    """Статусы функций"""

    DISABLED = "disabled"
    ENABLED = "enabled"
    TESTING = "testing"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SecurityFunction:
    """Класс для представления безопасной функции"""

    def __init__(
        self,
        function_id: str,
        name: str,
        description: str,
        function_type: str,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
    ):
        self.function_id = function_id
        self.name = name
        self.description = description
        self.function_type = function_type
        self.security_level = security_level
        self.status = FunctionStatus.DISABLED
        self.created_at = datetime.now()
        self.last_execution = None
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.average_execution_time = 0.0
        self.dependencies = []
        self.config = {}
        self.is_critical = False
        self.auto_enable = False

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "function_id": self.function_id,
            "name": self.name,
            "description": self.description,
            "function_type": self.function_type,
            "security_level": self.security_level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_execution": (
                self.last_execution.isoformat() if self.last_execution else None),
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "average_execution_time": self.average_execution_time,
            "dependencies": self.dependencies,
            "is_critical": self.is_critical,
            "auto_enable": self.auto_enable,
        }


class SafeFunctionManager(SecurityBase):
    """Главный менеджер безопасных функций ALADDIN"""

    def __init__(self, name: str = "SafeFunctionManager",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация менеджера
        self.auto_test_interval = config.get(
            "auto_test_interval", 3600) if config else 3600  # 1 час
        self.max_concurrent_functions = config.get(
            "max_concurrent_functions", 10) if config else 10
        self.function_timeout = config.get(
            "function_timeout", 300) if config else 300  # 5 минут
        self.enable_auto_management = config.get(
            "enable_auto_management", True) if config else True

        # Хранилище функций
        self.functions = {}
        self.function_handlers = {}
        self.function_dependencies = {}
        self.execution_queue = []
        self.active_executions = {}

        # Статистика
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.functions_enabled = 0
        self.functions_disabled = 0

        # Блокировки
        self.execution_lock = threading.Lock()
        self.function_lock = threading.Lock()

    def initialize(self) -> bool:
        """Инициализация менеджера безопасных функций"""
        try:
            self.log_activity(
                f"Инициализация менеджера безопасных функций {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Регистрация базовых функций
            self._register_basic_functions()

            # Настройка зависимостей
            self._setup_dependencies()

            # Инициализация критических функций
            self._initialize_critical_functions()

            # Запуск автоматического управления
            if self.enable_auto_management:
                self._start_auto_management()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер безопасных функций {self.name} успешно инициализирован")
            return True

        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации менеджера безопасных функций {self.name}: {e}",
                "error",
            )
            return False

    def _register_basic_functions(self):
        """Регистрация базовых функций"""
        basic_functions = [
            {
                "function_id": "core_base",
                "name": "CoreBase",
                "description": "Базовая архитектура системы",
                "function_type": "core",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "service_base",
                "name": "ServiceBase",
                "description": "Базовый сервис",
                "function_type": "core",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "security_base",
                "name": "SecurityBase",
                "description": "Базовая безопасность",
                "function_type": "security",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "database",
                "name": "Database",
                "description": "Модуль базы данных",
                "function_type": "core",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
            {
                "function_id": "configuration",
                "name": "Configuration",
                "description": "Управление конфигурацией",
                "function_type": "core",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True,
            },
            {
                "function_id": "logging_module",
                "name": "LoggingModule",
                "description": "Система логирования",
                "function_type": "core",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True,
            },
            {
                "function_id": "authentication",
                "name": "Authentication",
                "description": "Аутентификация",
                "function_type": "security",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True,
            },
        ]

        for func_data in basic_functions:
            self.register_function(
                function_id=func_data["function_id"],
                name=func_data["name"],
                description=func_data["description"],
                function_type=func_data["function_type"],
                security_level=func_data["security_level"],
                is_critical=func_data["is_critical"],
                auto_enable=func_data["auto_enable"],
            )

        self.log_activity(
            f"Зарегистрировано {len(basic_functions)} базовых функций")

    def _setup_dependencies(self):
        """Настройка зависимостей между функциями"""
        dependencies = {
            "service_base": ["core_base"],
            "security_base": ["core_base"],
            "database": ["core_base"],
            "configuration": ["core_base"],
            "logging_module": ["core_base"],
            "authentication": ["core_base", "database"],
        }

        for function_id, deps in dependencies.items():
            if function_id in self.functions:
                self.functions[function_id].dependencies = deps

        self.log_activity("Зависимости между функциями настроены")

    def _initialize_critical_functions(self):
        """Инициализация критических функций"""
        for function in self.functions.values():
            if function.is_critical and function.auto_enable:
                self.enable_function(function.function_id)

        self.log_activity("Критические функции инициализированы")

    def _start_auto_management(self):
        """Запуск автоматического управления"""
        # Здесь будет логика автоматического управления
        self.log_activity("Автоматическое управление функциями запущено")

    def register_function(
        self,
        function_id: str,
        name: str,
        description: str,
        function_type: str,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        is_critical: bool = False,
        auto_enable: bool = False,
    ) -> bool:
        """
        Регистрация новой функции

        Args:
            function_id: Уникальный ID функции
            name: Название функции
            description: Описание функции
            function_type: Тип функции
            security_level: Уровень безопасности
            is_critical: Критическая функция
            auto_enable: Автоматическое включение

        Returns:
            bool: True если функция зарегистрирована
        """
        try:
            with self.function_lock:
                if function_id in self.functions:
                    self.log_activity(
                        f"Функция {function_id} уже зарегистрирована", "warning")
                    return False

                function = SecurityFunction(
                    function_id=function_id,
                    name=name,
                    description=description,
                    function_type=function_type,
                    security_level=security_level,
                )
                function.is_critical = is_critical
                function.auto_enable = auto_enable

                self.functions[function_id] = function

                # Автоматическое включение если требуется
                if auto_enable:
                    self.enable_function(function_id)

                self.log_activity(
                    f"Зарегистрирована функция: {name} ({function_id})")
                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка регистрации функции {function_id}: {e}", "error")
            return False

    def unregister_function(self, function_id: str) -> bool:
        """
        Отмена регистрации функции

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция отменена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                # Проверка зависимостей
                if self._has_dependent_functions(function_id):
                    self.log_activity(
                        f"Невозможно удалить функцию {function_id}: есть зависимые функции", "error", )
                    return False

                # Отключение функции
                self.disable_function(function_id)

                # Удаление функции
                del self.functions[function_id]

                self.log_activity(f"Функция {function_id} отменена")
                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка отмены регистрации функции {function_id}: {e}",
                "error")
            return False

    def _has_dependent_functions(self, function_id: str) -> bool:
        """Проверка наличия зависимых функций"""
        for function in self.functions.values():
            if function_id in function.dependencies:
                return True
        return False

    def enable_function(self, function_id: str) -> bool:
        """
        Включение функции

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция включена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                # Проверка зависимостей
                if not self._check_dependencies(function_id):
                    self.log_activity(
                        f"Невозможно включить функцию {function_id}: зависимости не удовлетворены",
                        "error",
                    )
                    return False

                if function.status == FunctionStatus.ENABLED:
                    return True

                function.status = FunctionStatus.ENABLED
                self.functions_enabled += 1
                self.functions_disabled = max(0, self.functions_disabled - 1)

                self.log_activity(f"Функция {function_id} включена")
                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка включения функции {function_id}: {e}", "error")
            return False

    def disable_function(self, function_id: str) -> bool:
        """
        Отключение функции

        Args:
            function_id: ID функции

        Returns:
            bool: True если функция отключена
        """
        try:
            with self.function_lock:
                if function_id not in self.functions:
                    return False

                function = self.functions[function_id]

                if function.status == FunctionStatus.DISABLED:
                    return True

                function.status = FunctionStatus.DISABLED
                self.functions_disabled += 1
                self.functions_enabled = max(0, self.functions_enabled - 1)

                self.log_activity(f"Функция {function_id} отключена")
                return True

        except Exception as e:
            self.log_activity(
                f"Ошибка отключения функции {function_id}: {e}", "error")
            return False

    def _check_dependencies(self, function_id: str) -> bool:
        """Проверка зависимостей функции"""
        if function_id not in self.functions:
            return False

        function = self.functions[function_id]

        for dep_id in function.dependencies:
            if dep_id not in self.functions:
                return False

            dep_function = self.functions[dep_id]
            if dep_function.status != FunctionStatus.ENABLED:
                return False

        return True

    def execute_function(self,
                         function_id: str,
                         params: Optional[Dict[str,
                                               Any]] = None) -> Tuple[bool,
                                                                      Any,
                                                                      str]:
        """
        Выполнение функции

        Args:
            function_id: ID функции
            params: Параметры выполнения

        Returns:
            Tuple[bool, Any, str]: (успех, результат, сообщение)
        """
        try:
            with self.execution_lock:
                # Проверка существования функции
                if function_id not in self.functions:
                    return False, None, f"Функция {function_id} не найдена"

                function = self.functions[function_id]

                # Проверка статуса функции
                if function.status != FunctionStatus.ENABLED:
                    return (
                        False,
                        None,
                        f"Функция {function_id} не активна (статус: {function.status.value})",
                    )

                # Проверка лимита одновременных выполнений
                if len(self.active_executions) >= self.max_concurrent_functions:
                    return False, None, "Достигнут лимит одновременных выполнений"

                # Создание задачи выполнения
                execution_id = f"{function_id}_{int(time.time())}"
                self.active_executions[execution_id] = {
                    "function_id": function_id,
                    "start_time": datetime.now(),
                    "params": params or {},
                }

            # Выполнение функции
            start_time = time.time()
            try:
                result = self._execute_function_handler(
                    function_id, params or {})
                execution_time = time.time() - start_time

                # Обновление статистики
                self._update_function_stats(function_id, True, execution_time)

                self.log_activity(
                    f"Функция {function_id} выполнена успешно за {execution_time:.2f}с")
                return True, result, "Функция выполнена успешно"

            except Exception as e:
                execution_time = time.time() - start_time
                self._update_function_stats(function_id, False, execution_time)

                self.log_activity(
                    f"Ошибка выполнения функции {function_id}: {e}", "error")
                return False, None, f"Ошибка выполнения: {e}"

            finally:
                # Удаление из активных выполнений
                with self.execution_lock:
                    if execution_id in self.active_executions:
                        del self.active_executions[execution_id]

        except Exception as e:
            self.log_activity(
                f"Ошибка выполнения функции {function_id}: {e}", "error")
            return False, None, f"Системная ошибка: {e}"

    def _execute_function_handler(
            self, function_id: str, params: Dict[str, Any]) -> Any:
        """Выполнение обработчика функции"""
        if function_id in self.function_handlers:
            handler = self.function_handlers[function_id]
            return handler(params)
        else:
            # Заглушка для функций без обработчика
            return {
                "status": "executed",
                "function_id": function_id,
                "params": params}

    def _update_function_stats(
            self,
            function_id: str,
            success: bool,
            execution_time: float):
        """Обновление статистики функции"""
        if function_id not in self.functions:
            return

        function = self.functions[function_id]
        function.execution_count += 1
        function.last_execution = datetime.now()

        if success:
            function.success_count += 1
            self.successful_executions += 1
        else:
            function.error_count += 1
            self.failed_executions += 1

        # Обновление среднего времени выполнения
        total_time = function.average_execution_time * \
            (function.execution_count - 1) + execution_time
        function.average_execution_time = total_time / function.execution_count

        self.total_executions += 1

    def register_function_handler(
            self,
            function_id: str,
            handler: Callable) -> bool:
        """
        Регистрация обработчика функции

        Args:
            function_id: ID функции
            handler: Обработчик функции

        Returns:
            bool: True если обработчик зарегистрирован
        """
        try:
            if function_id not in self.functions:
                return False

            self.function_handlers[function_id] = handler
            self.log_activity(
                f"Зарегистрирован обработчик для функции {function_id}")
            return True

        except Exception as e:
            self.log_activity(
                f"Ошибка регистрации обработчика для функции {function_id}: {e}", "error", )
            return False

    def get_function_status(
            self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статуса функции

        Args:
            function_id: ID функции

        Returns:
            Optional[Dict[str, Any]]: Статус функции
        """
        if function_id not in self.functions:
            return None

        function = self.functions[function_id]
        return function.to_dict()

    def get_all_functions_status(self) -> List[Dict[str, Any]]:
        """
        Получение статуса всех функций

        Returns:
            List[Dict[str, Any]]: Список статусов функций
        """
        return [function.to_dict() for function in self.functions.values()]

    def get_enabled_functions(self) -> List[Dict[str, Any]]:
        """
        Получение включенных функций

        Returns:
            List[Dict[str, Any]]: Список включенных функций
        """
        return [function.to_dict() for function in self.functions.values()
                if function.status == FunctionStatus.ENABLED]

    def get_critical_functions(self) -> List[Dict[str, Any]]:
        """
        Получение критических функций

        Returns:
            List[Dict[str, Any]]: Список критических функций
        """
        return [function.to_dict()
                for function in self.functions.values() if function.is_critical]

    def get_function_dependencies(self, function_id: str) -> List[str]:
        """
        Получение зависимостей функции

        Args:
            function_id: ID функции

        Returns:
            List[str]: Список зависимостей
        """
        if function_id not in self.functions:
            return []

        return self.functions[function_id].dependencies.copy()

    def get_dependent_functions(self, function_id: str) -> List[str]:
        """
        Получение функций, зависящих от указанной

        Args:
            function_id: ID функции

        Returns:
            List[str]: Список зависимых функций
        """
        dependent_functions = []
        for func_id, function in self.functions.items():
            if function_id in function.dependencies:
                dependent_functions.append(func_id)

        return dependent_functions

    def test_function(self, function_id: str) -> Tuple[bool, str]:
        """
        Тестирование функции

        Args:
            function_id: ID функции

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            if function_id not in self.functions:
                return False, f"Функция {function_id} не найдена"

            function = self.functions[function_id]
            original_status = function.status

            # Временное включение для тестирования
            function.status = FunctionStatus.TESTING

            # Выполнение теста
            success, result, message = self.execute_function(
                function_id, {"test": True})

            # Восстановление статуса
            function.status = original_status

            if success:
                self.log_activity(
                    f"Тест функции {function_id} пройден успешно")
                return True, "Тест пройден успешно"
            else:
                self.log_activity(
                    f"Тест функции {function_id} провален: {message}", "error")
                return False, f"Тест провален: {message}"

        except Exception as e:
            self.log_activity(
                f"Ошибка тестирования функции {function_id}: {e}", "error")
            return False, f"Ошибка тестирования: {e}"

    def get_safe_function_stats(self) -> Dict[str, Any]:
        """
        Получение статистики менеджера безопасных функций

        Returns:
            Dict[str, Any]: Статистика менеджера
        """
        return {
            "total_functions": len(self.functions),
            "enabled_functions": self.functions_enabled,
            "disabled_functions": self.functions_disabled,
            "critical_functions": len([f for f in self.functions.values() if f.is_critical]),
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "active_executions": len(self.active_executions),
            "execution_success_rate": (
                (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
            ),
            "functions_by_type": self._get_functions_by_type(),
            "functions_by_security_level": self._get_functions_by_security_level(),
        }

    def _get_functions_by_type(self) -> Dict[str, int]:
        """Получение количества функций по типам"""
        types_count = {}
        for function in self.functions.values():
            func_type = function.function_type
            types_count[func_type] = types_count.get(func_type, 0) + 1
        return types_count

    def _get_functions_by_security_level(self) -> Dict[str, int]:
        """Получение количества функций по уровням безопасности"""
        levels_count = {}
        for function in self.functions.values():
            level = function.security_level.value
            levels_count[level] = levels_count.get(level, 0) + 1
        return levels_count

    def start(self) -> bool:
        """Запуск менеджера безопасных функций"""
        try:
            self.log_activity(
                f"Запуск менеджера безопасных функций {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Менеджер безопасных функций {self.name} успешно запущен")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска менеджера безопасных функций {self.name}: {e}",
                "error")
            return False

    def stop(self) -> bool:
        """Остановка менеджера безопасных функций"""
        try:
            self.log_activity(
                f"Остановка менеджера безопасных функций {self.name}")

            # Остановка всех активных выполнений
            with self.execution_lock:
                self.active_executions.clear()

            # Отключение всех функций
            for function_id in list(self.functions.keys()):
                self.disable_function(function_id)

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Менеджер безопасных функций {self.name} успешно остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки менеджера безопасных функций {self.name}: {e}",
                "error",
            )
            return False
