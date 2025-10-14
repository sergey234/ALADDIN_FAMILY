#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция расширенной системы алертов с SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.advanced_alerting_system import alerting_system
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel

def integrate_alerting_system():
    """Интеграция системы алертов"""
    print("🔗 Интеграция AdvancedAlertingSystem с SafeFunctionManager...")
    
    try:
        # Получаем SafeFunctionManager
        safe_manager = SafeFunctionManager()
        
        # Регистрируем систему алертов
        result = safe_manager.register_function(
            function_id="advanced_alerting_system",
            name="Advanced Alerting System",
            description="Расширенная система алертов безопасности",
            function_type="security",
            security_level=SecurityLevel.HIGH,
            auto_enable=True
        )
        
        if result:
            print("✅ AdvancedAlertingSystem успешно интегрирован")
            
            # Тестируем систему
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
            print("❌ Ошибка интеграции AdvancedAlertingSystem")
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