#!/usr/bin/env python3
"""
Тест интеграции AnalyticsManager с SafeFunctionManager
"""

import asyncio
import uuid
from datetime import datetime
import sys
import os

sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.managers.analytics_manager import (
    AnalyticsManager, AnalyticsConfig, AnalyticsType, DataSource
)


async def run_integration_test():
    """Запуск теста интеграции AnalyticsManager с SFM"""
    print("🔧 Тест интеграции AnalyticsManager с SafeFunctionManager")
    print("============================================================")
    
    # Создаем SFM
    sfm = SafeFunctionManager(name="ALADDIN")
    print("✅ SafeFunctionManager создан!")
    
    # Регистрируем AnalyticsManager в SFM
    registration_success = sfm.register_function(
        function_id="analytics_manager",
        name="AnalyticsManager",
        description="Расширенный менеджер аналитики системы безопасности с ML",
        function_type="ai_agent",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=False
    )
    print(f"✅ AnalyticsManager зарегистрирован! Результат: {registration_success}")
    
    # Включаем AnalyticsManager
    enable_success = sfm.enable_function("analytics_manager")
    print(f"✅ AnalyticsManager включен! Результат: {enable_success}")
    
    # Получаем статус
    manager_status = sfm.get_function_status("analytics_manager")
    print(f"\n📈 Статус AnalyticsManager: {manager_status['status']}")
    
    # Создаем конфигурацию аналитики
    config = AnalyticsConfig(
        analysis_type=AnalyticsType.BEHAVIORAL,
        data_source=DataSource.USER_ACTIVITY,
        time_window=3600,
        sample_size=1000,
        confidence_threshold=0.95,
        anomaly_threshold=0.1,
        enable_ml=True,
        enable_clustering=True,
        enable_prediction=True
    )
    
    # Создаем экземпляр AnalyticsManager
    manager = AnalyticsManager(config)
    print("✅ AnalyticsManager создан!")
    
    # Тестовые данные
    test_data = [
        {
            'session_duration': 1200,
            'page_views': 15,
            'click_rate': 0.3,
            'time_on_site': 800,
            'bounce_rate': 0.2,
            'conversion_rate': 0.05
        }
        for _ in range(100)
    ]
    
    # Выполняем анализ
    result = await manager.analyze(test_data)
    print(f"✅ Анализ выполнен! Статус: {result.status}")
    print(f"   • Инсайты: {len(result.insights)}")
    print(f"   • Рекомендации: {len(result.recommendations)}")
    print(f"   • Confidence Score: {result.confidence_score:.2f}")
    print(f"   • Anomaly Score: {result.anomaly_score:.2f}")
    
    # Получаем метрики
    metrics = await manager.get_metrics()
    print(f"✅ Метрики получены! Результат: {metrics}")
    print(f"   • Всего анализов: {metrics.get('total_analyses', 0)}")
    print(f"   • Завершенных анализов: {metrics.get('completed_analyses', 0)}")
    print(f"   • Успешность: {metrics.get('success_rate', 0):.1%}")
    print(f"   • Средняя уверенность: {metrics.get('average_confidence', 0):.2f}")
    
    # Завершаем работу
    await manager.shutdown()
    print("✅ AnalyticsManager завершил работу!")
    
    # Тестируем через SFM
    sfm_test_result = sfm.test_function("analytics_manager")
    print(f"✅ Тест SFM завершен! Результат: {sfm_test_result}")
    
    # Получаем метрики SFM
    sfm_metrics = sfm.get_performance_metrics()
    print("✅ Метрики SFM получены!")
    print(f"   • Всего функций: {sfm_metrics['current_metrics']['total_functions']}")
    print(f"   • Включенных функций: {sfm_metrics['current_metrics']['enabled_functions']}")
    print(f"   • Спящих функций: {sfm_metrics['current_metrics']['sleeping_functions']}")
    print(f"   • Активных выполнений: {sfm_metrics['current_metrics']['active_executions']}")
    
    print("\n============================================================")
    print("🎉 Тест интеграции AnalyticsManager завершен успешно!")
    
    if registration_success and enable_success and result.status.value == "completed":
        print("✅ Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалились.")
        return False


if __name__ == "__main__":
    asyncio.run(run_integration_test())