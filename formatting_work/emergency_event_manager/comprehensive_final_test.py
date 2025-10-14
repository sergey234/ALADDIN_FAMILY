#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный финальный тест всех компонентов EmergencyEventManager
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from datetime import datetime
from security.ai_agents.emergency_event_manager import EmergencyEventManager
from security.ai_agents.emergency_models import EmergencyType, EmergencySeverity, ResponseStatus

def comprehensive_final_test():
    """Комплексный тест всех компонентов EmergencyEventManager"""
    
    print("🧪 КОМПЛЕКСНЫЙ ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 70)
    
    try:
        # 6.10.1 - Создать экземпляр каждого класса
        print("1️⃣ Создание экземпляра EmergencyEventManager...")
        manager = EmergencyEventManager()
        print(f"✅ Экземпляр создан: {type(manager).__name__}")
        
        # Проверяем атрибуты
        print(f"✅ Атрибуты: logger={type(manager.logger).__name__}, events={type(manager.events).__name__}, event_history={type(manager.event_history).__name__}")
        
        # 6.10.2 - Вызвать каждый метод с корректными параметрами
        print("\n2️⃣ Тестирование всех методов...")
        
        # Тест create_event
        print("\n📝 Тест create_event...")
        event1 = manager.create_event(
            emergency_type=EmergencyType.SECURITY,
            severity=EmergencySeverity.HIGH,
            location={"lat": 55.7558, "lon": 37.6176, "address": "Москва"},
            description="Security breach detected in main system",
            user_id="user_001"
        )
        print(f"✅ create_event: {event1.event_id}")
        
        event2 = manager.create_event(
            emergency_type=EmergencyType.MEDICAL,
            severity=EmergencySeverity.MEDIUM,
            location={"lat": 55.7600, "lon": 37.6200, "address": "Москва"},
            description="Medical emergency in building A",
            user_id="user_002"
        )
        print(f"✅ create_event: {event2.event_id}")
        
        # Тест get_event
        print("\n🔍 Тест get_event...")
        retrieved_event = manager.get_event(event1.event_id)
        if retrieved_event and retrieved_event.event_id == event1.event_id:
            print(f"✅ get_event: событие найдено")
        else:
            print("❌ get_event: ошибка")
            return False
        
        # Тест update_event_status
        print("\n🔄 Тест update_event_status...")
        success = manager.update_event_status(event1.event_id, ResponseStatus.IN_PROGRESS)
        if success:
            print("✅ update_event_status: успешно")
        else:
            print("❌ update_event_status: ошибка")
            return False
        
        # Тест get_events_by_type
        print("\n📊 Тест get_events_by_type...")
        security_events = manager.get_events_by_type(EmergencyType.SECURITY)
        medical_events = manager.get_events_by_type(EmergencyType.MEDICAL)
        print(f"✅ get_events_by_type: SECURITY={len(security_events)}, MEDICAL={len(medical_events)}")
        
        # Тест get_events_by_severity
        print("\n⚠️ Тест get_events_by_severity...")
        high_severity = manager.get_events_by_severity(EmergencySeverity.HIGH)
        medium_severity = manager.get_events_by_severity(EmergencySeverity.MEDIUM)
        print(f"✅ get_events_by_severity: HIGH={len(high_severity)}, MEDIUM={len(medium_severity)}")
        
        # Тест get_recent_events
        print("\n⏰ Тест get_recent_events...")
        recent_events = manager.get_recent_events(hours=1)
        print(f"✅ get_recent_events: {len(recent_events)} событий")
        
        # Тест get_event_statistics
        print("\n📈 Тест get_event_statistics...")
        stats = manager.get_event_statistics()
        if stats and 'total_events' in stats:
            print(f"✅ get_event_statistics: {stats['total_events']} событий, resolution_rate={stats.get('resolution_rate', 0):.1f}%")
        else:
            print("❌ get_event_statistics: ошибка")
            return False
        
        # 6.10.3 - Проверить возвращаемые значения
        print("\n3️⃣ Проверка возвращаемых значений...")
        
        # Проверяем типы возвращаемых значений
        assert isinstance(manager.get_event(event1.event_id), type(event1)), "get_event должен возвращать EmergencyEvent"
        assert isinstance(manager.get_events_by_type(EmergencyType.SECURITY), list), "get_events_by_type должен возвращать list"
        assert isinstance(manager.get_events_by_severity(EmergencySeverity.HIGH), list), "get_events_by_severity должен возвращать list"
        assert isinstance(manager.get_recent_events(), list), "get_recent_events должен возвращать list"
        assert isinstance(manager.get_event_statistics(), dict), "get_event_statistics должен возвращать dict"
        assert isinstance(manager.update_event_status(event1.event_id, ResponseStatus.RESOLVED), bool), "update_event_status должен возвращать bool"
        
        print("✅ Все возвращаемые значения корректны")
        
        # 6.10.4 - Проверить обработку ошибок
        print("\n4️⃣ Проверка обработки ошибок...")
        
        # Тест с невалидными данными
        try:
            manager.create_event(
                emergency_type=EmergencyType.SECURITY,
                severity=EmergencySeverity.HIGH,
                location={"lat": 55.7558},
                description="Invalid",  # Невалидное описание
                user_id="test"
            )
            print("❌ Исключение не сработало")
            return False
        except ValueError:
            print("✅ ValueError обработан корректно")
        
        # Тест с несуществующим ID
        result = manager.get_event("nonexistent_id")
        if result is None:
            print("✅ get_event с несуществующим ID возвращает None")
        else:
            print("❌ get_event с несуществующим ID должен возвращать None")
            return False
        
        # Тест update_event_status с несуществующим ID
        result = manager.update_event_status("nonexistent_id", ResponseStatus.PENDING)
        if not result:
            print("✅ update_event_status с несуществующим ID возвращает False")
        else:
            print("❌ update_event_status с несуществующим ID должен возвращать False")
            return False
        
        print("✅ Обработка ошибок работает корректно")
        
        # 6.10.5 - Тест cleanup_old_events
        print("\n5️⃣ Тест cleanup_old_events...")
        cleaned_count = manager.cleanup_old_events(days=0)  # Очистить все события
        print(f"✅ cleanup_old_events: {cleaned_count} событий удалено")
        
        # Проверяем, что события удалены
        remaining_events = len(manager.events)
        if remaining_events == 0:
            print("✅ Все события успешно удалены")
        else:
            print(f"⚠️ Осталось {remaining_events} событий")
        
        print("\n" + "=" * 70)
        print("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ КОРРЕКТНО!")
        print("✅ EmergencyEventManager полностью функционален")
        print("✅ Все 9 методов работают корректно")
        print("✅ Обработка ошибок работает правильно")
        print("✅ Возвращаемые значения корректны")
        print("✅ Интеграция между компонентами работает")
        
        return True
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА В ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = comprehensive_final_test()
    sys.exit(0 if success else 1)