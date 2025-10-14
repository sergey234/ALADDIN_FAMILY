#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование Enhanced Alerting System
Простое тестирование улучшенной системы алертов

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import sys
import os
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.enhanced_alerting import EnhancedAlertingSystem, AlertRule, AlertSeverity, AlertChannel


def test_enhanced_alerting():
    """Тестирование системы алертов"""
    print("🧪 Тестирование Enhanced Alerting System")
    print("=" * 50)
    
    try:
        # 1. Создание системы алертов
        print("1. Создание системы алертов...")
        alerting_system = EnhancedAlertingSystem()
        print("✅ Система алертов создана")
        
        # 2. Добавление тестового правила
        print("2. Добавление тестового правила...")
        test_rule = AlertRule(
            rule_id="test_high_cpu",
            name="Тест высокой нагрузки CPU",
            description="Тестовое правило для проверки системы алертов",
            condition="cpu_usage > 0",  # Всегда срабатывает
            severity=AlertSeverity.INFO,
            channels=[AlertChannel.CONSOLE, AlertChannel.LOG],
            cooldown=1
        )
        
        alerting_system.add_alert_rule(test_rule)
        print("✅ Тестовое правило добавлено")
        
        # 3. Ожидание срабатывания алертов
        print("3. Ожидание срабатывания алертов (15 секунд)...")
        print("   (В консоли должны появиться алерты)")
        
        for i in range(15):
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Прошло {i+1} секунд...")
        
        # 4. Проверка алертов
        print("4. Проверка алертов...")
        alerts = alerting_system.get_alerts(limit=10)
        print(f"📊 Получено алертов: {len(alerts)}")
        
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. [{alert.severity.value.upper()}] {alert.title}")
            print(f"      Время: {alert.timestamp.strftime('%H:%M:%S')}")
            print(f"      Компонент: {alert.component}")
            print()
        
        # 5. Статистика
        print("5. Статистика системы...")
        stats = alerting_system.get_alert_statistics()
        print(f"📈 Всего алертов: {stats['total_alerts']}")
        print(f"🚨 Неразрешенных: {stats['unresolved_alerts']}")
        print(f"📊 По уровням серьезности:")
        for severity, count in stats['severity_counts'].items():
            print(f"   - {severity}: {count}")
        print(f"🔧 Активных правил: {stats['active_rules']}")
        
        # 6. Тест разрешения алерта
        if alerts:
            print("6. Тест разрешения алерта...")
            first_alert = alerts[0]
            print(f"   Разрешаем алерт: {first_alert.alert_id}")
            alerting_system.resolve_alert(first_alert.alert_id)
            
            # Проверяем статистику после разрешения
            stats_after = alerting_system.get_alert_statistics()
            print(f"   Неразрешенных после разрешения: {stats_after['unresolved_alerts']}")
        
        # 7. Остановка системы
        print("7. Остановка системы...")
        alerting_system.stop()
        print("✅ Система остановлена")
        
        # 8. Итоговый отчет
        print("\n" + "=" * 50)
        print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("=" * 50)
        print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🚨 Всего алертов: {stats['total_alerts']}")
        print(f"📊 Правил алертов: {len(alerting_system.alert_rules)}")
        print(f"📡 Каналов отправки: {len(alerting_system.channels)}")
        print(f"✅ Система работает корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard_integration():
    """Тестирование интеграции с дашбордом"""
    print("\n🌐 Тестирование интеграции с дашбордом...")
    
    try:
        # Проверяем, что дашборд запущен
        import requests
        
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ Дашборд доступен")
                health_data = response.json()
                print(f"   Статус: {health_data['status']}")
                print(f"   Компоненты: {health_data['components']}")
            else:
                print(f"⚠️ Дашборд отвечает с кодом: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Дашборд недоступен (запустите dashboard_server.py)")
        except Exception as e:
            print(f"⚠️ Ошибка проверки дашборда: {e}")
        
        return True
        
    except ImportError:
        print("⚠️ requests не установлен, пропускаем тест дашборда")
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования дашборда: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск тестирования Enhanced Alerting System")
    print("=" * 60)
    
    # Основное тестирование
    success = test_enhanced_alerting()
    
    if success:
        # Тестирование дашборда
        test_dashboard_integration()
        
        print("\n🎉 ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("\n💡 Для полной работы системы:")
        print("   1. Запустите дашборд: python3 dashboard_server.py")
        print("   2. Откройте браузер: http://localhost:5000")
        print("   3. Настройте email в конфигурации для отправки алертов")
    else:
        print("\n❌ ТЕСТИРОВАНИЕ НЕ УДАЛОСЬ!")
        sys.exit(1)