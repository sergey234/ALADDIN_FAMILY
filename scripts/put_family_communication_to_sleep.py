#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевода FamilyCommunicationHub в спящий режим
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
from security.ai_agents.family_communication_hub import FamilyCommunicationHub

def put_family_communication_to_sleep():
    """Перевести FamilyCommunicationHub в спящий режим"""
    try:
        print("🔄 Перевод FamilyCommunicationHub в спящий режим...")
        
        # Создаем менеджер функций
        manager = SafeFunctionManager()
        
        # Создаем экземпляр FamilyCommunicationHub
        hub = FamilyCommunicationHub("FamilyCommunicationHub")
        
        # Регистрируем функцию в менеджере
        function_id = "family_communication_hub"
        success = manager.register_function(
            function_id=function_id,
            name="FamilyCommunicationHub",
            description="Семейный коммуникационный центр с AI-анализом",
            function_type="family",
            is_critical=False
        )
        
        if success:
            print(f"✅ FamilyCommunicationHub зарегистрирован: {function_id}")
            
            # Переводим в спящий режим (отключаем)
            sleep_success = manager.disable_function(function_id)
            if sleep_success:
                print("😴 FamilyCommunicationHub переведен в спящий режим")
                
                # Получаем статус
                status = manager.get_function_status(function_id)
                print(f"📊 Статус: {status}")
                
                return True
            else:
                print("❌ Ошибка перевода в спящий режим")
                return False
        else:
            print("❌ Ошибка регистрации FamilyCommunicationHub")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = put_family_communication_to_sleep()
    if success:
        print("\n🎉 FamilyCommunicationHub успешно переведен в спящий режим!")
    else:
        print("\n💥 Ошибка при переводе в спящий режим!")