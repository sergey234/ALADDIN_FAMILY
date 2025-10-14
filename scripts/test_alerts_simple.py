#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое тестирование системы алертов ALADDIN
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.advanced_alerting_system import alerting_system

def test_alerts_simple():
    """Простое тестирование системы алертов"""
    print("🧪 Простое тестирование AdvancedAlertingSystem...")
    
    # Тестовые данные
    test_data = {
        'threat_level': 'critical',
        'cpu_usage': 95,
        'memory_usage': 90,
        'error_count': 15,
        'compliance_score': 75,
        'suspicious_activity': True,
        'backup_status': 'failed',
        'integration_status': 'failed'
    }
    
    print(f"📊 Тестовые данные: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    # Проверяем алерты
    alerts = alerting_system.check_alerts(test_data)
    
    print(f"\n🚨 Сгенерировано алертов: {len(alerts)}")
    
    for i, alert in enumerate(alerts, 1):
        print(f"\n{i}. {alert.title}")
        print(f"   Тип: {alert.alert_type.value}")
        print(f"   Критичность: {alert.severity.value}")
        print(f"   Правило: {alert.rule_name}")
        print(f"   Время: {alert.timestamp.strftime('%H:%M:%S')}")
        print(f"   Сообщение: {alert.message[:100]}...")
    
    # Получаем статистику
    stats = alerting_system.get_alert_statistics()
    print(f"\n📈 Статистика:")
    print(f"  - Всего алертов: {stats['total_alerts']}")
    print(f"  - Активных: {stats['active_alerts']}")
    print(f"  - Разрешенных: {stats['resolved_alerts']}")
    print(f"  - По типам: {stats['type_statistics']}")
    print(f"  - По критичности: {stats['severity_statistics']}")
    
    # Получаем активные алерты
    active_alerts = alerting_system.get_active_alerts()
    print(f"\n🔴 Активные алерты: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f"  - {alert.title} ({alert.severity.value})")
    
    # Тестируем разрешение алерта
    if active_alerts:
        first_alert = active_alerts[0]
        print(f"\n🔧 Разрешаем алерт: {first_alert.id}")
        success = alerting_system.resolve_alert(first_alert.id)
        if success:
            print("✅ Алерт успешно разрешен")
        else:
            print("❌ Ошибка разрешения алерта")
    
    # Финальная статистика
    final_stats = alerting_system.get_alert_statistics()
    print(f"\n📊 Финальная статистика:")
    print(f"  - Всего алертов: {final_stats['total_alerts']}")
    print(f"  - Активных: {final_stats['active_alerts']}")
    print(f"  - Разрешенных: {final_stats['resolved_alerts']}")
    
    return len(alerts) > 0

def main():
    """Основная функция"""
    print("🚀 Запуск простого тестирования системы алертов")
    print("=" * 60)
    
    success = test_alerts_simple()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Тестирование завершено успешно!")
        print("✅ Система алертов работает корректно")
    else:
        print("💥 Тестирование не прошло!")
        print("❌ Система алертов не работает")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)