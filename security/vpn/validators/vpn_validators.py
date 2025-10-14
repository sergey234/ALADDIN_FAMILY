#!/usr/bin/env python3
"""
ALADDIN VPN - Validators
Валидаторы для VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import ipaddress
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union
from urllib.parse import urlparse

import asyncio

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    dns = None

# ============================================================================
# БАЗОВЫЕ ВАЛИДАТОРЫ
# ============================================================================


class BaseValidator:
    """Базовый класс для валидаторов"""

    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        """Валидация обязательного поля"""
        if value is None or value == "":
            raise ValueError(f"Field '{field_name}' is required")

    @staticmethod
    def validate_type(
        value: Any, expected_type: type, field_name: str
    ) -> None:
        """Валидация типа поля"""
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Field '{field_name}' must be of type "
                f"{expected_type.__name__}, got {type(value).__name__}"
            )

    @staticmethod
    def validate_range(
        value: Union[int, float],
        min_val: Union[int, float],
        max_val: Union[int, float],
        field_name: str,
    ) -> None:
        """Валидация диапазона значений"""
        if not (min_val <= value <= max_val):
            raise ValueError(
                f"Field '{field_name}' must be between {min_val} and "
                f"{max_val}, got {value}"
            )


# ============================================================================
# СЕТЕВЫЕ ВАЛИДАТОРЫ
# ============================================================================


class NetworkValidator(BaseValidator):
    """Валидаторы для сетевых адресов"""

    IPV4_PATTERN = (
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    IPV6_PATTERN = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
    DOMAIN_PATTERN = (
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
    )
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    URL_PATTERN = (
        r"^https?://(?:[-\w.])+(?:\:[0-9]+)?"
        r"(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
    )

    @staticmethod
    def validate_ipv4(ip: str) -> bool:
        """Валидация IPv4 адреса"""
        if not isinstance(ip, str):
            return False

        if not re.match(NetworkValidator.IPV4_PATTERN, ip):
            return False

        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def validate_ipv6(ip: str) -> bool:
        """Валидация IPv6 адреса"""
        if not isinstance(ip, str):
            return False

        if not re.match(NetworkValidator.IPV6_PATTERN, ip):
            return False

        try:
            ipaddress.IPv6Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Валидация IP адреса (IPv4 или IPv6)"""
        return NetworkValidator.validate_ipv4(
            ip
        ) or NetworkValidator.validate_ipv6(ip)

    @staticmethod
    def validate_domain_name(domain: str) -> bool:
        """Валидация доменного имени"""
        if not isinstance(domain, str):
            return False

        if len(domain) > 253:
            return False

        if not re.match(NetworkValidator.DOMAIN_PATTERN, domain):
            return False

        # Проверяем, что домен не начинается или заканчивается точкой
        if domain.startswith(".") or domain.endswith("."):
            return False

        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация email адреса"""
        if not isinstance(email, str):
            return False

        if len(email) > 254:
            return False

        if not re.match(NetworkValidator.EMAIL_PATTERN, email):
            return False

        # Дополнительная проверка длины локальной части
        local_part, domain_part = email.split("@", 1)
        if len(local_part) > 64:
            return False

        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Валидация URL"""
        if not isinstance(url, str):
            return False

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in [
                "http",
                "https",
            ]
        except Exception:
            return False

    @staticmethod
    def validate_port(port: Union[int, str]) -> bool:
        """Валидация порта"""
        try:
            port_int = int(port)
            return 1 <= port_int <= 65535
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_cidr(cidr: str) -> bool:
        """Валидация CIDR блока"""
        if not isinstance(cidr, str):
            return False

        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False

    @staticmethod
    async def validate_dns_resolution(
        domain: str, record_type: str = "A"
    ) -> bool:
        """Асинхронная валидация DNS разрешения"""
        if not NetworkValidator.validate_domain_name(domain):
            return False

        if not DNS_AVAILABLE:
            # Если DNS модуль недоступен, возвращаем True для совместимости
            return True

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            resolver.query(domain, record_type)
            return True
        except Exception:
            return False

    @staticmethod
    async def validate_connectivity(
        host: str, port: int, timeout: int = 5
    ) -> bool:
        """Асинхронная валидация подключения к хосту"""
        if not NetworkValidator.validate_ip_address(
            host
        ) and not NetworkValidator.validate_domain_name(host):
            return False

        if not NetworkValidator.validate_port(port):
            return False

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False


# ============================================================================
# ВАЛИДАТОРЫ БЕЗОПАСНОСТИ
# ============================================================================


class SecurityValidator(BaseValidator):
    """Валидаторы для безопасности"""

    @staticmethod
    def validate_password_strength(
        password: str, min_length: int = 8
    ) -> Tuple[bool, List[str]]:
        """Валидация силы пароля"""
        errors = []

        if len(password) < min_length:
            errors.append(
                f"Password must be at least {min_length} characters long"
            )

        if not re.search(r"[a-z]", password):
            errors.append(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"[A-Z]", password):
            errors.append(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(
                "Password must contain at least one special character"
            )

        # Проверка на общие пароли
        common_passwords = [
            "password",
            "123456",
            "123456789",
            "qwerty",
            "abc123",
            "password123",
            "admin",
            "letmein",
            "welcome",
            "monkey",
        ]

        if password.lower() in common_passwords:
            errors.append("Password is too common")

        return len(errors) == 0, errors

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, List[str]]:
        """Валидация имени пользователя"""
        errors = []

        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")

        if len(username) > 20:
            errors.append("Username must be no more than 20 characters long")

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            errors.append(
                "Username can only contain letters, numbers, "
                "underscores, and hyphens"
            )

        if username.startswith("_") or username.endswith("_"):
            errors.append("Username cannot start or end with underscore")

        if username.startswith("-") or username.endswith("-"):
            errors.append("Username cannot start or end with hyphen")

        return len(errors) == 0, errors

    @staticmethod
    def validate_2fa_code(code: str, method: str) -> bool:
        """Валидация кода двухфакторной аутентификации"""
        if method == "totp":
            # TOTP код должен быть 6-8 цифр
            return re.match(r"^\d{6,8}$", code) is not None

        elif method == "sms":
            # SMS код должен быть 4-8 цифр
            return re.match(r"^\d{4,8}$", code) is not None

        elif method == "email":
            # Email код должен быть 6-8 символов (буквы и цифры)
            return re.match(r"^[A-Z0-9]{6,8}$", code) is not None

        elif method == "backup_code":
            # Backup код должен быть 8-16 символов
            return re.match(r"^[A-Z0-9]{8,16}$", code) is not None

        return False

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Валидация API ключа"""
        if not isinstance(api_key, str):
            return False

        # API ключ должен быть 32-64 символа, содержать только буквы,
        # цифры и дефисы
        if not re.match(r"^[a-zA-Z0-9-]{32,64}$", api_key):
            return False

        return True

    @staticmethod
    def validate_jwt_token(token: str) -> bool:
        """Валидация JWT токена"""
        if not isinstance(token, str):
            return False

        # JWT должен содержать 3 части, разделенные точками
        parts = token.split(".")
        if len(parts) != 3:
            return False

        # Каждая часть должна быть base64url закодирована
        import base64

        try:
            for part in parts:
                base64.urlsafe_b64decode(part + "==")  # Добавляем padding
            return True
        except Exception:
            return False


# ============================================================================
# ВАЛИДАТОРЫ ДАННЫХ
# ============================================================================


class DataValidator(BaseValidator):
    """Валидаторы для данных"""

    @staticmethod
    def validate_json_schema(
        data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Валидация JSON данных по схеме"""
        errors = []

        # Простая валидация схемы (можно заменить на jsonschema)
        for field, rules in schema.items():
            if "required" in rules and rules["required"]:
                if field not in data:
                    errors.append(f"Required field '{field}' is missing")
                    continue

            if field in data:
                value = data[field]

                if "type" in rules:
                    expected_type = rules["type"]
                    if expected_type == "string" and not isinstance(
                        value, str
                    ):
                        errors.append(f"Field '{field}' must be a string")
                    elif expected_type == "integer" and not isinstance(
                        value, int
                    ):
                        errors.append(f"Field '{field}' must be an integer")
                    elif expected_type == "number" and not isinstance(
                        value, (int, float)
                    ):
                        errors.append(f"Field '{field}' must be a number")
                    elif expected_type == "boolean" and not isinstance(
                        value, bool
                    ):
                        errors.append(f"Field '{field}' must be a boolean")

                if (
                    "min_length" in rules
                    and isinstance(value, str)
                    and len(value) < rules["min_length"]
                ):
                    errors.append(
                        f"Field '{field}' must be at least "
                        f"{rules['min_length']} characters long"
                    )

                if (
                    "max_length" in rules
                    and isinstance(value, str)
                    and len(value) > rules["max_length"]
                ):
                    errors.append(
                        f"Field '{field}' must be no more than "
                        f"{rules['max_length']} characters long"
                    )

                if (
                    "min" in rules
                    and isinstance(value, (int, float))
                    and value < rules["min"]
                ):
                    errors.append(
                        f"Field '{field}' must be at least {rules['min']}"
                    )

                if (
                    "max" in rules
                    and isinstance(value, (int, float))
                    and value > rules["max"]
                ):
                    errors.append(
                        f"Field '{field}' must be no more than {rules['max']}"
                    )

                if (
                    "pattern" in rules
                    and isinstance(value, str)
                    and not re.match(rules["pattern"], value)
                ):
                    errors.append(
                        f"Field '{field}' does not match required pattern"
                    )

        return len(errors) == 0, errors

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Валидация диапазона дат"""
        if not isinstance(start_date, datetime) or not isinstance(
            end_date, datetime
        ):
            return False

        return start_date <= end_date

    @staticmethod
    def validate_timezone(timezone: str) -> bool:
        """Валидация часового пояса"""
        try:
            import pytz

            pytz.timezone(timezone)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_language_code(language: str) -> bool:
        """Валидация кода языка"""
        # Простая валидация ISO 639-1 кодов
        return re.match(r"^[a-z]{2}(-[A-Z]{2})?$", language) is not None

    @staticmethod
    def validate_currency_code(currency: str) -> bool:
        """Валидация кода валюты"""
        # Валидация ISO 4217 кодов валют
        return (
            re.match(r"^[A-Z]{3}$", currency) is not None
            and len(currency) == 3
        )


# ============================================================================
# ВАЛИДАТОРЫ КОНФИГУРАЦИИ
# ============================================================================


class ConfigValidator(BaseValidator):
    """Валидаторы для конфигурации"""

    @staticmethod
    def validate_database_config(
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Валидация конфигурации базы данных"""
        errors = []
        required_fields = ["host", "port", "database", "username", "password"]

        for field in required_fields:
            if field not in config:
                errors.append(
                    f"Database config missing required field: {field}"
                )

        if (
            "host" in config
            and not NetworkValidator.validate_domain_name(config["host"])
            and not NetworkValidator.validate_ip_address(config["host"])
        ):
            errors.append(
                "Database host must be a valid IP address or domain name"
            )

        if "port" in config and not NetworkValidator.validate_port(
            config["port"]
        ):
            errors.append("Database port must be between 1 and 65535")

        if "pool_size" in config and (
            not isinstance(config["pool_size"], int) or config["pool_size"] < 1
        ):
            errors.append("Database pool_size must be a positive integer")

        return len(errors) == 0, errors

    @staticmethod
    def validate_redis_config(
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Валидация конфигурации Redis"""
        errors = []
        required_fields = ["host", "port"]

        for field in required_fields:
            if field not in config:
                errors.append(f"Redis config missing required field: {field}")

        if (
            "host" in config
            and not NetworkValidator.validate_domain_name(config["host"])
            and not NetworkValidator.validate_ip_address(config["host"])
        ):
            errors.append(
                "Redis host must be a valid IP address or domain name"
            )

        if "port" in config and not NetworkValidator.validate_port(
            config["port"]
        ):
            errors.append("Redis port must be between 1 and 65535")

        if "database" in config and (
            not isinstance(config["database"], int)
            or not 0 <= config["database"] <= 15
        ):
            errors.append("Redis database must be between 0 and 15")

        return len(errors) == 0, errors

    @staticmethod
    def validate_logging_config(
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Валидация конфигурации логирования"""
        errors = []

        if "level" in config and config["level"] not in [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]:
            errors.append(
                "Logging level must be one of: DEBUG, INFO, WARNING, "
                "ERROR, CRITICAL"
            )

        if "format" in config and config["format"] not in [
            "json",
            "text",
            "syslog",
        ]:
            errors.append("Logging format must be one of: json, text, syslog")

        if "max_file_size" in config:
            if not re.match(r"^\d+[KMGT]?B$", config["max_file_size"]):
                errors.append(
                    "Logging max_file_size must be in format like '10MB'"
                )

        if "backup_count" in config and (
            not isinstance(config["backup_count"], int)
            or config["backup_count"] < 0
        ):
            errors.append(
                "Logging backup_count must be a non-negative integer"
            )

        return len(errors) == 0, errors


# ============================================================================
# КОМПОЗИТНЫЕ ВАЛИДАТОРЫ
# ============================================================================


class CompositeValidator(BaseValidator):
    """Композитные валидаторы"""

    @staticmethod
    def validate_vpn_connection_data(
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Валидация данных VPN подключения"""
        errors = []

        # Схема валидации
        schema = {
            "connection_id": {
                "required": True,
                "type": "string",
                "min_length": 1,
                "max_length": 50,
            },
            "user_id": {
                "required": True,
                "type": "string",
                "min_length": 1,
                "max_length": 50,
            },
            "server_id": {
                "required": True,
                "type": "string",
                "min_length": 1,
                "max_length": 50,
            },
            "protocol": {
                "required": True,
                "type": "string",
                "pattern": r"^(wireguard|openvpn|ipsec|l2tp|pptp)$",
            },
            "status": {
                "required": True,
                "type": "string",
                "pattern": (
                    r"^(connecting|connected|disconnected|failed|"
                    r"reconnecting)$"
                ),
            },
            "local_ip": {"required": False, "type": "string"},
            "remote_ip": {"required": False, "type": "string"},
            "bytes_sent": {"required": False, "type": "integer", "min": 0},
            "bytes_received": {"required": False, "type": "integer", "min": 0},
        }

        # Валидация по схеме
        is_valid, schema_errors = DataValidator.validate_json_schema(
            data, schema
        )
        errors.extend(schema_errors)

        # Дополнительные валидации
        if (
            "local_ip" in data
            and data["local_ip"]
            and not NetworkValidator.validate_ip_address(data["local_ip"])
        ):
            errors.append("local_ip must be a valid IP address")

        if (
            "remote_ip" in data
            and data["remote_ip"]
            and not NetworkValidator.validate_ip_address(data["remote_ip"])
        ):
            errors.append("remote_ip must be a valid IP address")

        return len(errors) == 0, errors

    @staticmethod
    def validate_security_event_data(
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Валидация данных события безопасности"""
        errors = []

        # Схема валидации
        schema = {
            "event_id": {
                "required": True,
                "type": "string",
                "min_length": 1,
                "max_length": 50,
            },
            "event_type": {
                "required": True,
                "type": "string",
                "min_length": 1,
                "max_length": 50,
            },
            "severity": {
                "required": True,
                "type": "string",
                "pattern": r"^(low|medium|high|critical)$",
            },
            "source_ip": {"required": True, "type": "string"},
            "description": {
                "required": True,
                "type": "string",
                "min_length": 1,
                "max_length": 500,
            },
            "user_id": {"required": False, "type": "string", "max_length": 50},
        }

        # Валидация по схеме
        is_valid, schema_errors = DataValidator.validate_json_schema(
            data, schema
        )
        errors.extend(schema_errors)

        # Дополнительные валидации
        if "source_ip" in data and not NetworkValidator.validate_ip_address(
            data["source_ip"]
        ):
            errors.append("source_ip must be a valid IP address")

        return len(errors) == 0, errors


# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Базовые классы
    "BaseValidator",
    # Сетевые валидаторы
    "NetworkValidator",
    # Валидаторы безопасности
    "SecurityValidator",
    # Валидаторы данных
    "DataValidator",
    # Валидаторы конфигурации
    "ConfigValidator",
    # Композитные валидаторы
    "CompositeValidator",
]
