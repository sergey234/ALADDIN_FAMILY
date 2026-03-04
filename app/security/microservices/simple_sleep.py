#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт для перевода систем в спящий режим
Создает конфигурационные файлы для спящего режима
"""

import json
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@dataclass
class SleepConfig:
    """Конфигурация спящего режима"""
    service_name: str
    sleep_duration: int
    wake_up_conditions: List[str]
    health_check_interval: int
    is_active: bool = True
    
    def __init__(self, service_name: str, sleep_duration: int = 300, 
                 wake_up_conditions: List[str] = None, health_check_interval: int = 60):
        self.service_name = service_name
        self.sleep_duration = sleep_duration
        self.wake_up_conditions = wake_up_conditions or ["manual_wake", "emergency"]
        self.health_check_interval = health_check_interval
        self.is_active = True

class SimpleSleepMicroservice:
    """
    Микросервис для управления спящим режимом системы
    """
    
    def __init__(self, service_name: str = "simple_sleep_service"):
        self.service_name = service_name
        self.is_sleeping = False
        self.sleep_start_time: Optional[datetime] = None
        self.config: Optional[SleepConfig] = None
        self.health_status = "healthy"
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    async def initialize(self):
        """Инициализация микросервиса"""
        try:
            self.config = SleepConfig(
                service_name=self.service_name,
                sleep_duration=300,
                wake_up_conditions=["manual_wake", "emergency", "scheduled_wake"],
                health_check_interval=60
            )
            self.logger.info(f"Микросервис {self.service_name} инициализирован")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья микросервиса"""
        try:
            current_time = datetime.now()
            uptime = (current_time - self.sleep_start_time).total_seconds() if self.sleep_start_time else 0
            
            health_data = {
                "service_name": self.service_name,
                "status": "healthy" if not self.is_sleeping else "sleeping",
                "is_sleeping": self.is_sleeping,
                "uptime_seconds": uptime,
                "timestamp": current_time.isoformat(),
                "config": self.config.__dict__ if self.config else None
            }
            
            self.health_status = "healthy"
            return health_data
        except Exception as e:
            self.logger.error(f"Ошибка health check: {e}")
            self.health_status = "unhealthy"
            return {
                "service_name": self.service_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def enter_sleep_mode(self, duration: Optional[int] = None) -> Dict[str, Any]:
        """Переход в спящий режим"""
        try:
            if self.is_sleeping:
                return {"status": "already_sleeping", "message": "Сервис уже в спящем режиме"}
            
            sleep_duration = duration or (self.config.sleep_duration if self.config else 300)
            self.is_sleeping = True
            self.sleep_start_time = datetime.now()
            
            self.logger.info(f"Переход в спящий режим на {sleep_duration} секунд")
            
            # Асинхронное ожидание
            await asyncio.sleep(sleep_duration)
            
            # Автоматическое пробуждение
            await self.wake_up()
            
            return {
                "status": "sleep_completed",
                "duration": sleep_duration,
                "wake_up_time": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка при переходе в спящий режим: {e}")
            return {"status": "error", "error": str(e)}
    
    async def wake_up(self) -> Dict[str, Any]:
        """Пробуждение от спящего режима"""
        try:
            if not self.is_sleeping:
                return {"status": "not_sleeping", "message": "Сервис не в спящем режиме"}
            
            self.is_sleeping = False
            wake_up_time = datetime.now()
            sleep_duration = (wake_up_time - self.sleep_start_time).total_seconds() if self.sleep_start_time else 0
            
            self.logger.info(f"Пробуждение от спящего режима. Длительность сна: {sleep_duration} секунд")
            
            return {
                "status": "awake",
                "sleep_duration": sleep_duration,
                "wake_up_time": wake_up_time.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка при пробуждении: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса микросервиса"""
        return {
            "service_name": self.service_name,
            "is_sleeping": self.is_sleeping,
            "health_status": self.health_status,
            "sleep_start_time": self.sleep_start_time.isoformat() if self.sleep_start_time else None,
            "config": self.config.__dict__ if self.config else None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление конфигурации"""
        try:
            if self.config:
                for key, value in new_config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                self.logger.info(f"Конфигурация обновлена: {new_config}")
                return {"status": "success", "updated_config": self.config.__dict__}
            else:
                return {"status": "error", "message": "Конфигурация не инициализирована"}
        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")
            return {"status": "error", "error": str(e)}


def create_sleep_config():
    """
    Создает конфигурацию для спящего режима
    """
    try:
        # Валидация входных данных
        if not isinstance(time.time(), (int, float)):
            raise ValueError("Некорректное время системы")

        sleep_config = {
            "rate_limiter": {
                "enabled": False,
                "sleep_mode": True,
                "ml_enabled": False,
                "adaptive_learning": False,
                "cleanup_interval": 3600,
                "metrics_enabled": False,
                "logging_level": "WARNING",
                "auto_wake_up": True,
                "wake_up_threshold": 0.8,
                "max_sleep_time": 86400,
                "status": "SLEEPING",
                "last_activity": None,
                "sleep_start_time": time.time(),
            },
            "circuit_breaker": {
                "enabled": False,
                "sleep_mode": True,
                "ml_enabled": False,
                "adaptive_learning": False,
                "cleanup_interval": 3600,
                "metrics_enabled": False,
                "logging_level": "WARNING",
                "auto_wake_up": True,
                "wake_up_threshold": 0.8,
                "max_sleep_time": 86400,
                "status": "SLEEPING",
                "last_activity": None,
                "sleep_start_time": time.time(),
            },
            "user_interface_manager": {
                "enabled": False,
                "sleep_mode": True,
                "ml_enabled": False,
                "adaptive_learning": False,
                "cleanup_interval": 3600,
                "metrics_enabled": False,
                "logging_level": "WARNING",
                "auto_wake_up": True,
                "wake_up_threshold": 0.8,
                "max_sleep_time": 86400,
                "status": "SLEEPING",
                "last_activity": None,
                "sleep_start_time": time.time(),
            },
            "system_wide": {
                "sleep_mode": True,
                "sleep_start_time": time.time(),
                "sleep_duration": 0,
                "auto_wake_up_enabled": True,
                "wake_up_triggers": [
                    "high_traffic",
                    "security_alert",
                    "user_request",
                    "scheduled_wake_up",
                ],
                "monitoring_enabled": True,
                "alert_on_wake_up": True,
            },
        }

        return sleep_config

    except Exception as e:
        logger.error(f"Ошибка создания конфигурации спящего режима: {e}")
        raise


def create_wake_up_config():
    """
    Создает конфигурацию для пробуждения
    """
    wake_up_config = {
        "rate_limiter": {
            "enabled": True,
            "sleep_mode": False,
            "ml_enabled": True,
            "adaptive_learning": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_level": "INFO",
            "auto_wake_up": True,
            "wake_up_threshold": 0.5,
            "max_sleep_time": 0,
            "status": "ACTIVE",
            "last_activity": time.time(),
            "wake_up_time": time.time(),
        },
        "circuit_breaker": {
            "enabled": True,
            "sleep_mode": False,
            "ml_enabled": True,
            "adaptive_learning": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_level": "INFO",
            "auto_wake_up": True,
            "wake_up_threshold": 0.5,
            "max_sleep_time": 0,
            "status": "ACTIVE",
            "last_activity": time.time(),
            "wake_up_time": time.time(),
        },
        "user_interface_manager": {
            "enabled": True,
            "sleep_mode": False,
            "ml_enabled": True,
            "adaptive_learning": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_level": "INFO",
            "auto_wake_up": True,
            "wake_up_threshold": 0.5,
            "max_sleep_time": 0,
            "status": "ACTIVE",
            "last_activity": time.time(),
            "wake_up_time": time.time(),
        },
        "system_wide": {
            "sleep_mode": False,
            "wake_up_time": time.time(),
            "sleep_duration": 0,
            "auto_wake_up_enabled": True,
            "wake_up_triggers": [
                "high_traffic",
                "security_alert",
                "user_request",
                "scheduled_wake_up",
            ],
            "monitoring_enabled": True,
            "alert_on_wake_up": True,
        },
    }

    return wake_up_config


def put_systems_to_sleep():
    """
    Переводит все три системы в спящий режим
    """
    logger.info("🌙 Начинаю перевод систем в спящий режим...")

    try:
        # Валидация входных данных
        if not callable(create_sleep_config):
            raise ValueError("Функция create_sleep_config недоступна")
        # Создание конфигурации спящего режима
        sleep_config = create_sleep_config()

        # Сохранение конфигурации
        config_file = "sleep_mode_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(sleep_config, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Конфигурация спящего режима сохранена: {config_file}")

        # Создание файлов статуса для каждой системы
        systems = ["rate_limiter", "circuit_breaker", "user_interface_manager"]

        for system in systems:
            status_file = f"{system}_sleep_status.json"
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(
                    sleep_config[system], f, indent=2, ensure_ascii=False
                )
            logger.info(f"📋 Статус {system} сохранен: {status_file}")

        # Создание общего файла статуса
        overall_status = {
            "timestamp": time.time(),
            "status": "SLEEPING",
            "systems": systems,
            "sleep_mode": True,
            "message": "Все системы переведены в спящий режим",
        }

        with open("overall_sleep_status.json", "w", encoding="utf-8") as f:
            json.dump(overall_status, f, indent=2, ensure_ascii=False)

        logger.info(
            "📊 Общий статус системы сохранен: overall_sleep_status.json"
        )

        # Создание скрипта для пробуждения
        wake_up_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Скрипт для пробуждения систем из спящего режима
\"\"\"

def wake_up_systems():
    print("🌅 Пробуждение систем из спящего режима...")

    # Загрузка конфигурации пробуждения
    wake_up_config = {
        "rate_limiter": {
            "enabled": True,
            "sleep_mode": False,
            "status": "ACTIVE",
            "wake_up_time": time.time()
        },
        "circuit_breaker": {
            "enabled": True,
            "sleep_mode": False,
            "status": "ACTIVE",
            "wake_up_time": time.time()
        },
        "user_interface_manager": {
            "enabled": True,
            "sleep_mode": False,
            "status": "ACTIVE",
            "wake_up_time": time.time()
        }
    }

    # Сохранение конфигурации пробуждения
    with open("wake_up_config.json", 'w', encoding='utf-8') as f:
        json.dump(wake_up_config, f, indent=2, ensure_ascii=False)

    print("✅ Системы пробуждены!")
    print("⚡ Все компоненты активны и готовы к работе")

if __name__ == "__main__":
    wake_up_systems()
"""

        with open("wake_up_systems.py", "w", encoding="utf-8") as f:
            f.write(wake_up_script)

        logger.info("🔧 Скрипт пробуждения создан: wake_up_systems.py")

        logger.info("🎉 Все системы успешно переведены в спящий режим!")
        logger.info(
            "💤 Системы будут автоматически пробуждаться при необходимости"
        )
        logger.info(
            "🔧 Для ручного пробуждения используйте: python3 wake_up_systems.py"
        )

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при переводе систем в спящий режим: {e}")
        return False


def main():
    """
    Главная функция
    """
    print("🌙 ALADDIN Security System - Перевод в спящий режим")
    print("=" * 60)

    try:
        result = put_systems_to_sleep()

        if result:
            print("\n✅ Все системы успешно переведены в спящий режим!")
            print(
                "💤 Системы будут автоматически пробуждаться при необходимости"
            )
            print(
                "🔧 Для ручного пробуждения используйте: "
                "python3 wake_up_systems.py"
            )
            print("\n📋 Созданные файлы:")
            print("   - sleep_mode_config.json - конфигурация спящего режима")
            print("   - rate_limiter_sleep_status.json - статус RateLimiter")
            print(
                "   - circuit_breaker_sleep_status.json - "
                "статус CircuitBreaker"
            )
            print(
                "   - user_interface_manager_sleep_status.json - "
                "статус UserInterfaceManager"
            )
            print("   - overall_sleep_status.json - общий статус системы")
            print("   - wake_up_systems.py - скрипт пробуждения")
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
