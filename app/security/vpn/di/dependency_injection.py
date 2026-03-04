#!/usr/bin/env python3
"""
ALADDIN VPN - Dependency Injection Container
Система внедрения зависимостей для VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

from typing import Dict, Any, Optional, Type, Callable, List
import inspect
import logging
from dataclasses import dataclass
from enum import Enum
from security.types.security_types import (
    ConfigurationManager, Logger, SecurityManager,
    AuthenticationManager, MonitoringManager
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ТИПЫ ЖИЗНЕННОГО ЦИКЛА
# ============================================================================

class LifecycleType(Enum):
    """Типы жизненного цикла объектов"""
    SINGLETON = "singleton"      # Один экземпляр на весь контейнер
    TRANSIENT = "transient"      # Новый экземпляр при каждом запросе
    SCOPED = "scoped"           # Один экземпляр на область видимости
    PER_REQUEST = "per_request"  # Один экземпляр на запрос

# ============================================================================
# ОБЛАСТИ ВИДИМОСТИ
# ============================================================================

class Scope:
    """Область видимости для scoped объектов"""

    def __init__(self, name: str):
        self.name = name
        self._instances: Dict[str, Any] = {}

    def get_instance(self, key: str) -> Optional[Any]:
        """Получение экземпляра из области видимости"""
        return self._instances.get(key)

    def set_instance(self, key: str, instance: Any) -> None:
        """Установка экземпляра в область видимости"""
        self._instances[key] = instance

    def clear(self) -> None:
        """Очистка области видимости"""
        self._instances.clear()

# ============================================================================
# РЕГИСТРАЦИЯ ЗАВИСИМОСТЕЙ
# ============================================================================
@dataclass
class ServiceRegistration:
    """Регистрация сервиса"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifecycle: LifecycleType = LifecycleType.TRANSIENT
    dependencies: List[str] = None
    configuration: Dict[str, Any] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.configuration is None:
            self.configuration = {}

# ============================================================================
# КОНТЕЙНЕР ЗАВИСИМОСТЕЙ
# ============================================================================
class DIContainer:
    """Контейнер внедрения зависимостей"""

    def __init__(self):
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._singletons: Dict[str, Any] = {}
        self._scopes: Dict[str, Scope] = {}
        self._current_scope: Optional[Scope] = None

    def register_singleton(self, service_type: Type, implementation_type: Type = None,
                           factory: Callable = None, instance: Any = None) -> 'DIContainer':
        """Регистрация singleton сервиса"""
        return self._register(service_type, implementation_type, factory, instance,
                              LifecycleType.SINGLETON)

    def register_transient(self, service_type: Type, implementation_type: Type = None,
                           factory: Callable = None) -> 'DIContainer':
        """Регистрация transient сервиса"""
        return self._register(service_type, implementation_type, factory, None,
                              LifecycleType.TRANSIENT)

    def register_scoped(self, service_type: Type, implementation_type: Type = None,
                        factory: Callable = None) -> 'DIContainer':
        """Регистрация scoped сервиса"""
        return self._register(service_type, implementation_type, factory, None,
                              LifecycleType.SCOPED)

    def register_per_request(self, service_type: Type, implementation_type: Type = None,
                             factory: Callable = None) -> 'DIContainer':
        """Регистрация per-request сервиса"""
        return self._register(service_type, implementation_type, factory, None,
                              LifecycleType.PER_REQUEST)

    def _register(self, service_type: Type, implementation_type: Type = None,
                  factory: Callable = None, instance: Any = None,
                  lifecycle: LifecycleType = LifecycleType.TRANSIENT) -> 'DIContainer':
        """Внутренняя регистрация сервиса"""
        key = self._get_service_key(service_type)

        # Определяем зависимости
        dependencies = []
        if implementation_type:
            dependencies = self._get_constructor_dependencies(implementation_type)

        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            instance=instance,
            lifecycle=lifecycle,
            dependencies=dependencies
        )

        self._registrations[key] = registration
        logger.info(f"Registered {lifecycle.value} service: {service_type.__name__}")

        return self

    def get(self, service_type: Type) -> Any:
        """Получение экземпляра сервиса"""
        key = self._get_service_key(service_type)

        if key not in self._registrations:
            raise ValueError(f"Service {service_type.__name__} not registered")

        registration = self._registrations[key]

        # Проверяем жизненный цикл
        if registration.lifecycle == LifecycleType.SINGLETON:
            return self._get_singleton(key, registration)
        elif registration.lifecycle == LifecycleType.TRANSIENT:
            return self._create_instance(registration)
        elif registration.lifecycle == LifecycleType.SCOPED:
            return self._get_scoped(key, registration)
        elif registration.lifecycle == LifecycleType.PER_REQUEST:
            return self._get_per_request(key, registration)
        else:
            raise ValueError(f"Unknown lifecycle type: {registration.lifecycle}")

    def _get_singleton(self, key: str, registration: ServiceRegistration) -> Any:
        """Получение singleton экземпляра"""
        if key in self._singletons:
            return self._singletons[key]

        instance = self._create_instance(registration)
        self._singletons[key] = instance
        return instance

    def _get_scoped(self, key: str, registration: ServiceRegistration) -> Any:
        """Получение scoped экземпляра"""
        if not self._current_scope:
            raise RuntimeError("No active scope for scoped service")

        instance = self._current_scope.get_instance(key)
        if instance is not None:
            return instance

        instance = self._create_instance(registration)
        self._current_scope.set_instance(key, instance)
        return instance

    def _get_per_request(self, key: str, registration: ServiceRegistration) -> Any:
        """Получение per-request экземпляра"""
        # Для per-request создаем новый экземпляр каждый раз
        return self._create_instance(registration)

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Создание экземпляра сервиса"""
        # Если есть готовый экземпляр
        if registration.instance is not None:
            return registration.instance

        # Если есть фабрика
        if registration.factory is not None:
            return registration.factory()

        # Если есть тип реализации
        if registration.implementation_type is not None:
            return self._create_from_type(registration)

        # Если сервис сам является типом
        if inspect.isclass(registration.service_type):
            return self._create_from_type(ServiceRegistration(
                service_type=registration.service_type,
                implementation_type=registration.service_type,
                lifecycle=registration.lifecycle
            ))

        raise ValueError(f"Cannot create instance for {registration.service_type}")

    def _create_from_type(self, registration: ServiceRegistration) -> Any:
        """Создание экземпляра из типа"""
        implementation_type = registration.implementation_type

        # Получаем конструктор
        constructor = implementation_type.__init__
        signature = inspect.signature(constructor)

        # Собираем аргументы для конструктора
        args = {}
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue

            # Получаем тип параметра
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                continue

            # Пытаемся разрешить зависимость
            try:
                dependency = self.get(param_type)
                args[param_name] = dependency
            except ValueError:
                # Если зависимость не зарегистрирована, используем значение по умолчанию
                if param.default != inspect.Parameter.empty:
                    args[param_name] = param.default
                else:
                    logger.warning(
                        f"Could not resolve dependency {param_type.__name__} "
                        f"for {implementation_type.__name__}"
                    )

        # Создаем экземпляр
        return implementation_type(**args)

    def _get_constructor_dependencies(self, implementation_type: Type) -> List[str]:
        """Получение зависимостей конструктора"""
        dependencies = []
        constructor = implementation_type.__init__
        signature = inspect.signature(constructor)

        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue

            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                dependencies.append(param_type.__name__)

        return dependencies

    def _get_service_key(self, service_type: Type) -> str:
        """Получение ключа сервиса"""
        return f"{service_type.__module__}.{service_type.__name__}"

    def create_scope(self, name: str) -> Scope:
        """Создание области видимости"""
        scope = Scope(name)
        self._scopes[name] = scope
        return scope

    def enter_scope(self, scope: Scope) -> None:
        """Вход в область видимости"""
        self._current_scope = scope

    def exit_scope(self) -> None:
        """Выход из области видимости"""
        if self._current_scope:
            self._current_scope.clear()
        self._current_scope = None

    def is_registered(self, service_type: Type) -> bool:
        """Проверка регистрации сервиса"""
        key = self._get_service_key(service_type)
        return key in self._registrations

    def get_registered_services(self) -> List[str]:
        """Получение списка зарегистрированных сервисов"""
        return list(self._registrations.keys())

    def clear(self) -> None:
        """Очистка контейнера"""
        self._registrations.clear()
        self._singletons.clear()
        self._scopes.clear()
        self._current_scope = None

# ============================================================================
# ДЕКОРАТОРЫ ДЛЯ АВТОМАТИЧЕСКОЙ РЕГИСТРАЦИИ
# ============================================================================
def singleton(service_type: Type = None):
    """Декоратор для регистрации singleton сервиса"""
    def decorator(cls):
        container = DIContainer.get_instance()
        container.register_singleton(service_type or cls, cls)
        return cls
    return decorator
def transient(service_type: Type = None):
    """Декоратор для регистрации transient сервиса"""
    def decorator(cls):
        container = DIContainer.get_instance()
        container.register_transient(service_type or cls, cls)
        return cls
    return decorator
def scoped(service_type: Type = None):
    """Декоратор для регистрации scoped сервиса"""
    def decorator(cls):
        container = DIContainer.get_instance()
        container.register_scoped(service_type or cls, cls)
        return cls
    return decorator
def inject(service_type: Type):
    """Декоратор для внедрения зависимости"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            container = DIContainer.get_instance()
            dependency = container.get(service_type)
            return func(dependency, *args, **kwargs)
        return wrapper
    return decorator

# ============================================================================
# ГЛОБАЛЬНЫЙ КОНТЕЙНЕР
# ============================================================================
class GlobalDIContainer:
    """Глобальный контейнер зависимостей"""

    _instance: Optional[DIContainer] = None

    @classmethod
    def get_instance(cls) -> DIContainer:
        """Получение глобального экземпляра контейнера"""
        if cls._instance is None:
            cls._instance = DIContainer()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Сброс глобального контейнера"""
        cls._instance = None

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================
def get_container() -> DIContainer:
    """Получение глобального контейнера"""
    return GlobalDIContainer.get_instance()
def register_vpn_services(container: DIContainer) -> None:
    """Регистрация всех VPN сервисов"""
    from interfaces.vpn_protocols import (
        VPNServer, VPNClient, SecurityManager, AuthenticationManager,
        Logger, MonitoringManager, ConfigurationManager
    )

    # Регистрируем основные сервисы
    container.register_singleton(ConfigurationManager)
    container.register_singleton(Logger)
    container.register_singleton(SecurityManager)
    container.register_singleton(AuthenticationManager)
    container.register_singleton(MonitoringManager)
    container.register_transient(VPNServer)
    container.register_transient(VPNClient)

    logger.info("Registered all VPN services")
def create_vpn_system() -> Dict[str, Any]:
    """Создание полной VPN системы с внедрением зависимостей"""
    container = get_container()
    register_vpn_services(container)

    # Создаем основные компоненты
    config_manager = container.get(ConfigurationManager)
    logger = container.get(Logger)
    security_manager = container.get(SecurityManager)
    auth_manager = container.get(AuthenticationManager)
    monitoring_manager = container.get(MonitoringManager)

    return {
        "config_manager": config_manager,
        "logger": logger,
        "security_manager": security_manager,
        "auth_manager": auth_manager,
        "monitoring_manager": monitoring_manager,
        "container": container
    }

# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Основные классы
    "DIContainer", "ServiceRegistration", "Scope", "LifecycleType",

    # Глобальный контейнер
    "GlobalDIContainer",

    # Декораторы
    "singleton", "transient", "scoped", "inject",

    # Вспомогательные функции
    "get_container", "register_vpn_services", "create_vpn_system"
]
