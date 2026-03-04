"""
Multi-hop подключения для ALADDIN VPN
Обеспечивает дополнительную безопасность через цепочку серверов
"""

import json
import logging as std_logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncio

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class HopType(Enum):
    """Типы хопов в цепочке"""

    ENTRY = "entry"  # Входной сервер
    MIDDLE = "middle"  # Промежуточный сервер
    EXIT = "exit"  # Выходной сервер


class HopStatus(Enum):
    """Статусы хопов"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class VPNHop:
    """VPN хоп в цепочке"""

    hop_id: str
    server_id: str
    country: str
    city: str
    hop_type: HopType
    ip_address: str
    port: int
    protocol: str
    encryption: str
    status: HopStatus
    latency: float
    load: float
    is_secure: bool
    supports_obfuscation: bool
    created_at: float


@dataclass
class MultiHopChain:
    """Цепочка multi-hop подключений"""

    chain_id: str
    name: str
    description: str
    hops: List[VPNHop]
    is_active: bool
    total_latency: float
    security_level: int  # 1-5
    created_at: float


class ALADDINMultiHop:
    """Multi-hop подключения для ALADDIN VPN"""

    def __init__(self):
        self.available_servers: Dict[str, VPNHop] = {}
        self.active_chains: Dict[str, MultiHopChain] = {}
        self.predefined_chains: Dict[str, MultiHopChain] = {}

        # Создаем доступные серверы
        self._create_available_servers()

        # Создаем предопределенные цепочки
        self._create_predefined_chains()

        logger.info("Multi-hop система инициализирована")

    def _create_available_servers(self):
        """Создание доступных серверов"""
        servers_data = [
            # Входные серверы (близко к пользователю)
            {
                "hop_id": "entry_moscow",
                "server_id": "moscow_1",
                "country": "Россия",
                "city": "Москва",
                "hop_type": HopType.ENTRY,
                "ip_address": "95.213.123.45",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 5.0,
                "load": 0.3,
                "supports_obfuscation": True,
            },
            {
                "hop_id": "entry_spb",
                "server_id": "spb_1",
                "country": "Россия",
                "city": "Санкт-Петербург",
                "hop_type": HopType.ENTRY,
                "ip_address": "95.213.124.67",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 8.0,
                "load": 0.2,
                "supports_obfuscation": True,
            },
            # Промежуточные серверы
            {
                "hop_id": "middle_finland",
                "server_id": "finland_1",
                "country": "Финляндия",
                "city": "Хельсинки",
                "hop_type": HopType.MIDDLE,
                "ip_address": "95.213.125.89",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 15.0,
                "load": 0.4,
                "supports_obfuscation": True,
            },
            {
                "hop_id": "middle_estonia",
                "server_id": "estonia_1",
                "country": "Эстония",
                "city": "Таллин",
                "hop_type": HopType.MIDDLE,
                "ip_address": "95.213.126.12",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 12.0,
                "load": 0.3,
                "supports_obfuscation": True,
            },
            # Выходные серверы
            {
                "hop_id": "exit_singapore",
                "server_id": "singapore_1",
                "country": "Сингапур",
                "city": "Сингапур",
                "hop_type": HopType.EXIT,
                "ip_address": "95.213.127.34",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 25.0,
                "load": 0.5,
                "supports_obfuscation": True,
            },
            {
                "hop_id": "exit_germany",
                "server_id": "germany_1",
                "country": "Германия",
                "city": "Франкфурт",
                "hop_type": HopType.EXIT,
                "ip_address": "95.213.128.56",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 35.0,
                "load": 0.6,
                "supports_obfuscation": True,
            },
            {
                "hop_id": "exit_netherlands",
                "server_id": "netherlands_1",
                "country": "Нидерланды",
                "city": "Амстердам",
                "hop_type": HopType.EXIT,
                "ip_address": "95.213.129.78",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 30.0,
                "load": 0.4,
                "supports_obfuscation": True,
            },
            {
                "hop_id": "exit_japan",
                "server_id": "japan_1",
                "country": "Япония",
                "city": "Токио",
                "hop_type": HopType.EXIT,
                "ip_address": "95.213.130.90",
                "port": 51820,
                "protocol": "wireguard",
                "encryption": "aes-256-gcm",
                "latency": 40.0,
                "load": 0.3,
                "supports_obfuscation": True,
            },
        ]

        for server_data in servers_data:
            hop = VPNHop(
                hop_id=server_data["hop_id"],
                server_id=server_data["server_id"],
                country=server_data["country"],
                city=server_data["city"],
                hop_type=server_data["hop_type"],
                ip_address=server_data["ip_address"],
                port=server_data["port"],
                protocol=server_data["protocol"],
                encryption=server_data["encryption"],
                status=HopStatus.DISCONNECTED,
                latency=server_data["latency"],
                load=server_data["load"],
                is_secure=True,
                supports_obfuscation=server_data["supports_obfuscation"],
                created_at=time.time(),
            )
            self.available_servers[hop.hop_id] = hop

    def _create_predefined_chains(self):
        """Создание предопределенных цепочек"""
        chains_data = [
            {
                "chain_id": "fast_chain",
                "name": "Быстрая цепочка",
                "description": "Оптимизирована для скорости",
                "hop_ids": ["entry_moscow", "exit_singapore"],
                "security_level": 2,
            },
            {
                "chain_id": "secure_chain",
                "name": "Безопасная цепочка",
                "description": "Максимальная безопасность",
                "hop_ids": ["entry_moscow", "middle_finland", "exit_germany"],
                "security_level": 4,
            },
            {
                "chain_id": "stealth_chain",
                "name": "Скрытная цепочка",
                "description": "Для обхода блокировок",
                "hop_ids": ["entry_spb", "middle_estonia", "exit_netherlands"],
                "security_level": 5,
            },
            {
                "chain_id": "gaming_chain",
                "name": "Игровая цепочка",
                "description": "Низкая задержка для игр",
                "hop_ids": ["entry_moscow", "exit_singapore"],
                "security_level": 1,
            },
            {
                "chain_id": "streaming_chain",
                "name": "Стриминговая цепочка",
                "description": "Для доступа к контенту",
                "hop_ids": ["entry_moscow", "middle_finland", "exit_japan"],
                "security_level": 3,
            },
        ]

        for chain_data in chains_data:
            hops = []
            total_latency = 0.0

            for hop_id in chain_data["hop_ids"]:
                if hop_id in self.available_servers:
                    hop = self.available_servers[hop_id]
                    hops.append(hop)
                    total_latency += hop.latency

            chain = MultiHopChain(
                chain_id=chain_data["chain_id"],
                name=chain_data["name"],
                description=chain_data["description"],
                hops=hops,
                is_active=False,
                total_latency=total_latency,
                security_level=chain_data["security_level"],
                created_at=time.time(),
            )

            self.predefined_chains[chain.chain_id] = chain

    async def create_custom_chain(
        self,
        name: str,
        description: str,
        hop_ids: List[str],
        security_level: int = 3,
    ) -> Optional[str]:
        """Создание пользовательской цепочки"""
        try:
            chain_id = f"custom_{int(time.time() * 1000)}"
            hops = []
            total_latency = 0.0

            # Проверяем доступность хопов
            for hop_id in hop_ids:
                if hop_id in self.available_servers:
                    hop = self.available_servers[hop_id]
                    hops.append(hop)
                    total_latency += hop.latency
                else:
                    logger.error(f"Хоп {hop_id} не найден")
                    return None

            if len(hops) < 2:
                logger.error("Цепочка должна содержать минимум 2 хопа")
                return None

            chain = MultiHopChain(
                chain_id=chain_id,
                name=name,
                description=description,
                hops=hops,
                is_active=False,
                total_latency=total_latency,
                security_level=min(5, max(1, security_level)),
                created_at=time.time(),
            )

            self.predefined_chains[chain_id] = chain
            logger.info(f"Пользовательская цепочка {name} создана")
            return chain_id

        except Exception as e:
            logger.error(f"Ошибка создания пользовательской цепочки: {e}")
            return None

    async def connect_chain(self, chain_id: str) -> bool:
        """Подключение к цепочке"""
        try:
            if chain_id not in self.predefined_chains:
                logger.error(f"Цепочка {chain_id} не найдена")
                return False

            chain = self.predefined_chains[chain_id]

            # Проверяем доступность всех хопов
            for hop in chain.hops:
                if not await self._check_hop_availability(hop):
                    logger.error(f"Хоп {hop.hop_id} недоступен")
                    return False

            # Подключаемся к хопам последовательно
            for i, hop in enumerate(chain.hops):
                logger.info(
                    f"Подключение к хопу {i+1}/{len(chain.hops)}: {hop.city}, {hop.country}"
                )

                hop.status = HopStatus.CONNECTING
                success = await self._connect_to_hop(hop)

                if success:
                    hop.status = HopStatus.CONNECTED
                    logger.info(f"✅ Подключен к {hop.city}")
                else:
                    hop.status = HopStatus.ERROR
                    logger.error(f"❌ Ошибка подключения к {hop.city}")

                    # Отключаемся от уже подключенных хопов
                    for j in range(i):
                        chain.hops[j].status = HopStatus.DISCONNECTED
                    return False

            chain.is_active = True
            self.active_chains[chain_id] = chain

            logger.info(f"✅ Цепочка {chain.name} подключена")
            return True

        except Exception as e:
            logger.error(f"Ошибка подключения к цепочке: {e}")
            return False

    async def disconnect_chain(self, chain_id: str) -> bool:
        """Отключение от цепочки"""
        try:
            if chain_id not in self.active_chains:
                logger.error(f"Активная цепочка {chain_id} не найдена")
                return False

            chain = self.active_chains[chain_id]

            # Отключаемся от хопов в обратном порядке
            for hop in reversed(chain.hops):
                if hop.status == HopStatus.CONNECTED:
                    logger.info(f"Отключение от {hop.city}")
                    await self._disconnect_from_hop(hop)
                    hop.status = HopStatus.DISCONNECTED

            chain.is_active = False
            del self.active_chains[chain_id]

            logger.info(f"✅ Цепочка {chain.name} отключена")
            return True

        except Exception as e:
            logger.error(f"Ошибка отключения от цепочки: {e}")
            return False

    async def _check_hop_availability(self, hop: VPNHop) -> bool:
        """Проверка доступности хопа"""
        try:
            # Имитация проверки доступности
            await asyncio.sleep(0.1)

            # Проверяем нагрузку и задержку
            if hop.load > 0.9:
                logger.warning(
                    f"Хоп {hop.hop_id} перегружен (load: {hop.load})"
                )
                return False

            if hop.latency > 200:
                logger.warning(
                    f"Хоп {hop.hop_id} имеет высокую задержку ({hop.latency}ms)"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Ошибка проверки доступности хопа: {e}")
            return False

    async def _connect_to_hop(self, hop: VPNHop) -> bool:
        """Подключение к хопу"""
        try:
            # Имитация подключения
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # Имитация случайных ошибок (5% вероятность)
            if random.random() < 0.05:
                logger.warning(f"Ошибка подключения к {hop.hop_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Ошибка подключения к хопу: {e}")
            return False

    async def _disconnect_from_hop(self, hop: VPNHop) -> bool:
        """Отключение от хопа"""
        try:
            # Имитация отключения
            await asyncio.sleep(0.2)
            return True

        except Exception as e:
            logger.error(f"Ошибка отключения от хопа: {e}")
            return False

    def get_available_chains(self) -> List[Dict[str, Any]]:
        """Получение доступных цепочек"""
        try:
            chains = []
            for chain in self.predefined_chains.values():
                chains.append(
                    {
                        "chain_id": chain.chain_id,
                        "name": chain.name,
                        "description": chain.description,
                        "hop_count": len(chain.hops),
                        "total_latency": chain.total_latency,
                        "security_level": chain.security_level,
                        "is_active": chain.is_active,
                        "hops": [
                            {
                                "hop_id": hop.hop_id,
                                "country": hop.country,
                                "city": hop.city,
                                "hop_type": hop.hop_type.value,
                                "latency": hop.latency,
                                "load": hop.load,
                            }
                            for hop in chain.hops
                        ],
                    }
                )

            return chains

        except Exception as e:
            logger.error(f"Ошибка получения доступных цепочек: {e}")
            return []

    def get_active_chains(self) -> List[Dict[str, Any]]:
        """Получение активных цепочек"""
        try:
            active_chains = []
            for chain_id, chain in self.active_chains.items():
                active_chains.append(
                    {
                        "chain_id": chain_id,
                        "name": chain.name,
                        "description": chain.description,
                        "hop_count": len(chain.hops),
                        "total_latency": chain.total_latency,
                        "security_level": chain.security_level,
                        "hops": [
                            {
                                "hop_id": hop.hop_id,
                                "country": hop.country,
                                "city": hop.city,
                                "hop_type": hop.hop_type.value,
                                "status": hop.status.value,
                                "latency": hop.latency,
                                "load": hop.load,
                            }
                            for hop in chain.hops
                        ],
                    }
                )

            return active_chains

        except Exception as e:
            logger.error(f"Ошибка получения активных цепочек: {e}")
            return []

    def get_chain_stats(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Получение статистики цепочки"""
        try:
            if chain_id in self.active_chains:
                chain = self.active_chains[chain_id]

                # Подсчитываем статистику
                connected_hops = sum(
                    1
                    for hop in chain.hops
                    if hop.status == HopStatus.CONNECTED
                )
                total_hops = len(chain.hops)

                return {
                    "chain_id": chain_id,
                    "name": chain.name,
                    "is_active": chain.is_active,
                    "connected_hops": connected_hops,
                    "total_hops": total_hops,
                    "connection_percentage": (
                        (connected_hops / total_hops * 100)
                        if total_hops > 0
                        else 0
                    ),
                    "total_latency": chain.total_latency,
                    "security_level": chain.security_level,
                    "hops_status": [
                        {
                            "hop_id": hop.hop_id,
                            "country": hop.country,
                            "city": hop.city,
                            "status": hop.status.value,
                            "latency": hop.latency,
                            "load": hop.load,
                        }
                        for hop in chain.hops
                    ],
                }
            else:
                logger.warning(f"Активная цепочка {chain_id} не найдена")
                return None

        except Exception as e:
            logger.error(f"Ошибка получения статистики цепочки: {e}")
            return None

    def optimize_chain(self, chain_id: str) -> bool:
        """Оптимизация цепочки"""
        try:
            if chain_id not in self.predefined_chains:
                logger.error(f"Цепочка {chain_id} не найдена")
                return False

            chain = self.predefined_chains[chain_id]

            # Сортируем хопы по задержке и нагрузке
            chain.hops.sort(key=lambda hop: (hop.latency, hop.load))

            # Пересчитываем общую задержку
            chain.total_latency = sum(hop.latency for hop in chain.hops)

            logger.info(f"Цепочка {chain.name} оптимизирована")
            return True

        except Exception as e:
            logger.error(f"Ошибка оптимизации цепочки: {e}")
            return False


# Пример использования
async def main():
    """Основная функция для тестирования"""
    multi_hop = ALADDINMultiHop()

    print("=== MULTI-HOP ПОДКЛЮЧЕНИЯ ALADDIN VPN ===")

    # Получаем доступные цепочки
    chains = multi_hop.get_available_chains()
    print(f"\n📋 Доступные цепочки ({len(chains)}):")
    for chain in chains:
        print(
            f"  {chain['name']}: {chain['hop_count']} хопов, "
            f"задержка {chain['total_latency']:.1f}мс, "
            f"безопасность {chain['security_level']}/5"
        )

    # Подключаемся к быстрой цепочке
    print("\n🔗 Подключение к быстрой цепочке...")
    if await multi_hop.connect_chain("fast_chain"):
        print("✅ Подключение успешно")

        # Получаем статистику
        stats = multi_hop.get_chain_stats("fast_chain")
        if stats:
            print("\n📊 Статистика цепочки:")
            print(f"  Название: {stats['name']}")
            print(
                f"  Подключено хопов: {stats['connected_hops']}/{stats['total_hops']}"
            )
            print(
                f"  Процент подключения: {stats['connection_percentage']:.1f}%"
            )
            print(f"  Общая задержка: {stats['total_latency']:.1f}мс")
            print(f"  Уровень безопасности: {stats['security_level']}/5")

            print("\n🌍 Хопы:")
            for hop in stats["hops_status"]:
                print(
                    f"  {hop['city']}, {hop['country']}: {hop['status']} "
                    f"({hop['latency']:.1f}мс, нагрузка {hop['load']:.1f})"
                )

        # Отключаемся
        print("\n🔌 Отключение...")
        if await multi_hop.disconnect_chain("fast_chain"):
            print("✅ Отключение успешно")

    # Создаем пользовательскую цепочку
    print("\n🛠️ Создание пользовательской цепочки...")
    custom_chain_id = await multi_hop.create_custom_chain(
        name="Моя цепочка",
        description="Пользовательская цепочка для тестирования",
        hop_ids=["entry_moscow", "middle_finland", "exit_germany"],
        security_level=4,
    )

    if custom_chain_id:
        print(f"✅ Пользовательская цепочка создана: {custom_chain_id}")

        # Подключаемся к пользовательской цепочке
        if await multi_hop.connect_chain(custom_chain_id):
            print("✅ Подключение к пользовательской цепочке успешно")

            # Отключаемся
            await multi_hop.disconnect_chain(custom_chain_id)
            print("✅ Отключение от пользовательской цепочки")


if __name__ == "__main__":
    asyncio.run(main())
