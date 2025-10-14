#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода систем в спящий режим
Переводит RateLimiter, CircuitBreaker и UserInterfaceManager в спящий режим
"""

import asyncio
import logging
import os
import sys

# Добавляем путь к модулям
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

from circuit_breaker import CircuitBreaker  # noqa: E402
from rate_limiter import RateLimiter  # noqa: E402
from user_interface_manager import UserInterfaceManager  # noqa: E402

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def put_systems_to_sleep():
    """
    Переводит все три системы в спящий режим
    """
    logger.info("🌙 Начинаю перевод систем в спящий режим...")

    # Конфигурация для спящего режима
    sleep_config = {
        "redis_url": "redis://localhost:6379/0",
        "database_url": "sqlite:///sleep_mode.db",
        "ml_enabled": False,  # Отключаем ML для экономии ресурсов
        "adaptive_learning": False,  # Отключаем адаптивное обучение
        "cleanup_interval": 3600,  # Увеличиваем интервал очистки
        "metrics_enabled": False,  # Отключаем метрики
        "logging_enabled": True,  # Оставляем только критичные логи
        "sleep_mode": True,  # Включаем спящий режим
        "auto_wake_up": True,  # Автоматическое пробуждение при необходимости
        "wake_up_threshold": 0.8,  # Порог для пробуждения
        "max_sleep_time": 86400,  # Максимальное время сна (24 часа)
    }

    systems = []

    try:
        # Инициализируем RateLimiter в спящем режиме
        logger.info("⏳ Инициализация RateLimiter в спящем режиме...")
        rate_limiter = RateLimiter(
            redis_url=sleep_config["redis_url"],
            max_requests=10,  # Минимальные лимиты
            window_size=60,
            sleep_mode=True,
        )
        systems.append(("RateLimiter", rate_limiter))
        logger.info("✅ RateLimiter инициализирован в спящем режиме")

        # Инициализируем CircuitBreaker в спящем режиме
        logger.info("⏳ Инициализация CircuitBreaker в спящем режиме...")
        circuit_breaker = CircuitBreaker(
            redis_url=sleep_config["redis_url"],
            failure_threshold=5,
            recovery_timeout=30,
            sleep_mode=True,
        )
        systems.append(("CircuitBreaker", circuit_breaker))
        logger.info("✅ CircuitBreaker инициализирован в спящем режиме")

        # Инициализируем UserInterfaceManager в спящем режиме
        logger.info("⏳ Инициализация UserInterfaceManager в спящем режиме...")
        ui_manager = UserInterfaceManager(
            database_url=sleep_config["database_url"],
            sleep_mode=True,
            ml_enabled=sleep_config["ml_enabled"],
            adaptive_learning=sleep_config["adaptive_learning"],
        )
        systems.append(("UserInterfaceManager", ui_manager))
        logger.info("✅ UserInterfaceManager инициализирован в спящем режиме")

        # Переводим все системы в спящий режим
        logger.info("😴 Перевод всех систем в спящий режим...")
        for name, system in systems:
            try:
                if hasattr(system, "sleep"):
                    await system.sleep()
                    logger.info(f"✅ {name} переведен в спящий режим")
                else:
                    logger.warning(f"⚠️ {name} не поддерживает спящий режим")
            except Exception as e:
                logger.error(
                    f"❌ Ошибка при переводе {name} в спящий режим: {e}"
                )

        # Настраиваем автоматическое пробуждение
        if sleep_config["auto_wake_up"]:
            logger.info("🔔 Настройка автоматического пробуждения...")
            for name, system in systems:
                try:
                    if hasattr(system, "set_auto_wake_up"):
                        await system.set_auto_wake_up(
                            threshold=sleep_config["wake_up_threshold"],
                            max_sleep_time=sleep_config["max_sleep_time"],
                        )
                        logger.info(
                            f"✅ {name} настроен на автоматическое пробуждение"
                        )
                except Exception as e:
                    logger.error(
                        f"❌ Ошибка при настройке автопробуждения для {name}: "
                        f"{e}"
                    )

        logger.info("🎉 Все системы успешно переведены в спящий режим!")
        logger.info(
            "💤 Системы будут автоматически просыпаться при необходимости"
        )

        # Показываем статус систем
        logger.info("📊 Статус систем:")
        for name, system in systems:
            try:
                if hasattr(system, "get_status"):
                    status = await system.get_status()
                    logger.info(f"  {name}: {status}")
                else:
                    logger.info(f"  {name}: Спящий режим активирован")
            except Exception as e:
                logger.error(f"  {name}: Ошибка получения статуса - {e}")

    except Exception as e:
        logger.error(
            f"❌ Критическая ошибка при переводе систем в спящий режим: {e}"
        )
        raise


async def main():
    """
    Основная функция
    """
    try:
        await put_systems_to_sleep()
        logger.info("✅ Скрипт завершен успешно")
    except Exception as e:
        logger.error(f"❌ Скрипт завершен с ошибкой: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
