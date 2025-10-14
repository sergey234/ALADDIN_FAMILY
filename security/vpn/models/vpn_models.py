#!/usr/bin/env python3
"""
ALADDIN VPN - Pydantic Models
Pydantic модели для валидации данных VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

# ============================================================================
# БАЗОВЫЕ МОДЕЛИ
# ============================================================================


class BaseVPNModel(BaseModel):
    """Базовая модель для VPN системы"""

    class Config:
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"
        json_encoders = {datetime: lambda v: v.isoformat()}


class TimestampMixin(BaseModel):
    """Mixin для добавления временных меток"""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# МОДЕЛИ VPN ПРОТОКОЛОВ
# ============================================================================


class VPNProtocolModel(BaseModel):
    """Модель VPN протокола"""

    protocol: Literal["wireguard", "openvpn", "ipsec", "l2tp", "pptp"]
    port: int = Field(ge=1, le=65535)
    encryption: Literal[
        "aes-256-gcm", "aes-256-cbc", "chacha20-poly1305", "aes-128-gcm"
    ]
    key_size: int = Field(ge=128, le=4096, default=256)


class VPNConnectionModel(BaseVPNModel, TimestampMixin):
    """Модель VPN подключения"""

    connection_id: str = Field(..., min_length=1, max_length=50)
    user_id: str = Field(..., min_length=1, max_length=50)
    server_id: str = Field(..., min_length=1, max_length=50)
    protocol: VPNProtocolModel
    status: Literal[
        "connecting", "connected", "disconnected", "failed", "reconnecting"
    ]
    local_ip: Optional[str] = None
    remote_ip: Optional[str] = None
    bytes_sent: int = Field(ge=0, default=0)
    bytes_received: int = Field(ge=0, default=0)
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None

    @validator("local_ip", "remote_ip")
    def validate_ip_address(cls, v):
        if v is not None:
            ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            if not re.match(ip_pattern, v):
                raise ValueError("Invalid IP address format")
        return v

    @validator("status")
    def validate_status_transition(cls, v, values):
        if "status" in values:
            # Здесь можно добавить логику валидации переходов статусов
            pass
        return v


# ============================================================================
# МОДЕЛИ СЕРВЕРОВ
# ============================================================================


class ServerLocationModel(BaseModel):
    """Модель местоположения сервера"""

    country: str = Field(..., min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    city: str = Field(..., min_length=1, max_length=50)
    region: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class ServerPerformanceModel(BaseModel):
    """Модель производительности сервера"""

    max_connections: int = Field(ge=1, le=10000, default=1000)
    max_bandwidth_mbps: int = Field(ge=1, le=10000, default=1000)
    cpu_cores: int = Field(ge=1, le=64, default=2)
    ram_mb: int = Field(ge=512, le=65536, default=2048)
    storage_gb: int = Field(ge=10, le=2000, default=100)


class VPNServerModel(BaseVPNModel, TimestampMixin):
    """Модель VPN сервера"""

    server_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    location: ServerLocationModel
    performance: ServerPerformanceModel
    ip_address: str = Field(
        ...,
        pattern=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    )
    status: Literal["online", "offline", "maintenance", "overloaded", "error"]
    protocols: List[VPNProtocolModel] = Field(..., min_items=1)
    current_connections: int = Field(ge=0, default=0)
    load_percentage: float = Field(ge=0, le=100, default=0)
    latency_ms: Optional[float] = Field(None, ge=0, le=10000)
    last_health_check: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

    @validator("current_connections")
    def validate_connections_limit(cls, v, values):
        if (
            "performance" in values
            and v > values["performance"].max_connections
        ):
            raise ValueError("Current connections exceed maximum allowed")
        return v

    @validator("load_percentage")
    def validate_load_percentage(cls, v):
        if v > 100:
            raise ValueError("Load percentage cannot exceed 100%")
        return v


# ============================================================================
# МОДЕЛИ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================================


class UserProfileModel(BaseModel):
    """Модель профиля пользователя"""

    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: str = Field(
        ..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", min_length=2, max_length=5)


class UserPreferencesModel(BaseModel):
    """Модель предпочтений пользователя"""

    auto_connect: bool = Field(default=False)
    kill_switch: bool = Field(default=True)
    dns_protection: bool = Field(default=True)
    ad_blocker: bool = Field(default=False)
    split_tunneling: bool = Field(default=False)
    preferred_protocol: Literal["wireguard", "openvpn", "ipsec"] = Field(
        default="wireguard"
    )
    preferred_servers: List[str] = Field(default_factory=list)
    blocked_servers: List[str] = Field(default_factory=list)


class UserModel(BaseVPNModel, TimestampMixin):
    """Модель пользователя"""

    user_id: str = Field(..., min_length=1, max_length=50)
    username: str = Field(
        ..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    profile: UserProfileModel
    preferences: UserPreferencesModel
    role: Literal["admin", "user", "viewer"] = Field(default="user")
    status: Literal["active", "inactive", "suspended", "pending"] = Field(
        default="active"
    )
    two_factor_enabled: bool = Field(default=False)
    last_login: Optional[datetime] = None
    login_count: int = Field(ge=0, default=0)
    subscription_tier: Literal["free", "basic", "premium", "enterprise"] = (
        Field(default="free")
    )
    subscription_expires: Optional[datetime] = None

    @validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v


# ============================================================================
# МОДЕЛИ БЕЗОПАСНОСТИ
# ============================================================================


class SecurityEventModel(BaseVPNModel, TimestampMixin):
    """Модель события безопасности"""

    event_id: str = Field(..., min_length=1, max_length=50)
    event_type: Literal[
        "login_attempt",
        "login_success",
        "login_failure",
        "logout",
        "ddos_attack",
        "rate_limit_exceeded",
        "intrusion_detected",
        "ip_blocked",
        "ip_unblocked",
        "2fa_enabled",
        "2fa_disabled",
        "password_changed",
        "account_locked",
        "account_unlocked",
    ]
    severity: Literal["low", "medium", "high", "critical"] = Field(
        default="medium"
    )
    source_ip: str = Field(
        ...,
        pattern=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    )
    user_id: Optional[str] = Field(None, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    details: Dict[str, Any] = Field(default_factory=dict)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = Field(None, max_length=50)


class DDoSAttackModel(BaseVPNModel, TimestampMixin):
    """Модель DDoS атаки"""

    attack_id: str = Field(..., min_length=1, max_length=50)
    attack_type: Literal[
        "flood", "amplification", "reflection", "slowloris", "mixed"
    ]
    source_ips: List[str] = Field(..., min_items=1)
    target_ip: str = Field(
        ...,
        pattern=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    )
    requests_per_second: float = Field(ge=0)
    duration_seconds: int = Field(ge=0)
    total_requests: int = Field(ge=0)
    blocked: bool = Field(default=False)
    blocked_at: Optional[datetime] = None
    mitigation_applied: List[str] = Field(default_factory=list)

    @validator("source_ips")
    def validate_source_ips(cls, v):
        ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        for ip in v:
            if not re.match(ip_pattern, ip):
                raise ValueError(f"Invalid IP address format: {ip}")
        return v


class RateLimitRuleModel(BaseModel):
    """Модель правила ограничения скорости"""

    rule_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    endpoint_pattern: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(..., ge=1, le=1000000)
    window_seconds: int = Field(..., ge=1, le=86400)
    action: Literal["block", "throttle", "captcha", "log"] = Field(
        default="block"
    )
    enabled: bool = Field(default=True)
    priority: int = Field(ge=0, le=100, default=50)
    conditions: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# МОДЕЛИ АУТЕНТИФИКАЦИИ
# ============================================================================


class TwoFactorMethodModel(BaseModel):
    """Модель метода двухфакторной аутентификации"""

    method: Literal["totp", "sms", "email", "backup_code"]
    enabled: bool = Field(default=False)
    secret_key: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email_address: Optional[str] = Field(
        None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    backup_codes: List[str] = Field(default_factory=list)
    last_used: Optional[datetime] = None


class TwoFactorAuthModel(BaseVPNModel, TimestampMixin):
    """Модель двухфакторной аутентификации"""

    user_id: str = Field(..., min_length=1, max_length=50)
    enabled: bool = Field(default=False)
    methods: List[TwoFactorMethodModel] = Field(default_factory=list)
    backup_codes_count: int = Field(ge=0, le=20, default=10)
    last_verification: Optional[datetime] = None
    failed_attempts: int = Field(ge=0, default=0)
    locked_until: Optional[datetime] = None

    @validator("methods")
    def validate_methods(cls, v):
        if not v:
            return v

        method_types = [method.method for method in v]
        if len(method_types) != len(set(method_types)):
            raise ValueError("Duplicate method types not allowed")

        return v


# ============================================================================
# МОДЕЛИ МОНИТОРИНГА
# ============================================================================


class MetricDataModel(BaseModel):
    """Модель данных метрики"""

    metric_name: str = Field(..., min_length=1, max_length=100)
    value: Union[int, float] = Field(...)
    unit: str = Field(..., min_length=1, max_length=20)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class AlertRuleModel(BaseModel):
    """Модель правила алерта"""

    rule_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    metric_name: str = Field(..., min_length=1, max_length=100)
    condition: Literal["gt", "lt", "eq", "gte", "lte", "ne"] = Field(...)
    threshold: Union[int, float] = Field(...)
    duration_seconds: int = Field(ge=0, le=3600, default=0)
    severity: Literal["low", "medium", "high", "critical"] = Field(
        default="medium"
    )
    enabled: bool = Field(default=True)
    notification_channels: List[str] = Field(default_factory=list)


class AlertModel(BaseVPNModel, TimestampMixin):
    """Модель алерта"""

    alert_id: str = Field(..., min_length=1, max_length=50)
    rule_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    severity: Literal["low", "medium", "high", "critical"] = Field(...)
    status: Literal["active", "acknowledged", "resolved", "suppressed"] = (
        Field(default="active")
    )
    metric_value: Union[int, float] = Field(...)
    threshold_value: Union[int, float] = Field(...)
    acknowledged_by: Optional[str] = Field(None, max_length=50)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = Field(None, max_length=50)
    notifications_sent: List[str] = Field(default_factory=list)


# ============================================================================
# МОДЕЛИ API ЗАПРОСОВ И ОТВЕТОВ
# ============================================================================


class APIRequestModel(BaseModel):
    """Модель API запроса"""

    request_id: str = Field(..., min_length=1, max_length=50)
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(...)
    endpoint: str = Field(..., min_length=1, max_length=200)
    headers: Dict[str, str] = Field(default_factory=dict)
    query_params: Dict[str, Any] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = Field(None, max_length=50)
    ip_address: str = Field(
        ...,
        pattern=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    )
    user_agent: Optional[str] = Field(None, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIResponseModel(BaseModel):
    """Модель API ответа"""

    request_id: str = Field(..., min_length=1, max_length=50)
    status_code: int = Field(..., ge=100, le=599)
    message: str = Field(..., min_length=1, max_length=500)
    data: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    response_time_ms: float = Field(ge=0, default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator("status_code")
    def validate_status_code(cls, v):
        if v < 100 or v > 599:
            raise ValueError("Status code must be between 100 and 599")
        return v


# ============================================================================
# МОДЕЛИ КОНФИГУРАЦИИ
# ============================================================================


class DatabaseConfigModel(BaseModel):
    """Модель конфигурации базы данных"""

    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535, default=5432)
    database: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)
    ssl_mode: Literal[
        "disable", "allow", "prefer", "require", "verify-ca", "verify-full"
    ] = Field(default="prefer")
    pool_size: int = Field(ge=1, le=100, default=10)
    max_overflow: int = Field(ge=0, le=100, default=20)
    timeout: int = Field(ge=1, le=300, default=30)


class RedisConfigModel(BaseModel):
    """Модель конфигурации Redis"""

    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535, default=6379)
    password: Optional[str] = Field(None, max_length=100)
    database: int = Field(ge=0, le=15, default=0)
    ssl: bool = Field(default=False)
    max_connections: int = Field(ge=1, le=1000, default=100)
    timeout: int = Field(ge=1, le=300, default=30)


class LoggingConfigModel(BaseModel):
    """Модель конфигурации логирования"""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    format: Literal["json", "text", "syslog"] = Field(default="json")
    file_path: Optional[str] = Field(None, max_length=500)
    max_file_size: str = Field(default="10MB", pattern=r"^\d+[KMGT]?B$")
    backup_count: int = Field(ge=0, le=100, default=5)
    enable_console: bool = Field(default=True)
    enable_syslog: bool = Field(default=False)
    syslog_host: Optional[str] = Field(None, max_length=255)
    syslog_port: int = Field(ge=1, le=65535, default=514)


class VPNConfigModel(BaseVPNModel):
    """Модель конфигурации VPN"""

    database: DatabaseConfigModel
    redis: RedisConfigModel
    logging: LoggingConfigModel
    security: Dict[str, Any] = Field(default_factory=dict)
    monitoring: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, bool] = Field(default_factory=dict)
    limits: Dict[str, int] = Field(default_factory=dict)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def validate_ip_address(ip: str) -> bool:
    """Валидация IP адреса"""
    pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))


def validate_domain_name(domain: str) -> bool:
    """Валидация доменного имени"""
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
    return bool(re.match(pattern, domain))


def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Базовые модели
    "BaseVPNModel",
    "TimestampMixin",
    # VPN модели
    "VPNProtocolModel",
    "VPNConnectionModel",
    # Серверы
    "ServerLocationModel",
    "ServerPerformanceModel",
    "VPNServerModel",
    # Пользователи
    "UserProfileModel",
    "UserPreferencesModel",
    "UserModel",
    # Безопасность
    "SecurityEventModel",
    "DDoSAttackModel",
    "RateLimitRuleModel",
    # Аутентификация
    "TwoFactorMethodModel",
    "TwoFactorAuthModel",
    # Мониторинг
    "MetricDataModel",
    "AlertRuleModel",
    "AlertModel",
    # API
    "APIRequestModel",
    "APIResponseModel",
    # Конфигурация
    "DatabaseConfigModel",
    "RedisConfigModel",
    "LoggingConfigModel",
    "VPNConfigModel",
    # Вспомогательные функции
    "validate_ip_address",
    "validate_domain_name",
    "validate_email",
]
