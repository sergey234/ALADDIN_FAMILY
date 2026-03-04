"""
Кэширование соединений для ALADDIN VPN
Оптимизирует производительность за счет кэширования активных соединений
"""

import logging as std_logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import asyncio

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class ConnectionState(Enum):
    """Состояния соединения"""

    IDLE = "idle"
    ACTIVE = "active"
    CONNECTING = "connecting"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


@dataclass
class CachedConnection:
    """Кэшированное соединение"""

    connection_id: str
    server_id: str
    state: ConnectionState
    created_at: float
    last_used: float
    usage_count: int
    connection_data: Dict[str, Any]
    is_reusable: bool = True


class ALADDINConnectionCache:
    """Кэш соединений для ALADDIN VPN"""

    def __init__(self, max_connections: int = 10, ttl: int = 300):
        self.max_connections = max_connections
        self.ttl = ttl  # Time to live в секундах
        self.cache: OrderedDict[str, CachedConnection] = OrderedDict()
        self.lock = threading.RLock()
        self.cleanup_interval = 60  # Очистка каждые 60 секунд
        self._cleanup_task = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Запуск задачи очистки кэша"""

        def cleanup_loop():
            while True:
                time.sleep(self.cleanup_interval)
                self.cleanup_expired_connections()

        self._cleanup_task = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_task.start()
        logger.info("Задача очистки кэша запущена")

    def get_connection(self, server_id: str) -> Optional[CachedConnection]:
        """Получение соединения из кэша"""
        try:
            with self.lock:
                # Ищем подходящее соединение
                for conn_id, connection in self.cache.items():
                    if (
                        connection.server_id == server_id
                        and connection.state == ConnectionState.IDLE
                        and connection.is_reusable
                        and self._is_connection_valid(connection)
                    ):

                        # Обновляем статистику использования
                        connection.last_used = time.time()
                        connection.usage_count += 1
                        connection.state = ConnectionState.ACTIVE

                        # Перемещаем в конец (LRU)
                        self.cache.move_to_end(conn_id)

                        logger.info(
                            f"Найдено кэшированное соединение для сервера {server_id}"
                        )
                        return connection

                logger.info(
                    f"Кэшированное соединение для сервера {server_id} не найдено"
                )
                return None

        except Exception as e:
            logger.error(f"Ошибка получения соединения из кэша: {e}")
            return None

    def cache_connection(
        self,
        connection_id: str,
        server_id: str,
        connection_data: Dict[str, Any],
    ) -> bool:
        """Кэширование соединения"""
        try:
            with self.lock:
                # Удаляем старые соединения если достигнут лимит
                if len(self.cache) >= self.max_connections:
                    self._evict_oldest_connection()

                # Создаем новое кэшированное соединение
                cached_conn = CachedConnection(
                    connection_id=connection_id,
                    server_id=server_id,
                    state=ConnectionState.IDLE,
                    created_at=time.time(),
                    last_used=time.time(),
                    usage_count=0,
                    connection_data=connection_data,
                    is_reusable=True,
                )

                # Добавляем в кэш
                self.cache[connection_id] = cached_conn

                logger.info(
                    f"Соединение {connection_id} для сервера {server_id} закэшировано"
                )
                return True

        except Exception as e:
            logger.error(f"Ошибка кэширования соединения: {e}")
            return False

    def update_connection_state(
        self, connection_id: str, state: ConnectionState
    ) -> bool:
        """Обновление состояния соединения"""
        try:
            with self.lock:
                if connection_id in self.cache:
                    self.cache[connection_id].state = state
                    self.cache[connection_id].last_used = time.time()

                    logger.info(
                        f"Состояние соединения {connection_id} обновлено на {state.value}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Соединение {connection_id} не найдено в кэше"
                    )
                    return False

        except Exception as e:
            logger.error(f"Ошибка обновления состояния соединения: {e}")
            return False

    def remove_connection(self, connection_id: str) -> bool:
        """Удаление соединения из кэша"""
        try:
            with self.lock:
                if connection_id in self.cache:
                    del self.cache[connection_id]
                    logger.info(f"Соединение {connection_id} удалено из кэша")
                    return True
                else:
                    logger.warning(
                        f"Соединение {connection_id} не найдено в кэше"
                    )
                    return False

        except Exception as e:
            logger.error(f"Ошибка удаления соединения из кэша: {e}")
            return False

    def cleanup_expired_connections(self) -> int:
        """Очистка просроченных соединений"""
        try:
            with self.lock:
                current_time = time.time()
                expired_connections = []

                for conn_id, connection in self.cache.items():
                    if (current_time - connection.last_used) > self.ttl:
                        expired_connections.append(conn_id)

                # Удаляем просроченные соединения
                for conn_id in expired_connections:
                    del self.cache[conn_id]

                if expired_connections:
                    logger.info(
                        f"Удалено {len(expired_connections)} просроченных соединений"
                    )

                return len(expired_connections)

        except Exception as e:
            logger.error(f"Ошибка очистки просроченных соединений: {e}")
            return 0

    def _evict_oldest_connection(self):
        """Удаление самого старого соединения (LRU)"""
        try:
            if self.cache:
                oldest_conn_id = next(iter(self.cache))
                del self.cache[oldest_conn_id]
                logger.info(
                    f"Удалено самое старое соединение {oldest_conn_id}"
                )
        except Exception as e:
            logger.error(f"Ошибка удаления старого соединения: {e}")

    def _is_connection_valid(self, connection: CachedConnection) -> bool:
        """Проверка валидности соединения"""
        current_time = time.time()
        return (current_time - connection.last_used) < self.ttl

    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        try:
            with self.lock:
                current_time = time.time()
                total_connections = len(self.cache)

                # Подсчитываем соединения по состояниям
                state_counts = {}
                for connection in self.cache.values():
                    state = connection.state.value
                    state_counts[state] = state_counts.get(state, 0) + 1

                # Подсчитываем среднее время жизни
                avg_age = 0
                if total_connections > 0:
                    total_age = sum(
                        current_time - conn.created_at
                        for conn in self.cache.values()
                    )
                    avg_age = total_age / total_connections

                # Подсчитываем общее количество использований
                total_usage = sum(
                    conn.usage_count for conn in self.cache.values()
                )

                return {
                    "total_connections": total_connections,
                    "max_connections": self.max_connections,
                    "ttl": self.ttl,
                    "state_counts": state_counts,
                    "average_age": round(avg_age, 2),
                    "total_usage": total_usage,
                    "cache_hit_ratio": self._calculate_hit_ratio(),
                }

        except Exception as e:
            logger.error(f"Ошибка получения статистики кэша: {e}")
            return {}

    def _calculate_hit_ratio(self) -> float:
        """Расчет коэффициента попаданий в кэш"""
        try:
            total_usage = sum(conn.usage_count for conn in self.cache.values())
            if total_usage == 0:
                return 0.0

            # Простая оценка (в реальной реализации нужна более точная метрика)
            return min(0.95, total_usage / (total_usage + len(self.cache)))
        except Exception as e:
            logger.error(f"Ошибка расчета коэффициента попаданий: {e}")
            return 0.0

    def clear_cache(self) -> int:
        """Очистка всего кэша"""
        try:
            with self.lock:
                cleared_count = len(self.cache)
                self.cache.clear()
                logger.info(f"Кэш очищен, удалено {cleared_count} соединений")
                return cleared_count
        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")
            return 0


# Пример использования
def main():
    """Основная функция для тестирования"""
    cache = ALADDINConnectionCache(max_connections=5, ttl=60)

    print("=== КЭШИРОВАНИЕ СОЕДИНЕНИЙ ALADDIN VPN ===")

    # Кэшируем несколько соединений
    for i in range(3):
        conn_id = f"conn_{i+1}"
        server_id = f"server_{i+1}"
        connection_data = {
            "protocol": "wireguard",
            "port": 51820,
            "encryption": "aes-256-gcm",
        }

        cache.cache_connection(conn_id, server_id, connection_data)
        print(f"✅ Соединение {conn_id} для сервера {server_id} закэшировано")

    # Получаем соединение из кэша
    cached_conn = cache.get_connection("server_1")
    if cached_conn:
        print(
            f"✅ Найдено кэшированное соединение: {cached_conn.connection_id}"
        )
        cache.update_connection_state(
            cached_conn.connection_id, ConnectionState.ACTIVE
        )
    else:
        print("❌ Кэшированное соединение не найдено")

    # Получаем статистику
    stats = cache.get_cache_stats()
    print("\n📊 Статистика кэша:")
    print(f"  Всего соединений: {stats['total_connections']}")
    print(f"  Максимум соединений: {stats['max_connections']}")
    print(f"  TTL: {stats['ttl']} сек")
    print(f"  Состояния: {stats['state_counts']}")
    print(f"  Средний возраст: {stats['average_age']} сек")
    print(f"  Общее использование: {stats['total_usage']}")
    print(f"  Коэффициент попаданий: {stats['cache_hit_ratio']:.2%}")


if __name__ == "__main__":
    main()
