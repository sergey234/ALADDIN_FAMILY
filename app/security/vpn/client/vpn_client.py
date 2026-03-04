"""
VPN клиент для системы семейной безопасности ALADDIN
Обеспечивает безопасное подключение к интернету через зарубежные серверы
"""

import logging as std_logging
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Статусы подключения"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class VPNProtocol(Enum):
    """Протоколы VPN"""
    WIREGUARD = "wireguard"
    OPENVPN = "openvpn"
    SHADOWSOCKS = "shadowsocks"
    V2RAY = "v2ray"


class VPNEnergyMode(Enum):
    """Режимы энергопотребления VPN"""
    FULL = "full"           # 100% - полная защита (AES-256)
    NORMAL = "normal"       # 60% - обычный режим (AES-128)
    ECO = "eco"             # 30% - экономный режим (ChaCha20)
    MINIMAL = "minimal"     # 10% - минимальный режим
    SLEEP = "sleep"         # 0% - сон (VPN отключен)


@dataclass
class VPNServer:
    """VPN сервер"""
    id: str
    name: str
    location: str
    country: str
    ip: str
    port: int
    protocol: VPNProtocol
    is_available: bool
    performance_score: float


@dataclass
class ConnectionInfo:
    """Информация о подключении"""
    server: VPNServer
    start_time: float
    bytes_sent: int
    bytes_received: int
    status: ConnectionStatus


class ALADDINVPNClient:
    """VPN клиент для ALADDIN"""

    def __init__(self):
        self.current_connection: Optional[ConnectionInfo] = None
        self.available_servers: List[VPNServer] = []
        self.connection_history: List[ConnectionInfo] = []
        self.is_running = False

        # Энергосбережение
        self.energy_mode = VPNEnergyMode.FULL
        self.battery_level = 100
        self.last_activity_time = time.time()
        self.idle_timeout = 900  # 15 минут по умолчанию
        self.auto_sleep_enabled = True
        self.last_connected_server: Optional[VPNServer] = None
        self.connection_suspended = False
        
        # Настройки энергосбережения
        self.energy_settings = {
            'auto_mode': True,
            'idle_timeout': 900,  # 15 минут
            'battery_threshold': 20,  # Минимальный уровень батареи
            'home_network_disable': True,
            'home_networks': []  # SSID домашних сетей
        }
        
        # Параметры текущего режима
        self.encryption_strength = 'aes-256-gcm'
        self.monitoring_interval = 60
        self.keep_alive_interval = 30

        # Загружаем конфигурацию
        self.config = self._load_config()

        # Инициализируем серверы
        self._init_servers()

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            with open('config/vpn_client_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем конфигурацию по умолчанию
            default_config = {
                "auto_connect": True,
                "preferred_protocol": "wireguard",
                "max_retries": 3,
                "timeout": 30,
                "encryption": "AES-256",
                "dns_servers": ["8.8.8.8", "1.1.1.1"],
                "kill_switch": True,
                "family_mode": True
            }
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: Dict[str, Any]):
        """Сохранение конфигурации"""
        try:
            with open('config/vpn_client_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    def _init_servers(self):
        """Инициализация серверов"""
        self.available_servers = [
            VPNServer(
                id="sg-singapore-1",
                name="Сингапур-1",
                location="Сингапур",
                country="SG",
                ip="192.168.2.10",
                port=443,
                protocol=VPNProtocol.SHADOWSOCKS,
                is_available=True,
                performance_score=95.0
            ),
            VPNServer(
                id="de-frankfurt-1",
                name="Франкфурт-1",
                location="Франкфурт",
                country="DE",
                ip="192.168.2.11",
                port=443,
                protocol=VPNProtocol.V2RAY,
                is_available=True,
                performance_score=92.0
            ),
            VPNServer(
                id="hk-hongkong-1",
                name="Гонконг-1",
                location="Гонконг",
                country="HK",
                ip="192.168.2.12",
                port=443,
                protocol=VPNProtocol.SHADOWSOCKS,
                is_available=True,
                performance_score=88.0
            ),
            VPNServer(
                id="jp-tokyo-1",
                name="Токио-1",
                location="Токио",
                country="JP",
                ip="192.168.2.13",
                port=51820,
                protocol=VPNProtocol.WIREGUARD,
                is_available=True,
                performance_score=90.0
            ),
            VPNServer(
                id="us-newyork-1",
                name="Нью-Йорк-1",
                location="Нью-Йорк",
                country="US",
                ip="192.168.2.14",
                port=1194,
                protocol=VPNProtocol.OPENVPN,
                is_available=True,
                performance_score=85.0
            ),
            VPNServer(
                id="ca-toronto-1",
                name="Торонто-1",
                location="Торонто",
                country="CA",
                ip="192.168.2.15",
                port=51820,
                protocol=VPNProtocol.WIREGUARD,
                is_available=True,
                performance_score=87.0
            )
        ]

    def get_available_servers(self) -> List[VPNServer]:
        """Получение доступных серверов"""
        return [server for server in self.available_servers if server.is_available]

    def select_best_server(self, preferred_country: Optional[str] = None) -> Optional[VPNServer]:
        """Выбор лучшего сервера"""
        try:
            available_servers = self.get_available_servers()

            if not available_servers:
                logger.warning("Нет доступных серверов")
                return None

            # Если указана предпочтительная страна
            if preferred_country:
                country_servers = [s for s in available_servers if s.country == preferred_country]
                if country_servers:
                    available_servers = country_servers

            # Выбираем сервер с лучшей производительностью
            best_server = max(available_servers, key=lambda s: s.performance_score)

            logger.info(f"Выбран сервер: {best_server.name} ({best_server.location})")
            return best_server

        except Exception as e:
            logger.error(f"Ошибка выбора сервера: {e}")
            return None

    async def connect(self, server: Optional[VPNServer] = None) -> bool:
        """Подключение к VPN серверу"""
        try:
            if not server:
                server = self.select_best_server()
                if not server:
                    return False

            logger.info(f"Подключение к серверу {server.name}...")

            # Создаем информацию о подключении
            self.current_connection = ConnectionInfo(
                server=server,
                start_time=time.time(),
                bytes_sent=0,
                bytes_received=0,
                status=ConnectionStatus.CONNECTING
            )

            # Симулируем подключение (в реальной реализации здесь будет подключение к серверу)
            await asyncio.sleep(2)

            # Проверяем успешность подключения
            if await self._test_connection(server):
                self.current_connection.status = ConnectionStatus.CONNECTED
                self.connection_history.append(self.current_connection)
                logger.info(f"Успешно подключен к {server.name}")
                return True
            else:
                self.current_connection.status = ConnectionStatus.ERROR
                logger.error(f"Ошибка подключения к {server.name}")
                return False

        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            if self.current_connection:
                self.current_connection.status = ConnectionStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Отключение от VPN"""
        try:
            if not self.current_connection:
                logger.warning("Нет активного подключения")
                return True

            logger.info(f"Отключение от {self.current_connection.server.name}...")

            # Симулируем отключение
            await asyncio.sleep(1)

            # Обновляем статистику
            if self.current_connection:
                self.current_connection.status = ConnectionStatus.DISCONNECTED

            self.current_connection = None
            logger.info("Отключение завершено")
            return True

        except Exception as e:
            logger.error(f"Ошибка отключения: {e}")
            return False

    async def _test_connection(self, server: VPNServer) -> bool:
        """Тестирование подключения"""
        try:
            # В реальной реализации здесь будет ping или HTTP запрос
            # Пока что симулируем успешное подключение
            await asyncio.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Ошибка тестирования подключения: {e}")
            return False

    def get_connection_status(self) -> Optional[ConnectionStatus]:
        """Получение статуса подключения"""
        if self.current_connection:
            return self.current_connection.status
        return ConnectionStatus.DISCONNECTED

    def get_connection_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации о подключении"""
        if not self.current_connection:
            return None

        connection_time = time.time() - self.current_connection.start_time

        return {
            "server": {
                "name": self.current_connection.server.name,
                "location": self.current_connection.server.location,
                "country": self.current_connection.server.country,
                "protocol": self.current_connection.server.protocol.value
            },
            "status": self.current_connection.status.value,
            "connection_time": round(connection_time, 2),
            "bytes_sent": self.current_connection.bytes_sent,
            "bytes_received": self.current_connection.bytes_received,
            "speed": self._calculate_speed()
        }

    def _calculate_speed(self) -> Dict[str, float]:
        """Расчет скорости подключения"""
        if not self.current_connection:
            return {"download": 0.0, "upload": 0.0}

        connection_time = time.time() - self.current_connection.start_time
        if connection_time == 0:
            return {"download": 0.0, "upload": 0.0}

        # Симулируем скорость (в реальной реализации будет реальный расчет)
        download_speed = (self.current_connection.bytes_received /
                          connection_time / 1024)  # KB/s
        upload_speed = (self.current_connection.bytes_sent /
                        connection_time / 1024)  # KB/s

        return {
            "download": round(download_speed, 2),
            "upload": round(upload_speed, 2)
        }

    def get_server_statistics(self) -> Dict[str, Any]:
        """Получение статистики серверов"""
        try:
            total_servers = len(self.available_servers)
            available_servers = len(self.get_available_servers())

            # Группировка по странам
            countries = {}
            for server in self.available_servers:
                if server.country not in countries:
                    countries[server.country] = 0
                countries[server.country] += 1

            # Группировка по протоколам
            protocols = {}
            for server in self.available_servers:
                if server.protocol.value not in protocols:
                    protocols[server.protocol.value] = 0
                protocols[server.protocol.value] += 1

            # Средняя производительность
            avg_performance = (sum(s.performance_score for s in self.available_servers) /
                               total_servers if total_servers > 0 else 0)

            return {
                "total_servers": total_servers,
                "available_servers": available_servers,
                "countries": countries,
                "protocols": protocols,
                "average_performance": avg_performance,
                "last_update": time.time()
            }

        except Exception as e:
            logger.error(f"Ошибка получения статистики серверов: {e}")
            return {}

    def update_config(self, new_config: Dict[str, Any]):
        """Обновление конфигурации"""
        try:
            self.config.update(new_config)
            self._save_config(self.config)
            logger.info("Конфигурация обновлена")
        except Exception as e:
            logger.error(f"Ошибка обновления конфигурации: {e}")

    # ==================== ЭНЕРГОСБЕРЕЖЕНИЕ ====================

    def _get_battery_level(self) -> int:
        """Получить уровень заряда батареи"""
        try:
            import platform
            
            # Desktop (для тестирования)
            if platform.system() in ['Darwin', 'Windows', 'Linux']:
                try:
                    import psutil
                    battery = psutil.sensors_battery()
                    if battery:
                        return int(battery.percent)
                except ImportError:
                    pass
            
            # По умолчанию возвращаем 100%
            return 100
            
        except Exception as e:
            logger.warning(f"Не удалось получить уровень батареи: {e}")
            return 100

    def _get_network_type(self) -> str:
        """Определить тип сети (home/public)"""
        try:
            # Для тестирования - всегда public
            # TODO: Реальная реализация для iOS/Android
            return 'public'
        except Exception as e:
            logger.warning(f"Не удалось определить тип сети: {e}")
            return 'public'

    def _calculate_target_mode(
        self, battery: int, idle_time: float, network: str
    ) -> VPNEnergyMode:
        """Вычислить целевой режим энергопотребления"""
        
        # Если авто-режим выключен - не меняем
        if not self.energy_settings['auto_mode']:
            return self.energy_mode
        
        # 1. КРИТИЧНЫЙ уровень батареи (<10%)
        if battery < 10:
            return VPNEnergyMode.SLEEP
        
        # 2. НИЗКИЙ уровень (<20%)
        if battery < self.energy_settings['battery_threshold']:
            return VPNEnergyMode.MINIMAL
        
        # 3. ДОЛГОЕ бездействие (30+ минут)
        if idle_time > 1800:  # 30 минут
            # В домашней сети можно отключить
            if network == 'home' and self.energy_settings['home_network_disable']:
                return VPNEnergyMode.SLEEP
            return VPNEnergyMode.ECO
        
        # 4. СРЕДНЕЕ бездействие (15+ минут)
        if idle_time > self.energy_settings['idle_timeout']:
            return VPNEnergyMode.ECO
        
        # 5. КОРОТКОЕ бездействие (5+ минут)
        if idle_time > 300:
            return VPNEnergyMode.NORMAL
        
        # 6. Активность - полный режим
        return VPNEnergyMode.FULL

    async def monitor_energy(self):
        """Мониторинг энергопотребления и управление режимами"""
        logger.info("⚡ VPN Energy Monitor: Запущен")
        
        while self.is_running:
            try:
                # 1. Получаем текущее состояние
                battery = self._get_battery_level()
                self.battery_level = battery
                idle_time = time.time() - self.last_activity_time
                network = self._get_network_type()
                
                # 2. Определяем нужный режим
                target_mode = self._calculate_target_mode(
                    battery, idle_time, network
                )
                
                # 3. Переключаем режим если нужно
                if target_mode != self.energy_mode:
                    await self._switch_energy_mode(target_mode)
                
                # 4. Логируем статистику
                logger.debug(
                    f"Energy: {self.energy_mode.value} | "
                    f"Battery: {battery}% | "
                    f"Idle: {idle_time:.0f}s"
                )
                
            except Exception as e:
                logger.error(f"Energy Monitor Error: {e}")
            
            # Проверяем каждые 60 секунд
            await asyncio.sleep(60)

    async def _switch_energy_mode(self, new_mode: VPNEnergyMode):
        """Переключение режима энергопотребления"""
        old_mode = self.energy_mode
        logger.info(f"⚡ VPN Energy: {old_mode.value} → {new_mode.value}")
        
        if new_mode == VPNEnergyMode.SLEEP:
            await self._enter_sleep_mode()
        elif new_mode == VPNEnergyMode.MINIMAL:
            await self._enter_minimal_mode()
        elif new_mode == VPNEnergyMode.ECO:
            await self._enter_eco_mode()
        elif new_mode == VPNEnergyMode.NORMAL:
            await self._enter_normal_mode()
        else:  # FULL
            await self._enter_full_mode()
        
        self.energy_mode = new_mode

    async def _enter_full_mode(self):
        """Полный режим (100% защита)"""
        self.encryption_strength = 'aes-256-gcm'
        self.monitoring_interval = 60  # каждую минуту
        self.keep_alive_interval = 30
        logger.info("🟢 VPN: Полный режим (AES-256)")

    async def _enter_normal_mode(self):
        """Обычный режим (60% ресурсов)"""
        self.encryption_strength = 'aes-128-gcm'
        self.monitoring_interval = 120  # каждые 2 минуты
        self.keep_alive_interval = 60
        logger.info("🟡 VPN: Обычный режим (AES-128)")

    async def _enter_eco_mode(self):
        """Экономный режим (30% ресурсов)"""
        self.encryption_strength = 'chacha20-poly1305'
        self.monitoring_interval = 300  # каждые 5 минут
        self.keep_alive_interval = 120
        logger.info("🟠 VPN: Экономный режим (ChaCha20)")

    async def _enter_minimal_mode(self):
        """Минимальный режим (10% ресурсов)"""
        self.encryption_strength = 'chacha20'
        self.monitoring_interval = 600  # каждые 10 минут
        self.keep_alive_interval = 300
        logger.info("🔴 VPN: Минимальный режим")

    async def _enter_sleep_mode(self):
        """Перевод в режим сна"""
        logger.info("💤 VPN → Режим сна: Отключение...")
        if self.current_connection:
            self.last_connected_server = self.current_connection.server
        await self.disconnect()
        self.connection_suspended = True

    async def _wake_up_from_sleep(self):
        """Быстрое пробуждение из режима сна"""
        logger.info("⚡ VPN: Пробуждение...")
        start_time = time.time()
        
        # Восстанавливаем соединение с последним сервером
        if self.last_connected_server:
            success = await self.connect(self.last_connected_server)
        else:
            best_server = self.select_best_server()
            success = await self.connect(best_server) if best_server else False
        
        wake_time = time.time() - start_time
        
        if success:
            logger.info(f"✅ VPN включен за {wake_time:.2f} сек")
            self.energy_mode = VPNEnergyMode.FULL
            self.connection_suspended = False
        else:
            logger.error("❌ Не удалось восстановить VPN")

    async def on_user_activity(self):
        """Вызывается при активности пользователя"""
        self.last_activity_time = time.time()
        
        # Если VPN спал - быстро пробуждаем
        if self.energy_mode == VPNEnergyMode.SLEEP:
            await self._wake_up_from_sleep()
        
        # Если был в ECO/MINIMAL - переводим в NORMAL
        elif self.energy_mode in [VPNEnergyMode.ECO, VPNEnergyMode.MINIMAL]:
            await self._switch_energy_mode(VPNEnergyMode.NORMAL)

    def get_energy_stats(self) -> dict:
        """Получить статистику энергопотребления"""
        idle_time = time.time() - self.last_activity_time
        
        return {
            'current_mode': self.energy_mode.value,
            'battery_level': self.battery_level,
            'idle_time': idle_time,
            'encryption': self.encryption_strength,
            'monitoring_interval': self.monitoring_interval,
            'connection_suspended': self.connection_suspended
        }

    def update_energy_settings(self, settings: dict):
        """Обновить настройки энергосбережения"""
        self.energy_settings.update(settings)
        logger.info(f"⚙️ Настройки энергосбережения обновлены: {settings}")


# Пример использования
async def main():
    """Основная функция для тестирования"""
    vpn_client = ALADDINVPNClient()

    print("=== VPN КЛИЕНТ ALADDIN ===")

    # Получаем статистику серверов
    stats = vpn_client.get_server_statistics()
    print(f"Доступных серверов: {stats['available_servers']}/{stats['total_servers']}")
    print(f"Средняя производительность: {stats['average_performance']:.1f}%")
    print(f"Страны: {stats['countries']}")
    print(f"Протоколы: {stats['protocols']}")

    # Выбираем лучший сервер
    best_server = vpn_client.select_best_server()
    if best_server:
        print(f"\nЛучший сервер: {best_server.name} ({best_server.location})")

        # Подключаемся
        if await vpn_client.connect(best_server):
            print("✅ Подключение успешно!")

            # Получаем информацию о подключении
            info = vpn_client.get_connection_info()
            if info:
                print(f"Сервер: {info['server']['name']}")
                print(f"Статус: {info['status']}")
                print(f"Время подключения: {info['connection_time']} сек")
                print(f"Скорость: {info['speed']['download']} KB/s ↓ / {info['speed']['upload']} KB/s ↑")

            # Отключаемся
            await asyncio.sleep(2)
            await vpn_client.disconnect()
            print("✅ Отключение завершено")
        else:
            print("❌ Ошибка подключения")

if __name__ == "__main__":
    asyncio.run(main())
