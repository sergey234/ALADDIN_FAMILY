#!/usr/bin/env python3
"""
Скрипт интеграции расширенного мониторинга в SafeFunctionManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.advanced_monitoring_manager import advanced_monitoring_manager
from security.safe_function_manager import SafeFunctionManager
from core.base import SecurityLevel, ComponentStatus
from core.logging_module import LoggingManager
import time

logger = LoggingManager(name="IntegrateAdvancedMonitoring")

def integrate_advanced_monitoring():
    """Интеграция расширенного мониторинга"""
    logger.log("INFO", "🚀 Запуск интеграции расширенного мониторинга...")
    
    try:
        # Инициализация SafeFunctionManager
        safe_manager = SafeFunctionManager()
        logger.log("INFO", "✅ SafeFunctionManager инициализирован")
        
        # Регистрация функций мониторинга
        monitoring_functions = [
            {
                "function_id": "advanced_monitoring_manager",
                "name": "Advanced Monitoring Manager",
                "description": "Расширенный мониторинг системы с метриками и алертами",
                "function_type": "monitoring",
                "security_level": SecurityLevel.HIGH,
                "is_critical": True,
                "auto_enable": True
            },
            {
                "function_id": "get_system_metrics",
                "name": "Get System Metrics",
                "description": "Получение системных метрик",
                "function_type": "monitoring",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True
            },
            {
                "function_id": "get_alerts",
                "name": "Get Alerts",
                "description": "Получение алертов системы",
                "function_type": "monitoring",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True
            },
            {
                "function_id": "get_dashboard_data",
                "name": "Get Dashboard Data",
                "description": "Получение данных для дашборда",
                "function_type": "monitoring",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True
            },
            {
                "function_id": "get_monitoring_status",
                "name": "Get Monitoring Status",
                "description": "Получение статуса мониторинга",
                "function_type": "monitoring",
                "security_level": SecurityLevel.MEDIUM,
                "is_critical": False,
                "auto_enable": True
            }
        ]
        
        # Регистрация функций
        registered_count = 0
        for func_info in monitoring_functions:
            try:
                success = safe_manager.register_function(
                    function_id=func_info["function_id"],
                    name=func_info["name"],
                    description=func_info["description"],
                    function_type=func_info["function_type"],
                    security_level=func_info["security_level"],
                    is_critical=func_info["is_critical"],
                    auto_enable=func_info["auto_enable"]
                )
                
                if success:
                    registered_count += 1
                    logger.log("INFO", f"✅ Зарегистрирована функция: {func_info['name']}")
                else:
                    logger.log("WARNING", f"⚠️ Не удалось зарегистрировать: {func_info['name']}")
                    
            except Exception as e:
                logger.log("ERROR", f"❌ Ошибка регистрации {func_info['name']}: {e}")
        
        logger.log("INFO", f"📊 Зарегистрировано функций мониторинга: {registered_count}/{len(monitoring_functions)}")
        
        # Проверка статуса
        status = safe_manager.get_status()
        logger.log("INFO", f"📈 Статус SafeFunctionManager: {status.get('status', 'unknown')}")
        logger.log("INFO", f"🔧 Всего функций: {status.get('total_functions', 0)}")
        logger.log("INFO", f"✅ Активных функций: {status.get('active_functions', 0)}")
        
        # Тестирование функций
        logger.log("INFO", "🧪 Тестирование функций мониторинга...")
        
        try:
            # Тест получения метрик
            metrics = advanced_monitoring_manager.get_metrics()
            logger.log("INFO", f"📊 Метрики получены: {len(metrics)} типов")
            
            # Тест получения алертов
            alerts = advanced_monitoring_manager.get_alerts()
            logger.log("INFO", f"🚨 Алерты получены: {len(alerts)} штук")
            
            # Тест получения дашборда
            dashboard = advanced_monitoring_manager.get_dashboard_data()
            logger.log("INFO", f"📈 Данные дашборда получены: {len(dashboard)} разделов")
            
            # Тест статуса
            monitoring_status = advanced_monitoring_manager.get_status()
            logger.log("INFO", f"🔍 Статус мониторинга: {monitoring_status['status']}")
            
        except Exception as e:
            logger.log("ERROR", f"❌ Ошибка тестирования: {e}")
        
        logger.log("CRITICAL", "🎉 Интеграция расширенного мониторинга завершена успешно!")
        return True
        
    except Exception as e:
        logger.log("CRITICAL", f"❌ Критическая ошибка при интеграции: {e}")
        return False

if __name__ == '__main__':
    success = integrate_advanced_monitoring()
    if success:
        print("\n✅ Интеграция расширенного мониторинга завершена успешно!")
        print("🚀 Теперь можно запустить Monitoring API Server:")
        print("   python3 monitoring_api_server.py")
        print("   или")
        print("   ./start_monitoring.sh")
    else:
        print("\n❌ Интеграция завершилась с ошибками")
        sys.exit(1)