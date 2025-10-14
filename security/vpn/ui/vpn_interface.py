"""
VPN интерфейс для ALADDIN
Простой и интуитивный интерфейс для управления VPN подключением
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

class VPNStatus(Enum):
    """Статусы VPN"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"

@dataclass
class ServerInfo:
    """Информация о сервере"""
    id: str
    name: str
    country: str
    flag: str
    ping: int
    load: int
    is_available: bool

class ALADDINVPNInterface:
    """VPN интерфейс для ALADDIN"""
    
    def __init__(self):
        self.status = VPNStatus.DISCONNECTED
        self.current_server: Optional[ServerInfo] = None
        self.connection_start_time: Optional[float] = None
        self.bytes_sent = 0
        self.bytes_received = 0
        
        # Список доступных серверов
        self.servers = [
            ServerInfo("sg-1", "Сингапур", "SG", "🇸🇬", 25, 15, True),
            ServerInfo("de-1", "Германия", "DE", "🇩🇪", 45, 25, True),
            ServerInfo("hk-1", "Гонконг", "HK", "🇭🇰", 35, 20, True),
            ServerInfo("jp-1", "Япония", "JP", "🇯🇵", 40, 30, True),
            ServerInfo("us-1", "США", "US", "🇺🇸", 80, 40, True),
            ServerInfo("ca-1", "Канада", "CA", "🇨🇦", 75, 35, True)
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Получение текущего статуса"""
        connection_time = 0
        if self.connection_start_time:
            connection_time = time.time() - self.connection_start_time
        
        return {
            "status": self.status.value,
            "current_server": {
                "id": self.current_server.id if self.current_server else None,
                "name": self.current_server.name if self.current_server else None,
                "country": self.current_server.country if self.current_server else None,
                "flag": self.current_server.flag if self.current_server else None
            },
            "connection_time": round(connection_time, 2),
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "speed": self._calculate_speed()
        }
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """Получение списка серверов"""
        return [
            {
                "id": server.id,
                "name": server.name,
                "country": server.country,
                "flag": server.flag,
                "ping": server.ping,
                "load": server.load,
                "is_available": server.is_available
            }
            for server in self.servers
        ]
    
    def select_server(self, server_id: str) -> bool:
        """Выбор сервера"""
        try:
            server = next((s for s in self.servers if s.id == server_id), None)
            if not server:
                logger.error(f"Сервер {server_id} не найден")
                return False
            
            if not server.is_available:
                logger.error(f"Сервер {server_id} недоступен")
                return False
            
            self.current_server = server
            logger.info(f"Выбран сервер: {server.name} ({server.country})")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выбора сервера: {e}")
            return False
    
    async def connect(self) -> bool:
        """Подключение к VPN"""
        try:
            if self.status != VPNStatus.DISCONNECTED:
                logger.warning("VPN уже подключен или подключается")
                return False
            
            if not self.current_server:
                # Выбираем лучший сервер автоматически
                best_server = self._select_best_server()
                if not best_server:
                    logger.error("Нет доступных серверов")
                    return False
                self.current_server = best_server
            
            logger.info(f"Подключение к {self.current_server.name}...")
            self.status = VPNStatus.CONNECTING
            
            # Симулируем подключение
            await asyncio.sleep(2)
            
            # Проверяем успешность подключения
            if await self._test_connection():
                self.status = VPNStatus.CONNECTED
                self.connection_start_time = time.time()
                logger.info(f"Подключение к {self.current_server.name} успешно")
                return True
            else:
                self.status = VPNStatus.ERROR
                logger.error(f"Ошибка подключения к {self.current_server.name}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            self.status = VPNStatus.ERROR
            return False
    
    async def disconnect(self) -> bool:
        """Отключение от VPN"""
        try:
            if self.status == VPNStatus.DISCONNECTED:
                logger.warning("VPN не подключен")
                return True
            
            logger.info("Отключение от VPN...")
            self.status = VPNStatus.DISCONNECTING
            
            # Симулируем отключение
            await asyncio.sleep(1)
            
            self.status = VPNStatus.DISCONNECTED
            self.current_server = None
            self.connection_start_time = None
            logger.info("Отключение от VPN завершено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отключения: {e}")
            return False
    
    def _select_best_server(self) -> Optional[ServerInfo]:
        """Автоматический выбор лучшего сервера"""
        available_servers = [s for s in self.servers if s.is_available]
        if not available_servers:
            return None
        
        # Выбираем сервер с наименьшим пингом и нагрузкой
        best_server = min(available_servers, key=lambda s: s.ping + s.load)
        return best_server
    
    async def _test_connection(self) -> bool:
        """Тестирование подключения"""
        try:
            # В реальной реализации здесь будет ping или HTTP запрос
            await asyncio.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Ошибка тестирования подключения: {e}")
            return False
    
    def _calculate_speed(self) -> Dict[str, float]:
        """Расчет скорости подключения"""
        if not self.connection_start_time:
            return {"download": 0.0, "upload": 0.0}
        
        connection_time = time.time() - self.connection_start_time
        if connection_time == 0:
            return {"download": 0.0, "upload": 0.0}
        
        # Симулируем скорость
        download_speed = self.bytes_received / connection_time / 1024  # KB/s
        upload_speed = self.bytes_sent / connection_time / 1024  # KB/s
        
        return {
            "download": round(download_speed, 2),
            "upload": round(upload_speed, 2)
        }
    
    def update_traffic(self, bytes_sent: int, bytes_received: int):
        """Обновление статистики трафика"""
        self.bytes_sent += bytes_sent
        self.bytes_received += bytes_received
    
    def get_quick_connect_servers(self) -> List[Dict[str, Any]]:
        """Получение серверов для быстрого подключения"""
        return [
            {
                "id": server.id,
                "name": server.name,
                "country": server.country,
                "flag": server.flag,
                "ping": server.ping
            }
            for server in sorted(self.servers, key=lambda s: s.ping)[:4]
        ]
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Получение сводки подключения"""
        status = self.get_status()
        
        return {
            "is_connected": self.status == VPNStatus.CONNECTED,
            "status_text": self._get_status_text(),
            "server_info": status["current_server"],
            "connection_time": status["connection_time"],
            "speed": status["speed"],
            "data_usage": {
                "sent": self.bytes_sent,
                "received": self.bytes_received,
                "total": self.bytes_sent + self.bytes_received
            }
        }
    
    def _get_status_text(self) -> str:
        """Получение текстового описания статуса"""
        status_texts = {
            VPNStatus.DISCONNECTED: "Отключен",
            VPNStatus.CONNECTING: "Подключение...",
            VPNStatus.CONNECTED: "Подключен",
            VPNStatus.DISCONNECTING: "Отключение...",
            VPNStatus.ERROR: "Ошибка"
        }
        return status_texts.get(self.status, "Неизвестно")

# Пример использования
async def main():
    """Основная функция для тестирования"""
    vpn_ui = ALADDINVPNInterface()
    
    print("=== VPN ИНТЕРФЕЙС ALADDIN ===")
    
    # Получаем список серверов
    servers = vpn_ui.get_servers()
    print(f"Доступных серверов: {len(servers)}")
    for server in servers:
        print(f"  {server['flag']} {server['name']} - {server['ping']}ms (нагрузка: {server['load']}%)")
    
    # Получаем серверы для быстрого подключения
    quick_servers = vpn_ui.get_quick_connect_servers()
    print(f"\nБыстрые подключения: {[s['name'] for s in quick_servers]}")
    
    # Выбираем сервер
    if vpn_ui.select_server("sg-1"):
        print("✅ Сервер выбран")
        
        # Подключаемся
        if await vpn_ui.connect():
            print("✅ VPN подключение успешно")
            
            # Получаем сводку подключения
            summary = vpn_ui.get_connection_summary()
            print(f"Статус: {summary['status_text']}")
            print(f"Сервер: {summary['server_info']['name']} {summary['server_info']['flag']}")
            print(f"Время подключения: {summary['connection_time']} сек")
            print(f"Скорость: {summary['speed']['download']} KB/s ↓ / {summary['speed']['upload']} KB/s ↑")
            
            # Отключаемся
            await asyncio.sleep(2)
            await vpn_ui.disconnect()
            print("✅ VPN отключение завершено")
        else:
            print("❌ Ошибка подключения VPN")
    else:
        print("❌ Ошибка выбора сервера")

if __name__ == "__main__":
    asyncio.run(main())