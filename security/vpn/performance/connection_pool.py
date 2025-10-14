"""
Пул соединений для ALADDIN VPN
Управляет пулом переиспользуемых соединений для оптимизации производительности
"""

import logging as std_logging
import threading
import time
import weakref
from dataclasses import dataclass
from enum import Enum
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

import asyncio

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class PoolState(Enum):
    """Состояния пула соединений"""

    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class PooledConnection:
    """Соединение в пуле"""

    connection_id: str
    server_id: str
    state: PoolState
    created_at: float
    last_used: float
    usage_count: int
    connection_data: Dict[str, Any]
    is_healthy: bool = True
    error_count: int = 0


class ALADDINConnectionPool:
    """Пул соединений для ALADDIN VPN"""

    def __init__(
        self,
        min_connections: int = 2,
        max_connections: int = 10,
        connection_timeout: int = 30,
        idle_timeout: int = 300,
        health_check_interval: int = 60,
    ):

        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval

        # Пул соединений
        self.available_connections: Queue = Queue()
        self.active_connections: Dict[str, PooledConnection] = {}
        self.all_connections: Dict[str, PooledConnection] = {}

        # Управление пулом
        self.lock = threading.RLock()
        self.pool_state = PoolState.IDLE
        self.connection_factory: Optional[Callable] = None

        # Мониторинг и очистка
        self._health_check_task = None
        self._cleanup_task = None
        self._start_background_tasks()

        logger.info(
            f"Пул соединений создан: min={min_connections}, max={max_connections}"
        )

    def set_connection_factory(self, factory: Callable[[str], Dict[str, Any]]):
        """Установка фабрики для создания соединений"""
        self.connection_factory = factory
        logger.info("Фабрика соединений установлена")

    def _start_background_tasks(self):
        """Запуск фоновых задач"""

        # Задача проверки здоровья соединений
        def health_check_loop():
            while self.pool_state != PoolState.CLOSED:
                time.sleep(self.health_check_interval)
                self._health_check_connections()

        # Задача очистки неактивных соединений
        def cleanup_loop():
            while self.pool_state != PoolState.CLOSED:
                time.sleep(self.health_check_interval)
                self._cleanup_idle_connections()

        self._health_check_task = threading.Thread(
            target=health_check_loop, daemon=True
        )
        self._cleanup_task = threading.Thread(target=cleanup_loop, daemon=True)

        self._health_check_task.start()
        self._cleanup_task.start()

        logger.info("Фоновые задачи пула запущены")

    def initialize_pool(self) -> bool:
        """Инициализация пула с минимальным количеством соединений"""
        try:
            with self.lock:
                if self.pool_state != PoolState.IDLE:
                    logger.warning("Пул уже инициализирован")
                    return False

                if not self.connection_factory:
                    logger.error("Фабрика соединений не установлена")
                    return False

                # Создаем минимальное количество соединений
                for i in range(self.min_connections):
                    if not self._create_connection():
                        logger.error(f"Не удалось создать соединение {i+1}")
                        return False

                self.pool_state = PoolState.ACTIVE
                logger.info(
                    f"Пул инициализирован с {self.min_connections} соединениями"
                )
                return True

        except Exception as e:
            logger.error(f"Ошибка инициализации пула: {e}")
            return False

    def get_connection(
        self, server_id: str, timeout: Optional[int] = None
    ) -> Optional[PooledConnection]:
        """Получение соединения из пула"""
        try:
            if timeout is None:
                timeout = self.connection_timeout

            # Сначала ищем доступное соединение
            try:
                connection = self.available_connections.get(timeout=1)
                if connection and connection.is_healthy:
                    with self.lock:
                        connection.state = PoolState.BUSY
                        connection.last_used = time.time()
                        connection.usage_count += 1
                        self.active_connections[connection.connection_id] = (
                            connection
                        )

                    logger.info(
                        f"Получено соединение {connection.connection_id} из пула"
                    )
                    return connection
            except Empty:
                pass

            # Если нет доступных соединений, создаем новое
            with self.lock:
                if len(self.all_connections) < self.max_connections:
                    new_connection = self._create_connection(server_id)
                    if new_connection:
                        new_connection.state = PoolState.BUSY
                        new_connection.last_used = time.time()
                        new_connection.usage_count = 1
                        self.active_connections[
                            new_connection.connection_id
                        ] = new_connection

                        logger.info(
                            f"Создано новое соединение {new_connection.connection_id}"
                        )
                        return new_connection
                else:
                    logger.warning("Достигнут максимум соединений в пуле")
                    return None

        except Exception as e:
            logger.error(f"Ошибка получения соединения из пула: {e}")
            return None

    def return_connection(self, connection_id: str) -> bool:
        """Возврат соединения в пул"""
        try:
            with self.lock:
                if connection_id in self.active_connections:
                    connection = self.active_connections[connection_id]
                    connection.state = PoolState.IDLE
                    connection.last_used = time.time()

                    # Удаляем из активных
                    del self.active_connections[connection_id]

                    # Возвращаем в доступные, если соединение здоровое
                    if connection.is_healthy:
                        self.available_connections.put(connection)
                        logger.info(
                            f"Соединение {connection_id} возвращено в пул"
                        )
                    else:
                        # Удаляем нездоровое соединение
                        self._remove_connection(connection_id)
                        logger.info(
                            f"Нездоровое соединение {connection_id} удалено из пула"
                        )

                    return True
                else:
                    logger.warning(
                        f"Соединение {connection_id} не найдено в активных"
                    )
                    return False

        except Exception as e:
            logger.error(f"Ошибка возврата соединения в пул: {e}")
            return False

    def _create_connection(
        self, server_id: str = "default"
    ) -> Optional[PooledConnection]:
        """Создание нового соединения"""
        try:
            if not self.connection_factory:
                logger.error("Фабрика соединений не установлена")
                return None

            connection_id = f"conn_{int(time.time() * 1000)}"
            connection_data = self.connection_factory(server_id)

            connection = PooledConnection(
                connection_id=connection_id,
                server_id=server_id,
                state=PoolState.IDLE,
                created_at=time.time(),
                last_used=time.time(),
                usage_count=0,
                connection_data=connection_data,
                is_healthy=True,
                error_count=0,
            )

            self.all_connections[connection_id] = connection
            self.available_connections.put(connection)

            logger.info(
                f"Создано соединение {connection_id} для сервера {server_id}"
            )
            return connection

        except Exception as e:
            logger.error(f"Ошибка создания соединения: {e}")
            return None

    def _remove_connection(self, connection_id: str):
        """Удаление соединения из пула"""
        try:
            if connection_id in self.all_connections:
                del self.all_connections[connection_id]
                logger.info(f"Соединение {connection_id} удалено из пула")
        except Exception as e:
            logger.error(f"Ошибка удаления соединения: {e}")

    def _health_check_connections(self):
        """Проверка здоровья соединений"""
        try:
            with self.lock:
                current_time = time.time()
                unhealthy_connections = []

                for conn_id, connection in self.all_connections.items():
                    # Проверяем время простоя
                    if (
                        current_time - connection.last_used
                    ) > self.idle_timeout:
                        connection.is_healthy = False
                        unhealthy_connections.append(conn_id)
                        logger.info(
                            f"Соединение {conn_id} помечено как нездоровое (время простоя)"
                        )

                    # Проверяем количество ошибок
                    elif connection.error_count > 3:
                        connection.is_healthy = False
                        unhealthy_connections.append(conn_id)
                        logger.info(
                            f"Соединение {conn_id} помечено как нездоровое (много ошибок)"
                        )

                # Удаляем нездоровые соединения
                for conn_id in unhealthy_connections:
                    self._remove_connection(conn_id)

                if unhealthy_connections:
                    logger.info(
                        f"Удалено {len(unhealthy_connections)} нездоровых соединений"
                    )

        except Exception as e:
            logger.error(f"Ошибка проверки здоровья соединений: {e}")

    def _get_available_connections_list(self):
        """Получение списка доступных соединений"""
        available_list = []
        while not self.available_connections.empty():
            try:
                conn = self.available_connections.get_nowait()
                available_list.append(conn)
            except Empty:
                break
        return available_list

    def _identify_idle_connections(self, available_list, current_time):
        """Определение неактивных соединений для удаления"""
        keep_count = max(self.min_connections, len(self.active_connections))
        if len(available_list) <= keep_count:
            return []

        excess_connections = available_list[keep_count:]
        idle_connections = []
        for conn in excess_connections:
            if (current_time - conn.last_used) > self.idle_timeout:
                idle_connections.append(conn.connection_id)
        return idle_connections

    def _return_remaining_connections(self, available_list, idle_connections):
        """Возврат оставшихся соединений в очередь"""
        for conn in available_list:
            if conn.connection_id not in idle_connections:
                self.available_connections.put(conn)

    def _cleanup_idle_connections(self):
        """Очистка неактивных соединений"""
        try:
            with self.lock:
                current_time = time.time()

                # Получаем список доступных соединений
                available_list = self._get_available_connections_list()

                # Сортируем по времени последнего использования
                available_list.sort(key=lambda x: x.last_used)

                # Определяем неактивные соединения для удаления
                idle_connections = self._identify_idle_connections(
                    available_list, current_time
                )

                # Удаляем избыточные неактивные соединения
                for conn_id in idle_connections:
                    self._remove_connection(conn_id)

                # Возвращаем оставшиеся соединения в очередь
                self._return_remaining_connections(available_list, idle_connections)

                if idle_connections:
                    logger.info(
                        f"Удалено {len(idle_connections)} неактивных соединений"
                    )

        except Exception as e:
            logger.error(f"Ошибка очистки неактивных соединений: {e}")

    def mark_connection_error(self, connection_id: str):
        """Отметка ошибки в соединении"""
        try:
            with self.lock:
                if connection_id in self.all_connections:
                    connection = self.all_connections[connection_id]
                    connection.error_count += 1

                    if connection.error_count > 3:
                        connection.is_healthy = False
                        logger.warning(
                            f"Соединение {connection_id} помечено как нездоровое"
                        )

        except Exception as e:
            logger.error(f"Ошибка отметки ошибки соединения: {e}")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Получение статистики пула"""
        try:
            with self.lock:
                current_time = time.time()

                # Подсчитываем соединения по состояниям
                state_counts = {}
                for connection in self.all_connections.values():
                    state = connection.state.value
                    state_counts[state] = state_counts.get(state, 0) + 1

                # Подсчитываем среднее время жизни
                avg_age = 0
                if self.all_connections:
                    total_age = sum(
                        current_time - conn.created_at
                        for conn in self.all_connections.values()
                    )
                    avg_age = total_age / len(self.all_connections)

                # Подсчитываем общее использование
                total_usage = sum(
                    conn.usage_count for conn in self.all_connections.values()
                )

                return {
                    "pool_state": self.pool_state.value,
                    "total_connections": len(self.all_connections),
                    "active_connections": len(self.active_connections),
                    "available_connections": self.available_connections.qsize(),
                    "min_connections": self.min_connections,
                    "max_connections": self.max_connections,
                    "state_counts": state_counts,
                    "average_age": round(avg_age, 2),
                    "total_usage": total_usage,
                    "healthy_connections": sum(
                        1
                        for conn in self.all_connections.values()
                        if conn.is_healthy
                    ),
                    "unhealthy_connections": sum(
                        1
                        for conn in self.all_connections.values()
                        if not conn.is_healthy
                    ),
                }

        except Exception as e:
            logger.error(f"Ошибка получения статистики пула: {e}")
            return {}

    def close_pool(self):
        """Закрытие пула соединений"""
        try:
            with self.lock:
                self.pool_state = PoolState.CLOSED

                # Закрываем все соединения
                for connection in self.all_connections.values():
                    connection.state = PoolState.CLOSED

                # Очищаем пулы
                while not self.available_connections.empty():
                    try:
                        self.available_connections.get_nowait()
                    except Empty:
                        break

                self.active_connections.clear()
                self.all_connections.clear()

                logger.info("Пул соединений закрыт")

        except Exception as e:
            logger.error(f"Ошибка закрытия пула: {e}")


# Пример использования
def create_wireguard_connection(server_id: str) -> Dict[str, Any]:
    """Фабрика для создания WireGuard соединений"""
    return {
        "protocol": "wireguard",
        "server_id": server_id,
        "port": 51820,
        "encryption": "aes-256-gcm",
        "key_exchange": "curve25519",
        "created_at": time.time(),
    }


def main():
    """Основная функция для тестирования"""
    pool = ALADDINConnectionPool(
        min_connections=2,
        max_connections=5,
        connection_timeout=10,
        idle_timeout=60,
    )

    print("=== ПУЛ СОЕДИНЕНИЙ ALADDIN VPN ===")

    # Устанавливаем фабрику соединений
    pool.set_connection_factory(create_wireguard_connection)

    # Инициализируем пул
    if pool.initialize_pool():
        print("✅ Пул инициализирован")
    else:
        print("❌ Ошибка инициализации пула")
        return

    # Получаем соединения
    connections = []
    for i in range(3):
        conn = pool.get_connection(f"server_{i+1}")
        if conn:
            connections.append(conn)
            print(f"✅ Получено соединение {conn.connection_id}")
        else:
            print(f"❌ Не удалось получить соединение для server_{i+1}")

    # Возвращаем соединения
    for conn in connections:
        if pool.return_connection(conn.connection_id):
            print(f"✅ Соединение {conn.connection_id} возвращено в пул")
        else:
            print(f"❌ Ошибка возврата соединения {conn.connection_id}")

    # Получаем статистику
    stats = pool.get_pool_stats()
    print("\n📊 Статистика пула:")
    print(f"  Состояние пула: {stats['pool_state']}")
    print(f"  Всего соединений: {stats['total_connections']}")
    print(f"  Активных: {stats['active_connections']}")
    print(f"  Доступных: {stats['available_connections']}")
    print(f"  Минимум: {stats['min_connections']}")
    print(f"  Максимум: {stats['max_connections']}")
    print(f"  Здоровых: {stats['healthy_connections']}")
    print(f"  Нездоровых: {stats['unhealthy_connections']}")
    print(f"  Средний возраст: {stats['average_age']} сек")
    print(f"  Общее использование: {stats['total_usage']}")

    # Закрываем пул
    pool.close_pool()
    print("✅ Пул закрыт")


if __name__ == "__main__":
    main()
