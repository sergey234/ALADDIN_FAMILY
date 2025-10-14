#!/usr/bin/env python3
"""
Упрощенная интеграция расширенного мониторинга
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.advanced_monitoring_manager import advanced_monitoring_manager
from core.logging_module import LoggingManager
import time

logger = LoggingManager(name="IntegrateAdvancedMonitoringSimple")

def integrate_advanced_monitoring_simple():
    """Упрощенная интеграция расширенного мониторинга"""
    logger.log("INFO", "🚀 Запуск упрощенной интеграции расширенного мониторинга...")
    
    try:
        # Проверяем статус менеджера мониторинга
        status = advanced_monitoring_manager.get_status()
        logger.log("INFO", f"📊 Статус AdvancedMonitoringManager: {status['status']}")
        logger.log("INFO", f"🔧 Метрики: {status['metrics_count']}")
        logger.log("INFO", f"🚨 Алерты: {status['alerts_count']}")
        logger.log("INFO", f"📋 Правила: {status['rules_count']}")
        
        # Тестируем основные функции
        logger.log("INFO", "🧪 Тестирование основных функций...")
        
        # Тест получения метрик
        try:
            metrics = advanced_monitoring_manager.get_metrics()
            logger.log("INFO", f"✅ Метрики получены: {len(metrics)} типов")
        except Exception as e:
            logger.log("ERROR", f"❌ Ошибка получения метрик: {e}")
        
        # Тест получения алертов
        try:
            alerts = advanced_monitoring_manager.get_alerts()
            logger.log("INFO", f"✅ Алерты получены: {len(alerts)} штук")
        except Exception as e:
            logger.log("ERROR", f"❌ Ошибка получения алертов: {e}")
        
        # Тест получения дашборда
        try:
            dashboard = advanced_monitoring_manager.get_dashboard_data()
            logger.log("INFO", f"✅ Данные дашборда получены: {len(dashboard)} разделов")
        except Exception as e:
            logger.log("ERROR", f"❌ Ошибка получения дашборда: {e}")
        
        # Тест добавления пользовательской метрики
        try:
            advanced_monitoring_manager._add_metric(
                "test.integration", 100.0, 
                advanced_monitoring_manager.MetricType.CUSTOM, 
                "test_units", {"integration": "success"}
            )
            logger.log("INFO", "✅ Пользовательская метрика добавлена")
        except Exception as e:
            logger.log("ERROR", f"❌ Ошибка добавления метрики: {e}")
        
        # Тест добавления правила мониторинга
        try:
            from security.advanced_monitoring_manager import MonitoringRule, AlertSeverity
            
            test_rule = MonitoringRule(
                rule_id="test_integration_rule",
                name="Test Integration Rule",
                metric_name="test.integration",
                condition=">",
                threshold=50.0,
                severity=AlertSeverity.INFO
            )
            
            success = advanced_monitoring_manager.add_monitoring_rule(test_rule)
            if success:
                logger.log("INFO", "✅ Правило мониторинга добавлено")
            else:
                logger.log("WARNING", "⚠️ Не удалось добавить правило мониторинга")
        except Exception as e:
            logger.log("ERROR", f"❌ Ошибка добавления правила: {e}")
        
        # Финальная проверка статуса
        final_status = advanced_monitoring_manager.get_status()
        logger.log("INFO", f"📈 Финальный статус: {final_status['status']}")
        logger.log("INFO", f"⏱️ Время работы: {final_status['uptime']:.1f} секунд")
        
        logger.log("CRITICAL", "🎉 Упрощенная интеграция расширенного мониторинга завершена успешно!")
        return True
        
    except Exception as e:
        logger.log("CRITICAL", f"❌ Критическая ошибка при интеграции: {e}")
        return False

if __name__ == '__main__':
    success = integrate_advanced_monitoring_simple()
    if success:
        print("\n✅ Упрощенная интеграция расширенного мониторинга завершена успешно!")
        print("🚀 Теперь можно запустить Monitoring API Server:")
        print("   python3 monitoring_api_server.py")
        print("   или")
        print("   ./start_monitoring.sh")
    else:
        print("\n❌ Интеграция завершилась с ошибками")
        sys.exit(1)