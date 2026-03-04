#!/usr/bin/env python3
"""
ALADDIN VPN - Constants Configuration
Централизованные константы для VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

from enum import Enum
from typing import Any, Dict, List

# ============================================================================
# СЕТЕВЫЕ КОНСТАНТЫ
# ============================================================================


class VPNProtocol(Enum):
    """Протоколы VPN"""

    WIREGUARD = "wireguard"
    OPENVPN = "openvpn"
    IPSEC = "ipsec"
    L2TP = "l2tp"
    PPTP = "pptp"


class EncryptionType(Enum):
    """Типы шифрования"""

    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    AES_128_GCM = "aes-128-gcm"


# Порты по умолчанию
DEFAULT_PORTS = {
    VPNProtocol.WIREGUARD: 51820,
    VPNProtocol.OPENVPN: 1194,
    VPNProtocol.IPSEC: 500,
    VPNProtocol.L2TP: 1701,
    VPNProtocol.PPTP: 1723,
}

# ============================================================================
# КОНФИГУРАЦИОННЫЕ КОНСТАНТЫ
# ============================================================================

# Настройки сервера
SERVER_CONFIG = {
    "max_connections": 1000,
    "max_bandwidth_mbps": 1000,
    "session_timeout_minutes": 1440,  # 24 часа
    "keepalive_interval": 25,
    "mtu": 1420,
    "dns_servers": ["1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4"],
}

# Настройки безопасности
SECURITY_CONFIG = {
    "key_size": 256,
    "handshake_timeout": 120,
    "rekey_interval": 3600,  # 1 час
    "max_failed_attempts": 3,
    "lockout_duration_minutes": 15,
    "certificate_validity_days": 365,
}

# Настройки мониторинга
MONITORING_CONFIG = {
    "check_interval_seconds": 60,
    "memory_threshold_percent": 80,
    "cpu_threshold_percent": 70,
    "disk_threshold_percent": 90,
    "network_timeout_seconds": 30,
    "log_retention_days": 30,
}

# ============================================================================
# СТАТУСЫ И СОСТОЯНИЯ
# ============================================================================


class ConnectionStatus(Enum):
    """Статусы подключения"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    BLOCKED = "blocked"


class ServerStatus(Enum):
    """Статусы сервера"""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"
    ERROR = "error"


class SecurityLevel(Enum):
    """Уровни безопасности"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


# ============================================================================
# ОГРАНИЧЕНИЯ И ЛИМИТЫ
# ============================================================================

# Rate Limiting
RATE_LIMITS = {
    "max_requests_per_minute": 100,
    "max_requests_per_hour": 1000,
    "max_requests_per_day": 10000,
    "max_connections_per_ip": 5,
    "max_bandwidth_per_user_mbps": 100,
}

# DDoS Protection
DDOS_LIMITS = {
    "max_requests_per_second": 10,
    "max_concurrent_connections": 100,
    "block_duration_minutes": 60,
    "whitelist_ips": ["127.0.0.1", "::1"],
    "blacklist_ips": [],
}

# ============================================================================
# ПУТИ И ФАЙЛЫ
# ============================================================================

# Директории
DIRECTORIES = {
    "config": "config",
    "logs": "logs",
    "ssl": "ssl",
    "keys": "keys",
    "certificates": "certificates",
    "backups": "backups",
    "templates": "templates",
    "scripts": "scripts",
}

# Файлы конфигурации
CONFIG_FILES = {
    "main": "config/vpn_config.json",
    "servers": "config/servers.json",
    "users": "config/users.json",
    "security": "config/security.json",
    "monitoring": "config/monitoring.json",
    "ddos": "config/ddos_config.json",
    "rate_limiting": "config/rate_limiting.json",
    "ids": "config/ids_config.json",
    "audit": "config/audit_config.json",
    "2fa": "config/2fa_config.json",
}

# Файлы логов
LOG_FILES = {
    "main": "logs/vpn.log",
    "security": "logs/security.log",
    "audit": "logs/audit.log",
    "error": "logs/error.log",
    "access": "logs/access.log",
    "monitoring": "logs/monitoring.log",
}

# ============================================================================
# СООБЩЕНИЯ И КОДЫ ОШИБОК
# ============================================================================


class ErrorCode(Enum):
    """Коды ошибок"""

    SUCCESS = 0
    GENERAL_ERROR = 1000
    CONNECTION_FAILED = 1001
    AUTHENTICATION_FAILED = 1002
    AUTHORIZATION_DENIED = 1003
    INVALID_CONFIGURATION = 1004
    SERVER_UNAVAILABLE = 1005
    RATE_LIMIT_EXCEEDED = 1006
    SECURITY_VIOLATION = 1007
    RESOURCE_EXHAUSTED = 1008
    TIMEOUT = 1009


# Сообщения об ошибках
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "Success",
    ErrorCode.GENERAL_ERROR: "General error occurred",
    ErrorCode.CONNECTION_FAILED: "Connection failed",
    ErrorCode.AUTHENTICATION_FAILED: "Authentication failed",
    ErrorCode.AUTHORIZATION_DENIED: "Authorization denied",
    ErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
    ErrorCode.SERVER_UNAVAILABLE: "Server unavailable",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
    ErrorCode.SECURITY_VIOLATION: "Security violation detected",
    ErrorCode.RESOURCE_EXHAUSTED: "Resources exhausted",
    ErrorCode.TIMEOUT: "Operation timeout",
}

# ============================================================================
# API КОНСТАНТЫ
# ============================================================================

# HTTP статус коды
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "CONFLICT": 409,
    "RATE_LIMITED": 429,
    "INTERNAL_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
}

# API версии
API_VERSIONS = {"v1": "1.0.0", "v2": "2.0.0", "latest": "2.0.0"}

# ============================================================================
# ГЕОГРАФИЧЕСКИЕ КОНСТАНТЫ
# ============================================================================

# Поддерживаемые страны
SUPPORTED_COUNTRIES = [
    "US",
    "CA",
    "GB",
    "DE",
    "FR",
    "NL",
    "SG",
    "JP",
    "AU",
    "BR",
    "IT",
    "ES",
    "SE",
    "NO",
    "DK",
    "FI",
    "CH",
    "AT",
    "BE",
    "PL",
    "CZ",
    "HU",
    "RO",
    "BG",
    "HR",
    "SI",
    "SK",
    "LT",
    "LV",
    "EE",
    "IE",
    "PT",
    "GR",
    "CY",
    "MT",
    "LU",
    "IS",
    "LI",
    "MC",
    "AD",
]

# Регионы
REGIONS = {
    "NORTH_AMERICA": ["US", "CA"],
    "EUROPE": ["GB", "DE", "FR", "NL", "IT", "ES", "SE", "NO", "DK", "FI"],
    "ASIA_PACIFIC": ["SG", "JP", "AU", "HK", "TW", "KR", "TH", "MY", "ID"],
    "SOUTH_AMERICA": ["BR", "AR", "CL", "CO", "PE", "UY", "PY", "BO"],
    "AFRICA": ["ZA", "EG", "NG", "KE", "MA", "TN", "GH", "UG"],
    "MIDDLE_EAST": ["AE", "SA", "IL", "TR", "EG", "JO", "LB", "KW"],
}

# ============================================================================
# ПРОИЗВОДИТЕЛЬНОСТЬ
# ============================================================================

# Производительность серверов
PERFORMANCE_TIERS = {
    "BASIC": {
        "max_connections": 100,
        "bandwidth_mbps": 100,
        "cpu_cores": 1,
        "ram_mb": 512,
        "storage_gb": 20,
    },
    "STANDARD": {
        "max_connections": 500,
        "bandwidth_mbps": 500,
        "cpu_cores": 2,
        "ram_mb": 1024,
        "storage_gb": 50,
    },
    "PREMIUM": {
        "max_connections": 1000,
        "bandwidth_mbps": 1000,
        "cpu_cores": 4,
        "ram_mb": 2048,
        "storage_gb": 100,
    },
    "ENTERPRISE": {
        "max_connections": 5000,
        "bandwidth_mbps": 5000,
        "cpu_cores": 8,
        "ram_mb": 4096,
        "storage_gb": 200,
    },
}

# ============================================================================
# БЕЗОПАСНОСТЬ
# ============================================================================

# Алгоритмы хеширования
HASH_ALGORITHMS = ["SHA256", "SHA384", "SHA512", "BLAKE2s", "BLAKE2b"]

# Алгоритмы подписи
SIGNATURE_ALGORITHMS = ["RSA", "ECDSA", "EdDSA"]

# Длины ключей
KEY_LENGTHS = {
    "RSA": [2048, 3072, 4096],
    "ECDSA": [256, 384, 521],
    "EdDSA": [256, 448],
}

# ============================================================================
# МОНИТОРИНГ
# ============================================================================

# Метрики для мониторинга
METRICS = {
    "CONNECTION_COUNT": "connection_count",
    "BANDWIDTH_USAGE": "bandwidth_usage",
    "CPU_USAGE": "cpu_usage",
    "MEMORY_USAGE": "memory_usage",
    "DISK_USAGE": "disk_usage",
    "LATENCY": "latency",
    "PACKET_LOSS": "packet_loss",
    "ERROR_RATE": "error_rate",
}

# Пороги для алертов
ALERT_THRESHOLDS = {
    "HIGH_CPU": 80,
    "HIGH_MEMORY": 85,
    "HIGH_DISK": 90,
    "HIGH_LATENCY": 1000,  # мс
    "HIGH_PACKET_LOSS": 5,  # %
    "HIGH_ERROR_RATE": 5,  # %
}

# ============================================================================
# ВАЛИДАЦИЯ
# ============================================================================

# Регулярные выражения
REGEX_PATTERNS = {
    "IP_ADDRESS": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    "IPV6_ADDRESS": r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
    "DOMAIN_NAME": r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$",
    "EMAIL": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "USERNAME": r"^[a-zA-Z0-9_-]{3,20}$",
    "PASSWORD": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
}

# Ограничения длины
LENGTH_LIMITS = {
    "USERNAME_MIN": 3,
    "USERNAME_MAX": 20,
    "PASSWORD_MIN": 8,
    "PASSWORD_MAX": 128,
    "SERVER_NAME_MIN": 3,
    "SERVER_NAME_MAX": 50,
    "DESCRIPTION_MAX": 500,
}

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def get_config_value(key: str, default: Any = None) -> Any:
    """Получение значения конфигурации"""
    # Здесь можно добавить логику загрузки из файла
    return default


def validate_ip_address(ip: str) -> bool:
    """Валидация IP адреса"""
    import re

    return bool(re.match(REGEX_PATTERNS["IP_ADDRESS"], ip))


def validate_domain_name(domain: str) -> bool:
    """Валидация доменного имени"""
    import re

    return bool(re.match(REGEX_PATTERNS["DOMAIN_NAME"], domain))


def get_supported_protocols() -> List[str]:
    """Получение списка поддерживаемых протоколов"""
    return [protocol.value for protocol in VPNProtocol]


def get_supported_countries() -> List[str]:
    """Получение списка поддерживаемых стран"""
    return SUPPORTED_COUNTRIES.copy()


def get_performance_tier(tier_name: str) -> Dict[str, Any]:
    """Получение конфигурации производительности по имени"""
    return PERFORMANCE_TIERS.get(tier_name.upper(), PERFORMANCE_TIERS["BASIC"])


# ============================================================================
# ЭКСПОРТ КОНСТАНТ
# ============================================================================

__all__ = [
    "VPNProtocol",
    "EncryptionType",
    "ConnectionStatus",
    "ServerStatus",
    "SecurityLevel",
    "ErrorCode",
    "HTTP_STATUS",
    "API_VERSIONS",
    "DEFAULT_PORTS",
    "SERVER_CONFIG",
    "SECURITY_CONFIG",
    "MONITORING_CONFIG",
    "RATE_LIMITS",
    "DDOS_LIMITS",
    "DIRECTORIES",
    "CONFIG_FILES",
    "LOG_FILES",
    "ERROR_MESSAGES",
    "SUPPORTED_COUNTRIES",
    "REGIONS",
    "PERFORMANCE_TIERS",
    "HASH_ALGORITHMS",
    "SIGNATURE_ALGORITHMS",
    "KEY_LENGTHS",
    "METRICS",
    "ALERT_THRESHOLDS",
    "REGEX_PATTERNS",
    "LENGTH_LIMITS",
    "get_config_value",
    "validate_ip_address",
    "validate_domain_name",
    "get_supported_protocols",
    "get_supported_countries",
    "get_performance_tier",
]
