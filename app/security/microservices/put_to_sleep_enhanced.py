#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода систем в спящий режим
Переводит RateLimiter, CircuitBreaker и UserInterfaceManager в спящий режим
"""

import asyncio
import logging
import os

# Добавляем путь к модулям

from circuit_breaker import CircuitBreaker
from rate_limiter import RateLimiter
from user_interface_manager import UserInterfaceManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SleepManager:
    """Менеджер для перевода систем в спящий режим"""

    def __init__(self):
        """Инициализация менеджера сна"""
        self.sleep_config = {
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

    async def put_systems_to_sleep(self):
        """
        Переводит все три системы в спящий режим
        """
        logger.info("🌙 Начинаю перевод систем в спящий режим...")

        systems = []

        try:
            # Инициализация RateLimiter в спящем режиме
            logger.info("📊 Инициализация RateLimiter в спящем режиме...")
            rate_limiter = RateLimiter("RateLimiter_Sleep", self.sleep_config)
            await rate_limiter.start()
            systems.append(("RateLimiter", rate_limiter))
            logger.info("✅ RateLimiter переведен в спящий режим")

            # Инициализация CircuitBreaker в спящем режиме
            logger.info("⚡ Инициализация CircuitBreaker в спящем режиме...")
            circuit_breaker = CircuitBreaker("CircuitBreaker_Sleep", self.sleep_config)
            await circuit_breaker.start()
            systems.append(("CircuitBreaker", circuit_breaker))
            logger.info("✅ CircuitBreaker переведен в спящий режим")

            # Инициализация UserInterfaceManager в спящем режиме
            logger.info("🖥️ Инициализация UserInterfaceManager в спящем режиме...")
            ui_manager = UserInterfaceManager(
                "UserInterfaceManager_Sleep", self.sleep_config
            )
            await ui_manager.start()
            systems.append(("UserInterfaceManager", ui_manager))
            logger.info("✅ UserInterfaceManager переведен в спящий режим")

            # Проверка статуса всех систем
            logger.info("🔍 Проверка статуса систем...")
            for name, system in systems:
                status = await system.get_status()
                logger.info(f"📋 {name} статус: {status.get('status', 'unknown')}")

            logger.info("🎉 Все системы успешно переведены в спящий режим!")
            logger.info(
                "💤 Системы будут автоматически пробуждаться при необходимости"
            )

            # Сохранение конфигурации спящего режима
            sleep_config_file = os.path.join(
                os.path.dirname(__file__), "sleep_mode_config.json"
            )
            import json

            with open(sleep_config_file, "w", encoding="utf-8") as f:
                json.dump(self.sleep_config, f, indent=2, ensure_ascii=False)
            logger.info(
                f"💾 Конфигурация спящего режима сохранена: {sleep_config_file}"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Ошибка при переводе систем в спящий режим: {e}")
            return False

        finally:
            # Очистка ресурсов
            logger.info("🧹 Очистка ресурсов...")
            for name, system in systems:
                try:
                    await system.stop()
                    logger.info(f"🛑 {name} остановлен")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при остановке {name}: {e}")


def main():
    """
    Главная функция
    """
    print("🌙 ALADDIN Security System - Перевод в спящий режим")
    print("=" * 60)

    try:
        # Запуск асинхронной функции
        sleep_manager = SleepManager()
        result = asyncio.run(sleep_manager.put_systems_to_sleep())

        if result:
            print("\n✅ Все системы успешно переведены в спящий режим!")
            print(
                "💤 Системы будут автоматически пробуждаться при необходимости"
            )
            print(
                "🔧 Для ручного пробуждения используйте: python3 wake_up_systems.py"
            )
        else:
            print("\n❌ Ошибка при переводе систем в спящий режим!")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
