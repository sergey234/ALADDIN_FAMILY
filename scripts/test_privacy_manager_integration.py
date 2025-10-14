#!/usr/bin/env python3
"""
Тест интеграции UniversalPrivacyManager с SafeFunctionManager
"""

import asyncio
import uuid
from datetime import datetime
import sys
import os

sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from security.privacy.universal_privacy_manager import (
    UniversalPrivacyManager, DataCategory, ConsentType, PrivacyAction
)


async def run_integration_test():
    """Запуск теста интеграции UniversalPrivacyManager с SFM"""
    print("🔧 Тест интеграции UniversalPrivacyManager с SafeFunctionManager")
    print("============================================================")
    
    # Создаем SFM
    sfm = SafeFunctionManager(name="ALADDIN")
    print("✅ SafeFunctionManager создан!")
    
    # Регистрируем UniversalPrivacyManager в SFM
    registration_success = sfm.register_function(
        function_id="privacy_manager",
        name="UniversalPrivacyManager",
        description="Универсальный менеджер приватности для соответствия международным стандартам",
        function_type="privacy",
        security_level=SecurityLevel.HIGH,
        is_critical=True,
        auto_enable=False
    )
    print(f"✅ UniversalPrivacyManager зарегистрирован! Результат: {registration_success}")
    
    # Включаем UniversalPrivacyManager
    enable_success = sfm.enable_function("privacy_manager")
    print(f"✅ UniversalPrivacyManager включен! Результат: {enable_success}")
    
    # Получаем статус
    manager_status = sfm.get_function_status("privacy_manager")
    print(f"\n📈 Статус UniversalPrivacyManager: {manager_status['status']}")
    
    # Создаем экземпляр UniversalPrivacyManager
    manager = UniversalPrivacyManager()
    print("✅ UniversalPrivacyManager создан!")
    
    # Регистрируем субъекта данных
    register_success = manager.register_data_subject(
        user_id="test_user_123",
        email="test@example.com",
        phone="+1234567890"
    )
    print(f"✅ Субъект данных зарегистрирован! Результат: {register_success}")
    
    # Добавляем согласие
    consent_success = manager.add_consent(
        user_id="test_user_123",
        consent_type=ConsentType.EXPLICIT,
        data_category=DataCategory.PERSONAL,
        granted=True
    )
    print(f"✅ Согласие добавлено! Результат: {consent_success}")
    
    # Проверяем согласие
    has_consent = manager.check_consent("test_user_123", DataCategory.PERSONAL)
    print(f"✅ Согласие проверено! Результат: {has_consent}")
    
    # Обрабатываем действие с данными
    action_success = manager.process_data_action(
        user_id="test_user_123",
        action=PrivacyAction.PROCESS,
        data_category=DataCategory.PERSONAL,
        details={
            "purpose": "аналитика",
            "legal_basis": "согласие",
            "sale_notice": True
        }
    )
    print(f"✅ Действие с данными обработано! Результат: {action_success}")
    
    # Получаем информацию о субъекте данных
    subject_info = manager.get_data_subject_info("test_user_123")
    print(f"✅ Информация о субъекте получена! Результат: {subject_info}")
    print(f"   • Email: {subject_info.get('email', 'N/A')}")
    print(f"   • Категории данных: {subject_info.get('data_categories', [])}")
    print(f"   • Согласий: {len(subject_info.get('consents', []))}")
    
    # Получаем события приватности
    events = manager.get_privacy_events("test_user_123", limit=5)
    print(f"✅ События приватности получены! Количество: {len(events)}")
    for event in events:
        print(f"   • {event['action']} - {event['data_category']} ({event['timestamp']})")
    
    # Получаем отчет о соответствии
    compliance_report = manager.get_compliance_report()
    print(f"✅ Отчет о соответствии получен! Результат: {compliance_report}")
    print(f"   • Всего событий: {compliance_report.get('total_events', 0)}")
    print(f"   • Соответствующих: {compliance_report.get('compliant_events', 0)}")
    print(f"   • Процент соответствия: {compliance_report.get('compliance_rate', 0):.1f}%")
    
    # Экспортируем данные
    export_data = manager.export_data("test_user_123")
    print(f"✅ Данные экспортированы! Результат: {export_data}")
    print(f"   • Субъект данных: {export_data.get('data_subject', {}).get('user_id', 'N/A')}")
    print(f"   • Событий: {len(export_data.get('privacy_events', []))}")
    
    # Тестируем отзыв согласия
    revoke_success = manager.revoke_consent("test_user_123", DataCategory.PERSONAL)
    print(f"✅ Согласие отозвано! Результат: {revoke_success}")
    
    # Получаем статус компонента
    status = manager.get_status()
    print(f"✅ Статус компонента получен! Результат: {status}")
    print(f"   • Статус: {status.status}")
    print(f"   • Здоровье: {status.health_score}")
    print(f"   • Субъектов данных: {status.details.get('data_subjects_count', 0)}")
    print(f"   • Событий: {status.details.get('privacy_events_count', 0)}")
    
    # Тестируем через SFM
    sfm_test_result = sfm.test_function("privacy_manager")
    print(f"✅ Тест SFM завершен! Результат: {sfm_test_result}")
    
    # Получаем метрики SFM
    sfm_metrics = sfm.get_performance_metrics()
    print("✅ Метрики SFM получены!")
    print(f"   • Всего функций: {sfm_metrics['current_metrics']['total_functions']}")
    print(f"   • Включенных функций: {sfm_metrics['current_metrics']['enabled_functions']}")
    print(f"   • Спящих функций: {sfm_metrics['current_metrics']['sleeping_functions']}")
    print(f"   • Активных выполнений: {sfm_metrics['current_metrics']['active_executions']}")
    
    print("\n============================================================")
    print("🎉 Тест интеграции UniversalPrivacyManager завершен успешно!")
    
    if (registration_success and enable_success and register_success and 
        consent_success and has_consent and action_success):
        print("✅ Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалились.")
        return False


if __name__ == "__main__":
    asyncio.run(run_integration_test())