#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода EmergencyResponseInterface в спящий режим
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
from security.ai_agents.emergency_response_interface import EmergencyResponseInterface

def put_emergency_response_to_sleep():
    """Перевести EmergencyResponseInterface в спящий режим"""
    try:
        print("🔄 Перевод EmergencyResponseInterface в спящий режим...")
        
        # Создаем менеджер функций
        manager = SafeFunctionManager()
        
        # Создаем экземпляр EmergencyResponseInterface
        interface = EmergencyResponseInterface("EmergencyResponseInterface")
        
        # Регистрируем функцию в менеджере
        function_id = "emergency_response_interface"
        success = manager.register_function(
            function_id=function_id,
            name="EmergencyResponseInterface",
            description="Интерфейс экстренного реагирования с AI-анализом",
            function_type="emergency",
            is_critical=True
        )
        
        if success:
            print(f"✅ EmergencyResponseInterface зарегистрирован: {function_id}")
            
            # Переводим в спящий режим (отключаем)
            sleep_success = manager.disable_function(function_id)
            if sleep_success:
                print("😴 EmergencyResponseInterface переведен в спящий режим")
                
                # Получаем статус
                status = manager.get_function_status(function_id)
                print(f"📊 Статус: {status}")
                
                return True
            else:
                print("❌ Ошибка перевода в спящий режим")
                return False
        else:
            print("❌ Ошибка регистрации EmergencyResponseInterface")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = put_emergency_response_to_sleep()
    if success:
        print("\n🎉 EmergencyResponseInterface успешно переведен в спящий режим!")
    else:
        print("\n💥 Ошибка при переводе в спящий режим!")