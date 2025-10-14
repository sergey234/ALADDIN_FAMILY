#!/usr/bin/env python3
"""
Тест интеграции DashboardManager с SafeFunctionManager
"""

import asyncio
import uuid
from datetime import datetime
import sys
import os

sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.ai_agents.dashboard_manager import (
    DashboardManager, DashboardConfig, DashboardTheme, WidgetConfig, WidgetType, UserRole
)


async def run_integration_test():
    """Запуск теста интеграции DashboardManager с SFM"""
    print("🔧 Тест интеграции DashboardManager с SafeFunctionManager")
    print("============================================================")
    
    # Создаем SFM
    sfm = SafeFunctionManager(name="ALADDIN")
    print("✅ SafeFunctionManager создан!")
    
    # Регистрируем DashboardManager в SFM
    registration_success = sfm.register_function(
        function_id="dashboard_manager",
        name="DashboardManager",
        description="Расширенный менеджер панели управления с персонализацией",
        function_type="ai_agent",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=False
    )
    print(f"✅ DashboardManager зарегистрирован! Результат: {registration_success}")
    
    # Включаем DashboardManager
    enable_success = sfm.enable_function("dashboard_manager")
    print(f"✅ DashboardManager включен! Результат: {enable_success}")
    
    # Получаем статус
    manager_status = sfm.get_function_status("dashboard_manager")
    print(f"\n📈 Статус DashboardManager: {manager_status['status']}")
    
    # Создаем конфигурацию панели управления
    widgets = [
        WidgetConfig(
            widget_id="security_score",
            widget_type=WidgetType.GAUGE,
            title="Уровень безопасности",
            position=(0, 0),
            size=(2, 2),
            data_source="security_metrics"
        ),
        WidgetConfig(
            widget_id="threats_chart",
            widget_type=WidgetType.CHART,
            title="Обнаруженные угрозы",
            position=(2, 0),
            size=(3, 2),
            data_source="threat_data"
        ),
        WidgetConfig(
            widget_id="incidents_metric",
            widget_type=WidgetType.METRIC,
            title="Инциденты",
            position=(0, 2),
            size=(1, 1),
            data_source="incident_data"
        )
    ]
    
    config = DashboardConfig(
        dashboard_id="test_dashboard",
        name="Тестовая панель безопасности",
        description="Тестовая панель управления системой безопасности",
        theme=DashboardTheme.SECURITY,
        widgets=widgets,
        user_roles=[UserRole.ADMIN, UserRole.ANALYST],
        auto_refresh=True,
        refresh_interval=30
    )
    
    # Создаем экземпляр DashboardManager
    manager = DashboardManager(config)
    print("✅ DashboardManager создан!")
    
    # Инициализируем
    init_success = await manager.initialize()
    print(f"✅ DashboardManager инициализирован! Результат: {init_success}")
    
    # Рендерим панель управления
    dashboard = await manager.render_dashboard()
    print(f"✅ Панель управления отрендерена! Виджетов: {len(dashboard.get('widgets', []))}")
    print(f"   • Название: {dashboard.get('name', 'N/A')}")
    print(f"   • Тема: {dashboard.get('theme', 'N/A')}")
    print(f"   • Статус: {dashboard.get('status', 'N/A')}")
    
    # Получаем метрики
    metrics = await manager.get_metrics()
    print(f"✅ Метрики получены! Результат: {metrics}")
    print(f"   • Всего виджетов: {metrics.get('widgets_count', 0)}")
    print(f"   • Видимых виджетов: {metrics.get('visible_widgets', 0)}")
    print(f"   • Алертов: {metrics.get('alerts_count', 0)}")
    
    # Тестируем добавление виджета
    new_widget = WidgetConfig(
        widget_id="test_widget",
        widget_type=WidgetType.METRIC,
        title="Тестовый виджет",
        position=(5, 5),
        size=(1, 1),
        data_source="test_data"
    )
    
    add_widget_success = await manager.add_widget(new_widget)
    print(f"✅ Виджет добавлен! Результат: {add_widget_success}")
    
    # Тестируем удаление виджета
    remove_widget_success = await manager.remove_widget("test_widget")
    print(f"✅ Виджет удален! Результат: {remove_widget_success}")
    
    # Завершаем работу
    await manager.shutdown()
    print("✅ DashboardManager завершил работу!")
    
    # Тестируем через SFM
    sfm_test_result = sfm.test_function("dashboard_manager")
    print(f"✅ Тест SFM завершен! Результат: {sfm_test_result}")
    
    # Получаем метрики SFM
    sfm_metrics = sfm.get_performance_metrics()
    print("✅ Метрики SFM получены!")
    print(f"   • Всего функций: {sfm_metrics['current_metrics']['total_functions']}")
    print(f"   • Включенных функций: {sfm_metrics['current_metrics']['enabled_functions']}")
    print(f"   • Спящих функций: {sfm_metrics['current_metrics']['sleeping_functions']}")
    print(f"   • Активных выполнений: {sfm_metrics['current_metrics']['active_executions']}")
    
    print("\n============================================================")
    print("🎉 Тест интеграции DashboardManager завершен успешно!")
    
    if registration_success and enable_success and init_success:
        print("✅ Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалились.")
        return False


if __name__ == "__main__":
    asyncio.run(run_integration_test())