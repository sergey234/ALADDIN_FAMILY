#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция NotificationBotMain в SafeFunctionManager
Интеграция основного бота уведомлений в систему SFM
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from security.ai_agents.notification_bot_main import NotificationBotMain, Notification, NotificationChannel, NotificationPriority
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_notification_bot_main():
    """Тестирование NotificationBotMain"""
    try:
        logger.info("🚀 Тестирование NotificationBotMain...")
        
        # Создание бота
        bot = NotificationBotMain()
        
        # Тест создания уведомления
        logger.info("📱 Тестирование создания уведомления...")
        notification = Notification(
            id="test_001",
            user_id="user_123",
            title="Тестовое уведомление",
            message="Это тестовое уведомление от NotificationBotMain",
            channel=NotificationChannel.PUSH,
            priority=NotificationPriority.HIGH,
            created_at=datetime.now()
        )
        
        # Тест отправки уведомления
        logger.info("📤 Тестирование отправки уведомления...")
        success = bot.send_notification(notification)
        logger.info(f"✅ Результат отправки: {success}")
        
        # Тест получения статуса
        logger.info("📊 Тестирование получения статуса...")
        status = await bot.get_status()
        logger.info(f"✅ Статус бота: {status}")
        
        logger.info("✅ NotificationBotMain успешно протестирован!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования NotificationBotMain: {e}")
        return False


def integrate_with_safe_function_manager():
    """Интеграция с SafeFunctionManager"""
    try:
        logger.info("🔗 Интеграция NotificationBotMain с SafeFunctionManager...")
        
        # Создание SFM
        sfm = SafeFunctionManager()
        
        # Регистрация NotificationBotMain
        logger.info("📝 Регистрация NotificationBotMain...")
        success = sfm.register_function(
            function_id="notification_bot_main",
            name="NotificationBotMain",
            description="Основной бот уведомлений с поддержкой 8 каналов",
            function_type="ai_agent",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=True
        )
        
        if success:
            logger.info("✅ NotificationBotMain успешно зарегистрирован!")
            
            # Создание обработчика
            def notification_bot_main_handler(*args, **kwargs):
                """Обработчик для NotificationBotMain"""
                try:
                    from security.ai_agents.notification_bot_main import NotificationBotMain
                    bot = NotificationBotMain()
                    return {
                        'status': 'success',
                        'function_id': 'notification_bot_main',
                        'handler_name': 'NotificationBotMain',
                        'message': 'NotificationBotMain успешно инициализирован',
                        'bot': bot
                    }
                except Exception as e:
                    return {
                        'status': 'error',
                        'function_id': 'notification_bot_main',
                        'handler_name': 'NotificationBotMain',
                        'message': f'Ошибка инициализации NotificationBotMain: {e}'
                    }
            
            # Регистрация обработчика
            sfm.register_function_handler('notification_bot_main', notification_bot_main_handler)
            logger.info("✅ Обработчик NotificationBotMain зарегистрирован!")
            
            # Включение функции
            sfm.enable_function('notification_bot_main')
            logger.info("✅ NotificationBotMain включен!")
            
            # Сохранение в реестр
            sfm._save_functions()
            logger.info("✅ Функции сохранены в реестр!")
            
            return True
        else:
            logger.error("❌ Ошибка регистрации NotificationBotMain")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка интеграции с SafeFunctionManager: {e}")
        return False


def verify_integration():
    """Проверка интеграции"""
    try:
        logger.info("🔍 Проверка интеграции NotificationBotMain...")
        
        # Создание SFM
        sfm = SafeFunctionManager()
        
        # Проверка регистрации
        if 'notification_bot_main' in sfm.functions:
            logger.info("✅ NotificationBotMain найден в реестре SFM!")
            
            # Проверка статуса
            status = sfm.get_function_status('notification_bot_main')
            logger.info(f"📊 Статус: {status}")
            
            # Проверка обработчика
            if 'notification_bot_main' in sfm.function_handlers:
                logger.info("✅ Обработчик NotificationBotMain найден!")
                
                # Тест выполнения
                result = sfm.execute_function('notification_bot_main')
                logger.info(f"✅ Результат выполнения: {result}")
                
                return True
            else:
                logger.error("❌ Обработчик NotificationBotMain не найден!")
                return False
        else:
            logger.error("❌ NotificationBotMain не найден в реестре SFM!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка проверки интеграции: {e}")
        return False


async def main():
    """Основная функция"""
    try:
        logger.info("🚀 ИНТЕГРАЦИЯ NOTIFICATIONBOTMAIN В SFM")
        logger.info("=" * 60)
        
        # Тестирование
        logger.info("1️⃣ Тестирование NotificationBotMain...")
        test_success = await test_notification_bot_main()
        
        if test_success:
            # Интеграция
            logger.info("2️⃣ Интеграция с SafeFunctionManager...")
            integration_success = integrate_with_safe_function_manager()
            
            if integration_success:
                # Проверка
                logger.info("3️⃣ Проверка интеграции...")
                verify_success = verify_integration()
                
                if verify_success:
                    logger.info("🎉 NotificationBotMain успешно интегрирован в SFM!")
                    return True
                else:
                    logger.error("❌ Ошибка проверки интеграции")
                    return False
            else:
                logger.error("❌ Ошибка интеграции с SFM")
                return False
        else:
            logger.error("❌ Ошибка тестирования")
            return False
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return False


if __name__ == "__main__":
    # Запуск интеграции
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("✅ NotificationBotMain интегрирован в SFM")
        print("✅ Функция зарегистрирована и включена")
        print("✅ Обработчик настроен")
        print("✅ Реестр обновлен")
    else:
        print("\n❌ ИНТЕГРАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ!")
        print("❌ Проверьте логи для деталей")
    
    sys.exit(0 if success else 1)