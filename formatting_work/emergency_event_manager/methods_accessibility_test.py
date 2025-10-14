#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест доступности и вызова всех методов EmergencyEventManager
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from datetime import datetime
from security.ai_agents.emergency_event_manager import EmergencyEventManager
from security.ai_agents.emergency_models import EmergencyType, EmergencySeverity, ResponseStatus

def test_all_methods():
    """Тестирует все методы EmergencyEventManager"""
    
    print("🧪 ТЕСТ ДОСТУПНОСТИ И ВЫЗОВА ВСЕХ МЕТОДОВ")
    print("=" * 60)
    
    try:
        # Создаем экземпляр
        print("1️⃣ Создание экземпляра...")
        manager = EmergencyEventManager()
        print("✅ EmergencyEventManager создан")
        
        # Тест 1: create_event
        print("\n2️⃣ Тест create_event...")
        event = manager.create_event(
            emergency_type=EmergencyType.SECURITY,
            severity=EmergencySeverity.HIGH,
            location={"lat": 55.7558, "lon": 37.6176, "address": "Москва"},
            description="Security breach detected in main system",
            user_id="test_user_123"
        )
        print(f"✅ create_event: {event.event_id}")
        
        # Тест 2: get_event
        print("\n3️⃣ Тест get_event...")
        retrieved_event = manager.get_event(event.event_id)
        if retrieved_event:
            print(f"✅ get_event: {retrieved_event.event_id}")
        else:
            print("❌ get_event: событие не найдено")
            return False
        
        # Тест 3: update_event_status
        print("\n4️⃣ Тест update_event_status...")
        success = manager.update_event_status(event.event_id, ResponseStatus.IN_PROGRESS)
        if success:
            print("✅ update_event_status: успешно")
        else:
            print("❌ update_event_status: ошибка")
            return False
        
        # Тест 4: get_events_by_type
        print("\n5️⃣ Тест get_events_by_type...")
        events_by_type = manager.get_events_by_type(EmergencyType.SECURITY)
        print(f"✅ get_events_by_type: {len(events_by_type)} событий")
        
        # Тест 5: get_events_by_severity
        print("\n6️⃣ Тест get_events_by_severity...")
        events_by_severity = manager.get_events_by_severity(EmergencySeverity.HIGH)
        print(f"✅ get_events_by_severity: {len(events_by_severity)} событий")
        
        # Тест 6: get_recent_events
        print("\n7️⃣ Тест get_recent_events...")
        recent_events = manager.get_recent_events(hours=1)
        print(f"✅ get_recent_events: {len(recent_events)} событий")
        
        # Тест 7: get_event_statistics
        print("\n8️⃣ Тест get_event_statistics...")
        stats = manager.get_event_statistics()
        if stats and 'total_events' in stats:
            print(f"✅ get_event_statistics: {stats['total_events']} событий")
        else:
            print("❌ get_event_statistics: ошибка")
            return False
        
        # Тест 8: cleanup_old_events
        print("\n9️⃣ Тест cleanup_old_events...")
        cleaned_count = manager.cleanup_old_events(days=0)  # Очистить все
        print(f"✅ cleanup_old_events: {cleaned_count} событий удалено")
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ МЕТОДЫ РАБОТАЮТ КОРРЕКТНО!")
        print("✅ Все 8 public методов доступны и функциональны")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_methods()
    sys.exit(0 if success else 1)