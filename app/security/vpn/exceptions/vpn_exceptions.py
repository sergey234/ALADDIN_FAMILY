#!/usr/bin/env python3
"""
ALADDIN VPN - Custom Exceptions
Кастомные исключения для VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

from datetime import datetime
from typing import Any, Dict, List

# ============================================================================
# БАЗОВЫЕ ИСКЛЮЧЕНИЯ
# ============================================================================


class VPNException(Exception):
    """Базовое исключение для VPN системы"""

    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "VPN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для логирования"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class VPNConfigurationError(VPNException):
    """Ошибка конфигурации VPN"""

    def __init__(self, message: str, config_key: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "CONFIG_ERROR", details)
        self.config_key = config_key


class VPNConnectionError(VPNException):
    """Ошибка подключения VPN"""

    def __init__(self, message: str, server_id: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "CONNECTION_ERROR", details)
        self.server_id = server_id


class VPNSecurityError(VPNException):
    """Ошибка безопасности VPN"""

    def __init__(self, message: str, threat_type: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "SECURITY_ERROR", details)
        self.threat_type = threat_type


# ============================================================================
# ИСКЛЮЧЕНИЯ ПОДКЛЮЧЕНИЯ
# ============================================================================


class ConnectionTimeoutError(VPNConnectionError):
    """Таймаут подключения"""

    def __init__(self, server_id: str, timeout_seconds: int, details: Dict[str, Any] = None):
        message = f"Connection timeout to server {server_id} after {timeout_seconds} seconds"
        super().__init__(message, server_id, details)
        self.timeout_seconds = timeout_seconds


class ConnectionRefusedError(VPNConnectionError):
    """Отказ в подключении"""

    def __init__(self, server_id: str, reason: str = None, details: Dict[str, Any] = None):
        message = f"Connection refused to server {server_id}"
        if reason:
            message += f": {reason}"
        super().__init__(message, server_id, details)
        self.reason = reason


class ConnectionLostError(VPNConnectionError):
    """Потеря соединения"""

    def __init__(self, server_id: str, duration_seconds: int = None, details: Dict[str, Any] = None):
        message = f"Connection lost to server {server_id}"
        if duration_seconds:
            message += f" after {duration_seconds} seconds"
        super().__init__(message, server_id, details)
        self.duration_seconds = duration_seconds


class InvalidServerError(VPNConnectionError):
    """Неверный сервер"""

    def __init__(self, server_id: str, reason: str = None, details: Dict[str, Any] = None):
        message = f"Invalid server {server_id}"
        if reason:
            message += f": {reason}"
        super().__init__(message, server_id, details)
        self.reason = reason


class ServerUnavailableError(VPNConnectionError):
    """Сервер недоступен"""

    def __init__(self, server_id: str, status: str = None, details: Dict[str, Any] = None):
        message = f"Server {server_id} is unavailable"
        if status:
            message += f" (status: {status})"
        super().__init__(message, server_id, details)
        self.status = status


# ============================================================================
# ИСКЛЮЧЕНИЯ АУТЕНТИФИКАЦИИ
# ============================================================================


class AuthenticationError(VPNException):
    """Ошибка аутентификации"""

    def __init__(self, message: str, username: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "AUTH_ERROR", details)
        self.username = username


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""

    def __init__(self, username: str = None, details: Dict[str, Any] = None):
        message = "Invalid credentials"
        if username:
            message += f" for user {username}"
        super().__init__(message, username, details)


class AccountLockedError(AuthenticationError):
    """Заблокированный аккаунт"""

    def __init__(self, username: str, lockout_duration: int = None, details: Dict[str, Any] = None):
        message = f"Account {username} is locked"
        if lockout_duration:
            message += f" for {lockout_duration} minutes"
        super().__init__(message, username, details)
        self.lockout_duration = lockout_duration


class TwoFactorRequiredError(AuthenticationError):
    """Требуется двухфакторная аутентификация"""

    def __init__(self, username: str, methods: List[str] = None, details: Dict[str, Any] = None):
        message = f"Two-factor authentication required for user {username}"
        super().__init__(message, username, details)
        self.methods = methods or []


class TwoFactorInvalidError(AuthenticationError):
    """Неверный код двухфакторной аутентификации"""

    def __init__(self, username: str, method: str = None, details: Dict[str, Any] = None):
        message = f"Invalid two-factor code for user {username}"
        if method:
            message += f" (method: {method})"
        super().__init__(message, username, details)
        self.method = method


class SessionExpiredError(AuthenticationError):
    """Истекшая сессия"""

    def __init__(self, session_id: str = None, details: Dict[str, Any] = None):
        message = "Session has expired"
        if session_id:
            message += f" (session: {session_id})"
        super().__init__(message, details=details)
        self.session_id = session_id


# ============================================================================
# ИСКЛЮЧЕНИЯ БЕЗОПАСНОСТИ
# ============================================================================


class SecurityViolationError(VPNSecurityError):
    """Нарушение безопасности"""

    def __init__(self, message: str, violation_type: str, ip_address: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "SECURITY_VIOLATION", details)
        self.violation_type = violation_type
        self.ip_address = ip_address


class DDoSAttackDetectedError(VPNSecurityError):
    """Обнаружена DDoS атака"""

    def __init__(self, source_ips: List[str], attack_type: str, details: Dict[str, Any] = None):
        message = f"DDoS attack detected from {len(source_ips)} IPs (type: {attack_type})"
        super().__init__(message, "DDOS_ATTACK", details)
        self.source_ips = source_ips
        self.attack_type = attack_type


class RateLimitExceededError(VPNSecurityError):
    """Превышен лимит скорости"""

    def __init__(self, identifier: str, limit: int, window: str, details: Dict[str, Any] = None):
        message = f"Rate limit exceeded for {identifier}: {limit} requests per {window}"
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)
        self.identifier = identifier
        self.limit = limit
        self.window = window


class IntrusionDetectedError(VPNSecurityError):
    """Обнаружено вторжение"""

    def __init__(self, attack_type: str, source_ip: str, details: Dict[str, Any] = None):
        message = f"Intrusion detected: {attack_type} from {source_ip}"
        super().__init__(message, "INTRUSION_DETECTED", details)
        self.attack_type = attack_type
        self.source_ip = source_ip


class IPBlockedError(VPNSecurityError):
    """IP заблокирован"""

    def __init__(self, ip_address: str, reason: str = None, duration: int = None, details: Dict[str, Any] = None):
        message = f"IP {ip_address} is blocked"
        if reason:
            message += f" (reason: {reason})"
        if duration:
            message += f" for {duration} minutes"
        super().__init__(message, "IP_BLOCKED", details)
        self.ip_address = ip_address
        self.reason = reason
        self.duration = duration


# ============================================================================
# ИСКЛЮЧЕНИЯ КОНФИГУРАЦИИ
# ============================================================================


class InvalidConfigurationError(VPNConfigurationError):
    """Неверная конфигурация"""

    def __init__(
        self, config_key: str, expected_type: str = None, actual_value: Any = None, details: Dict[str, Any] = None
    ):
        message = f"Invalid configuration for key '{config_key}'"
        if expected_type and actual_value:
            message += f": expected {expected_type}, got {type(actual_value).__name__}"
        super().__init__(message, config_key, details)
        self.expected_type = expected_type
        self.actual_value = actual_value


class MissingConfigurationError(VPNConfigurationError):
    """Отсутствует конфигурация"""

    def __init__(self, config_key: str, details: Dict[str, Any] = None):
        message = f"Missing required configuration: {config_key}"
        super().__init__(message, config_key, details)


class ConfigurationValidationError(VPNConfigurationError):
    """Ошибка валидации конфигурации"""

    def __init__(self, config_key: str, validation_errors: List[str], details: Dict[str, Any] = None):
        message = f"Configuration validation failed for '{config_key}': {', '.join(validation_errors)}"
        super().__init__(message, config_key, details)
        self.validation_errors = validation_errors


# ============================================================================
# ИСКЛЮЧЕНИЯ СЕТИ
# ============================================================================


class NetworkError(VPNException):
    """Ошибка сети"""

    def __init__(self, message: str, network_interface: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "NETWORK_ERROR", details)
        self.network_interface = network_interface


class DNSResolutionError(NetworkError):
    """Ошибка разрешения DNS"""

    def __init__(self, hostname: str, details: Dict[str, Any] = None):
        message = f"DNS resolution failed for {hostname}"
        super().__init__(message, details=details)
        self.hostname = hostname


class PortUnavailableError(NetworkError):
    """Порт недоступен"""

    def __init__(self, port: int, protocol: str = None, details: Dict[str, Any] = None):
        message = f"Port {port} is unavailable"
        if protocol:
            message += f" for protocol {protocol}"
        super().__init__(message, details=details)
        self.port = port
        self.protocol = protocol


class FirewallBlockedError(NetworkError):
    """Заблокировано файрволом"""

    def __init__(self, port: int, protocol: str = None, details: Dict[str, Any] = None):
        message = f"Connection blocked by firewall on port {port}"
        if protocol:
            message += f" ({protocol})"
        super().__init__(message, details=details)
        self.port = port
        self.protocol = protocol


# ============================================================================
# ИСКЛЮЧЕНИЯ БАЗЫ ДАННЫХ
# ============================================================================


class DatabaseError(VPNException):
    """Ошибка базы данных"""

    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation


class ConnectionPoolExhaustedError(DatabaseError):
    """Исчерпан пул соединений"""

    def __init__(self, max_connections: int, details: Dict[str, Any] = None):
        message = f"Connection pool exhausted (max: {max_connections})"
        super().__init__(message, "CONNECTION_POOL", details)
        self.max_connections = max_connections


class QueryTimeoutError(DatabaseError):
    """Таймаут запроса"""

    def __init__(self, query: str, timeout_seconds: int, details: Dict[str, Any] = None):
        message = f"Query timeout after {timeout_seconds} seconds"
        super().__init__(message, "QUERY_TIMEOUT", details)
        self.query = query
        self.timeout_seconds = timeout_seconds


class ConstraintViolationError(DatabaseError):
    """Нарушение ограничений"""

    def __init__(self, constraint: str, table: str = None, details: Dict[str, Any] = None):
        message = f"Constraint violation: {constraint}"
        if table:
            message += f" on table {table}"
        super().__init__(message, "CONSTRAINT_VIOLATION", details)
        self.constraint = constraint
        self.table = table


# ============================================================================
# ИСКЛЮЧЕНИЯ МОНИТОРИНГА
# ============================================================================


class MonitoringError(VPNException):
    """Ошибка мониторинга"""

    def __init__(self, message: str, metric_name: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "MONITORING_ERROR", details)
        self.metric_name = metric_name


class MetricCollectionError(MonitoringError):
    """Ошибка сбора метрик"""

    def __init__(self, metric_name: str, reason: str = None, details: Dict[str, Any] = None):
        message = f"Failed to collect metric {metric_name}"
        if reason:
            message += f": {reason}"
        super().__init__(message, metric_name, details)
        self.reason = reason


class AlertDeliveryError(MonitoringError):
    """Ошибка доставки алерта"""

    def __init__(self, alert_id: str, channel: str = None, details: Dict[str, Any] = None):
        message = f"Failed to deliver alert {alert_id}"
        if channel:
            message += f" via {channel}"
        super().__init__(message, details=details)
        self.alert_id = alert_id
        self.channel = channel


# ============================================================================
# ИСКЛЮЧЕНИЯ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================


class PerformanceError(VPNException):
    """Ошибка производительности"""

    def __init__(self, message: str, resource_type: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "PERFORMANCE_ERROR", details)
        self.resource_type = resource_type


class ResourceExhaustedError(PerformanceError):
    """Исчерпаны ресурсы"""

    def __init__(self, resource_type: str, current_usage: float, limit: float, details: Dict[str, Any] = None):
        message = f"Resource {resource_type} exhausted: {current_usage:.1f}% of {limit:.1f}%"
        super().__init__(message, resource_type, details)
        self.current_usage = current_usage
        self.limit = limit


class MemoryExhaustedError(ResourceExhaustedError):
    """Исчерпана память"""

    def __init__(self, current_usage: float, limit: float, details: Dict[str, Any] = None):
        super().__init__("memory", current_usage, limit, details)


class CPUExhaustedError(ResourceExhaustedError):
    """Исчерпан CPU"""

    def __init__(self, current_usage: float, limit: float, details: Dict[str, Any] = None):
        super().__init__("cpu", current_usage, limit, details)


class DiskSpaceExhaustedError(ResourceExhaustedError):
    """Исчерпано место на диске"""

    def __init__(self, current_usage: float, limit: float, details: Dict[str, Any] = None):
        super().__init__("disk", current_usage, limit, details)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def get_exception_hierarchy() -> Dict[str, List[str]]:
    """Получение иерархии исключений"""
    hierarchy = {}

    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, VPNException) and obj != VPNException:
            base_classes = [cls.__name__ for cls in obj.__mro__[1:-1] if cls != object]
            hierarchy[name] = base_classes

    return hierarchy


def get_exception_by_code(error_code: str) -> type:
    """Получение класса исключения по коду ошибки"""
    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, VPNException):
            if hasattr(obj, "__init__"):
                # Создаем временный экземпляр для проверки кода ошибки
                try:
                    temp_instance = obj("test")
                    if temp_instance.error_code == error_code:
                        return obj
                except Exception:
                    continue
    return VPNException


def format_exception_for_logging(exception: VPNException) -> str:
    """Форматирование исключения для логирования"""
    return f"[{exception.error_code}] {exception.message} | Details: {exception.details}"


# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Базовые исключения
    "VPNException",
    "VPNConfigurationError",
    "VPNConnectionError",
    "VPNSecurityError",
    # Исключения подключения
    "ConnectionTimeoutError",
    "ConnectionRefusedError",
    "ConnectionLostError",
    "InvalidServerError",
    "ServerUnavailableError",
    # Исключения аутентификации
    "AuthenticationError",
    "InvalidCredentialsError",
    "AccountLockedError",
    "TwoFactorRequiredError",
    "TwoFactorInvalidError",
    "SessionExpiredError",
    # Исключения безопасности
    "SecurityViolationError",
    "DDoSAttackDetectedError",
    "RateLimitExceededError",
    "IntrusionDetectedError",
    "IPBlockedError",
    # Исключения конфигурации
    "InvalidConfigurationError",
    "MissingConfigurationError",
    "ConfigurationValidationError",
    # Исключения сети
    "NetworkError",
    "DNSResolutionError",
    "PortUnavailableError",
    "FirewallBlockedError",
    # Исключения базы данных
    "DatabaseError",
    "ConnectionPoolExhaustedError",
    "QueryTimeoutError",
    "ConstraintViolationError",
    # Исключения мониторинга
    "MonitoringError",
    "MetricCollectionError",
    "AlertDeliveryError",
    # Исключения производительности
    "PerformanceError",
    "ResourceExhaustedError",
    "MemoryExhaustedError",
    "CPUExhaustedError",
    "DiskSpaceExhaustedError",
    # Вспомогательные функции
    "get_exception_hierarchy",
    "get_exception_by_code",
    "format_exception_for_logging",
]
