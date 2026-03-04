#!/usr/bin/env python3
"""
ALADDIN VPN - Exceptions Module
Модуль исключений для VPN системы
"""

# Базовые исключения
from .vpn_exceptions import VPNException, VPNConfigurationError, VPNConnectionError, VPNSecurityError

# Исключения подключения
from .vpn_exceptions import (
    ConnectionTimeoutError, ConnectionRefusedError, ConnectionLostError,
    InvalidServerError, ServerUnavailableError
)

# Исключения аутентификации
from .vpn_exceptions import (
    AuthenticationError, InvalidCredentialsError, AccountLockedError,
    TwoFactorRequiredError, TwoFactorInvalidError, SessionExpiredError
)

# Исключения безопасности
from .vpn_exceptions import (
    SecurityViolationError, DDoSAttackDetectedError, RateLimitExceededError,
    IntrusionDetectedError, IPBlockedError
)

# Исключения конфигурации
from .vpn_exceptions import InvalidConfigurationError, MissingConfigurationError, ConfigurationValidationError

# Исключения сети
from .vpn_exceptions import NetworkError, DNSResolutionError, PortUnavailableError, FirewallBlockedError

# Исключения базы данных
from .vpn_exceptions import DatabaseError, ConnectionPoolExhaustedError, QueryTimeoutError, ConstraintViolationError

# Исключения мониторинга
from .vpn_exceptions import MonitoringError, MetricCollectionError, AlertDeliveryError

# Исключения производительности
from .vpn_exceptions import (
    PerformanceError, ResourceExhaustedError, MemoryExhaustedError,
    CPUExhaustedError, DiskSpaceExhaustedError
)

# Вспомогательные функции
from .vpn_exceptions import get_exception_hierarchy, get_exception_by_code, format_exception_for_logging

__all__ = [
    # Базовые исключения
    "VPNException", "VPNConfigurationError", "VPNConnectionError", "VPNSecurityError",

    # Исключения подключения
    "ConnectionTimeoutError", "ConnectionRefusedError", "ConnectionLostError",
    "InvalidServerError", "ServerUnavailableError",

    # Исключения аутентификации
    "AuthenticationError", "InvalidCredentialsError", "AccountLockedError",
    "TwoFactorRequiredError", "TwoFactorInvalidError", "SessionExpiredError",

    # Исключения безопасности
    "SecurityViolationError", "DDoSAttackDetectedError", "RateLimitExceededError",
    "IntrusionDetectedError", "IPBlockedError",

    # Исключения конфигурации
    "InvalidConfigurationError", "MissingConfigurationError", "ConfigurationValidationError",

    # Исключения сети
    "NetworkError", "DNSResolutionError", "PortUnavailableError", "FirewallBlockedError",

    # Исключения базы данных
    "DatabaseError", "ConnectionPoolExhaustedError", "QueryTimeoutError", "ConstraintViolationError",

    # Исключения мониторинга
    "MonitoringError", "MetricCollectionError", "AlertDeliveryError",

    # Исключения производительности
    "PerformanceError", "ResourceExhaustedError", "MemoryExhaustedError",
    "CPUExhaustedError", "DiskSpaceExhaustedError",

    # Вспомогательные функции
    "get_exception_hierarchy", "get_exception_by_code", "format_exception_for_logging"
]
