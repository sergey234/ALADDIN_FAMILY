#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование расширенной системы алертов ALADDIN
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.advanced_alerting_system import alerting_system

def test_alerting_system():
    """Тестирование системы алертов"""
    print("🧪 Тестирование AdvancedAlertingSystem...")
    
    # Тестовые сценарии
    test_scenarios = [
        {
            'name': 'Критическая угроза безопасности',
            'data': {
                'threat_level': 'critical',
                'attack_type': 'ddos',
                'source_ip': '192.168.1.100'
            }
        },
        {
            'name': 'Высокая загрузка CPU',
            'data': {
                'cpu_usage': 95,
                'memory_usage': 60,
                'disk_usage': 45
            }
        },
        {
            'name': 'Недостаток памяти',
            'data': {
                'cpu_usage': 50,
                'memory_usage': 90,
                'disk_usage': 30
            }
        },
        {
            'name': 'Системные ошибки',
            'data': {
                'error_count': 15,
                'error_types': ['database', 'network', 'auth'],
                'last_error': 'Connection timeout'
            }
        },
        {
            'name': 'Нарушение соответствия',
            'data': {
                'compliance_score': 75,
                'violations': ['data_retention', 'access_control'],
                'audit_date': '2025-09-08'
            }
        },
        {
            'name': 'Подозрительная активность',
            'data': {
                'suspicious_activity': True,
                'user_id': 'user123',
                'activity_type': 'unusual_login_time',
                'location': 'Unknown'
            }
        },
        {
            'name': 'Ошибка резервного копирования',
            'data': {
                'backup_status': 'failed',
                'backup_type': 'full',
                'error_message': 'Disk space insufficient'
            }
        },
        {
            'name': 'Ошибка интеграции',
            'data': {
                'integration_status': 'failed',
                'service': 'external_api',
                'error_code': 500
            }
        }
    ]
    
    total_alerts = 0
    
    for scenario in test_scenarios:
        print(f"\n🔍 Тест: {scenario['name']}")
        print(f"📊 Данные: {json.dumps(scenario['data'], indent=2, ensure_ascii=False)}")
        
        # Проверяем алерты
        alerts = alerting_system.check_alerts(scenario['data'])
        
        if alerts:
            print(f"🚨 Сгенерировано алертов: {len(alerts)}")
            for alert in alerts:
                print(f"  - {alert.title} ({alert.severity.value})")
                print(f"    Правило: {alert.rule_name}")
                print(f"    Время: {alert.timestamp.strftime('%H:%M:%S')}")
            total_alerts += len(alerts)
        else:
            print("✅ Алертов не сгенерировано")
        
        time.sleep(0.5)  # Небольшая пауза
    
    print(f"\n📊 Итого сгенерировано алертов: {total_alerts}")
    
    # Получаем статистику
    stats = alerting_system.get_alert_statistics()
    print(f"\n📈 Статистика системы алертов:")
    print(f"  - Всего алертов: {stats['total_alerts']}")
    print(f"  - Активных: {stats['active_alerts']}")
    print(f"  - Разрешенных: {stats['resolved_alerts']}")
    print(f"  - По типам: {stats['type_statistics']}")
    print(f"  - По критичности: {stats['severity_statistics']}")
    
    return total_alerts > 0

def test_alerts_api():
    """Тестирование API алертов"""
    print("\n🌐 Тестирование Alerts API...")
    
    api_url = "http://localhost:5003"
    
    try:
        # Проверка здоровья API
        response = requests.get(f"{api_url}/api/alerts/health", timeout=5)
        if response.status_code == 200:
            print("✅ API алертов доступен")
        else:
            print(f"❌ API недоступен: {response.status_code}")
            return False
        
        # Получение активных алертов
        response = requests.get(f"{api_url}/api/alerts/active", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Активных алертов: {data.get('count', 0)}")
        else:
            print(f"❌ Ошибка получения активных алертов: {response.status_code}")
        
        # Получение статистики
        response = requests.get(f"{api_url}/api/alerts/statistics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"📈 Статистика: {stats.get('total_alerts', 0)} всего, {stats.get('active_alerts', 0)} активных")
        else:
            print(f"❌ Ошибка получения статистики: {response.status_code}")
        
        # Получение правил
        response = requests.get(f"{api_url}/api/alerts/rules", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Правил алертов: {data.get('count', 0)}")
        else:
            print(f"❌ Ошибка получения правил: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ API алертов недоступен (сервер не запущен)")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования AdvancedAlertingSystem")
    print("=" * 50)
    
    # Тест системы алертов
    system_success = test_alerting_system()
    
    # Тест API
    api_success = test_alerts_api()
    
    print("\n" + "=" * 50)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"  Система алертов: {'✅ Успешно' if system_success else '❌ Ошибка'}")
    print(f"  API алертов: {'✅ Успешно' if api_success else '❌ Ошибка'}")
    
    if system_success and api_success:
        print("\n🎉 Все тесты пройдены успешно!")
        return True
    else:
        print("\n💥 Некоторые тесты не прошли!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)