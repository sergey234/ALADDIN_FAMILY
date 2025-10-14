#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая интеграция системы алертов с SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.advanced_alerting_system import alerting_system
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel

def integrate_alerting_system():
    """Простая интеграция системы алертов"""
    print("🔗 Простая интеграция AdvancedAlertingSystem с SafeFunctionManager...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Регистрируем систему алертов БЕЗ auto_enable
        result = safe_manager.register_function(
            function_id="advanced_alerting_system",
            name="Advanced Alerting System",
            description="Расширенная система алертов безопасности",
            function_type="security",
            security_level=SecurityLevel.HIGH,
            auto_enable=False  # Отключаем автоматическое включение
        )
        
        if result:
            print("✅ AdvancedAlertingSystem успешно зарегистрирован")
            
            # Проверяем статус
            function_status = safe_manager.get_function_status("advanced_alerting_system")
            
            if function_status:
                print(f"📊 Статус функции: {function_status.get('status', 'unknown')}")
                print(f"🔒 Уровень безопасности: {function_status.get('security_level', 'unknown')}")
                print(f"📝 Описание: {function_status.get('description', 'unknown')}")
                
                # Включаем функцию вручную
                enable_result = safe_manager.enable_function("advanced_alerting_system")
                if enable_result:
                    print("✅ Функция успешно включена")
                else:
                    print("❌ Ошибка включения функции")
            else:
                print("❌ Функция не найдена")
            
            # Тестируем систему алертов
            test_data = {
                'threat_level': 'critical',
                'cpu_usage': 95,
                'memory_usage': 90,
                'error_count': 15
            }
            
            alerts = alerting_system.check_alerts(test_data)
            print(f"🧪 Тест: сгенерировано {len(alerts)} алертов")
            
            # Получаем статистику
            stats = alerting_system.get_alert_statistics()
            print(f"📊 Статистика алертов: {stats['total_alerts']} всего, {stats['active_alerts']} активных")
            
            return True
        else:
            print("❌ Ошибка регистрации AdvancedAlertingSystem")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

if __name__ == '__main__':
    success = integrate_alerting_system()
    if success:
        print("🎉 Интеграция завершена успешно!")
    else:
        print("💥 Интеграция не удалась!")
        sys.exit(1)