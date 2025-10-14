"""
Автоматическое переподключение для ALADDIN VPN
Обеспечивает стабильность соединения через автоматическое переподключение
"""

import logging as std_logging
import random
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import asyncio

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class ReconnectStrategy(Enum):
    """Стратегии переподключения"""

    IMMEDIATE = "immediate"  # Немедленное переподключение
    EXPONENTIAL = "exponential"  # Экспоненциальная задержка
    LINEAR = "linear"  # Линейная задержка
    FIXED = "fixed"  # Фиксированная задержка
    SMART = "smart"  # Умная стратегия


class ConnectionQuality(Enum):
    """Качество соединения"""

    EXCELLENT = "excellent"  # Отличное
    GOOD = "good"  # Хорошее
    FAIR = "fair"  # Удовлетворительное
    POOR = "poor"  # Плохое
    CRITICAL = "critical"  # Критическое


@dataclass
class ReconnectConfig:
    """Конфигурация переподключения"""

    max_attempts: int = 10
    base_delay: float = 1.0  # Базовая задержка в секундах
    max_delay: float = 300.0  # Максимальная задержка в секундах
    strategy: ReconnectStrategy = ReconnectStrategy.EXPONENTIAL
    quality_threshold: float = 0.7  # Порог качества для переподключения
    health_check_interval: float = 30.0  # Интервал проверки здоровья
    jitter: bool = True  # Добавлять случайность к задержкам


@dataclass
class ReconnectStats:
    """Статистика переподключений"""

    total_attempts: int = 0
    successful_reconnects: int = 0
    failed_reconnects: int = 0
    current_attempt: int = 0
    last_reconnect_time: float = 0.0
    average_reconnect_time: float = 0.0
    consecutive_failures: int = 0
    max_consecutive_failures: int = 0


class ALADDINAutoReconnect:
    """Автоматическое переподключение для ALADDIN VPN"""

    def __init__(self, config: Optional[ReconnectConfig] = None):
        self.config = config or ReconnectConfig()
        self.stats = ReconnectStats()

        # Состояние
        self.is_enabled = False
        self.is_reconnecting = False
        self.current_connection_id: Optional[str] = None
        self.connection_quality = ConnectionQuality.EXCELLENT

        # Callbacks
        self.on_reconnect_start: Optional[Callable] = None
        self.on_reconnect_success: Optional[Callable] = None
        self.on_reconnect_failure: Optional[Callable] = None
        self.on_quality_change: Optional[Callable] = None

        # Мониторинг
        self.health_check_task: Optional[asyncio.Task] = None
        self.lock = asyncio.Lock()

        logger.info("Автоматическое переподключение инициализировано")

    def set_callbacks(
        self,
        on_reconnect_start: Optional[Callable] = None,
        on_reconnect_success: Optional[Callable] = None,
        on_reconnect_failure: Optional[Callable] = None,
        on_quality_change: Optional[Callable] = None,
    ):
        """Установка callback функций"""
        self.on_reconnect_start = on_reconnect_start
        self.on_reconnect_success = on_reconnect_success
        self.on_reconnect_failure = on_reconnect_failure
        self.on_quality_change = on_quality_change
        logger.info("Callbacks установлены")

    async def start(self):
        """Запуск автоматического переподключения"""
        try:
            if self.is_enabled:
                logger.warning("Автоматическое переподключение уже запущено")
                return

            self.is_enabled = True

            # Запускаем мониторинг здоровья
            self.health_check_task = asyncio.create_task(self._health_check_loop())

            logger.info("Автоматическое переподключение запущено")

        except Exception as e:
            logger.error(f"Ошибка запуска автоматического переподключения: {e}")
            raise

    async def stop(self):
        """Остановка автоматического переподключения"""
        try:
            if not self.is_enabled:
                logger.warning("Автоматическое переподключение не запущено")
                return

            self.is_enabled = False

            # Останавливаем мониторинг
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
                self.health_check_task = None

            logger.info("Автоматическое переподключение остановлено")

        except Exception as e:
            logger.error(f"Ошибка остановки автоматического переподключения: {e}")

    async def _health_check_loop(self):
        """Цикл проверки здоровья соединения"""
        logger.info("Мониторинг здоровья соединения запущен")

        while self.is_enabled:
            try:
                await asyncio.sleep(self.config.health_check_interval)

                if self.current_connection_id:
                    # Проверяем качество соединения
                    quality = await self._check_connection_quality()

                    if quality != self.connection_quality:
                        old_quality = self.connection_quality
                        self.connection_quality = quality

                        logger.info(f"Качество соединения изменилось: {old_quality.value} -> {quality.value}")

                        if self.on_quality_change:
                            await self._safe_callback(self.on_quality_change, quality)

                    # Проверяем, нужно ли переподключение
                    if self._should_reconnect(quality):
                        logger.warning(f"Требуется переподключение (качество: {quality.value})")
                        await self._trigger_reconnect()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле проверки здоровья: {e}")
                await asyncio.sleep(5)  # Небольшая задержка при ошибке

        logger.info("Мониторинг здоровья соединения остановлен")

    async def _check_connection_quality(self) -> ConnectionQuality:
        """Проверка качества соединения"""
        try:
            # Имитация проверки качества соединения
            # В реальной реализации здесь будут реальные метрики

            # Симулируем различные условия
            rand = random.random()

            if rand < 0.7:
                return ConnectionQuality.EXCELLENT
            elif rand < 0.85:
                return ConnectionQuality.GOOD
            elif rand < 0.95:
                return ConnectionQuality.FAIR
            elif rand < 0.98:
                return ConnectionQuality.POOR
            else:
                return ConnectionQuality.CRITICAL

        except Exception as e:
            logger.error(f"Ошибка проверки качества соединения: {e}")
            return ConnectionQuality.CRITICAL

    def _should_reconnect(self, quality: ConnectionQuality) -> bool:
        """Определение необходимости переподключения"""
        try:
            # Проверяем, не идет ли уже переподключение
            if self.is_reconnecting:
                return False

            # Проверяем качество соединения
            quality_thresholds = {
                ConnectionQuality.EXCELLENT: 0.9,
                ConnectionQuality.GOOD: 0.8,
                ConnectionQuality.FAIR: 0.6,
                ConnectionQuality.POOR: 0.3,
                ConnectionQuality.CRITICAL: 0.1,
            }

            threshold = quality_thresholds.get(quality, 0.5)
            return threshold < self.config.quality_threshold

        except Exception as e:
            logger.error(f"Ошибка определения необходимости переподключения: {e}")
            return False

    async def _trigger_reconnect(self):
        """Запуск процесса переподключения"""
        try:
            async with self.lock:
                if self.is_reconnecting:
                    logger.warning("Переподключение уже в процессе")
                    return

                self.is_reconnecting = True
                self.stats.current_attempt = 0

            logger.info("Запуск автоматического переподключения")

            if self.on_reconnect_start:
                await self._safe_callback(self.on_reconnect_start)

            # Выполняем переподключение
            success = await self._perform_reconnect()

            if success:
                self.stats.successful_reconnects += 1
                self.stats.consecutive_failures = 0

                if self.on_reconnect_success:
                    await self._safe_callback(self.on_reconnect_success)

                logger.info("Переподключение успешно")
            else:
                self.stats.failed_reconnects += 1
                self.stats.consecutive_failures += 1
                self.stats.max_consecutive_failures = max(
                    self.stats.max_consecutive_failures, self.stats.consecutive_failures
                )

                if self.on_reconnect_failure:
                    await self._safe_callback(self.on_reconnect_failure)

                logger.error("Переподключение не удалось")

        except Exception as e:
            logger.error(f"Ошибка запуска переподключения: {e}")
        finally:
            async with self.lock:
                self.is_reconnecting = False

    async def _perform_reconnect(self) -> bool:
        """Выполнение переподключения"""
        try:
            for attempt in range(1, self.config.max_attempts + 1):
                self.stats.current_attempt = attempt
                self.stats.total_attempts += 1

                logger.info(f"Попытка переподключения {attempt}/{self.config.max_attempts}")

                # Вычисляем задержку
                delay = self._calculate_delay(attempt)
                if delay > 0:
                    logger.info(f"Ожидание {delay:.1f} секунд перед попыткой {attempt}")
                    await asyncio.sleep(delay)

                # Выполняем попытку переподключения
                success = await self._attempt_reconnect()

                if success:
                    self.stats.last_reconnect_time = time.time()
                    self._update_average_reconnect_time()
                    return True
                else:
                    logger.warning(f"Попытка {attempt} не удалась")

            logger.error(f"Все {self.config.max_attempts} попыток переподключения исчерпаны")
            return False

        except Exception as e:
            logger.error(f"Ошибка выполнения переподключения: {e}")
            return False

    def _calculate_delay(self, attempt: int) -> float:
        """Вычисление задержки для попытки"""
        try:
            if self.config.strategy == ReconnectStrategy.IMMEDIATE:
                return 0.0
            elif self.config.strategy == ReconnectStrategy.FIXED:
                delay = self.config.base_delay
            elif self.config.strategy == ReconnectStrategy.LINEAR:
                delay = self.config.base_delay * attempt
            elif self.config.strategy == ReconnectStrategy.EXPONENTIAL:
                delay = self.config.base_delay * (2 ** (attempt - 1))
            elif self.config.strategy == ReconnectStrategy.SMART:
                # Умная стратегия: учитывает качество соединения
                quality_factor = {
                    ConnectionQuality.EXCELLENT: 1.0,
                    ConnectionQuality.GOOD: 0.8,
                    ConnectionQuality.FAIR: 0.6,
                    ConnectionQuality.POOR: 0.4,
                    ConnectionQuality.CRITICAL: 0.2,
                }.get(self.connection_quality, 0.5)

                delay = self.config.base_delay * (2 ** (attempt - 1)) * quality_factor
            else:
                delay = self.config.base_delay

            # Ограничиваем максимальной задержкой
            delay = min(delay, self.config.max_delay)

            # Добавляем jitter для избежания thundering herd
            if self.config.jitter:
                jitter = random.uniform(0.8, 1.2)
                delay *= jitter

            return delay

        except Exception as e:
            logger.error(f"Ошибка вычисления задержки: {e}")
            return self.config.base_delay

    async def _attempt_reconnect(self) -> bool:
        """Попытка переподключения"""
        try:
            # Имитация попытки переподключения
            # В реальной реализации здесь будет реальное переподключение

            await asyncio.sleep(random.uniform(0.5, 2.0))

            # Симулируем успех/неудачу
            # Вероятность успеха зависит от попытки (увеличивается с каждой попыткой)
            success_probability = min(0.9, 0.3 + (self.stats.current_attempt * 0.1))

            return random.random() < success_probability

        except Exception as e:
            logger.error(f"Ошибка попытки переподключения: {e}")
            return False

    def _update_average_reconnect_time(self):
        """Обновление среднего времени переподключения"""
        try:
            if self.stats.successful_reconnects > 0:
                current_avg = self.stats.average_reconnect_time
                new_avg = (
                    current_avg * (self.stats.successful_reconnects - 1) + self.stats.current_attempt
                ) / self.stats.successful_reconnects
                self.stats.average_reconnect_time = new_avg
            else:
                self.stats.average_reconnect_time = self.stats.current_attempt

        except Exception as e:
            logger.error(f"Ошибка обновления среднего времени переподключения: {e}")

    async def _safe_callback(self, callback: Callable, *args, **kwargs):
        """Безопасный вызов callback функции"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в callback функции: {e}")

    def set_connection_id(self, connection_id: str):
        """Установка ID текущего соединения"""
        self.current_connection_id = connection_id
        logger.info(f"ID соединения установлен: {connection_id}")

    def clear_connection_id(self):
        """Очистка ID соединения"""
        self.current_connection_id = None
        logger.info("ID соединения очищен")

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики переподключений"""
        try:
            return {
                "is_enabled": self.is_enabled,
                "is_reconnecting": self.is_reconnecting,
                "current_connection_id": self.current_connection_id,
                "connection_quality": self.connection_quality.value,
                "config": {
                    "max_attempts": self.config.max_attempts,
                    "base_delay": self.config.base_delay,
                    "max_delay": self.config.max_delay,
                    "strategy": self.config.strategy.value,
                    "quality_threshold": self.config.quality_threshold,
                    "health_check_interval": self.config.health_check_interval,
                    "jitter": self.config.jitter,
                },
                "stats": {
                    "total_attempts": self.stats.total_attempts,
                    "successful_reconnects": self.stats.successful_reconnects,
                    "failed_reconnects": self.stats.failed_reconnects,
                    "current_attempt": self.stats.current_attempt,
                    "last_reconnect_time": self.stats.last_reconnect_time,
                    "average_reconnect_time": self.stats.average_reconnect_time,
                    "consecutive_failures": self.stats.consecutive_failures,
                    "max_consecutive_failures": self.stats.max_consecutive_failures,
                },
                "success_rate": (self.stats.successful_reconnects / max(1, self.stats.total_attempts) * 100),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def reset_stats(self):
        """Сброс статистики"""
        try:
            self.stats = ReconnectStats()
            logger.info("Статистика переподключений сброшена")
        except Exception as e:
            logger.error(f"Ошибка сброса статистики: {e}")


# Пример использования
async def on_reconnect_start():
    print("🔄 Начало переподключения...")


async def on_reconnect_success():
    print("✅ Переподключение успешно!")


async def on_reconnect_failure():
    print("❌ Переподключение не удалось")


async def on_quality_change(quality: ConnectionQuality):
    print(f"📊 Качество соединения: {quality.value}")


async def main():
    """Основная функция для тестирования"""
    # Создаем конфигурацию
    config = ReconnectConfig(
        max_attempts=5,
        base_delay=2.0,
        max_delay=60.0,
        strategy=ReconnectStrategy.EXPONENTIAL,
        quality_threshold=0.6,
        health_check_interval=10.0,
        jitter=True,
    )

    # Создаем менеджер переподключения
    auto_reconnect = ALADDINAutoReconnect(config)

    print("=== АВТОМАТИЧЕСКОЕ ПЕРЕПОДКЛЮЧЕНИЕ ALADDIN VPN ===")

    # Устанавливаем callbacks
    auto_reconnect.set_callbacks(
        on_reconnect_start=on_reconnect_start,
        on_reconnect_success=on_reconnect_success,
        on_reconnect_failure=on_reconnect_failure,
        on_quality_change=on_quality_change,
    )

    # Запускаем
    await auto_reconnect.start()
    print("✅ Автоматическое переподключение запущено")

    # Устанавливаем ID соединения
    auto_reconnect.set_connection_id("test_connection_123")
    print("✅ ID соединения установлен")

    try:
        # Ждем некоторое время для демонстрации
        print("⏳ Мониторинг соединения в течение 30 секунд...")
        await asyncio.sleep(30)

        # Получаем статистику
        stats = auto_reconnect.get_stats()
        print("\n📊 Статистика переподключений:")
        print(f"  Включено: {stats['is_enabled']}")
        print(f"  Переподключение: {stats['is_reconnecting']}")
        print(f"  Качество: {stats['connection_quality']}")
        print(f"  Всего попыток: {stats['stats']['total_attempts']}")
        print(f"  Успешных: {stats['stats']['successful_reconnects']}")
        print(f"  Неудачных: {stats['stats']['failed_reconnects']}")
        print(f"  Процент успеха: {stats['success_rate']:.1f}%")
        print(f"  Среднее время: {stats['stats']['average_reconnect_time']:.1f} попыток")
        print(f"  Подряд неудач: {stats['stats']['consecutive_failures']}")

    finally:
        # Останавливаем
        await auto_reconnect.stop()
        print("✅ Автоматическое переподключение остановлено")


if __name__ == "__main__":
    asyncio.run(main())
