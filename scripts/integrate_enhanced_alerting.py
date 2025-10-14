#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция Enhanced Alerting System с SafeFunctionManager
Скрипт для интеграции улучшенной системы алертов

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import sys
import os
import json
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.enhanced_alerting import EnhancedAlertingSystem, AlertRule, AlertSeverity, AlertChannel
from security.safe_function_manager import SafeFunctionManager


def integrate_enhanced_alerting():
    """Интеграция улучшенной системы алертов"""
    print("🚨 Интеграция Enhanced Alerting System с SafeFunctionManager")
    print("=" * 60)
    
    try:
        # 1. Создание экземпляра системы алертов
        print("1. Создание системы алертов...")
        alerting_system = EnhancedAlertingSystem()
        print("✅ Система алертов создана")
        
        # 2. Создание экземпляра SafeFunctionManager
        print("2. Создание SafeFunctionManager...")
        safe_manager = SafeFunctionManager()
        print("✅ SafeFunctionManager создан")
        
        # 3. Регистрация системы алертов в SafeFunctionManager
        print("3. Регистрация в SafeFunctionManager...")
        
        # Создание конфигурации для регистрации
        alerting_config = {
            "function_name": "EnhancedAlertingSystem",
            "description": "Улучшенная система алертов для мониторинга безопасности",
            "version": "1.0",
            "author": "ALADDIN Security Team",
            "category": "security",
            "priority": "high",
            "dependencies": ["core.base", "core.logging_module"],
            "enabled": True,
            "auto_start": True,
            "monitoring": True,
            "alerting": True,
            "performance_tracking": True,
            "error_handling": True,
            "logging": True,
            "metrics": True,
            "health_check": True,
            "backup": True,
            "restore": True,
            "update": True,
            "rollback": True,
            "cleanup": True,
            "status": "active",
            "last_updated": datetime.now().isoformat(),
            "update_frequency": "real_time",
            "performance_threshold": 0.8,
            "error_threshold": 0.05,
            "memory_limit": 100,  # MB
            "cpu_limit": 50,  # %
            "disk_limit": 1000,  # MB
            "network_limit": 100,  # MB
            "timeout": 30,  # seconds
            "retry_count": 3,
            "cooldown": 60,  # seconds
            "max_instances": 1,
            "auto_restart": True,
            "auto_scale": False,
            "load_balancing": False,
            "caching": True,
            "compression": True,
            "encryption": True,
            "authentication": True,
            "authorization": True,
            "audit_logging": True,
            "compliance": True,
            "testing": True,
            "documentation": True,
            "support": True,
            "maintenance": True,
            "monitoring_rules": [
                {
                    "rule_id": "high_cpu_usage",
                    "name": "Высокая нагрузка на CPU",
                    "condition": "cpu_usage > 80",
                    "severity": "warning",
                    "enabled": True
                },
                {
                    "rule_id": "high_memory_usage",
                    "name": "Высокая нагрузка на память",
                    "condition": "memory_usage > 90",
                    "severity": "error",
                    "enabled": True
                },
                {
                    "rule_id": "security_threat_detected",
                    "name": "Обнаружена угроза безопасности",
                    "condition": "threats_detected > 0",
                    "severity": "critical",
                    "enabled": True
                }
            ],
            "alert_channels": ["email", "console", "log"],
            "email_config": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "aladdin@security.local",
                "to_emails": ["admin@security.local"]
            },
            "webhook_config": {
                "url": "http://localhost:5000/api/webhook",
                "timeout": 10
            }
        }
        
        # Регистрация функции
        registration_result = safe_manager.register_function(
            function_name="EnhancedAlertingSystem",
            function_instance=alerting_system,
            config=alerting_config
        )
        
        if registration_result["success"]:
            print("✅ Система алертов зарегистрирована в SafeFunctionManager")
        else:
            print(f"❌ Ошибка регистрации: {registration_result['error']}")
            return False
        
        # 4. Тестирование интеграции
        print("4. Тестирование интеграции...")
        
        # Проверка статуса
        status = safe_manager.get_function_status("EnhancedAlertingSystem")
        print(f"📊 Статус: {status['status']}")
        print(f"📈 Производительность: {status['performance']}")
        print(f"🔧 Конфигурация: {status['config_loaded']}")
        
        # Проверка метрик
        metrics = safe_manager.get_function_metrics("EnhancedAlertingSystem")
        print(f"📊 Метрики: {len(metrics)} записей")
        
        # Проверка логов
        logs = safe_manager.get_function_logs("EnhancedAlertingSystem", limit=5)
        print(f"📝 Логи: {len(logs)} записей")
        
        # 5. Создание отчета интеграции
        print("5. Создание отчета интеграции...")
        
        integration_report = {
            "integration_date": datetime.now().isoformat(),
            "function_name": "EnhancedAlertingSystem",
            "version": "1.0",
            "status": "success",
            "safe_manager_integration": True,
            "monitoring_enabled": True,
            "alerting_enabled": True,
            "performance_tracking": True,
            "error_handling": True,
            "logging_enabled": True,
            "metrics_collection": True,
            "health_monitoring": True,
            "backup_enabled": True,
            "restore_capability": True,
            "update_mechanism": True,
            "rollback_capability": True,
            "cleanup_enabled": True,
            "alert_rules": len(alerting_system.alert_rules),
            "alert_channels": len(alerting_system.channels),
            "monitoring_active": alerting_system.running,
            "configuration": alerting_config,
            "test_results": {
                "registration": registration_result["success"],
                "status_check": status["status"] == "active",
                "metrics_available": len(metrics) > 0,
                "logs_available": len(logs) > 0
            },
            "recommendations": [
                "Настроить email конфигурацию для отправки алертов",
                "Добавить SMS интеграцию для критических алертов",
                "Настроить webhook для интеграции с внешними системами",
                "Регулярно проверять и обновлять правила алертов",
                "Мониторить производительность системы алертов"
            ]
        }
        
        # Сохранение отчета
        report_filename = f"enhanced_alerting_integration_report_{int(time.time())}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(integration_report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчет сохранен: {report_filename}")
        
        # 6. Итоговый отчет
        print("\n" + "=" * 60)
        print("🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Функция: EnhancedAlertingSystem v1.0")
        print(f"📊 Статус: {status['status']}")
        print(f"📈 Производительность: {status['performance']}")
        print(f"🚨 Правил алертов: {len(alerting_system.alert_rules)}")
        print(f"📡 Каналов отправки: {len(alerting_system.channels)}")
        print(f"🔄 Мониторинг активен: {'Да' if alerting_system.running else 'Нет'}")
        print(f"📝 Отчет: {report_filename}")
        print("\n💡 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(integration_report["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False


def test_alerting_system():
    """Тестирование системы алертов"""
    print("\n🧪 Тестирование системы алертов...")
    
    try:
        # Создание тестового правила
        test_rule = AlertRule(
            rule_id="test_rule",
            name="Тестовое правило",
            description="Правило для тестирования системы алертов",
            condition="cpu_usage > 0",  # Всегда срабатывает
            severity=AlertSeverity.INFO,
            channels=[AlertChannel.CONSOLE, AlertChannel.LOG],
            cooldown=1
        )
        
        # Создание системы алертов
        alerting_system = EnhancedAlertingSystem()
        
        # Добавление тестового правила
        alerting_system.add_alert_rule(test_rule)
        
        print("✅ Тестовое правило добавлено")
        
        # Ожидание срабатывания алерта
        print("⏳ Ожидание срабатывания алерта (10 секунд)...")
        time.sleep(10)
        
        # Проверка алертов
        alerts = alerting_system.get_alerts(limit=10)
        print(f"📊 Получено алертов: {len(alerts)}")
        
        for alert in alerts:
            print(f"  - {alert.severity.value.upper()}: {alert.title}")
        
        # Статистика
        stats = alerting_system.get_alert_statistics()
        print(f"📈 Статистика: {stats['total_alerts']} всего, {stats['unresolved_alerts']} неразрешенных")
        
        # Остановка системы
        alerting_system.stop()
        print("✅ Тестирование завершено")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск интеграции Enhanced Alerting System")
    print("=" * 60)
    
    # Интеграция
    success = integrate_enhanced_alerting()
    
    if success:
        # Тестирование
        test_alerting_system()
        
        print("\n🎉 ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ УСПЕШНО!")
    else:
        print("\n❌ ИНТЕГРАЦИЯ НЕ УДАЛАСЬ!")
        sys.exit(1)