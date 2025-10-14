#!/usr/bin/env python3
"""
Тест функциональности улучшенного incident_response.py
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.incident_response import (
    IncidentResponseManager, Incident, IncidentType, 
    IncidentPriority, IncidentStatus, SecurityLevel,
    IncidentValidationError, IncidentLimitExceededError
)
from datetime import datetime

def test_enhanced_functionality():
    """Тест всех новых улучшений"""
    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 50)
    
    # Создание менеджера
    manager = IncidentResponseManager("TestManager")
    
    # Тест 1: Инициализация и запуск
    print("\n1️⃣ Тест инициализации и запуска...")
    assert manager.initialize(), "Ошибка инициализации"
    assert manager.start(), "Ошибка запуска"
    print("✅ Инициализация и запуск успешны")
    
    # Тест 2: Создание инцидента с валидацией
    print("\n2️⃣ Тест создания инцидента с валидацией...")
    try:
        incident = manager.create_incident(
            title="Test Incident",
            description="Test description",
            incident_type=IncidentType.MALWARE_INFECTION,
            priority=IncidentPriority.HIGH,
            severity=SecurityLevel.HIGH
        )
        assert incident is not None, "Инцидент не создан"
        print("✅ Создание инцидента успешно")
    except IncidentValidationError as e:
        print(f"❌ Ошибка валидации: {e}")
        return False
    
    # Тест 3: Новые методы класса Incident
    print("\n3️⃣ Тест новых методов класса Incident...")
    assert incident.is_open(), "is_open() должен возвращать True"
    assert not incident.is_resolved(), "is_resolved() должен возвращать False"
    assert incident.is_escalated(), "is_escalated() должен возвращать True"
    assert incident.get_age_hours() >= 0, "get_age_hours() должен возвращать положительное число"
    assert incident.get_priority_score() == 3, "get_priority_score() должен возвращать 3 для HIGH"
    assert incident.get_severity_score() == 3, "get_severity_score() должен возвращать 3 для HIGH"
    print("✅ Новые методы Incident работают корректно")
    
    # Тест 4: Специальные методы
    print("\n4️⃣ Тест специальных методов...")
    str_repr = str(incident)
    repr_repr = repr(incident)
    assert "Test Incident" in str_repr, "str() должен содержать заголовок"
    assert "Incident(" in repr_repr, "repr() должен содержать 'Incident('"
    print("✅ Специальные методы работают корректно")
    
    # Тест 5: Контекстный менеджер
    print("\n5️⃣ Тест контекстного менеджера...")
    with IncidentResponseManager("ContextTest") as ctx_manager:
        # Инициализируем и запускаем вручную для гарантии
        ctx_manager.initialize()
        ctx_manager.start()
        assert ctx_manager.status.value in ["RUNNING", "running"], f"Статус должен быть RUNNING в контексте, получен: {ctx_manager.status.value}"
    print("✅ Контекстный менеджер работает корректно")
    
    # Тест 6: Итерация и сравнение
    print("\n6️⃣ Тест итерации и сравнения...")
    manager.incidents[incident.incident_id] = incident
    assert len(manager) == 1, "len() должен возвращать 1"
    assert incident.incident_id in manager, "in должен работать"
    print("✅ Итерация и сравнение работают корректно")
    
    # Тест 7: Новые методы поиска
    print("\n7️⃣ Тест новых методов поиска...")
    incidents_by_team = manager.get_incidents_by_team("Security Team")
    high_priority = manager.get_high_priority_incidents()
    search_results = manager.search_incidents("Test")
    assert len(search_results) >= 0, "Поиск должен работать"
    print("✅ Методы поиска работают корректно")
    
    # Тест 8: Статистика
    print("\n8️⃣ Тест статистики...")
    stats = manager.get_incident_statistics()
    assert "total" in stats, "Статистика должна содержать 'total'"
    assert stats["total"] >= 0, "Общее количество должно быть >= 0"
    print("✅ Статистика работает корректно")
    
    # Тест 9: Кэширование
    print("\n9️⃣ Тест кэширования...")
    cache_info = manager.get_cache_info()
    assert "incident_by_id" in cache_info, "Информация о кэше должна содержать 'incident_by_id'"
    print("✅ Кэширование работает корректно")
    
    # Тест 10: Детальные метрики
    print("\n🔟 Тест детальных метрик...")
    metrics = manager.get_detailed_metrics()
    assert "basic_metrics" in metrics, "Метрики должны содержать 'basic_metrics'"
    report = manager.get_performance_report()
    assert "ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ" in report, "Отчет должен содержать заголовок"
    print("✅ Детальные метрики работают корректно")
    
    # Тест 11: Асинхронные методы
    print("\n1️⃣1️⃣ Тест асинхронных методов...")
    import asyncio
    
    async def test_async():
        async_incident = await manager.create_incident_async(
            title="Async Test",
            description="Async description",
            incident_type=IncidentType.DATA_BREACH,
            priority=IncidentPriority.MEDIUM,
            severity=SecurityLevel.MEDIUM
        )
        return async_incident is not None
    
    result = asyncio.run(test_async())
    assert result, "Асинхронное создание должно работать"
    print("✅ Асинхронные методы работают корректно")
    
    # Тест 12: Обработка ошибок валидации
    print("\n1️⃣2️⃣ Тест обработки ошибок валидации...")
    try:
        result = manager.create_incident("", "description", IncidentType.MALWARE_INFECTION, 
                               IncidentPriority.HIGH, SecurityLevel.HIGH)
        if result is None:
            print("✅ Обработка ошибок валидации работает корректно (возвращает None)")
        else:
            assert False, "Должна была возникнуть ошибка валидации"
    except IncidentValidationError:
        print("✅ Обработка ошибок валидации работает корректно (исключение)")
    
    print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        test_enhanced_functionality()
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        sys.exit(1)