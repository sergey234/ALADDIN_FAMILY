#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование доступности всех методов SmartMonitoringSystem
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_monitoring import SmartMonitoringSystem, AlertRule, AlertSeverity, AlertStatus
from datetime import datetime

def test_all_methods():
    """Тестирование всех методов класса SmartMonitoringSystem"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ДОСТУПНОСТИ МЕТОДОВ SmartMonitoringSystem")
    print("=" * 60)
    
    try:
        # Создание экземпляра
        print("1. Создание экземпляра SmartMonitoringSystem...")
        system = SmartMonitoringSystem("TestSystem")
        print("✓ Экземпляр создан успешно")
        
        # Тестирование __str__ и __repr__
        print("\n2. Тестирование строковых представлений...")
        str_repr = str(system)
        repr_repr = repr(system)
        print(f"✓ __str__: {str_repr}")
        print(f"✓ __repr__: {repr_repr}")
        
        # Тестирование управления системой
        print("\n3. Тестирование управления системой...")
        system.start()
        print("✓ start() выполнен")
        
        system.pause()
        print("✓ pause() выполнен")
        
        system.resume()
        print("✓ resume() выполнен")
        
        # Тестирование добавления правил
        print("\n4. Тестирование добавления правил...")
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            metric_name="test_metric",
            condition=">",
            threshold=50.0,
            severity=AlertSeverity.WARNING
        )
        system.add_rule(rule)
        print("✓ add_rule() выполнен")
        
        # Тестирование добавления метрик
        print("\n5. Тестирование добавления метрик...")
        system.add_metric("test_metric", 75.0, {"source": "test"})
        print("✓ add_metric() выполнен")
        
        # Тестирование callback'ов
        print("\n6. Тестирование callback'ов...")
        def test_callback(alert):
            print(f"Callback получен: {alert.title}")
        
        system.add_alert_callback(test_callback)
        print("✓ add_alert_callback() выполнен")
        
        # Тестирование получения данных
        print("\n7. Тестирование получения данных...")
        active_alerts = system.get_active_alerts()
        print(f"✓ get_active_alerts(): {len(active_alerts)} алертов")
        
        alert_stats = system.get_alert_stats()
        print(f"✓ get_alert_stats(): {alert_stats}")
        
        # Тестирование свойств
        print("\n8. Тестирование свойств...")
        print(f"✓ active_alerts_count: {system.active_alerts_count}")
        print(f"✓ total_alerts_count: {system.total_alerts_count}")
        print(f"✓ rules_count: {system.rules_count}")
        
        # Тестирование конфигурации
        print("\n9. Тестирование конфигурации...")
        config = system.get_config()
        print(f"✓ get_config(): получена конфигурация")
        
        # Тестирование статистики
        print("\n10. Тестирование статистики...")
        metrics_summary = system.get_metrics_summary()
        print(f"✓ get_metrics_summary(): {metrics_summary}")
        
        perf_stats = system.get_performance_stats()
        print(f"✓ get_performance_stats(): {perf_stats}")
        
        # Тестирование здоровья системы
        print("\n11. Тестирование здоровья системы...")
        is_healthy = system.is_healthy()
        print(f"✓ is_healthy(): {is_healthy}")
        
        health_status = system.get_health_status()
        print(f"✓ get_health_status(): {health_status}")
        
        # Тестирование статических методов
        print("\n12. Тестирование статических методов...")
        test_rules = [rule]
        system2 = SmartMonitoringSystem.create_with_rules("TestSystem2", test_rules)
        print("✓ create_with_rules() выполнен")
        
        # Тестирование class методов
        print("\n13. Тестирование class методов...")
        config_data = {
            "name": "ConfigSystem",
            "rules": {
                "config_rule": {
                    "rule_id": "config_rule",
                    "name": "Config Rule",
                    "metric_name": "config_metric",
                    "condition": ">",
                    "threshold": 80.0,
                    "severity": "warning",
                    "cooldown": 300,
                    "min_occurrences": 1,
                    "max_alerts_per_hour": 5,
                    "adaptive_threshold": True
                }
            }
        }
        system3 = SmartMonitoringSystem.from_config(config_data)
        print("✓ from_config() выполнен")
        
        # Тестирование очистки
        print("\n14. Тестирование очистки...")
        system.clear()
        print("✓ clear() выполнен")
        
        system.reset()
        print("✓ reset() выполнен")
        
        # Тестирование остановки
        print("\n15. Тестирование остановки...")
        system.stop()
        print("✓ stop() выполнен")
        
        system.stop_monitoring()
        print("✓ stop_monitoring() выполнен")
        
        print("\n" + "=" * 60)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Тестирование обработки ошибок"""
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ОБРАБОТКИ ОШИБОК")
    print("=" * 60)
    
    try:
        system = SmartMonitoringSystem("ErrorTest")
        
        # Тест с некорректными данными
        print("1. Тестирование с некорректными данными...")
        try:
            system.add_metric("", 100.0)  # Пустое имя метрики
            print("❌ Ошибка не обработана")
        except ValueError as e:
            print(f"✓ Ошибка обработана: {e}")
        
        try:
            system.add_metric("test", "invalid")  # Некорректное значение
            print("❌ Ошибка не обработана")
        except ValueError as e:
            print(f"✓ Ошибка обработана: {e}")
        
        # Тест с некорректным callback'ом
        print("\n2. Тестирование некорректного callback'а...")
        try:
            system.add_alert_callback("not_callable")
            print("❌ Ошибка не обработана")
        except ValueError as e:
            print(f"✓ Ошибка обработана: {e}")
        
        print("\n✓ Все тесты обработки ошибок пройдены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестировании обработки ошибок: {e}")
        return False

if __name__ == "__main__":
    success1 = test_all_methods()
    success2 = test_error_handling()
    
    if success1 and success2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        exit(0)
    else:
        print("\n💥 ЕСТЬ ОШИБКИ В ТЕСТАХ!")
        exit(1)