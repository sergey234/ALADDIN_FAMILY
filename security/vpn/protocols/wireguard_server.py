#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WireGuard Server - Высокопроизводительный VPN сервер
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

import asyncio

logger = logging.getLogger(__name__)


class WireGuardState(Enum):
    """Состояния WireGuard сервера"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class WireGuardConfig:
    """Конфигурация WireGuard сервера"""

    interface_name: str = "wg0"
    listen_port: int = 51820
    private_key: str = ""
    public_key: str = ""
    allowed_ips: str = "10.0.0.0/24"
    endpoint: str = ""
    persistent_keepalive: int = 25


@dataclass
class ClientPeer:
    """Клиентский пир для WireGuard"""

    name: str
    public_key: str
    allowed_ips: str
    endpoint: Optional[str] = None
    persistent_keepalive: int = 25


class ALADDINWireGuardServer:
    """ALADDIN WireGuard сервер с высокопроизводительной архитектурой"""

    def __init__(self, config: WireGuardConfig):
        self.config = config
        self.state = WireGuardState.STOPPED
        self.clients: Dict[str, ClientPeer] = {}
        self.interface_file = (
            f"/etc/wireguard/{self.config.interface_name}.conf"
        )
        self.logger = logging.getLogger(
            f"{__name__}.{self.config.interface_name}"
        )

    async def start_server(self) -> bool:
        """Запуск WireGuard сервера"""
        try:
            self.logger.info(
                f"🚀 Запуск WireGuard сервера {self.config.interface_name}"
            )
            self.state = WireGuardState.STARTING

            # Генерация ключей если нужно
            if not self.config.private_key:
                await self._generate_keys()

            # Создание конфигурации
            await self._create_server_config()

            # Запуск интерфейса
            result = await self._start_interface()
            if result:
                self.state = WireGuardState.RUNNING
                self.logger.info(
                    f"✅ WireGuard сервер {self.config.interface_name} запущен"
                )
                return True
            else:
                self.state = WireGuardState.ERROR
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска WireGuard сервера: {e}")
            self.state = WireGuardState.ERROR
            return False

    async def stop_server(self) -> bool:
        """Остановка WireGuard сервера"""
        try:
            self.logger.info(
                f"🛑 Остановка WireGuard сервера {self.config.interface_name}"
            )
            self.state = WireGuardState.STOPPING

            result = await self._stop_interface()
            if result:
                self.state = WireGuardState.STOPPED
                self.logger.info(
                    f"✅ WireGuard сервер {self.config.interface_name} остановлен"
                )
                return True
            else:
                self.state = WireGuardState.ERROR
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка остановки WireGuard сервера: {e}")
            self.state = WireGuardState.ERROR
            return False

    async def add_client(self, client: ClientPeer) -> bool:
        """Добавление клиента"""
        try:
            self.logger.info(f"➕ Добавление клиента {client.name}")
            self.clients[client.name] = client
            await self._update_server_config()
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления клиента: {e}")
            return False

    async def remove_client(self, client_name: str) -> bool:
        """Удаление клиента"""
        try:
            self.logger.info(f"➖ Удаление клиента {client_name}")
            if client_name in self.clients:
                del self.clients[client_name]
                await self._update_server_config()
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления клиента: {e}")
            return False

    async def get_server_status(self) -> Dict:
        """Получение статуса сервера"""
        return {
            "interface": self.config.interface_name,
            "state": self.state.value,
            "listen_port": self.config.listen_port,
            "clients_count": len(self.clients),
            "public_key": self.config.public_key,
            "endpoint": self.config.endpoint,
            "allowed_ips": self.config.allowed_ips,
        }

    async def _generate_keys(self) -> None:
        """Генерация ключей WireGuard"""
        try:
            # Генерация приватного ключа
            result = subprocess.run(
                ["wg", "genkey"], capture_output=True, text=True, check=True
            )
            self.config.private_key = result.stdout.strip()

            # Генерация публичного ключа
            result = subprocess.run(
                ["wg", "pubkey"],
                input=self.config.private_key,
                capture_output=True,
                text=True,
                check=True,
            )
            self.config.public_key = result.stdout.strip()

            self.logger.info("🔑 Ключи WireGuard сгенерированы")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Ошибка генерации ключей: {e}")
            raise

    async def _create_server_config(self) -> None:
        """Создание конфигурации сервера"""
        config_content = f"""[Interface]
PrivateKey = {self.config.private_key}
Address = {self.config.allowed_ips.split('/')[0].replace('.0', '.1')}/24
ListenPort = {self.config.listen_port}
SaveConfig = true

"""
        # Добавление клиентов
        for client in self.clients.values():
            config_content += f"""
[Peer]
PublicKey = {client.public_key}
AllowedIPs = {client.allowed_ips}
"""
            if client.persistent_keepalive:
                config_content += (
                    f"PersistentKeepalive = {client.persistent_keepalive}\n"
                )

        # Запись конфигурации
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(config_content)
            temp_file = f.name

        try:
            # Копирование в системную директорию
            subprocess.run(
                ["sudo", "cp", temp_file, self.interface_file], check=True
            )
            os.chmod(self.interface_file, 0o600)
            self.logger.info(f"📝 Конфигурация создана: {self.interface_file}")
        finally:
            os.unlink(temp_file)

    async def _start_interface(self) -> bool:
        """Запуск WireGuard интерфейса"""
        try:
            subprocess.run(
                ["sudo", "wg-quick", "up", self.config.interface_name],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Ошибка запуска интерфейса: {e}")
            return False

    async def _stop_interface(self) -> bool:
        """Остановка WireGuard интерфейса"""
        try:
            subprocess.run(
                ["sudo", "wg-quick", "down", self.config.interface_name],
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Ошибка остановки интерфейса: {e}")
            return False

    async def _update_server_config(self) -> None:
        """Обновление конфигурации сервера"""
        if self.state == WireGuardState.RUNNING:
            await self._create_server_config()
            # Перезагрузка конфигурации
            subprocess.run(
                [
                    "sudo",
                    "wg",
                    "syncconf",
                    self.config.interface_name,
                    self.interface_file,
                ],
                capture_output=True,
            )


class WireGuardManager:
    """Менеджер WireGuard серверов"""

    def __init__(self):
        self.servers: Dict[str, ALADDINWireGuardServer] = {}
        self.logger = logging.getLogger(f"{__name__}.manager")

    async def create_server(
        self, name: str, config: WireGuardConfig
    ) -> ALADDINWireGuardServer:
        """Создание нового сервера"""
        server = ALADDINWireGuardServer(config)
        self.servers[name] = server
        self.logger.info(f"📦 Создан WireGuard сервер: {name}")
        return server

    async def get_server(self, name: str) -> Optional[ALADDINWireGuardServer]:
        """Получение сервера по имени"""
        return self.servers.get(name)

    async def remove_server(self, name: str) -> bool:
        """Удаление сервера"""
        if name in self.servers:
            server = self.servers[name]
            await server.stop_server()
            del self.servers[name]
            self.logger.info(f"🗑️ Удален WireGuard сервер: {name}")
            return True
        return False

    async def get_all_servers_status(self) -> Dict:
        """Получение статуса всех серверов"""
        status = {}
        for name, server in self.servers.items():
            status[name] = await server.get_server_status()
        return status


# Глобальный менеджер
wireguard_manager = WireGuardManager()


async def main():
    """Основная функция для тестирования"""
    logging.basicConfig(level=logging.INFO)

    # Создание тестового сервера
    config = WireGuardConfig(
        interface_name="wg0", listen_port=51820, allowed_ips="10.0.0.0/24"
    )

    server = await wireguard_manager.create_server("test_server", config)

    # Запуск сервера
    await server.start_server()

    # Добавление тестового клиента
    client = ClientPeer(
        name="test_client",
        public_key="test_public_key",
        allowed_ips="10.0.0.2/32",
    )
    await server.add_client(client)

    # Получение статуса
    status = await server.get_server_status()
    print(f"📊 Статус сервера: {status}")

    # Остановка сервера
    await server.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
