#!/usr/bin/env python3
"""
Тест интеграции MonitorManager с SafeFunctionManager
"""

import asyncio
import uuid
from datetime import datetime
import sys
import os

sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.managers.monitor_manager import (
    MonitorManager, MonitorConfig, AlertRule, AlertSeverity
)


async def run_integration_test():
    """Запуск теста интеграции MonitorManager с SFM"""
    print("🔧 Тест интеграции MonitorManager с SafeFunctionManager")
    print("============================================================")
    
    # Создаем SFM
    sfm = SafeFunctionManager(name="ALADDIN")
    print("✅ SafeFunctionManager создан!")
    
    # Регистрируем MonitorManager в SFM
    registration_success = sfm.register_function(
        function_id="monitor_manager",
        name="MonitorManager",
        description="Централизованный мониторинг всех компонентов системы",
        function_type="ai_agent",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=False
    )
    print(f"✅ MonitorManager зарегистрирован! Результат: {registration_success}")
    
    # Включаем MonitorManager
    enable_success = sfm.enable_function("monitor_manager")
    print(f"✅ MonitorManager включен! Результат: {enable_success}")
    
    # Получаем статус
    manager_status = sfm.get_function_status("monitor_manager")
    print(f"\n📈 Статус MonitorManager: {manager_status['status']}")
    
    # Создаем конфигурацию мониторинга
    config = MonitorConfig(
        collection_interval=30,
        retention_days=30,
        anomaly_detection_enabled=True,
        alerting_enabled=True,
        cpu_threshold=80.0,
        memory_threshold=85.0,
        disk_threshold=90.0
    )
    
    # Создаем экземпляр MonitorManager
    manager = MonitorManager(config)
    print("✅ MonitorManager создан!")
    
    # Инициализируем
    init_success = await manager.initialize()
    print(f"✅ MonitorManager инициализирован! Результат: {init_success}")
    
    # Получаем статус системы
    system_status = await manager.get_system_status()
    print(f"✅ Статус системы получен! Результат: {system_status}")
    print(f"   • Общий статус: {system_status.get('overall_status', 'N/A')}")
    print(f"   • Активных алертов: {system_status.get('active_alerts_count', 0)}")
    print(f"   • Метрик в истории: {system_status.get('metrics_count', 0)}")
    print(f"   • Сборщиков: {system_status.get('collectors_count', 0)}")
    
    # Получаем метрики
    metrics = await manager.get_metrics(limit=5)
    print(f"✅ Метрики получены! Количество: {len(metrics)}")
    for metric in metrics:
        print(f"   • {metric.name}: {metric.value} {metric.unit} ({metric.status.value})")
    
    # Получаем алерты
    alerts = await manager.get_alerts()
    print(f"✅ Алерты получены! Количество: {len(alerts)}")
    for alert in alerts:
        print(f"   • {alert.rule_name}: {alert.message}")
    
    # Добавляем новое правило алерта
    new_rule = AlertRule(
        name="test_high_cpu",
        metric_name="cpu_usage",
        threshold=50.0,
        operator=">",
        severity=AlertSeverity.MEDIUM,
        enabled=True,
        cooldown=60
    )
    
    await manager.add_alert_rule(new_rule)
    print("✅ Новое правило алерта добавлено!")
    
    # Тестируем разрешение алерта (если есть)
    if alerts:
        first_alert = alerts[0]
        resolve_success = await manager.resolve_alert(first_alert.id)
        print(f"✅ Алерт разрешен! Результат: {resolve_success}")
    
    # Завершаем работу
    await manager.shutdown()
    print("✅ MonitorManager завершил работу!")
    
    # Тестируем через SFM
    sfm_test_result = sfm.test_function("monitor_manager")
    print(f"✅ Тест SFM завершен! Результат: {sfm_test_result}")
    
    # Получаем метрики SFM
    sfm_metrics = sfm.get_performance_metrics()
    print("✅ Метрики SFM получены!")
    print(f"   • Всего функций: {sfm_metrics['current_metrics']['total_functions']}")
    print(f"   • Включенных функций: {sfm_metrics['current_metrics']['enabled_functions']}")
    print(f"   • Спящих функций: {sfm_metrics['current_metrics']['sleeping_functions']}")
    print(f"   • Активных выполнений: {sfm_metrics['current_metrics']['active_executions']}")
    
    print("\n============================================================")
    print("🎉 Тест интеграции MonitorManager завершен успешно!")
    
    if registration_success and enable_success and init_success:
        print("✅ Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалились.")
        return False


if __name__ == "__main__":
    asyncio.run(run_integration_test())