#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN Security System - Основная система VPN безопасности
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .core.vpn_core import VPNCore

logger = logging.getLogger(__name__)


class VPNSecurityLevel(Enum):
    """Уровни безопасности VPN"""

    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class VPNSecurityConfig:
    """Конфигурация безопасности VPN"""

    encryption: str = "AES-256-GCM"
    kill_switch: bool = True
    dns_protection: bool = True
    security_level: VPNSecurityLevel = VPNSecurityLevel.HIGH


class VPNSecuritySystem:
    """Основная система VPN безопасности"""

    def __init__(self, name: str = "VPNSecuritySystem"):
        self.name = name
        self.vpn_core: Optional[VPNCore] = None
        self.security_config = VPNSecurityConfig()

        # Статистика
        self.total_connections = 0
        self.successful_connections = 0
        self.failed_connections = 0
        self.uptime_start = datetime.now()

        # Инициализация
        self._initialize_components()

        logger.info(f"VPN Security System инициализирован: {name}")

    def _initialize_components(self):
        """Инициализация компонентов"""
        try:
            self.vpn_core = VPNCore("VPNSecurityCore")
            logger.info("VPN Core инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации компонентов: {e}")
            raise

    async def connect(
        self,
        user_id: str,
        country: Optional[str] = None,
        server_id: Optional[str] = None,
        security_level: Optional[VPNSecurityLevel] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Подключение к VPN"""
        try:
            start_time = time.time()

            # Установка уровня безопасности
            if security_level:
                self.security_config.security_level = security_level

            # Подключение через VPN Core
            if not self.vpn_core:
                return False, "VPN Core не инициализирован", {}

            success, message = await self.vpn_core.connect(
                user_id, server_id, country
            )

            # Обновление статистики
            self.total_connections += 1
            if success:
                self.successful_connections += 1
            else:
                self.failed_connections += 1

            connection_time = time.time() - start_time

            # Создание отчета о подключении
            connection_report = {
                "user_id": user_id,
                "success": success,
                "message": message,
                "provider": "internal",
                "connection_time": connection_time,
                "security_level": self.security_config.security_level.value,
                "timestamp": datetime.now().isoformat(),
                "server_country": country,
                "server_id": server_id,
            }

            if success:
                logger.info(f"Пользователь {user_id} успешно подключен")
            else:
                logger.warning(
                    f"Ошибка подключения пользователя {user_id}: {message}"
                )

            return success, message, connection_report

        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            self.failed_connections += 1
            return False, f"Ошибка подключения: {str(e)}", {}

    async def disconnect(self, user_id: str) -> Tuple[bool, str]:
        """Отключение от VPN"""
        try:
            if not self.vpn_core:
                return False, "VPN Core не инициализирован"

            success, message = await self.vpn_core.disconnect(user_id)

            if success:
                logger.info(f"Пользователь {user_id} отключен от VPN")
            else:
                logger.warning(
                    f"Ошибка отключения пользователя {user_id}: {message}"
                )

            return success, message

        except Exception as e:
            logger.error(f"Ошибка отключения: {e}")
            return False, f"Ошибка отключения: {str(e)}"

    def get_connection_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса подключения"""
        if not self.vpn_core:
            return None

        connection = self.vpn_core.get_connection_status(user_id)
        if not connection:
            return None

        return {
            "user_id": user_id,
            "status": connection.status.value,
            "server_id": connection.server_id,
            "start_time": connection.start_time.isoformat(),
            "bytes_sent": connection.bytes_sent,
            "bytes_received": connection.bytes_received,
        }

    def get_available_servers(
        self, country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получение доступных серверов"""
        servers = []

        if self.vpn_core:
            internal_servers = self.vpn_core.get_available_servers(country)
            for server in internal_servers:
                servers.append(
                    {
                        "id": server.id,
                        "name": server.name,
                        "country": server.country,
                        "city": server.city,
                        "protocol": server.protocol.value,
                        "latency": server.latency,
                        "load": server.load,
                        "type": "internal",
                    }
                )

        return servers

    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        uptime = int((datetime.now() - self.uptime_start).total_seconds())

        return {
            "uptime": uptime,
            "total_connections": self.total_connections,
            "successful_connections": self.successful_connections,
            "failed_connections": self.failed_connections,
            "success_rate": (
                self.successful_connections / max(self.total_connections, 1)
            )
            * 100,
            "security_level": self.security_config.security_level.value,
        }

    def set_security_level(self, level: VPNSecurityLevel) -> bool:
        """Установка уровня безопасности"""
        try:
            self.security_config.security_level = level
            logger.info(f"Уровень безопасности изменен: {level.value}")
            return True
        except Exception as e:
            logger.error(f"Ошибка установки уровня безопасности: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса компонента"""
        if not self.vpn_core:
            return {
                "status": "error",
                "message": "VPN Core не инициализирован",
            }

        return {
            "status": "healthy",
            "message": "VPN Security System работает нормально",
            "security_level": self.security_config.security_level.value,
            "stats": self.get_system_stats(),
        }


if __name__ == "__main__":
    # Тестирование
    vpn_system = VPNSecuritySystem("TestVPNSecuritySystem")
    print("VPN Security System создан успешно!")
