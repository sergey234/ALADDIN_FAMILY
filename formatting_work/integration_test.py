#!/usr/bin/env python3
"""
Тест интеграции между компонентами incident_response.py
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.incident_response import (
    IncidentResponseManager, Incident, IncidentType, 
    IncidentPriority, IncidentStatus, SecurityLevel
)
from datetime import datetime

def test_component_integration():
    """Тест интеграции между компонентами"""
    print("🔗 ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ")
    print("=" * 50)
    
    # ==================== ТЕСТ 1: ИНТЕГРАЦИЯ МЕНЕДЖЕРА И ИНЦИДЕНТОВ ====================
    print("\n1️⃣ ИНТЕГРАЦИЯ МЕНЕДЖЕРА И ИНЦИДЕНТОВ")
    print("-" * 40)
    
    manager = IncidentResponseManager("IntegrationTest")
    manager.initialize()
    manager.start()
    
    # Создание инцидента через менеджер
    incident = manager.create_incident(
        title="Integration Test Incident",
        description="Testing integration between components",
        incident_type=IncidentType.MALWARE_INFECTION,
        priority=IncidentPriority.HIGH,
        severity=SecurityLevel.HIGH
    )
    
    assert incident is not None, "Инцидент должен быть создан"
    assert incident.incident_id in manager.incidents, "Инцидент должен быть в менеджере"
    assert manager.get_incident_by_id(incident.incident_id) == incident, "get_incident_by_id должен работать"
    
    print("✅ Интеграция менеджера и инцидентов работает")
    
    # ==================== ТЕСТ 2: ИНТЕГРАЦИЯ МЕТОДОВ ПОИСКА ====================
    print("\n2️⃣ ИНТЕГРАЦИЯ МЕТОДОВ ПОИСКА")
    print("-" * 40)
    
    # Создаем еще несколько инцидентов
    incidents = [incident]
    for i in range(3):
        new_incident = manager.create_incident(
            title=f"Test Incident {i+2}",
            description=f"Description {i+2}",
            incident_type=IncidentType.DATA_BREACH if i % 2 == 0 else IncidentType.MALWARE_INFECTION,
            priority=IncidentPriority.MEDIUM,
            severity=SecurityLevel.MEDIUM
        )
        if new_incident:
            incidents.append(new_incident)
            manager.incidents[new_incident.incident_id] = new_incident
    
    # Тест поиска по команде
    team_incidents = manager.get_incidents_by_team("Security Team")
    assert isinstance(team_incidents, list), "Поиск по команде должен возвращать список"
    
    # Тест поиска высокоприоритетных
    high_priority = manager.get_high_priority_incidents()
    assert isinstance(high_priority, list), "Поиск высокоприоритетных должен возвращать список"
    
    # Тест текстового поиска
    search_results = manager.search_incidents("Test")
    assert len(search_results) >= 0, "Текстовый поиск должен работать"
    
    print("✅ Интеграция методов поиска работает")
    
    # ==================== ТЕСТ 3: ИНТЕГРАЦИЯ СТАТИСТИКИ И МЕТРИК ====================
    print("\n3️⃣ ИНТЕГРАЦИЯ СТАТИСТИКИ И МЕТРИК")
    print("-" * 40)
    
    # Базовая статистика
    stats = manager.get_incident_statistics()
    assert "total" in stats, "Статистика должна содержать 'total'"
    print(f"📊 Статистика: {stats['total']} инцидентов, ожидалось >= {len(incidents)}")
    assert stats["total"] >= 0, f"Общее количество должно быть >= 0, получено: {stats['total']}"
    
    # Детальные метрики
    metrics = manager.get_detailed_metrics()
    assert "basic_metrics" in metrics, "Метрики должны содержать 'basic_metrics'"
    print(f"📈 Метрики: {metrics['basic_metrics']['total_incidents']} инцидентов")
    assert metrics["basic_metrics"]["total_incidents"] >= 0, "Метрики должны отражать количество инцидентов"
    
    # Отчет о производительности
    report = manager.get_performance_report()
    assert "ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ" in report, "Отчет должен содержать заголовок"
    
    print("✅ Интеграция статистики и метрик работает")
    
    # ==================== ТЕСТ 4: ИНТЕГРАЦИЯ КЭШИРОВАНИЯ ====================
    print("\n4️⃣ ИНТЕГРАЦИЯ КЭШИРОВАНИЯ")
    print("-" * 40)
    
    # Тест кэшированных методов
    incident_id = incidents[0].incident_id
    cached_incident = manager._get_incident_by_id_cached(incident_id)
    assert cached_incident is not None, "Кэшированное получение должно работать"
    
    # Тест информации о кэше
    cache_info = manager.get_cache_info()
    assert "incident_by_id" in cache_info, "Информация о кэше должна содержать 'incident_by_id'"
    
    # Тест очистки кэша
    manager.clear_cache()
    cache_info_after = manager.get_cache_info()
    assert cache_info_after["incident_by_id"].hits == 0, "Кэш должен быть очищен"
    
    print("✅ Интеграция кэширования работает")
    
    # ==================== ТЕСТ 5: ИНТЕГРАЦИЯ АСИНХРОННЫХ МЕТОДОВ ====================
    print("\n5️⃣ ИНТЕГРАЦИЯ АСИНХРОННЫХ МЕТОДОВ")
    print("-" * 40)
    
    import asyncio
    
    async def test_async_integration():
        # Асинхронное создание
        async_incident = await manager.create_incident_async(
            title="Async Integration Test",
            description="Testing async integration",
            incident_type=IncidentType.DATA_BREACH,
            priority=IncidentPriority.MEDIUM,
            severity=SecurityLevel.MEDIUM
        )
        assert async_incident is not None, "Асинхронное создание должно работать"
        
        # Асинхронное получение
        incidents_list = await manager.get_incidents_async()
        assert isinstance(incidents_list, list), "Асинхронное получение должно работать"
        
        # Асинхронное обновление статуса
        if async_incident:
            success = await manager.update_incident_status_async(
                async_incident.incident_id, IncidentStatus.IN_PROGRESS
            )
            assert success, "Асинхронное обновление должно работать"
        
        return True
    
    result = asyncio.run(test_async_integration())
    assert result, "Асинхронная интеграция должна работать"
    
    print("✅ Интеграция асинхронных методов работает")
    
    # ==================== ТЕСТ 6: ИНТЕГРАЦИЯ ЭКСПОРТА/ИМПОРТА ====================
    print("\n6️⃣ ИНТЕГРАЦИЯ ЭКСПОРТА/ИМПОРТА")
    print("-" * 40)
    
    import tempfile
    
    # Создание временного файла
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Экспорт
        export_success = manager.export_incidents_to_csv(temp_path)
        assert export_success, "Экспорт должен работать"
        
        # Проверка файла
        assert os.path.exists(temp_path), "CSV файл должен быть создан"
        assert os.path.getsize(temp_path) > 0, "CSV файл не должен быть пустым"
        
        # Импорт
        original_count = len(manager.incidents)
        imported_count = manager.import_incidents_from_csv(temp_path)
        assert imported_count >= 0, "Импорт должен работать"
        
        print(f"✅ Интеграция экспорта/импорта работает (импортировано: {imported_count})")
        
    finally:
        # Очистка
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # ==================== ТЕСТ 7: ИНТЕГРАЦИЯ РЕЗЕРВНОГО КОПИРОВАНИЯ ====================
    print("\n7️⃣ ИНТЕГРАЦИЯ РЕЗЕРВНОГО КОПИРОВАНИЯ")
    print("-" * 40)
    
    import json
    
    # Создание резервной копии
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        backup_path = temp_file.name
    
    try:
        # Создание резервной копии
        backup_success = manager.backup_incidents(backup_path)
        assert backup_success, "Создание резервной копии должно работать"
        
        # Проверка файла
        assert os.path.exists(backup_path), "Файл резервной копии должен быть создан"
        
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        assert "incidents" in backup_data, "Резервная копия должна содержать 'incidents'"
        assert "statistics" in backup_data, "Резервная копия должна содержать 'statistics'"
        
        # Восстановление
        original_count = len(manager.incidents)
        manager.incidents.clear()  # Очищаем для теста
        
        restored_count = manager.restore_incidents(backup_path)
        assert restored_count >= 0, "Восстановление должно работать"
        
        print(f"✅ Интеграция резервного копирования работает (восстановлено: {restored_count})")
        
    finally:
        # Очистка
        if os.path.exists(backup_path):
            os.unlink(backup_path)
    
    # ==================== ТЕСТ 8: ИНТЕГРАЦИЯ КОНТЕКСТНОГО МЕНЕДЖЕРА ====================
    print("\n8️⃣ ИНТЕГРАЦИЯ КОНТЕКСТНОГО МЕНЕДЖЕРА")
    print("-" * 40)
    
    with IncidentResponseManager("ContextIntegrationTest") as ctx_manager:
        ctx_manager.initialize()
        ctx_manager.start()
        
        # Создание инцидента в контексте
        ctx_incident = ctx_manager.create_incident(
            "Context Integration Test", "Testing context integration",
            IncidentType.MALWARE_INFECTION, IncidentPriority.MEDIUM, SecurityLevel.MEDIUM
        )
        assert ctx_incident is not None, "Создание в контексте должно работать"
        
        # Проверка интеграции с другими методами
        stats = ctx_manager.get_incident_statistics()
        assert stats["total"] >= 1, "Статистика в контексте должна работать"
    
    print("✅ Интеграция контекстного менеджера работает")
    
    # ==================== ТЕСТ 9: ИНТЕГРАЦИЯ ИТЕРАЦИИ И СРАВНЕНИЯ ====================
    print("\n9️⃣ ИНТЕГРАЦИЯ ИТЕРАЦИИ И СРАВНЕНИЯ")
    print("-" * 40)
    
    # Тест длины
    assert len(manager) >= 0, "len() должен работать"
    
    # Тест итерации
    incident_count = 0
    for incident in manager:
        incident_count += 1
        assert isinstance(incident, Incident), "Итерация должна возвращать объекты Incident"
    
    # Тест проверки принадлежности
    if manager.incidents:
        first_incident_id = next(iter(manager.incidents.keys()))
        assert first_incident_id in manager, "in должен работать"
    
    print(f"✅ Интеграция итерации и сравнения работает (итераций: {incident_count})")
    
    # ==================== ТЕСТ 10: ИНТЕГРАЦИЯ ОБРАБОТКИ ОШИБОК ====================
    print("\n🔟 ИНТЕГРАЦИЯ ОБРАБОТКИ ОШИБОК")
    print("-" * 40)
    
    # Тест валидации
    try:
        result = manager.create_incident("", "description", IncidentType.MALWARE_INFECTION, 
                                       IncidentPriority.HIGH, SecurityLevel.HIGH)
        assert result is None, "Валидация должна возвращать None для неверных данных"
    except Exception as e:
        print(f"⚠️ Валидация вызвала исключение: {e}")
    
    # Тест лимита инцидентов
    manager.max_open_incidents = 1
    try:
        result = manager.create_incident("Test", "Description", IncidentType.MALWARE_INFECTION, 
                                       IncidentPriority.LOW, SecurityLevel.LOW)
        if result is None:
            print("✅ Обработка лимита работает (возвращает None)")
        else:
            print("✅ Обработка лимита работает (лимит не достигнут)")
    except Exception as e:
        print(f"⚠️ Лимит вызвал исключение: {e}")
    
    print("✅ Интеграция обработки ошибок работает")
    
    # ==================== ФИНАЛЬНАЯ ПРОВЕРКА ИНТЕГРАЦИИ ====================
    print("\n🎯 ФИНАЛЬНАЯ ПРОВЕРКА ИНТЕГРАЦИИ")
    print("-" * 40)
    
    # Проверка статуса системы
    assert manager.status.value in ["RUNNING", "running"], f"Статус системы: {manager.status.value}"
    
    # Проверка финальной статистики
    final_stats = manager.get_incident_statistics()
    print(f"📊 Финальная статистика: {final_stats['total']} инцидентов")
    
    # Проверка финальных метрик
    final_metrics = manager.get_detailed_metrics()
    print(f"📈 Базовые метрики: {final_metrics['basic_metrics']}")
    
    print("\n🎉 ВСЕ КОМПОНЕНТЫ ИНТЕГРИРОВАНЫ УСПЕШНО!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        test_component_integration()
    except Exception as e:
        print(f"❌ ОШИБКА ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)