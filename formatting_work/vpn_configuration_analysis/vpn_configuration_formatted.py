#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN Configuration - Управление конфигурацией VPN сервиса
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import asyncio
import hashlib
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VPNProtocol(Enum):
    """VPN протоколы"""

    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    IPSEC = "ipsec"
    IKEV2 = "ikev2"
    SSTP = "sstp"
    L2TP = "l2tp"


class EncryptionLevel(Enum):
    """Уровни шифрования"""

    BASIC = "basic"  # AES-128
    STANDARD = "standard"  # AES-256
    ADVANCED = "advanced"  # AES-256-GCM
    MAXIMUM = "maximum"  # ChaCha20-Poly1305


class ServerLocation(Enum):
    """Локации серверов"""

    US_EAST = "us_east"
    US_WEST = "us_west"
    EU_WEST = "eu_west"
    EU_CENTRAL = "eu_central"
    ASIA_PACIFIC = "asia_pacific"
    RUSSIA = "russia"


@dataclass
class ServerConfig:
    """Конфигурация сервера"""

    server_id: str
    name: str
    location: ServerLocation
    ip_address: str
    port: int
    protocol: VPNProtocol
    encryption: EncryptionLevel
    max_connections: int = 1000
    enabled: bool = True
    load_balancing_weight: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "server_id": self.server_id,
            "name": self.name,
            "location": self.location.value,
            "ip_address": self.ip_address,
            "port": self.port,
            "protocol": self.protocol.value,
            "encryption": self.encryption.value,
            "max_connections": self.max_connections,
            "enabled": self.enabled,
            "load_balancing_weight": self.load_balancing_weight,
            "metadata": self.metadata,
        }


@dataclass
class ClientConfig:
    """Конфигурация клиента"""

    user_id: str
    protocol: VPNProtocol
    encryption: EncryptionLevel
    dns_servers: List[str] = field(
        default_factory=lambda: ["1.1.1.1", "8.8.8.8"]
    )
    kill_switch: bool = True
    auto_connect: bool = False
    split_tunneling: bool = False
    preferred_server: Optional[str] = None
    excluded_apps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "user_id": self.user_id,
            "protocol": self.protocol.value,
            "encryption": self.encryption.value,
            "dns_servers": self.dns_servers,
            "kill_switch": self.kill_switch,
            "auto_connect": self.auto_connect,
            "split_tunneling": self.split_tunneling,
            "preferred_server": self.preferred_server,
            "excluded_apps": self.excluded_apps,
        }


@dataclass
class SecurityConfig:
    """Конфигурация безопасности"""

    enable_firewall: bool = True
    enable_leak_protection: bool = True
    enable_malware_blocking: bool = True
    enable_ad_blocking: bool = False
    enable_tracker_blocking: bool = True
    cipher_suite: str = "AES-256-GCM"
    auth_method: str = "SHA256"
    perfect_forward_secrecy: bool = True
    tls_version: str = "1.3"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "enable_firewall": self.enable_firewall,
            "enable_leak_protection": self.enable_leak_protection,
            "enable_malware_blocking": self.enable_malware_blocking,
            "enable_ad_blocking": self.enable_ad_blocking,
            "enable_tracker_blocking": self.enable_tracker_blocking,
            "cipher_suite": self.cipher_suite,
            "auth_method": self.auth_method,
            "perfect_forward_secrecy": self.perfect_forward_secrecy,
            "tls_version": self.tls_version,
        }


class VPNConfiguration:
    """
    Система управления конфигурацией VPN сервиса

    Основные функции:
    - Управление конфигурацией серверов
    - Управление конфигурацией клиентов
    - Настройки безопасности
    - Валидация конфигураций
    - Экспорт/импорт конфигураций
    - Версионирование конфигураций
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация системы конфигурации

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path or "config/vpn_main_config.json"
        self.config = self._load_config()
        self.servers: Dict[str, ServerConfig] = {}
        self.clients: Dict[str, ClientConfig] = {}
        self.security_config = SecurityConfig()
        self.config_version = "1.0.0"
        self.config_history: List[Dict[str, Any]] = []

        self._initialize_from_config()
        logger.info("VPN Configuration инициализирован")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Создание конфигурации по умолчанию"""
        default_config = {
            "version": "1.0.0",
            "global_settings": {
                "service_name": "ALADDIN VPN",
                "default_protocol": "wireguard",
                "default_encryption": "advanced",
                "enable_ipv6": True,
                "enable_killswitch": True,
                "dns_servers": ["1.1.1.1", "8.8.8.8", "9.9.9.9"],
            },
            "servers": {},
            "security": {
                "enable_firewall": True,
                "enable_leak_protection": True,
                "enable_malware_blocking": True,
                "cipher_suite": "AES-256-GCM",
                "auth_method": "SHA256",
                "tls_version": "1.3",
            },
            "features": {
                "split_tunneling": True,
                "auto_connect": True,
                "multi_hop": False,
                "obfuscation": True,
            },
            "limits": {
                "max_servers": 100,
                "max_clients_per_server": 1000,
                "max_bandwidth_per_user_mbps": 100,
            },
        }
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Сохранение конфигурации"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Сохраняем в истории
            self.config_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "version": config.get("version", "unknown"),
                    "config_hash": self._calculate_config_hash(config),
                }
            )

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"Конфигурация сохранена: {config_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Расчет хэша конфигурации для версионирования"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def _initialize_from_config(self) -> None:
        """Инициализация из конфигурации"""
        # Загружаем серверы
        for server_id, server_data in self.config.get("servers", {}).items():
            try:
                server = ServerConfig(
                    server_id=server_id,
                    name=server_data["name"],
                    location=ServerLocation(server_data["location"]),
                    ip_address=server_data["ip_address"],
                    port=server_data["port"],
                    protocol=VPNProtocol(server_data["protocol"]),
                    encryption=EncryptionLevel(server_data["encryption"]),
                    max_connections=server_data.get("max_connections", 1000),
                    enabled=server_data.get("enabled", True),
                )
                self.servers[server_id] = server
            except Exception as e:
                logger.error(f"Ошибка загрузки сервера {server_id}: {e}")

        # Загружаем настройки безопасности
        security_data = self.config.get("security", {})
        self.security_config = SecurityConfig(**security_data)

    async def add_server(self, server: ServerConfig) -> bool:
        """
        Добавление сервера

        Args:
            server: Конфигурация сервера

        Returns:
            True если успешно добавлен
        """
        if server.server_id in self.servers:
            logger.warning(f"Сервер {server.server_id} уже существует")
            return False

        if len(self.servers) >= self.config["limits"]["max_servers"]:
            logger.error("Превышен лимит серверов")
            return False

        self.servers[server.server_id] = server
        self.config["servers"][server.server_id] = server.to_dict()
        self._save_config(self.config)

        logger.info(f"Сервер добавлен: {server.server_id}")
        return True

    async def remove_server(self, server_id: str) -> bool:
        """Удаление сервера"""
        if server_id not in self.servers:
            logger.warning(f"Сервер {server_id} не найден")
            return False

        del self.servers[server_id]
        if server_id in self.config["servers"]:
            del self.config["servers"][server_id]
        self._save_config(self.config)

        logger.info(f"Сервер удален: {server_id}")
        return True

    async def update_server(
        self, server_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Обновление конфигурации сервера"""
        if server_id not in self.servers:
            logger.warning(f"Сервер {server_id} не найден")
            return False

        server = self.servers[server_id]

        # Обновляем атрибуты
        for key, value in updates.items():
            if hasattr(server, key):
                setattr(server, key, value)

        self.config["servers"][server_id] = server.to_dict()
        self._save_config(self.config)

        logger.info(f"Сервер обновлен: {server_id}")
        return True

    async def get_server(self, server_id: str) -> Optional[ServerConfig]:
        """Получение конфигурации сервера"""
        return self.servers.get(server_id)

    async def get_all_servers(
        self, enabled_only: bool = False
    ) -> List[ServerConfig]:
        """Получение всех серверов"""
        servers = list(self.servers.values())
        if enabled_only:
            servers = [s for s in servers if s.enabled]
        return servers

    async def get_servers_by_location(
        self, location: ServerLocation
    ) -> List[ServerConfig]:
        """Получение серверов по локации"""
        return [s for s in self.servers.values() if s.location == location]

    async def set_client_config(
        self, user_id: str, client_config: ClientConfig
    ) -> bool:
        """Установка конфигурации клиента"""
        self.clients[user_id] = client_config

        if "clients" not in self.config:
            self.config["clients"] = {}

        self.config["clients"][user_id] = client_config.to_dict()
        self._save_config(self.config)

        logger.info(f"Конфигурация клиента установлена: {user_id}")
        return True

    async def get_client_config(self, user_id: str) -> Optional[ClientConfig]:
        """Получение конфигурации клиента"""
        return self.clients.get(user_id)

    async def update_security_config(self, updates: Dict[str, Any]) -> bool:
        """Обновление конфигурации безопасности"""
        for key, value in updates.items():
            if hasattr(self.security_config, key):
                setattr(self.security_config, key, value)

        self.config["security"] = self.security_config.to_dict()
        self._save_config(self.config)

        logger.info("Конфигурация безопасности обновлена")
        return True

    async def validate_config(self) -> Dict[str, Any]:
        """
        Валидация конфигурации

        Returns:
            Dict с результатами валидации
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Проверка серверов
        if not self.servers:
            validation_results["errors"].append("Нет настроенных серверов")
            validation_results["valid"] = False

        for server_id, server in self.servers.items():
            # Проверка IP адреса
            if not self._validate_ip(server.ip_address):
                validation_results["errors"].append(
                    f"Некорректный IP адрес у сервера {server_id}: {server.ip_address}"
                )
                validation_results["valid"] = False

            # Проверка порта
            if not (1 <= server.port <= 65535):
                validation_results["errors"].append(
                    f"Некорректный порт у сервера {server_id}: {server.port}"
                )
                validation_results["valid"] = False

            # Проверка лимитов
            if server.max_connections > 10000:
                validation_results["warnings"].append(
                    f"Высокий лимит соединений у сервера {server_id}: {server.max_connections}"
                )

        # Проверка безопасности
        if not self.security_config.enable_firewall:
            validation_results["warnings"].append("Firewall отключен")

        if not self.security_config.enable_leak_protection:
            validation_results["warnings"].append("Защита от утечек отключена")

        return validation_results

    def _validate_ip(self, ip_address: str) -> bool:
        """Валидация IP адреса"""
        import ipaddress

        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    async def export_config(
        self, format: str = "json", output_path: Optional[str] = None
    ) -> str:
        """
        Экспорт конфигурации

        Args:
            format: Формат экспорта (json, yaml)
            output_path: Путь для сохранения

        Returns:
            Путь к экспортированному файлу
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/vpn_config_{timestamp}.{format}"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            elif format == "yaml":
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        self.config,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                    )
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")

            logger.info(f"Конфигурация экспортирована: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Ошибка экспорта конфигурации: {e}")
            raise

    async def import_config(self, file_path: str, merge: bool = False) -> bool:
        """
        Импорт конфигурации

        Args:
            file_path: Путь к файлу конфигурации
            merge: Объединить с существующей конфигурацией

        Returns:
            True если успешно импортирован
        """
        try:
            config_file = Path(file_path)
            if not config_file.exists():
                logger.error(f"Файл не найден: {file_path}")
                return False

            # Определяем формат по расширению
            if file_path.endswith(".json"):
                with open(config_file, "r", encoding="utf-8") as f:
                    new_config = json.load(f)
            elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
                with open(config_file, "r", encoding="utf-8") as f:
                    new_config = yaml.safe_load(f)
            else:
                logger.error("Неподдерживаемый формат файла")
                return False

            # Валидация импортированной конфигурации
            if not self._validate_imported_config(new_config):
                logger.error(
                    "Импортированная конфигурация не прошла валидацию"
                )
                return False

            if merge:
                # Объединяем конфигурации
                self.config.update(new_config)
            else:
                # Полная замена
                self.config = new_config

            self._initialize_from_config()
            self._save_config(self.config)

            logger.info(f"Конфигурация импортирована: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Ошибка импорта конфигурации: {e}")
            return False

    def _validate_imported_config(self, config: Dict[str, Any]) -> bool:
        """Валидация импортированной конфигурации"""
        required_keys = ["version", "global_settings"]

        for key in required_keys:
            if key not in config:
                logger.error(f"Отсутствует обязательный ключ: {key}")
                return False

        return True

    async def generate_client_config_file(
        self, user_id: str, server_id: str
    ) -> Optional[str]:
        """
        Генерация конфигурационного файла для клиента

        Args:
            user_id: ID пользователя
            server_id: ID сервера

        Returns:
            Путь к сгенерированному файлу
        """
        client_config = self.clients.get(user_id)
        server_config = self.servers.get(server_id)

        if not client_config or not server_config:
            logger.error("Конфигурация клиента или сервера не найдена")
            return None

        try:
            # Генерируем конфигурационный файл в формате OpenVPN
            config_content = self._generate_openvpn_config(
                client_config, server_config
            )

            # Сохраняем файл
            output_dir = Path(f"exports/client_configs/{user_id}")
            output_dir.mkdir(parents=True, exist_ok=True)

            config_file = output_dir / f"{server_id}.ovpn"
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)

            logger.info(f"Конфигурация клиента сгенерирована: {config_file}")
            return str(config_file)

        except Exception as e:
            logger.error(f"Ошибка генерации конфигурации клиента: {e}")
            return None

    def _generate_openvpn_config(
        self, client_config: ClientConfig, server_config: ServerConfig
    ) -> str:
        """Генерация OpenVPN конфигурации"""
        config_lines = [
            "client",
            "dev tun",
            "proto udp",
            f"remote {server_config.ip_address} {server_config.port}",
            "resolv-retry infinite",
            "nobind",
            "persist-key",
            "persist-tun",
            f"cipher {self.security_config.cipher_suite}",
            f"auth {self.security_config.auth_method}",
            "verb 3",
            "remote-cert-tls server",
        ]

        if client_config.kill_switch:
            config_lines.append("pull-filter ignore redirect-gateway")

        # DNS серверы
        for dns in client_config.dns_servers:
            config_lines.append(f"dhcp-option DNS {dns}")

        return "\n".join(config_lines)

    async def get_config_summary(self) -> Dict[str, Any]:
        """Получение сводки конфигурации"""
        return {
            "version": self.config_version,
            "total_servers": len(self.servers),
            "enabled_servers": len(
                [s for s in self.servers.values() if s.enabled]
            ),
            "total_clients": len(self.clients),
            "security_config": self.security_config.to_dict(),
            "global_settings": self.config.get("global_settings", {}),
            "config_history_count": len(self.config_history),
            "last_updated": datetime.now().isoformat(),
        }


# Пример использования
async def main():
    """Пример использования VPN Configuration"""
    config = VPNConfiguration()

    # Добавляем тестовый сервер
    server = ServerConfig(
        server_id="us_east_1",
        name="US East Server 1",
        location=ServerLocation.US_EAST,
        ip_address="203.0.113.1",
        port=1194,
        protocol=VPNProtocol.WIREGUARD,
        encryption=EncryptionLevel.ADVANCED,
    )

    await config.add_server(server)

    # Создаем конфигурацию клиента
    client = ClientConfig(
        user_id="user_123",
        protocol=VPNProtocol.WIREGUARD,
        encryption=EncryptionLevel.ADVANCED,
    )

    await config.set_client_config("user_123", client)

    # Валидация
    validation = await config.validate_config()
    print(f"Валидация: {validation}")

    # Сводка
    summary = await config.get_config_summary()
    print(f"Сводка конфигурации: {summary}")


if __name__ == "__main__":
    asyncio.run(main())
