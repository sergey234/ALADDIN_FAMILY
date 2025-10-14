#!/usr/bin/env python3
"""
ALADDIN VPN - Factory Pattern Implementation
Фабрики для создания объектов VPN системы

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 01.10.2025
"""

import importlib
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type

try:
    from interfaces.vpn_protocols import (
        APIManager,
        AuditLogger,
        AuthenticationManager,
        ConfigurationManager,
        DatabaseManager,
        DDoSProtection,
        EncryptionManager,
        IntegrationManager,
        IntrusionDetection,
        Logger,
        MetricsCollector,
        MonitoringManager,
        NetworkManager,
        RateLimiter,
        SecurityManager,
        TwoFactorAuth,
        VPNClient,
        VPNServer,
    )
    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False
    # Создаем mock классы для совместимости

    class MockInterface:
        pass
    APIManager = MockInterface
    AuditLogger = MockInterface
    AuthenticationManager = MockInterface
    ConfigurationManager = MockInterface
    DatabaseManager = MockInterface
    DDoSProtection = MockInterface
    EncryptionManager = MockInterface
    IntegrationManager = MockInterface
    IntrusionDetection = MockInterface
    Logger = MockInterface
    MetricsCollector = MockInterface
    MonitoringManager = MockInterface
    NetworkManager = MockInterface
    RateLimiter = MockInterface
    SecurityManager = MockInterface
    TwoFactorAuth = MockInterface
    VPNClient = MockInterface
    VPNServer = MockInterface

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# БАЗОВАЯ ФАБРИКА
# ============================================================================


class VPNFactory(ABC):
    """Базовый интерфейс фабрики"""

    @abstractmethod
    def create(self, config: Dict[str, Any]) -> Any:
        """Создание объекта"""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов"""
        pass


# ============================================================================
# ФАБРИКА VPN СЕРВЕРОВ
# ============================================================================


class VPNServerType(Enum):
    """Типы VPN серверов"""

    WIREGUARD = "wireguard"
    OPENVPN = "openvpn"
    IPSEC = "ipsec"
    L2TP = "l2tp"
    PPTP = "pptp"


class VPNServerFactory(VPNFactory):
    """Фабрика VPN серверов"""

    def __init__(self):
        self._server_classes = {
            VPNServerType.WIREGUARD: "servers.wireguard_server.WireGuardServer",
            VPNServerType.OPENVPN: "servers.openvpn_server.OpenVPNServer",
            VPNServerType.IPSEC: "servers.ipsec_server.IPSecServer",
            VPNServerType.L2TP: "servers.l2tp_server.L2TPServer",
            VPNServerType.PPTP: "servers.pptp_server.PPTPServer",
        }

    def create(self, config: Dict[str, Any]) -> VPNServer:
        """Создание VPN сервера"""
        server_type = VPNServerType(config.get("type", "wireguard"))

        try:
            # Динамический импорт класса сервера
            module_path, class_name = self._server_classes[server_type].rsplit(
                ".", 1
            )
            module = importlib.import_module(f"servers.{module_path}")
            server_class = getattr(module, class_name)

            # Создание экземпляра
            server = server_class()

            # Инициализация с конфигурацией
            if hasattr(server, "load_config"):
                server.load_config(config)

            logger.info(f"Created {server_type.value} server")
            return server

        except Exception as e:
            logger.error(f"Error creating {server_type.value} server: {e}")
            raise

    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов серверов"""
        return [server_type.value for server_type in VPNServerType]


# ============================================================================
# ФАБРИКА VPN КЛИЕНТОВ
# ============================================================================


class VPNClientType(Enum):
    """Типы VPN клиентов"""

    WIREGUARD = "wireguard"
    OPENVPN = "openvpn"
    IPSEC = "ipsec"
    L2TP = "l2tp"
    PPTP = "pptp"


class VPNClientFactory(VPNFactory):
    """Фабрика VPN клиентов"""

    def __init__(self):
        self._client_classes = {
            VPNClientType.WIREGUARD: "clients.wireguard_client.WireGuardClient",
            VPNClientType.OPENVPN: "clients.openvpn_client.OpenVPNClient",
            VPNClientType.IPSEC: "clients.ipsec_client.IPSecClient",
            VPNClientType.L2TP: "clients.l2tp_client.L2TPClient",
            VPNClientType.PPTP: "clients.pptp_client.PPTPClient",
        }

    def create(self, config: Dict[str, Any]) -> VPNClient:
        """Создание VPN клиента"""
        client_type = VPNClientType(config.get("type", "wireguard"))

        try:
            # Динамический импорт класса клиента
            module_path, class_name = self._client_classes[client_type].rsplit(
                ".", 1
            )
            module = importlib.import_module(f"clients.{module_path}")
            client_class = getattr(module, class_name)

            # Создание экземпляра
            client = client_class()

            # Инициализация с конфигурацией
            if hasattr(client, "load_config"):
                client.load_config(config)

            logger.info(f"Created {client_type.value} client")
            return client

        except Exception as e:
            logger.error(f"Error creating {client_type.value} client: {e}")
            raise

    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов клиентов"""
        return [client_type.value for client_type in VPNClientType]


# ============================================================================
# ФАБРИКА СИСТЕМ БЕЗОПАСНОСТИ
# ============================================================================


class SecuritySystemType(Enum):
    """Типы систем безопасности"""

    DDOS_PROTECTION = "ddos_protection"
    RATE_LIMITER = "rate_limiter"
    INTRUSION_DETECTION = "intrusion_detection"
    FIREWALL = "firewall"
    ANTIVIRUS = "antivirus"


class SecuritySystemFactory(VPNFactory):
    """Фабрика систем безопасности"""

    def __init__(self):
        self._security_classes = {
            SecuritySystemType.DDOS_PROTECTION: "protection.ddos_protection.DDoSProtectionSystem",
            SecuritySystemType.RATE_LIMITER: "protection.rate_limiter.AdvancedRateLimiter",
            SecuritySystemType.INTRUSION_DETECTION: "protection.intrusion_detection.IntrusionDetectionSystem",
            SecuritySystemType.FIREWALL: "protection.firewall.FirewallManager",
            SecuritySystemType.ANTIVIRUS: "protection.antivirus.AntivirusManager",
        }

    def create(self, config: Dict[str, Any]) -> SecurityManager:
        """Создание системы безопасности"""
        system_type = SecuritySystemType(config.get("type", "ddos_protection"))

        try:
            # Динамический импорт класса системы
            module_path, class_name = self._security_classes[
                system_type
            ].rsplit(".", 1)
            module = importlib.import_module(module_path)
            system_class = getattr(module, class_name)

            # Создание экземпляра
            system = system_class()

            # Инициализация с конфигурацией
            if hasattr(system, "load_config"):
                system.load_config(config)

            logger.info(f"Created {system_type.value} security system")
            return system

        except Exception as e:
            logger.error(
                f"Error creating {system_type.value} security system: {e}"
            )
            raise

    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов систем безопасности"""
        return [system_type.value for system_type in SecuritySystemType]


# ============================================================================
# ФАБРИКА СИСТЕМ АУТЕНТИФИКАЦИИ
# ============================================================================


class AuthSystemType(Enum):
    """Типы систем аутентификации"""

    TWO_FACTOR_AUTH = "two_factor_auth"
    LDAP_AUTH = "ldap_auth"
    OAUTH_AUTH = "oauth_auth"
    SAML_AUTH = "saml_auth"
    RADIUS_AUTH = "radius_auth"


class AuthSystemFactory(VPNFactory):
    """Фабрика систем аутентификации"""

    def __init__(self):
        self._auth_classes = {
            AuthSystemType.TWO_FACTOR_AUTH: "auth.two_factor_auth.TwoFactorAuth",
            AuthSystemType.LDAP_AUTH: "auth.ldap_auth.LDAPAuth",
            AuthSystemType.OAUTH_AUTH: "auth.oauth_auth.OAuthAuth",
            AuthSystemType.SAML_AUTH: "auth.saml_auth.SAMLAuth",
            AuthSystemType.RADIUS_AUTH: "auth.radius_auth.RadiusAuth",
        }

    def create(self, config: Dict[str, Any]) -> AuthenticationManager:
        """Создание системы аутентификации"""
        auth_type = AuthSystemType(config.get("type", "two_factor_auth"))

        try:
            # Динамический импорт класса аутентификации
            module_path, class_name = self._auth_classes[auth_type].rsplit(
                ".", 1
            )
            module = importlib.import_module(module_path)
            auth_class = getattr(module, class_name)

            # Создание экземпляра
            auth_system = auth_class()

            # Инициализация с конфигурацией
            if hasattr(auth_system, "load_config"):
                auth_system.load_config(config)

            logger.info(f"Created {auth_type.value} authentication system")
            return auth_system

        except Exception as e:
            logger.error(
                f"Error creating {auth_type.value} authentication system: {e}"
            )
            raise

    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов аутентификации"""
        return [auth_type.value for auth_type in AuthSystemType]


# ============================================================================
# ФАБРИКА СИСТЕМ ЛОГИРОВАНИЯ
# ============================================================================


class LoggerType(Enum):
    """Типы логгеров"""

    AUDIT_LOGGER = "audit_logger"
    SECURITY_LOGGER = "security_logger"
    ACCESS_LOGGER = "access_logger"
    ERROR_LOGGER = "error_logger"
    PERFORMANCE_LOGGER = "performance_logger"


class LoggerFactory(VPNFactory):
    """Фабрика логгеров"""

    def __init__(self):
        self._logger_classes = {
            LoggerType.AUDIT_LOGGER: "audit_logging.audit_logger.SecurityAuditLogger",
            LoggerType.SECURITY_LOGGER: "logging.security_logger.SecurityLogger",
            LoggerType.ACCESS_LOGGER: "logging.access_logger.AccessLogger",
            LoggerType.ERROR_LOGGER: "logging.error_logger.ErrorLogger",
            LoggerType.PERFORMANCE_LOGGER: "logging.performance_logger.PerformanceLogger",
        }

    def create(self, config: Dict[str, Any]) -> Logger:
        """Создание логгера"""
        logger_type = LoggerType(config.get("type", "audit_logger"))

        try:
            # Динамический импорт класса логгера
            module_path, class_name = self._logger_classes[logger_type].rsplit(
                ".", 1
            )
            module = importlib.import_module(module_path)
            logger_class = getattr(module, class_name)

            # Создание экземпляра
            logger_instance = logger_class()

            # Инициализация с конфигурацией
            if hasattr(logger_instance, "load_config"):
                logger_instance.load_config(config)

            logger.info(f"Created {logger_type.value} logger")
            return logger_instance

        except Exception as e:
            logger.error(f"Error creating {logger_type.value} logger: {e}")
            raise

    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов логгеров"""
        return [logger_type.value for logger_type in LoggerType]


# ============================================================================
# ФАБРИКА СИСТЕМ МОНИТОРИНГА
# ============================================================================


class MonitoringSystemType(Enum):
    """Типы систем мониторинга"""

    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    ELK_STACK = "elk_stack"
    ZABBIX = "zabbix"
    NAGIOS = "nagios"


class MonitoringSystemFactory(VPNFactory):
    """Фабрика систем мониторинга"""

    def __init__(self):
        self._monitoring_classes = {
            MonitoringSystemType.PROMETHEUS: "monitoring.prometheus_monitor.PrometheusMonitor",
            MonitoringSystemType.GRAFANA: "monitoring.grafana_monitor.GrafanaMonitor",
            MonitoringSystemType.ELK_STACK: "monitoring.elk_monitor.ELKMonitor",
            MonitoringSystemType.ZABBIX: "monitoring.zabbix_monitor.ZabbixMonitor",
            MonitoringSystemType.NAGIOS: "monitoring.nagios_monitor.NagiosMonitor",
        }

    def create(self, config: Dict[str, Any]) -> MonitoringManager:
        """Создание системы мониторинга"""
        monitoring_type = MonitoringSystemType(
            config.get("type", "prometheus")
        )

        try:
            # Динамический импорт класса мониторинга
            module_path, class_name = self._monitoring_classes[
                monitoring_type
            ].rsplit(".", 1)
            module = importlib.import_module(module_path)
            monitoring_class = getattr(module, class_name)

            # Создание экземпляра
            monitoring_system = monitoring_class()

            # Инициализация с конфигурацией
            if hasattr(monitoring_system, "load_config"):
                monitoring_system.load_config(config)

            logger.info(f"Created {monitoring_type.value} monitoring system")
            return monitoring_system

        except Exception as e:
            logger.error(
                f"Error creating {monitoring_type.value} monitoring system: {e}"
            )
            raise

    def get_supported_types(self) -> List[str]:
        """Получение поддерживаемых типов мониторинга"""
        return [
            monitoring_type.value for monitoring_type in MonitoringSystemType
        ]


# ============================================================================
# УНИВЕРСАЛЬНАЯ ФАБРИКА
# ============================================================================


class UniversalVPNFactory:
    """Универсальная фабрика для всех компонентов VPN"""

    def __init__(self):
        self._factories = {
            "server": VPNServerFactory(),
            "client": VPNClientFactory(),
            "security": SecuritySystemFactory(),
            "auth": AuthSystemFactory(),
            "logger": LoggerFactory(),
            "monitoring": MonitoringSystemFactory(),
        }

    def create_component(
        self, component_type: str, config: Dict[str, Any]
    ) -> Any:
        """Создание компонента по типу"""
        factory = self._factories.get(component_type)
        if not factory:
            raise ValueError(f"Unknown component type: {component_type}")

        return factory.create(config)

    def get_supported_components(self) -> Dict[str, List[str]]:
        """Получение всех поддерживаемых компонентов"""
        return {
            component_type: factory.get_supported_types()
            for component_type, factory in self._factories.items()
        }

    def register_factory(
        self, component_type: str, factory: VPNFactory
    ) -> None:
        """Регистрация новой фабрики"""
        self._factories[component_type] = factory
        logger.info(f"Registered factory for component type: {component_type}")

    def unregister_factory(self, component_type: str) -> None:
        """Отмена регистрации фабрики"""
        if component_type in self._factories:
            del self._factories[component_type]
            logger.info(
                f"Unregistered factory for component type: {component_type}"
            )


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def create_vpn_server(server_type: str, config: Dict[str, Any]) -> VPNServer:
    """Создание VPN сервера"""
    factory = VPNServerFactory()
    config["type"] = server_type
    return factory.create(config)


def create_vpn_client(client_type: str, config: Dict[str, Any]) -> VPNClient:
    """Создание VPN клиента"""
    factory = VPNClientFactory()
    config["type"] = client_type
    return factory.create(config)


def create_security_system(
    system_type: str, config: Dict[str, Any]
) -> SecurityManager:
    """Создание системы безопасности"""
    factory = SecuritySystemFactory()
    config["type"] = system_type
    return factory.create(config)


def create_auth_system(
    auth_type: str, config: Dict[str, Any]
) -> AuthenticationManager:
    """Создание системы аутентификации"""
    factory = AuthSystemFactory()
    config["type"] = auth_type
    return factory.create(config)


def create_logger(logger_type: str, config: Dict[str, Any]) -> Logger:
    """Создание логгера"""
    factory = LoggerFactory()
    config["type"] = logger_type
    return factory.create(config)


def create_monitoring_system(
    monitoring_type: str, config: Dict[str, Any]
) -> MonitoringManager:
    """Создание системы мониторинга"""
    factory = MonitoringSystemFactory()
    config["type"] = monitoring_type
    return factory.create(config)


# ============================================================================
# ЭКСПОРТ
# ============================================================================

__all__ = [
    # Базовые классы
    "VPNFactory",
    # Фабрики компонентов
    "VPNServerFactory",
    "VPNClientFactory",
    "SecuritySystemFactory",
    "AuthSystemFactory",
    "LoggerFactory",
    "MonitoringSystemFactory",
    # Универсальная фабрика
    "UniversalVPNFactory",
    # Вспомогательные функции
    "create_vpn_server",
    "create_vpn_client",
    "create_security_system",
    "create_auth_system",
    "create_logger",
    "create_monitoring_system",
    # Перечисления
    "VPNServerType",
    "VPNClientType",
    "SecuritySystemType",
    "AuthSystemType",
    "LoggerType",
    "MonitoringSystemType",
]
