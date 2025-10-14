#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода NotificationBot в спящий режим
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
from security.ai_agents.notification_bot import NotificationBot

def put_notification_bot_to_sleep():
    """Перевести NotificationBot в спящий режим"""
    try:
        print("🔄 Перевод NotificationBot в спящий режим...")
        
        # Создаем менеджер функций
        manager = SafeFunctionManager()
        
        # Создаем экземпляр NotificationBot
        bot = NotificationBot("NotificationBot")
        
        # Регистрируем функцию в менеджере
        function_id = "notification_bot"
        success = manager.register_function(
            function_id=function_id,
            name="NotificationBot",
            description="Бот уведомлений с AI-анализом и персонализацией",
            function_type="notification",
            is_critical=False
        )
        
        if success:
            print(f"✅ NotificationBot зарегистрирован: {function_id}")
            
            # Переводим в спящий режим (отключаем)
            sleep_success = manager.disable_function(function_id)
            if sleep_success:
                print("😴 NotificationBot переведен в спящий режим")
                
                # Получаем статус
                status = manager.get_function_status(function_id)
                print(f"📊 Статус: {status}")
                
                return True
            else:
                print("❌ Ошибка перевода в спящий режим")
                return False
        else:
            print("❌ Ошибка регистрации NotificationBot")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = put_notification_bot_to_sleep()
    if success:
        print("\n🎉 NotificationBot успешно переведен в спящий режим!")
    else:
        print("\n💥 Ошибка при переводе в спящий режим!")