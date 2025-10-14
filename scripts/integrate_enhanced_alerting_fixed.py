#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленный скрипт интеграции Enhanced Alerting System в SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.safe_function_manager import SafeFunctionManager
from security.enhanced_alerting import EnhancedAlertingSystem
from core.base import SecurityLevel

def integrate_enhanced_alerting():
    """Интегрирует Enhanced Alerting System в SFM"""
    try:
        print("🔗 ИНТЕГРАЦИЯ 1/3: Enhanced Alerting System в SFM")
        print("=" * 60)
        
        # Создаем экземпляр SFM
        print("1. Создание экземпляра SafeFunctionManager...")
        sfm = SafeFunctionManager()
        print("✅ SafeFunctionManager создан")
        
        # Создаем экземпляр Enhanced Alerting System
        print("2. Создание экземпляра Enhanced Alerting System...")
        alerting_system = EnhancedAlertingSystem()
        print("✅ Enhanced Alerting System создан")
        
        # Регистрируем в SFM с правильными параметрами
        print("3. Регистрация в SafeFunctionManager...")
        success = sfm.register_function(
            function_id='enhanced_alerting_system',
            name='EnhancedAlertingSystem',
            description='Улучшенная система алертов для мониторинга безопасности',
            function_type='security',
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=True,
            handler=alerting_system
        )
        
        if success:
            print("✅ Enhanced Alerting System успешно интегрирован в SFM")
            print(f"📊 Новое количество функций в SFM: {len(sfm.functions)}")
            print(f"🔍 ID функции: enhanced_alerting_system")
            print(f"📝 Название: EnhancedAlertingSystem")
            print(f"📋 Описание: Улучшенная система алертов для мониторинга безопасности")
            print(f"🔒 Уровень безопасности: HIGH")
            print(f"⚡ Статус: enabled")
            print(f"🚨 Критический: True")
            
            # Проверяем работоспособность
            print("\n4. Проверка работоспособности...")
            if 'enhanced_alerting_system' in sfm.functions:
                func_info = sfm.functions['enhanced_alerting_system']
                instance = func_info['handler']
                print(f"✅ Экземпляр создан: {type(instance).__name__}")
                print(f"✅ Наследование от SecurityBase: {hasattr(instance, 'service_name')}")
                
                # Проверяем доступность методов
                methods = ['add_alert_rule', 'add_security_event', 'detect_threat']
                for method in methods:
                    if hasattr(instance, method):
                        print(f"✅ Метод {method}: ДОСТУПЕН")
                    else:
                        print(f"❌ Метод {method}: НЕ НАЙДЕН")
                
                print("\n🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
                return True
            else:
                print("❌ Функция не найдена в SFM после регистрации")
                return False
        else:
            print("❌ Ошибка регистрации функции")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка интеграции Enhanced Alerting System: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    integrate_enhanced_alerting()
