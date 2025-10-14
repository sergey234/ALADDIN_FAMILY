#!/usr/bin/env python3
"""
Тестирование всех модулей соответствия 152-ФЗ для ALADDIN VPN
Проверяет работоспособность всех компонентов системы соответствия
"""

import sys
import os
import logging
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compliance.integration import compliance_integration
from compliance.russia_compliance import RussiaComplianceManager
from compliance.data_localization import DataLocalizationManager
from compliance.no_logs_policy import NoLogsPolicyManager, LogLevel, LogType

# Настройка логирования
import logging as std_logging
std_logging.basicConfig(
    level=std_logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = std_logging.getLogger(__name__)

def test_russia_compliance():
    """Тестирование модуля соответствия российскому законодательству"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ СООТВЕТСТВИЯ 152-ФЗ")
    print("="*60)
    
    try:
        compliance_manager = RussiaComplianceManager()
        result = compliance_manager.run_full_compliance_check()
        
        print(f"✅ Общее соответствие: {result['compliance_percentage']:.1f}%")
        print(f"✅ Статус: {'СООТВЕТСТВУЕТ' if result['is_compliant'] else 'НЕ СООТВЕТСТВУЕТ'}")
        print(f"✅ Проверок выполнено: {result['total_checks']}")
        print(f"✅ Успешных: {result['compliant_checks']}")
        print(f"✅ Неуспешных: {result['non_compliant_checks']}")
        print(f"✅ Ошибок: {result['error_checks']}")
        
        print("\n📋 ДЕТАЛИ ПРОВЕРОК:")
        for check in result['checks']:
            status_icon = "✅" if check['status'] == 'compliant' else "❌"
            print(f"  {status_icon} {check['check_name']}: {check['message']}")
        
        return result['is_compliant']
        
    except Exception as e:
        print(f"❌ Ошибка тестирования соответствия 152-ФЗ: {e}")
        return False

def test_data_localization():
    """Тестирование модуля локализации данных"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ ЛОКАЛИЗАЦИИ ДАННЫХ")
    print("="*60)
    
    try:
        localization_manager = DataLocalizationManager()
        result = localization_manager.check_data_localization()
        
        print(f"✅ Соответствие: {result['compliance_percentage']:.1f}%")
        print(f"✅ Статус: {'СООТВЕТСТВУЕТ' if result['is_compliant'] else 'НЕ СООТВЕТСТВУЕТ'}")
        
        print(f"\n🇷🇺 РОССИЙСКИЕ СЕРВЕРЫ:")
        print(f"  Всего: {result['russian_servers']['total_servers']}")
        print(f"  Доступно: {result['russian_servers']['available_servers']}")
        print(f"  Статус: {result['russian_servers']['message']}")
        
        print(f"\n🌍 ЗАРУБЕЖНЫЕ СЕРВЕРЫ:")
        print(f"  Всего: {result['foreign_servers']['total_servers']}")
        print(f"  Соответствует: {result['foreign_servers']['compliant_servers']}")
        print(f"  Статус: {result['foreign_servers']['message']}")
        
        print(f"\n🗄️ БАЗА ДАННЫХ:")
        print(f"  Локация: {result['database']['location']}")
        print(f"  Провайдер: {result['database']['provider']}")
        print(f"  Статус: {result['database']['message']}")
        
        print(f"\n📊 ЛОГИ:")
        print(f"  Локация: {result['logs']['location']}")
        print(f"  Провайдер: {result['logs']['provider']}")
        print(f"  Статус: {result['logs']['message']}")
        
        return result['is_compliant']
        
    except Exception as e:
        print(f"❌ Ошибка тестирования локализации данных: {e}")
        return False

def test_no_logs_policy():
    """Тестирование модуля No-Logs политики"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ NO-LOGS ПОЛИТИКИ")
    print("="*60)
    
    try:
        no_logs_manager = NoLogsPolicyManager()
        
        # Тестируем разрешенные логи
        print("📝 Тестирование разрешенных логов...")
        no_logs_manager.log_system_event(LogLevel.INFO, "Система запущена")
        no_logs_manager.log_security_event(LogLevel.WARNING, "Обнаружена подозрительная активность")
        no_logs_manager.log_performance_event(LogLevel.INFO, "Производительность в норме")
        
        # Проверяем соответствие
        result = no_logs_manager.check_no_logs_compliance()
        
        print(f"✅ Соответствие: {result['compliance_percentage']:.1f}%")
        print(f"✅ Статус: {'СООТВЕТСТВУЕТ' if result['is_compliant'] else 'НЕ СООТВЕТСТВУЕТ'}")
        print(f"✅ Всего логов: {result['total_logs']}")
        print(f"✅ Нарушений: {result['violations_count']}")
        print(f"✅ Запрещенных логов: {result['forbidden_logs_count']}")
        print(f"✅ Необезличенных логов: {result['non_anonymized_count']}")
        
        # Получаем статистику
        stats = no_logs_manager.get_log_statistics()
        print(f"\n📊 СТАТИСТИКА ЛОГОВ:")
        print(f"  Типы логов: {stats['log_types']}")
        print(f"  Уровни логов: {stats['log_levels']}")
        print(f"  Обезличенных: {stats['anonymized_logs']}")
        print(f"  Необезличенных: {stats['non_anonymized_logs']}")
        
        return result['is_compliant']
        
    except Exception as e:
        print(f"❌ Ошибка тестирования No-Logs политики: {e}")
        return False

def test_integration():
    """Тестирование интеграции всех модулей"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ МОДУЛЕЙ")
    print("="*60)
    
    try:
        # Инициализируем интеграцию
        if not compliance_integration.initialize():
            print("❌ Ошибка инициализации интеграции")
            return False
        
        print("✅ Интеграция инициализирована")
        
        # Тестируем логирование VPN событий
        print("📝 Тестирование логирования VPN событий...")
        
        # Тестовые данные подключения
        connection_data = {
            "user_id": "user_12345",
            "ip_address": "192.168.1.100",
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "device_id": "device_67890",
            "timestamp": datetime.now(),
            "server": "ru-moscow-1"
        }
        
        # Логируем подключение
        compliance_integration.log_vpn_connection(connection_data)
        print("✅ VPN подключение залогировано")
        
        # Логируем отключение
        compliance_integration.log_vpn_disconnection(connection_data)
        print("✅ VPN отключение залогировано")
        
        # Логируем событие безопасности
        security_data = {
            "event_type": "suspicious_activity",
            "source_ip": "192.168.1.200",
            "target_ip": "192.168.1.100",
            "severity": "high"
        }
        
        compliance_integration.log_security_event("suspicious_activity", security_data)
        print("✅ Событие безопасности залогировано")
        
        # Логируем метрику производительности
        compliance_integration.log_performance_metric("connection_speed", 150.5)
        print("✅ Метрика производительности залогирована")
        
        # Запускаем полную проверку соответствия
        print("\n🔍 Запуск полной проверки соответствия...")
        result = compliance_integration.run_compliance_check()
        
        print(f"✅ Общее соответствие: {result['compliance_percentage']:.1f}%")
        print(f"✅ Статус: {'СООТВЕТСТВУЕТ' if result['overall_compliant'] else 'НЕ СООТВЕТСТВУЕТ'}")
        
        # Получаем отчет
        report = compliance_integration.get_compliance_report()
        print(f"\n📋 РЕКОМЕНДАЦИИ:")
        for recommendation in report['recommendations']:
            print(f"  • {recommendation}")
        
        return result['overall_compliant']
        
    except Exception as e:
        print(f"❌ Ошибка тестирования интеграции: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ МОДУЛЕЙ СООТВЕТСТВИЯ 152-ФЗ")
    print("="*60)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Результаты тестирования
    results = {}
    
    # Тестируем каждый модуль
    results['russia_compliance'] = test_russia_compliance()
    results['data_localization'] = test_data_localization()
    results['no_logs_policy'] = test_no_logs_policy()
    results['integration'] = test_integration()
    
    # Итоговый результат
    print("\n" + "="*60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    all_passed = all(results.values())
    
    for module, passed in results.items():
        status = "✅ ПРОЙДЕН" if passed else "❌ ПРОВАЛЕН"
        print(f"{module}: {status}")
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {'✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ' if all_passed else '❌ ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ'}")
    
    if all_passed:
        print("\n🎉 СИСТЕМА ПОЛНОСТЬЮ СООТВЕТСТВУЕТ ТРЕБОВАНИЯМ 152-ФЗ!")
        print("✅ Готово к использованию в production")
    else:
        print("\n⚠️ ТРЕБУЕТСЯ ДОРАБОТКА МОДУЛЕЙ СООТВЕТСТВИЯ")
        print("❌ Не готово к использованию в production")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)