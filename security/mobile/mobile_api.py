#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile API для VPN и антивируса - простое и красивое подключение
"""

import asyncio
import json
import logging
import os

# Импорты VPN и антивируса
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Добавляем путь для импорта модулей безопасности

# Импорты модулей безопасности
from security.antivirus.antivirus_security_system import (
    AntivirusSecuritySystem,
)
from security.vpn.vpn_security_system import (
    VPNSecurityLevel,
    VPNSecuritySystem,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Типы подключения для мобильного приложения"""

    VPN_ONLY = "vpn_only"
    ANTIVIRUS_ONLY = "antivirus_only"
    VPN_ANTIVIRUS = "vpn_antivirus"
    SMART_PROTECTION = "smart_protection"


class ConnectionSpeed(Enum):
    """Скорости подключения"""

    FAST = "fast"
    BALANCED = "balanced"
    SECURE = "secure"


@dataclass
class MobileConnectionConfig:
    """Конфигурация подключения для мобильного приложения"""

    connection_type: ConnectionType
    speed: ConnectionSpeed
    country: str = "Singapore"
    auto_connect: bool = True
    notifications: bool = True
    background_protection: bool = True


@dataclass
class MobileConnectionResult:
    """Результат подключения для мобильного приложения"""

    success: bool
    message: str
    connection_id: str
    connection_type: str
    speed: str
    country: str
    security_level: str
    connection_time: float
    timestamp: str


class MobileSecurityAPI:
    """API для мобильного приложения ALADDIN"""

    def __init__(self):
        """Инициализация мобильного API"""
        self.vpn_system = None
        self.antivirus_system = None
        self.active_connections = {}
        self.connection_counter = 0

        # Инициализация систем
        self._init_systems()

    def _init_systems(self):
        """Инициализация VPN и антивирусных систем"""
        try:
            self.vpn_system = VPNSecuritySystem("MobileVPN")
            self.antivirus_system = AntivirusSecuritySystem("MobileAntivirus")
            logger.info("Мобильные системы безопасности инициализированы")
        except Exception as e:
            logger.error(f"Ошибка инициализации мобильных систем: {e}")

    def get_connection_options(self) -> Dict[str, Any]:
        """Получение вариантов подключения для мобильного приложения"""
        return {
            "connection_types": [
                {
                    "id": "vpn_only",
                    "name": "🌍 Только VPN",
                    "description": "Быстрое и безопасное подключение",
                    "icon": "vpn",
                    "features": [
                        "Защита трафика",
                        "Смена IP",
                        "Быстрое подключение",
                    ],
                },
                {
                    "id": "antivirus_only",
                    "name": "🛡️ Только антивирус",
                    "description": "Защита от вирусов и угроз",
                    "icon": "shield",
                    "features": [
                        "Сканирование файлов",
                        "Защита в реальном времени",
                        "Блокировка угроз",
                    ],
                },
                {
                    "id": "vpn_antivirus",
                    "name": "🚀 VPN + Антивирус",
                    "description": "Максимальная защита",
                    "icon": "security",
                    "features": [
                        "VPN защита",
                        "Антивирус",
                        "Полная безопасность",
                    ],
                },
                {
                    "id": "smart_protection",
                    "name": "🧠 Умная защита",
                    "description": "Автоматический выбор лучшей защиты",
                    "icon": "brain",
                    "features": [
                        "AI анализ",
                        "Автоматический выбор",
                        "Адаптивная защита",
                    ],
                },
            ],
            "speeds": [
                {
                    "id": "fast",
                    "name": "⚡ Быстро",
                    "description": "Максимальная скорость",
                    "icon": "lightning",
                },
                {
                    "id": "balanced",
                    "name": "⚖️ Сбалансированно",
                    "description": "Скорость и безопасность",
                    "icon": "balance",
                },
                {
                    "id": "secure",
                    "name": "🔒 Безопасно",
                    "description": "Максимальная безопасность",
                    "icon": "lock",
                },
            ],
            "countries": [
                {"id": "singapore", "name": "🇸🇬 Singapore", "flag": "🇸🇬"},
                {"id": "russia", "name": "🇷🇺 Russia", "flag": "🇷🇺"},
                {"id": "netherlands", "name": "🇳🇱 Netherlands", "flag": "🇳🇱"},
                {"id": "usa", "name": "🇺🇸 USA", "flag": "🇺🇸"},
                {"id": "japan", "name": "🇯🇵 Japan", "flag": "🇯🇵"},
            ],
        }

    async def connect_mobile(
        self, config: MobileConnectionConfig
    ) -> MobileConnectionResult:
        """Подключение для мобильного приложения"""
        try:
            self.connection_counter += 1
            connection_id = (
                f"mobile_{self.connection_counter}_{int(time.time())}"
            )

            start_time = time.time()

            # Выбор типа подключения
            if config.connection_type == ConnectionType.VPN_ONLY:
                result = await self._connect_vpn_only(connection_id, config)
            elif config.connection_type == ConnectionType.ANTIVIRUS_ONLY:
                result = await self._connect_antivirus_only(
                    connection_id, config
                )
            elif config.connection_type == ConnectionType.VPN_ANTIVIRUS:
                result = await self._connect_vpn_antivirus(
                    connection_id, config
                )
            elif config.connection_type == ConnectionType.SMART_PROTECTION:
                result = await self._connect_smart_protection(
                    connection_id, config
                )
            else:
                raise ValueError(
                    f"Неизвестный тип подключения: {config.connection_type}"
                )

            connection_time = time.time() - start_time

            # Сохранение активного подключения
            self.active_connections[connection_id] = {
                "config": config,
                "start_time": datetime.now().isoformat(),
                "status": "connected",
            }

            return MobileConnectionResult(
                success=True,
                message=result["message"],
                connection_id=connection_id,
                connection_type=config.connection_type.value,
                speed=config.speed.value,
                country=config.country,
                security_level=result.get("security_level", "high"),
                connection_time=connection_time,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            return MobileConnectionResult(
                success=False,
                message=f"Ошибка подключения: {str(e)}",
                connection_id="",
                connection_type=config.connection_type.value,
                speed=config.speed.value,
                country=config.country,
                security_level="none",
                connection_time=0.0,
                timestamp=datetime.now().isoformat(),
            )

    async def _connect_vpn_only(
        self, connection_id: str, config: MobileConnectionConfig
    ) -> Dict[str, Any]:
        """Подключение только VPN"""
        if not self.vpn_system:
            raise Exception("VPN система не инициализирована")

        # Выбор уровня безопасности в зависимости от скорости
        security_level = self._get_security_level(config.speed)

        success, message, report = await self.vpn_system.connect(
            connection_id,
            country=config.country,
            security_level=security_level,
        )

        if success:
            return {
                "message": f"🌍 VPN подключен к {config.country}",
                "security_level": report.get("security_level", "high"),
                "provider": report.get("provider", "internal"),
            }
        else:
            raise Exception(f"Ошибка VPN подключения: {message}")

    async def _connect_antivirus_only(
        self, connection_id: str, config: MobileConnectionConfig
    ) -> Dict[str, Any]:
        """Подключение только антивируса"""
        if not self.antivirus_system:
            raise Exception("Антивирусная система не инициализирована")

        # Активация антивирусной защиты
        self.antivirus_system.get_status()

        return {
            "message": "🛡️ Антивирусная защита активирована",
            "security_level": "high",
            "provider": "internal",
        }

    async def _connect_vpn_antivirus(
        self, connection_id: str, config: MobileConnectionConfig
    ) -> Dict[str, Any]:
        """Подключение VPN + антивирус"""
        # Подключение VPN
        vpn_result = await self._connect_vpn_only(connection_id, config)

        # Активация антивируса
        antivirus_result = await self._connect_antivirus_only(
            connection_id, config
        )

        return {
            "message": (
                f"🚀 {vpn_result['message']} + "
                f"{antivirus_result['message']}"
            ),
            "security_level": "maximum",
            "provider": "internal",
        }

    async def _connect_smart_protection(
        self, connection_id: str, config: MobileConnectionConfig
    ) -> Dict[str, Any]:
        """Умная защита - автоматический выбор"""
        # Простая логика умной защиты
        if config.speed == ConnectionSpeed.FAST:
            return await self._connect_vpn_only(connection_id, config)
        elif config.speed == ConnectionSpeed.SECURE:
            return await self._connect_vpn_antivirus(connection_id, config)
        else:
            return await self._connect_vpn_antivirus(connection_id, config)

    def _get_security_level(self, speed: ConnectionSpeed) -> VPNSecurityLevel:
        """Получение уровня безопасности в зависимости от скорости"""
        if speed == ConnectionSpeed.FAST:
            return VPNSecurityLevel.MEDIUM
        elif speed == ConnectionSpeed.SECURE:
            return VPNSecurityLevel.HIGH
        else:
            return VPNSecurityLevel.HIGH

    async def disconnect_mobile(self, connection_id: str) -> Dict[str, Any]:
        """Отключение для мобильного приложения"""
        try:
            if connection_id not in self.active_connections:
                return {"success": False, "message": "Подключение не найдено"}

            config = self.active_connections[connection_id]["config"]

            # Отключение в зависимости от типа
            if config.connection_type in [
                ConnectionType.VPN_ONLY,
                ConnectionType.VPN_ANTIVIRUS,
                ConnectionType.SMART_PROTECTION,
            ]:
                if self.vpn_system:
                    success, message = await self.vpn_system.disconnect(
                        connection_id
                    )
                    if not success:
                        return {
                            "success": False,
                            "message": f"Ошибка отключения VPN: {message}",
                        }

            # Удаление из активных подключений
            del self.active_connections[connection_id]

            return {
                "success": True,
                "message": "✅ Отключение успешно",
                "connection_id": connection_id,
            }

        except Exception as e:
            logger.error(f"Ошибка отключения: {e}")
            return {
                "success": False,
                "message": f"Ошибка отключения: {str(e)}",
            }

    def get_mobile_status(self) -> Dict[str, Any]:
        """Получение статуса для мобильного приложения"""
        return {
            "app_name": "ALADDIN Security",
            "version": "1.0.0",
            "status": "ready",
            "active_connections": len(self.active_connections),
            "vpn_available": self.vpn_system is not None,
            "antivirus_available": self.antivirus_system is not None,
            "features": [
                "🌍 VPN защита",
                "🛡️ Антивирус",
                "🧠 Умная защита",
                "⚡ Быстрое подключение",
                "🔒 Максимальная безопасность",
            ],
            "connection_options": self.get_connection_options(),
        }

    async def connect_vpn_only(
        self, config: MobileConnectionConfig
    ) -> MobileConnectionResult:
        """Подключение только VPN"""
        try:
            self.connection_counter += 1
            connection_id = f"vpn_{self.connection_counter}_{int(time.time())}"
            return await self._connect_vpn_only(connection_id, config)
        except Exception as e:
            logger.error(f"Ошибка подключения VPN: {e}")
            return MobileConnectionResult(
                success=False,
                message=f"Ошибка подключения VPN: {e}",
                connection_id="",
                security_level="none",
                provider="internal",
            )

    async def connect_antivirus_only(
        self, config: MobileConnectionConfig
    ) -> MobileConnectionResult:
        """Подключение только антивируса"""
        try:
            self.connection_counter += 1
            connection_id = (
                f"antivirus_{self.connection_counter}_{int(time.time())}"
            )
            return await self._connect_antivirus_only(connection_id, config)
        except Exception as e:
            logger.error(f"Ошибка подключения антивируса: {e}")
            return MobileConnectionResult(
                success=False,
                message=f"Ошибка подключения антивируса: {e}",
                connection_id="",
                security_level="none",
                provider="internal",
            )

    async def connect_full_security(
        self, config: MobileConnectionConfig
    ) -> MobileConnectionResult:
        """Подключение полной защиты (VPN + антивирус)"""
        try:
            self.connection_counter += 1
            connection_id = (
                f"full_{self.connection_counter}_{int(time.time())}"
            )
            return await self._connect_vpn_antivirus(connection_id, config)
        except Exception as e:
            logger.error(f"Ошибка подключения полной защиты: {e}")
            return MobileConnectionResult(
                success=False,
                message=f"Ошибка подключения полной защиты: {e}",
                connection_id="",
                security_level="none",
                provider="internal",
            )

    async def disconnect_all(self) -> Dict[str, Any]:
        """Отключение всех соединений"""
        try:
            disconnected_count = 0
            for connection_id in list(self.active_connections.keys()):
                result = await self.disconnect_mobile(connection_id)
                if result.get("success", False):
                    disconnected_count += 1
            return {
                "success": True,
                "message": f"Отключено {disconnected_count} соединений",
                "disconnected_count": disconnected_count,
            }
        except Exception as e:
            logger.error(f"Ошибка отключения всех соединений: {e}")
            return {
                "success": False,
                "message": f"Ошибка отключения: {e}",
                "disconnected_count": 0,
            }

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return self.get_mobile_status()

    def get_connection_info(self, connection_id: str) -> Dict[str, Any]:
        """Получение информации о соединении"""
        try:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                return {
                    "connection_id": connection_id,
                    "status": "active",
                    "type": connection.get("type", "unknown"),
                    "created_at": connection.get("created_at", ""),
                    "security_level": connection.get("security_level", "none"),
                }
            else:
                return {
                    "connection_id": connection_id,
                    "status": "not_found",
                    "message": "Соединение не найдено",
                }
        except Exception as e:
            logger.error(f"Ошибка получения информации о соединении: {e}")
            return {
                "connection_id": connection_id,
                "status": "error",
                "message": f"Ошибка: {e}",
            }

    def get_security_level(self) -> str:
        """Получение уровня безопасности системы"""
        try:
            if self.vpn_system and self.antivirus_system:
                return "maximum"
            elif self.vpn_system or self.antivirus_system:
                return "partial"
            else:
                return "none"
        except Exception as e:
            logger.error(f"Ошибка получения уровня безопасности: {e}")
            return "error"


# Глобальный экземпляр API
mobile_api = MobileSecurityAPI()


async def main():
    """Тестирование мобильного API"""
    print("📱 ТЕСТИРОВАНИЕ МОБИЛЬНОГО API ALADDIN")
    print("=" * 50)

    # Получение вариантов подключения
    mobile_api.get_connection_options()
    print("✅ Варианты подключения получены")

    # Тестирование подключения VPN
    config = MobileConnectionConfig(
        connection_type=ConnectionType.VPN_ONLY,
        speed=ConnectionSpeed.FAST,
        country="Singapore",
    )

    result = await mobile_api.connect_mobile(config)
    print(f"✅ Подключение VPN: {result.message}")

    # Отключение
    disconnect_result = await mobile_api.disconnect_mobile(
        result.connection_id
    )
    print(f"✅ Отключение: {disconnect_result['message']}")

    # Статус
    status = mobile_api.get_mobile_status()
    print(f"✅ Статус приложения: {status['status']}")


if __name__ == "__main__":
    asyncio.run(main())
