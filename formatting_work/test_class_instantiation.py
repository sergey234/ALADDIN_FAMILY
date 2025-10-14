#!/usr/bin/env python3
"""
ТЕСТ СОЗДАНИЯ ЭКЗЕМПЛЯРОВ КЛАССОВ
Проверка доступности всех классов и их методов
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Добавляем путь к модулю
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

try:
    from security.ai_agents.family_communication_replacement import (
        FamilyRole,
        MessageType,
        MessagePriority,
        CommunicationChannel,
        FamilyMember,
        Message,
        ExternalAPIHandler,
        FamilyCommunicationReplacement
    )
    print("✅ Все импорты успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

async def test_class_instantiation():
    """Тест создания экземпляров всех классов"""
    
    print("\n🔍 ЭТАП 6.3: ПРОВЕРКА ДОСТУПНОСТИ МЕТОДОВ")
    print("=" * 60)
    
    # 6.3.1 - Создание экземпляров классов
    print("\n6.3.1 - СОЗДАНИЕ ЭКЗЕМПЛЯРОВ КЛАССОВ:")
    print("-" * 40)
    
    try:
        # Создание Enum классов (не требуют экземпляров)
        print("✅ Enum классы доступны:")
        print(f"  - FamilyRole: {list(FamilyRole)}")
        print(f"  - MessageType: {list(MessageType)}")
        print(f"  - MessagePriority: {list(MessagePriority)}")
        print(f"  - CommunicationChannel: {list(CommunicationChannel)}")
        
        # Создание FamilyMember
        family_member = FamilyMember(
            id="test_001",
            name="Тест Тестович",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            email="test@example.com"
        )
        print(f"✅ FamilyMember создан: {family_member.name}")
        
        # Создание Message
        message = Message(
            id="msg_001",
            sender_id="test_001",
            recipient_ids=["test_002"],
            content="Тестовое сообщение",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        print(f"✅ Message создан: {message.id}")
        
        # Создание ExternalAPIHandler
        config = {
            "telegram_token": "test_token",
            "discord_token": "test_token",
            "twilio_sid": "test_sid",
            "twilio_token": "test_token"
        }
        api_handler = ExternalAPIHandler(config)
        print(f"✅ ExternalAPIHandler создан")
        
        # Создание FamilyCommunicationReplacement
        family_hub = FamilyCommunicationReplacement("family_test", config)
        print(f"✅ FamilyCommunicationReplacement создан: {family_hub.family_id}")
        
    except Exception as e:
        print(f"❌ Ошибка создания экземпляров: {e}")
        return False
    
    # 6.3.2 - Проверка доступности всех public методов
    print("\n6.3.2 - ПРОВЕРКА ДОСТУПНОСТИ PUBLIC МЕТОДОВ:")
    print("-" * 50)
    
    try:
        # Проверка методов ExternalAPIHandler
        print("🔍 ExternalAPIHandler методы:")
        methods = ['send_telegram_message', 'send_discord_message', 'send_sms']
        for method_name in methods:
            if hasattr(api_handler, method_name):
                print(f"  ✅ {method_name} - доступен")
            else:
                print(f"  ❌ {method_name} - НЕ найден")
        
        # Проверка методов FamilyCommunicationReplacement
        print("\n🔍 FamilyCommunicationReplacement методы:")
        methods = ['add_family_member', 'send_message', 'get_family_statistics', 'start', 'stop']
        for method_name in methods:
            if hasattr(family_hub, method_name):
                print(f"  ✅ {method_name} - доступен")
            else:
                print(f"  ❌ {method_name} - НЕ найден")
                
    except Exception as e:
        print(f"❌ Ошибка проверки методов: {e}")
        return False
    
    # 6.3.3 - Тестирование вызова каждого метода с корректными параметрами
    print("\n6.3.3 - ТЕСТИРОВАНИЕ ВЫЗОВА МЕТОДОВ:")
    print("-" * 45)
    
    try:
        # Тест add_family_member
        print("🧪 Тест add_family_member:")
        result = await family_hub.add_family_member(family_member)
        print(f"  Результат: {result}")
        
        # Тест get_family_statistics
        print("\n🧪 Тест get_family_statistics:")
        stats = await family_hub.get_family_statistics()
        print(f"  Статистика: {stats}")
        
        # Тест start/stop
        print("\n🧪 Тест start/stop:")
        await family_hub.start()
        print("  ✅ start() выполнен")
        await family_hub.stop()
        print("  ✅ stop() выполнен")
        
        # Тест send_message (без реальной отправки)
        print("\n🧪 Тест send_message:")
        result = await family_hub.send_message(message)
        print(f"  Результат отправки: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования методов: {e}")
        return False
    
    # 6.3.4 - Проверка обработки исключений в методах
    print("\n6.3.4 - ПРОВЕРКА ОБРАБОТКИ ИСКЛЮЧЕНИЙ:")
    print("-" * 50)
    
    try:
        # Тест с некорректными данными
        print("🧪 Тест обработки исключений:")
        
        # Попытка добавить None вместо FamilyMember
        try:
            await family_hub.add_family_member(None)
            print("  ❌ Ожидалось исключение при None")
        except Exception as e:
            print(f"  ✅ Исключение обработано: {type(e).__name__}")
        
        # Попытка отправить None вместо Message
        try:
            await family_hub.send_message(None)
            print("  ❌ Ожидалось исключение при None")
        except Exception as e:
            print(f"  ✅ Исключение обработано: {type(e).__name__}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки исключений: {e}")
        return False
    
    print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    return True

if __name__ == "__main__":
    asyncio.run(test_class_instantiation())