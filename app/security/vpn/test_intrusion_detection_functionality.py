#!/usr/bin/env python3
"""
Комплексный тест работоспособности IntrusionDetectionSystem
"""
import sys
import os
import asyncio
sys.path.append('.')

async def test_intrusion_detection():
    try:
        from protection.intrusion_detection import IntrusionDetectionSystem
        print("✅ Импорт модуля успешен")
        
        # Создаем экземпляр системы
        ids = IntrusionDetectionSystem()
        print("✅ Создание экземпляра успешно")
        
        # Тестируем основные методы
        test_ip = "192.168.1.100"
        
        # Тест анализа запроса с правильными параметрами
        result = await ids.analyze_request(
            ip=test_ip,
            user_agent="Mozilla/5.0 (Test Browser)",
            endpoint="/admin",
            method="GET",
            payload="",
            headers={"User-Agent": "test"}
        )
        print(f"✅ Анализ запроса: {result[0]} (угроз: {len(result[1])})")
        
        # Тест проверки заблокированных IP
        is_blocked = ids.is_ip_blocked(test_ip)
        print(f"✅ Проверка блокировки IP: {is_blocked}")
        
        # Тест получения статистики
        stats = ids.get_statistics()
        print(f"✅ Получение статистики: {len(stats)} записей")
        
        # Тест получения событий угроз
        events = ids.get_threat_events()
        print(f"✅ Получение событий угроз: {len(events)} событий")
        
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_intrusion_detection())
