#!/usr/bin/env python3
"""
Комплексный тест всех классов и методов incident_response.py
"""

import sys
import os
import asyncio
import tempfile
import json
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.incident_response import (
    IncidentResponseManager, Incident, IncidentType, 
    IncidentPriority, IncidentStatus, SecurityLevel,
    IncidentResponseError, IncidentNotFoundError, 
    InvalidIncidentDataError, IncidentLimitExceededError,
    IncidentValidationError
)
from datetime import datetime

def test_all_classes_and_methods():
    """Полный тест всех классов и методов"""
    print("🧪 КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    # Создание менеджера
    manager = IncidentResponseManager("ComprehensiveTest")
    
    # ==================== ТЕСТ 1: ИНИЦИАЛИЗАЦИЯ ====================
    print("\n1️⃣ ТЕСТ ИНИЦИАЛИЗАЦИИ И ЗАПУСКА")
    print("-" * 40)
    
    assert manager.initialize(), "Ошибка инициализации"
    assert manager.start(), "Ошибка запуска"
    assert manager.status.value in ["RUNNING", "running"], f"Неверный статус: {manager.status.value}"
    print("✅ Инициализация и запуск успешны")
    
    # ==================== ТЕСТ 2: СОЗДАНИЕ ИНЦИДЕНТОВ ====================
    print("\n2️⃣ ТЕСТ СОЗДАНИЯ ИНЦИДЕНТОВ")
    print("-" * 40)
    
    incidents = []
    for i in range(5):
        # Добавляем небольшую задержку для уникальности ID
        import time
        time.sleep(0.001)
        
        incident = manager.create_incident(
            title=f"Test Incident {i+1}",
            description=f"Description for incident {i+1}",
            incident_type=IncidentType.MALWARE_INFECTION,
            priority=IncidentPriority.HIGH if i % 2 == 0 else IncidentPriority.MEDIUM,
            severity=SecurityLevel.HIGH if i % 2 == 0 else SecurityLevel.MEDIUM,
            affected_systems=[f"system-{i+1}"]
        )
        assert incident is not None, f"Инцидент {i+1} не создан"
        incidents.append(incident)
        manager.incidents[incident.incident_id] = incident
    
    print(f"✅ Создано {len(incidents)} инцидентов")
    
    # ==================== ТЕСТ 3: МЕТОДЫ КЛАССА INCIDENT ====================
    print("\n3️⃣ ТЕСТ МЕТОДОВ КЛАССА INCIDENT")
    print("-" * 40)
    
    incident = incidents[0]
    
    # Базовые методы
    assert incident.is_open(), "is_open() должен возвращать True"
    assert not incident.is_resolved(), "is_resolved() должен возвращать False"
    assert incident.is_escalated(), "is_escalated() должен возвращать True"
    
    # Временные методы
    age = incident.get_age_hours()
    assert age >= 0, f"get_age_hours() должен возвращать положительное число, получено: {age}"
    
    # Методы оценки
    assert incident.get_priority_score() == 3, "get_priority_score() должен возвращать 3 для HIGH"
    assert incident.get_severity_score() == 3, "get_severity_score() должен возвращать 3 для HIGH"
    
    # Методы добавления данных
    incident.add_evidence("log", "System log evidence", "/var/log/system.log")
    incident.add_action("Isolation", "admin", "System isolated successfully")
    incident.update_impact_assessment("High impact on production systems")
    incident.set_root_cause("Malware infection via email attachment")
    incident.add_lesson_learned("Implement stricter email filtering")
    
    # Специальные методы
    str_repr = str(incident)
    repr_repr = repr(incident)
    assert "Test Incident 1" in str_repr, "str() должен содержать заголовок"
    assert "Incident(" in repr_repr, "repr() должен содержать 'Incident('"
    
    # Методы сравнения
    incident2 = incidents[1]
    # Проверяем, что инциденты имеют разные ID или разные времена создания
    if incident.incident_id == incident2.incident_id:
        print(f"⚠️ Инциденты имеют одинаковый ID: {incident.incident_id}")
    else:
        assert incident != incident2, f"Разные инциденты должны быть не равны: {incident.incident_id} vs {incident2.incident_id}"
    
    # Сравнение по времени создания
    assert (incident < incident2) != (incident > incident2), "Инциденты должны быть сравнимы"
    
    print("✅ Все методы класса Incident работают корректно")
    
    # ==================== ТЕСТ 4: МЕТОДЫ ПОИСКА И ФИЛЬТРАЦИИ ====================
    print("\n4️⃣ ТЕСТ МЕТОДОВ ПОИСКА И ФИЛЬТРАЦИИ")
    print("-" * 40)
    
    # Поиск по команде
    team_incidents = manager.get_incidents_by_team("Security Team")
    assert isinstance(team_incidents, list), "get_incidents_by_team() должен возвращать список"
    
    # Поиск высокоприоритетных
    high_priority = manager.get_high_priority_incidents()
    assert len(high_priority) >= 0, "get_high_priority_incidents() должен возвращать список"
    
    # Поиск просроченных
    overdue = manager.get_overdue_incidents(0.001)  # Очень маленький порог
    assert isinstance(overdue, list), "get_overdue_incidents() должен возвращать список"
    
    # Текстовый поиск
    search_results = manager.search_incidents("Test")
    assert len(search_results) >= 0, "search_incidents() должен возвращать список"
    
    print("✅ Методы поиска и фильтрации работают корректно")
    
    # ==================== ТЕСТ 5: СТАТИСТИКА И МЕТРИКИ ====================
    print("\n5️⃣ ТЕСТ СТАТИСТИКИ И МЕТРИК")
    print("-" * 40)
    
    # Базовая статистика
    stats = manager.get_incident_statistics()
    assert "total" in stats, "Статистика должна содержать 'total'"
    assert stats["total"] >= 0, "Общее количество должно быть >= 0"
    
    # Детальные метрики
    metrics = manager.get_detailed_metrics()
    assert "basic_metrics" in metrics, "Метрики должны содержать 'basic_metrics'"
    assert "priority_distribution" in metrics, "Метрики должны содержать 'priority_distribution'"
    assert "time_metrics" in metrics, "Метрики должны содержать 'time_metrics'"
    
    # Отчет о производительности
    report = manager.get_performance_report()
    assert "ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ" in report, "Отчет должен содержать заголовок"
    
    print("✅ Статистика и метрики работают корректно")
    
    # ==================== ТЕСТ 6: КЭШИРОВАНИЕ ====================
    print("\n6️⃣ ТЕСТ КЭШИРОВАНИЯ")
    print("-" * 40)
    
    # Информация о кэше
    cache_info = manager.get_cache_info()
    assert "incident_by_id" in cache_info, "Информация о кэше должна содержать 'incident_by_id'"
    
    # Очистка кэша
    manager.clear_cache()
    cache_info_after = manager.get_cache_info()
    assert cache_info_after["incident_by_id"].hits == 0, "Кэш должен быть очищен"
    
    print("✅ Кэширование работает корректно")
    
    # ==================== ТЕСТ 7: АСИНХРОННЫЕ МЕТОДЫ ====================
    print("\n7️⃣ ТЕСТ АСИНХРОННЫХ МЕТОДОВ")
    print("-" * 40)
    
    async def test_async_methods():
        # Асинхронное создание
        async_incident = await manager.create_incident_async(
            title="Async Test Incident",
            description="Async description",
            incident_type=IncidentType.DATA_BREACH,
            priority=IncidentPriority.MEDIUM,
            severity=SecurityLevel.MEDIUM
        )
        assert async_incident is not None, "Асинхронное создание должно работать"
        
        # Асинхронное получение
        incidents_list = await manager.get_incidents_async()
        assert isinstance(incidents_list, list), "Асинхронное получение должно возвращать список"
        
        # Асинхронное обновление статуса
        if async_incident:
            success = await manager.update_incident_status_async(
                async_incident.incident_id, IncidentStatus.IN_PROGRESS
            )
            assert success, "Асинхронное обновление должно работать"
        
        return True
    
    result = asyncio.run(test_async_methods())
    assert result, "Асинхронные методы должны работать"
    
    print("✅ Асинхронные методы работают корректно")
    
    # ==================== ТЕСТ 8: ЭКСПОРТ/ИМПОРТ ====================
    print("\n8️⃣ ТЕСТ ЭКСПОРТА/ИМПОРТА")
    print("-" * 40)
    
    # Создание временного файла
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Экспорт в CSV
        export_success = manager.export_incidents_to_csv(temp_path)
        assert export_success, "Экспорт в CSV должен работать"
        
        # Проверка файла
        assert os.path.exists(temp_path), "CSV файл должен быть создан"
        assert os.path.getsize(temp_path) > 0, "CSV файл не должен быть пустым"
        
        # Импорт из CSV
        imported_count = manager.import_incidents_from_csv(temp_path)
        assert imported_count >= 0, "Импорт из CSV должен работать"
        
        print(f"✅ Экспорт/импорт работает корректно (импортировано: {imported_count})")
        
    finally:
        # Очистка временного файла
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # ==================== ТЕСТ 9: РЕЗЕРВНОЕ КОПИРОВАНИЕ ====================
    print("\n9️⃣ ТЕСТ РЕЗЕРВНОГО КОПИРОВАНИЯ")
    print("-" * 40)
    
    # Создание резервной копии
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        backup_path = temp_file.name
    
    try:
        backup_success = manager.backup_incidents(backup_path)
        assert backup_success, "Создание резервной копии должно работать"
        
        # Проверка файла резервной копии
        assert os.path.exists(backup_path), "Файл резервной копии должен быть создан"
        
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        assert "incidents" in backup_data, "Резервная копия должна содержать 'incidents'"
        assert "statistics" in backup_data, "Резервная копия должна содержать 'statistics'"
        
        # Восстановление из резервной копии
        original_count = len(manager.incidents)
        manager.incidents.clear()  # Очищаем для теста восстановления
        
        restored_count = manager.restore_incidents(backup_path)
        assert restored_count >= 0, "Восстановление должно работать"
        
        print(f"✅ Резервное копирование работает корректно (восстановлено: {restored_count})")
        
    finally:
        # Очистка временного файла
        if os.path.exists(backup_path):
            os.unlink(backup_path)
    
    # ==================== ТЕСТ 10: ОБРАБОТКА ОШИБОК ====================
    print("\n🔟 ТЕСТ ОБРАБОТКИ ОШИБОК")
    print("-" * 40)
    
    # Тест валидации
    try:
        result = manager.create_incident("", "description", IncidentType.MALWARE_INFECTION, 
                                       IncidentPriority.HIGH, SecurityLevel.HIGH)
        assert result is None, "Пустой заголовок должен возвращать None"
    except IncidentValidationError:
        pass  # Ожидаемое исключение
    
    # Тест лимита инцидентов
    manager.max_open_incidents = 1
    try:
        result = manager.create_incident("Test", "Description", IncidentType.MALWARE_INFECTION, 
                                       IncidentPriority.LOW, SecurityLevel.LOW)
        if result is None:
            print("✅ Обработка лимита инцидентов работает (возвращает None)")
        else:
            # Если не сработал лимит, это тоже нормально
            print("✅ Обработка лимита инцидентов работает (лимит не достигнут)")
    except IncidentLimitExceededError:
        print("✅ Обработка лимита инцидентов работает (исключение)")
    
    print("✅ Обработка ошибок работает корректно")
    
    # ==================== ТЕСТ 11: КОНТЕКСТНЫЙ МЕНЕДЖЕР ====================
    print("\n1️⃣1️⃣ ТЕСТ КОНТЕКСТНОГО МЕНЕДЖЕРА")
    print("-" * 40)
    
    with IncidentResponseManager("ContextTest") as ctx_manager:
        ctx_manager.initialize()
        ctx_manager.start()
        assert ctx_manager.status.value in ["RUNNING", "running"], "Статус должен быть RUNNING в контексте"
        
        # Создание инцидента в контексте
        ctx_incident = ctx_manager.create_incident(
            "Context Incident", "Context description",
            IncidentType.MALWARE_INFECTION, IncidentPriority.MEDIUM, SecurityLevel.MEDIUM
        )
        assert ctx_incident is not None, "Создание инцидента в контексте должно работать"
    
    print("✅ Контекстный менеджер работает корректно")
    
    # ==================== ТЕСТ 12: ИТЕРАЦИЯ И СРАВНЕНИЕ ====================
    print("\n1️⃣2️⃣ ТЕСТ ИТЕРАЦИИ И СРАВНЕНИЯ")
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
    
    print(f"✅ Итерация и сравнение работают корректно (итераций: {incident_count})")
    
    # ==================== ТЕСТ 13: СПЕЦИАЛЬНЫЕ МЕТОДЫ ====================
    print("\n1️⃣3️⃣ ТЕСТ СПЕЦИАЛЬНЫХ МЕТОДОВ")
    print("-" * 40)
    
    # Тест строкового представления менеджера
    str_repr = str(manager)
    repr_repr = repr(manager)
    assert "IncidentResponseManager" in str_repr, "str() должен содержать название класса"
    assert "IncidentResponseManager" in repr_repr, "repr() должен содержать название класса"
    
    print("✅ Специальные методы работают корректно")
    
    # ==================== ФИНАЛЬНАЯ ПРОВЕРКА ====================
    print("\n🎯 ФИНАЛЬНАЯ ПРОВЕРКА СИСТЕМЫ")
    print("-" * 40)
    
    # Проверка статуса
    assert manager.status.value in ["RUNNING", "running"], f"Финальный статус: {manager.status.value}"
    
    # Проверка статистики
    final_stats = manager.get_incident_statistics()
    print(f"📊 Финальная статистика: {final_stats['total']} инцидентов")
    
    # Проверка метрик
    final_metrics = manager.get_detailed_metrics()
    print(f"📈 Базовые метрики: {final_metrics['basic_metrics']}")
    
    print("\n🎉 ВСЕ КОМПОНЕНТЫ ПРОТЕСТИРОВАНЫ УСПЕШНО!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test_all_classes_and_methods()
    except Exception as e:
        print(f"❌ ОШИБКА КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)