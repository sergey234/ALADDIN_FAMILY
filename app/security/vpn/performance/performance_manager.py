"""
Менеджер производительности для ALADDIN VPN
Интегрирует кэширование, пул соединений и асинхронную обработку
"""

import logging as std_logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import asyncio

from .async_processor import ALADDINAsyncProcessor, AsyncTask, TaskPriority

# Импорты наших модулей
from .connection_cache import ALADDINConnectionCache, ConnectionState
from .connection_pool import ALADDINConnectionPool, PooledConnection, PoolState

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class PerformanceMode(Enum):
    """Режимы производительности"""

    BALANCED = "balanced"  # Сбалансированный
    HIGH_PERFORMANCE = "high"  # Высокая производительность
    MEMORY_OPTIMIZED = "memory"  # Оптимизированный по памяти
    LOW_LATENCY = "latency"  # Низкая задержка


@dataclass
class PerformanceConfig:
    """Конфигурация производительности"""

    mode: PerformanceMode
    cache_size: int
    pool_min_connections: int
    pool_max_connections: int
    async_workers: int
    connection_ttl: int
    task_timeout: int


class ALADDINPerformanceManager:
    """Менеджер производительности ALADDIN VPN"""

    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or self._get_default_config()

        # Инициализируем компоненты
        self.connection_cache = ALADDINConnectionCache(
            max_connections=self.config.cache_size, ttl=self.config.connection_ttl
        )

        self.connection_pool = ALADDINConnectionPool(
            min_connections=self.config.pool_min_connections,
            max_connections=self.config.pool_max_connections,
            connection_timeout=30,
            idle_timeout=self.config.connection_ttl,
        )

        self.async_processor = ALADDINAsyncProcessor(
            max_workers=self.config.async_workers, max_tasks=1000, task_timeout=self.config.task_timeout
        )

        # Состояние
        self.is_initialized = False
        self.performance_metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "async_tasks_completed": 0,
            "average_response_time": 0.0,
            "error_rate": 0.0,
        }

        logger.info(f"Менеджер производительности создан в режиме {self.config.mode.value}")

    def _get_default_config(self) -> PerformanceConfig:
        """Получение конфигурации по умолчанию"""
        return PerformanceConfig(
            mode=PerformanceMode.BALANCED,
            cache_size=50,
            pool_min_connections=5,
            pool_max_connections=20,
            async_workers=8,
            connection_ttl=300,
            task_timeout=60,
        )

    async def initialize(self) -> bool:
        """Инициализация менеджера производительности"""
        try:
            if self.is_initialized:
                logger.warning("Менеджер уже инициализирован")
                return True

            # Устанавливаем фабрику соединений для пула
            self.connection_pool.set_connection_factory(self._create_vpn_connection)

            # Инициализируем пул соединений
            if not self.connection_pool.initialize_pool():
                logger.error("Ошибка инициализации пула соединений")
                return False

            # Запускаем асинхронный процессор
            await self.async_processor.start()

            self.is_initialized = True
            logger.info("Менеджер производительности инициализирован")
            return True

        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера производительности: {e}")
            return False

    async def shutdown(self):
        """Завершение работы менеджера"""
        try:
            if not self.is_initialized:
                logger.warning("Менеджер не инициализирован")
                return

            # Останавливаем асинхронный процессор
            await self.async_processor.stop()

            # Закрываем пул соединений
            self.connection_pool.close_pool()

            # Очищаем кэш
            self.connection_cache.clear_cache()

            self.is_initialized = False
            logger.info("Менеджер производительности завершен")

        except Exception as e:
            logger.error(f"Ошибка завершения менеджера: {e}")

    def _create_vpn_connection(self, server_id: str) -> Dict[str, Any]:
        """Фабрика для создания VPN соединений"""
        return {
            "server_id": server_id,
            "protocol": "wireguard",
            "port": 51820,
            "encryption": "aes-256-gcm",
            "key_exchange": "curve25519",
            "created_at": time.time(),
            "is_secure": True,
        }

    async def get_connection(self, server_id: str, use_cache: bool = True) -> Optional[PooledConnection]:
        """Получение соединения с оптимизацией"""
        try:
            start_time = time.time()

            # Сначала проверяем кэш
            if use_cache:
                cached_conn = self.connection_cache.get_connection(server_id)
                if cached_conn:
                    self.performance_metrics["cache_hits"] += 1
                    logger.info(f"Соединение получено из кэша для сервера {server_id}")
                    return self._convert_cached_to_pooled(cached_conn)
                else:
                    self.performance_metrics["cache_misses"] += 1

            # Получаем из пула
            pooled_conn = self.connection_pool.get_connection(server_id)
            if pooled_conn:
                self.performance_metrics["pool_hits"] += 1

                # Кэшируем соединение
                if use_cache:
                    self.connection_cache.cache_connection(
                        pooled_conn.connection_id, server_id, pooled_conn.connection_data
                    )

                logger.info(f"Соединение получено из пула для сервера {server_id}")
            else:
                self.performance_metrics["pool_misses"] += 1
                logger.warning(f"Не удалось получить соединение для сервера {server_id}")

            # Обновляем метрики времени ответа
            response_time = time.time() - start_time
            self._update_response_time(response_time)

            return pooled_conn

        except Exception as e:
            logger.error(f"Ошибка получения соединения: {e}")
            self._update_error_rate()
            return None

    def return_connection(self, connection_id: str) -> bool:
        """Возврат соединения"""
        try:
            # Возвращаем в пул
            success = self.connection_pool.return_connection(connection_id)

            if success:
                logger.info(f"Соединение {connection_id} возвращено в пул")
            else:
                logger.warning(f"Ошибка возврата соединения {connection_id}")

            return success

        except Exception as e:
            logger.error(f"Ошибка возврата соединения: {e}")
            self._update_error_rate()
            return False

    def _convert_cached_to_pooled(self, cached_conn) -> PooledConnection:
        """Конвертация кэшированного соединения в пулированное"""
        return PooledConnection(
            connection_id=cached_conn.connection_id,
            server_id=cached_conn.server_id,
            state=cached_conn.state,
            created_at=cached_conn.created_at,
            last_used=cached_conn.last_used,
            usage_count=cached_conn.usage_count,
            connection_data=cached_conn.connection_data,
            is_healthy=True,
            error_count=0,
        )

    async def submit_async_task(
        self, function: Callable, *args, priority: TaskPriority = TaskPriority.NORMAL, **kwargs
    ) -> str:
        """Отправка асинхронной задачи"""
        try:
            if not self.is_initialized:
                raise RuntimeError("Менеджер не инициализирован")

            task_id = await self.async_processor.submit_task(function, *args, priority=priority, **kwargs)

            logger.info(f"Асинхронная задача {task_id} отправлена")
            return task_id

        except Exception as e:
            logger.error(f"Ошибка отправки асинхронной задачи: {e}")
            self._update_error_rate()
            raise

    async def get_async_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Получение результата асинхронной задачи"""
        try:
            result = await self.async_processor.get_task_result(task_id, timeout)
            self.performance_metrics["async_tasks_completed"] += 1
            return result

        except Exception as e:
            logger.error(f"Ошибка получения результата задачи {task_id}: {e}")
            self._update_error_rate()
            raise

    def _update_response_time(self, response_time: float):
        """Обновление среднего времени ответа"""
        try:
            current_avg = self.performance_metrics["average_response_time"]
            total_requests = (
                self.performance_metrics["cache_hits"]
                + self.performance_metrics["cache_misses"]
                + self.performance_metrics["pool_hits"]
                + self.performance_metrics["pool_misses"]
            )

            if total_requests > 0:
                new_avg = (current_avg * (total_requests - 1) + response_time) / total_requests
                self.performance_metrics["average_response_time"] = new_avg
            else:
                self.performance_metrics["average_response_time"] = response_time

        except Exception as e:
            logger.error(f"Ошибка обновления времени ответа: {e}")

    def _update_error_rate(self):
        """Обновление коэффициента ошибок"""
        try:
            total_requests = (
                self.performance_metrics["cache_hits"]
                + self.performance_metrics["cache_misses"]
                + self.performance_metrics["pool_hits"]
                + self.performance_metrics["pool_misses"]
            )

            if total_requests > 0:
                # Простая оценка (в реальной реализации нужна более точная метрика)
                self.performance_metrics["error_rate"] = min(
                    1.0, (total_requests - self.performance_metrics["pool_hits"]) / total_requests
                )

        except Exception as e:
            logger.error(f"Ошибка обновления коэффициента ошибок: {e}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        try:
            # Получаем статистику от компонентов
            cache_stats = self.connection_cache.get_cache_stats()
            pool_stats = self.connection_pool.get_pool_stats()

            # Объединяем статистику
            return {
                "manager_status": {
                    "initialized": self.is_initialized,
                    "mode": self.config.mode.value,
                    "config": {
                        "cache_size": self.config.cache_size,
                        "pool_min": self.config.pool_min_connections,
                        "pool_max": self.config.pool_max_connections,
                        "async_workers": self.config.async_workers,
                    },
                },
                "cache_stats": cache_stats,
                "pool_stats": pool_stats,
                "performance_metrics": self.performance_metrics.copy(),
                "efficiency": {
                    "cache_hit_ratio": self._calculate_cache_hit_ratio(),
                    "pool_utilization": self._calculate_pool_utilization(),
                    "overall_efficiency": self._calculate_overall_efficiency(),
                },
            }

        except Exception as e:
            logger.error(f"Ошибка получения статистики производительности: {e}")
            return {}

    def _calculate_cache_hit_ratio(self) -> float:
        """Расчет коэффициента попаданий в кэш"""
        try:
            total_cache_requests = self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]

            if total_cache_requests > 0:
                return self.performance_metrics["cache_hits"] / total_cache_requests
            return 0.0

        except Exception as e:
            logger.error(f"Ошибка расчета коэффициента попаданий в кэш: {e}")
            return 0.0

    def _calculate_pool_utilization(self) -> float:
        """Расчет утилизации пула"""
        try:
            pool_stats = self.connection_pool.get_pool_stats()
            if pool_stats.get("max_connections", 0) > 0:
                return pool_stats.get("total_connections", 0) / pool_stats.get("max_connections", 1)
            return 0.0

        except Exception as e:
            logger.error(f"Ошибка расчета утилизации пула: {e}")
            return 0.0

    def _calculate_overall_efficiency(self) -> float:
        """Расчет общей эффективности"""
        try:
            cache_ratio = self._calculate_cache_hit_ratio()
            pool_util = self._calculate_pool_utilization()
            error_rate = self.performance_metrics.get("error_rate", 0.0)

            # Формула эффективности (можно настроить)
            efficiency = cache_ratio * 0.4 + pool_util * 0.4 + (1 - error_rate) * 0.2
            return min(1.0, max(0.0, efficiency))

        except Exception as e:
            logger.error(f"Ошибка расчета общей эффективности: {e}")
            return 0.0

    def optimize_performance(self):
        """Оптимизация производительности на основе метрик"""
        try:

            # Анализируем метрики и применяем оптимизации
            cache_hit_ratio = self._calculate_cache_hit_ratio()
            pool_utilization = self._calculate_pool_utilization()
            error_rate = self.performance_metrics.get("error_rate", 0.0)

            optimizations = []

            # Оптимизация кэша
            if cache_hit_ratio < 0.7:
                optimizations.append("Увеличить размер кэша")
                # В реальной реализации здесь можно увеличить cache_size

            # Оптимизация пула
            if pool_utilization > 0.8:
                optimizations.append("Увеличить размер пула соединений")
                # В реальной реализации здесь можно увеличить max_connections

            if error_rate > 0.1:
                optimizations.append("Проверить стабильность соединений")
                # В реальной реализации здесь можно добавить проверки здоровья

            if optimizations:
                logger.info(f"Рекомендации по оптимизации: {', '.join(optimizations)}")
            else:
                logger.info("Система работает оптимально")

        except Exception as e:
            logger.error(f"Ошибка оптимизации производительности: {e}")


# Пример использования
async def main():
    """Основная функция для тестирования"""
    # Создаем конфигурацию
    config = PerformanceConfig(
        mode=PerformanceMode.HIGH_PERFORMANCE,
        cache_size=100,
        pool_min_connections=10,
        pool_max_connections=50,
        async_workers=16,
        connection_ttl=600,
        task_timeout=120,
    )

    # Создаем менеджер
    manager = ALADDINPerformanceManager(config)

    print("=== МЕНЕДЖЕР ПРОИЗВОДИТЕЛЬНОСТИ ALADDIN VPN ===")

    # Инициализируем
    if await manager.initialize():
        print("✅ Менеджер инициализирован")
    else:
        print("❌ Ошибка инициализации")
        return

    try:
        # Тестируем получение соединений
        for i in range(5):
            server_id = f"server_{i+1}"
            conn = await manager.get_connection(server_id)
            if conn:
                print(f"✅ Получено соединение для {server_id}")
                # Возвращаем соединение
                manager.return_connection(conn.connection_id)
            else:
                print(f"❌ Ошибка получения соединения для {server_id}")

        # Тестируем асинхронные задачи
        task_id = await manager.submit_async_task(lambda: time.sleep(1), priority=TaskPriority.NORMAL)  # Простая задача
        print(f"✅ Асинхронная задача {task_id} отправлена")

        # Получаем статистику
        stats = manager.get_performance_stats()
        print("\n📊 Статистика производительности:")
        print(f"  Режим: {stats['manager_status']['mode']}")
        print(f"  Кэш: {stats['cache_stats']}")
        print(f"  Пул: {stats['pool_stats']}")
        print(f"  Метрики: {stats['performance_metrics']}")
        print(f"  Эффективность: {stats['efficiency']}")

        # Оптимизация
        manager.optimize_performance()

    finally:
        # Завершаем работу
        await manager.shutdown()
        print("✅ Менеджер завершен")


if __name__ == "__main__":
    asyncio.run(main())
