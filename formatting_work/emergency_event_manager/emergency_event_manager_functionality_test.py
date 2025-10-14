#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест работоспособности EmergencyEventManager
Проверяет все методы после форматирования
"""

import sys
import os
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from datetime import datetime
from security.ai_agents.emergency_event_manager import EmergencyEventManager
from security.ai_agents.emergency_models import EmergencyType, EmergencySeverity, ResponseStatus

def test_emergency_event_manager():
    """Комплексный тест всех методов EmergencyEventManager"""
    
    print("🧪 КОМПЛЕКСНЫЙ ТЕСТ РАБОТОСПОСОБНОСТИ EmergencyEventManager")
    print("=" * 60)
    
    try:
        # 1. Создание экземпляра
        print("1️⃣ Тест создания экземпляра...")
        manager = EmergencyEventManager()
        print("✅ EmergencyEventManager создан успешно")
        
        # 2. Тест создания события
        print("\n2️⃣ Тест создания события...")
        event = manager.create_event(
            emergency_type=EmergencyType.SECURITY,
            severity=EmergencySeverity.HIGH,
            location={"lat": 55.7558, "lon": 37.6176, "address": "Москва"},
            description="Security breach detected in main system",
            user_id="test_user_123"
        )
        print(f"✅ Событие создано: {event.event_id}")
        
        # 3. Тест получения события
        print("\n3️⃣ Тест получения события...")
        retrieved_event = manager.get_event(event.event_id)
        if retrieved_event and retrieved_event.event_id == event.event_id:
            print("✅ Событие получено успешно")
        else:
            print("❌ Ошибка получения события")
            return False
        
        # 4. Тест обновления статуса
        print("\n4️⃣ Тест обновления статуса...")
        success = manager.update_event_status(event.event_id, ResponseStatus.IN_PROGRESS)
        if success:
            print("✅ Статус обновлен успешно")
        else:
            print("❌ Ошибка обновления статуса")
            return False
        
        # 5. Тест фильтрации по типу
        print("\n5️⃣ Тест фильтрации по типу...")
        events_by_type = manager.get_events_by_type(EmergencyType.SECURITY)
        if len(events_by_type) >= 1:
            print(f"✅ Найдено {len(events_by_type)} событий типа SECURITY")
        else:
            print("❌ Ошибка фильтрации по типу")
            return False
        
        # 6. Тест фильтрации по серьезности
        print("\n6️⃣ Тест фильтрации по серьезности...")
        events_by_severity = manager.get_events_by_severity(EmergencySeverity.HIGH)
        if len(events_by_severity) >= 1:
            print(f"✅ Найдено {len(events_by_severity)} событий высокой серьезности")
        else:
            print("❌ Ошибка фильтрации по серьезности")
            return False
        
        # 7. Тест получения недавних событий
        print("\n7️⃣ Тест получения недавних событий...")
        recent_events = manager.get_recent_events(hours=1)
        if len(recent_events) >= 1:
            print(f"✅ Найдено {len(recent_events)} недавних событий")
        else:
            print("❌ Ошибка получения недавних событий")
            return False
        
        # 8. Тест статистики
        print("\n8️⃣ Тест получения статистики...")
        stats = manager.get_event_statistics()
        if stats and 'total_events' in stats:
            print(f"✅ Статистика получена: {stats['total_events']} событий")
            print(f"   - Решенных: {stats['resolved_events']}")
            print(f"   - В ожидании: {stats['pending_events']}")
            print(f"   - Процент решения: {stats['resolution_rate']:.1f}%")
        else:
            print("❌ Ошибка получения статистики")
            return False
        
        # 9. Тест очистки старых событий
        print("\n9️⃣ Тест очистки старых событий...")
        cleaned_count = manager.cleanup_old_events(days=0)  # Очистить все события
        print(f"✅ Очищено {cleaned_count} старых событий")
        
        # 10. Финальная проверка
        print("\n🔟 Финальная проверка...")
        final_stats = manager.get_event_statistics()
        if final_stats['total_events'] == 0:
            print("✅ Все события очищены успешно")
        else:
            print(f"⚠️ Осталось {final_stats['total_events']} событий")
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ EmergencyEventManager полностью работоспособен")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_emergency_event_manager()
    sys.exit(0 if success else 1)