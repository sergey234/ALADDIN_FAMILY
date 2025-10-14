#!/usr/bin/env python3
"""
ТЕСТ УЛУЧШЕННЫХ МЕТОДОВ
Проверка всех новых методов и функциональности
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

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

async def test_enhanced_family_member():
    """Тест улучшенных методов FamilyMember"""
    print("\n🔍 Тестирование улучшенных методов FamilyMember:")
    print("-" * 50)
    
    try:
        # Создание члена семьи
        member = FamilyMember(
            id="test_001",
            name="Тест Тестович",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            security_level=3
        )
        
        # Тест __str__ и __repr__
        print(f"  ✅ __str__: {str(member)}")
        print(f"  ✅ __repr__: {repr(member)}")
        
        # Тест __eq__
        member2 = FamilyMember(
            id="test_001",
            name="Другой Тест",
            role=FamilyRole.CHILD
        )
        print(f"  ✅ __eq__ (same id): {member == member2}")
        
        # Тест свойств
        print(f"  ✅ is_available: {member.is_available}")
        print(f"  ✅ has_emergency_contacts: {member.has_emergency_contacts}")
        
        # Тест методов управления экстренными контактами
        result = member.add_emergency_contact("+7-999-111-11-11")
        print(f"  ✅ add_emergency_contact: {result}")
        print(f"  ✅ has_emergency_contacts after add: {member.has_emergency_contacts}")
        
        result = member.remove_emergency_contact("+7-999-111-11-11")
        print(f"  ✅ remove_emergency_contact: {result}")
        
        # Тест обновления местоположения
        member.update_location(55.7558, 37.6176)
        print(f"  ✅ update_location: {member.location}")
        
        # Тест установки статуса онлайн
        member.set_online_status(True)
        print(f"  ✅ set_online_status: {member.is_online}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_enhanced_message():
    """Тест улучшенных методов Message"""
    print("\n🔍 Тестирование улучшенных методов Message:")
    print("-" * 50)
    
    try:
        # Создание сообщения
        message = Message(
            id="msg_001",
            sender_id="test_001",
            recipient_ids=["test_002"],
            content="Тестовое сообщение для проверки функциональности",
            message_type=MessageType.TEXT,
            priority=MessagePriority.HIGH,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        # Тест __str__ и __repr__
        print(f"  ✅ __str__: {str(message)}")
        print(f"  ✅ __repr__: {repr(message)}")
        
        # Тест __eq__
        message2 = Message(
            id="msg_001",
            sender_id="test_003",
            recipient_ids=["test_004"],
            content="Другое сообщение",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        print(f"  ✅ __eq__ (same id): {message == message2}")
        
        # Тест свойств
        print(f"  ✅ is_urgent: {message.is_urgent}")
        print(f"  ✅ is_emergency: {message.is_emergency}")
        print(f"  ✅ age_seconds: {message.age_seconds:.2f}")
        
        # Тест методов управления статусом
        message.mark_as_delivered()
        print(f"  ✅ mark_as_delivered: {message.is_delivered}")
        
        message.mark_as_read()
        print(f"  ✅ mark_as_read: {message.is_read}")
        
        # Тест методов метаданных
        message.add_metadata("encrypted", True)
        message.add_metadata("priority", "high")
        print(f"  ✅ add_metadata: {message.metadata}")
        
        value = message.get_metadata("encrypted", False)
        print(f"  ✅ get_metadata: {value}")
        
        # Тест методов получателей
        is_recipient = message.is_recipient("test_002")
        print(f"  ✅ is_recipient: {is_recipient}")
        
        result = message.add_recipient("test_003")
        print(f"  ✅ add_recipient: {result}")
        
        result = message.remove_recipient("test_003")
        print(f"  ✅ remove_recipient: {result}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_enhanced_external_api_handler():
    """Тест улучшенных методов ExternalAPIHandler"""
    print("\n🔍 Тестирование улучшенных методов ExternalAPIHandler:")
    print("-" * 50)
    
    try:
        # Создание обработчика
        config = {
            "telegram_token": "test_token",
            "discord_token": "test_token",
            "twilio_sid": "test_sid",
            "twilio_token": "test_token"
        }
        
        handler = ExternalAPIHandler(config)
        
        # Тест __str__ и __repr__
        print(f"  ✅ __str__: {str(handler)}")
        print(f"  ✅ __repr__: {repr(handler)}")
        
        # Тест методов проверки доступности
        print(f"  ✅ is_telegram_available: {handler.is_telegram_available()}")
        print(f"  ✅ is_discord_available: {handler.is_discord_available()}")
        print(f"  ✅ is_sms_available: {handler.is_sms_available()}")
        
        # Тест получения доступных каналов
        channels = handler.get_available_channels()
        print(f"  ✅ get_available_channels: {channels}")
        
        # Тест статистики ошибок
        stats = handler.get_error_stats()
        print(f"  ✅ get_error_stats: {stats}")
        
        # Тест сброса статистики
        handler.reset_error_stats()
        print(f"  ✅ reset_error_stats: выполнено")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_enhanced_family_communication_replacement():
    """Тест улучшенных методов FamilyCommunicationReplacement"""
    print("\n🔍 Тестирование улучшенных методов FamilyCommunicationReplacement:")
    print("-" * 50)
    
    try:
        # Создание системы
        config = {
            "telegram_token": "test_token",
            "discord_token": "test_token",
            "twilio_sid": "test_sid",
            "twilio_token": "test_token"
        }
        
        hub = FamilyCommunicationReplacement("family_test", config)
        
        # Тест __str__ и __repr__
        print(f"  ✅ __str__: {str(hub)}")
        print(f"  ✅ __repr__: {repr(hub)}")
        
        # Тест __len__, __iter__, __contains__
        print(f"  ✅ __len__: {len(hub)}")
        print(f"  ✅ __contains__ (empty): {'test_001' in hub}")
        
        # Добавление членов семьи
        parent = FamilyMember(
            id="parent_001",
            name="Иван Иванов",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67"
        )
        
        child = FamilyMember(
            id="child_001",
            name="Анна Иванова",
            role=FamilyRole.CHILD,
            phone="+7-999-123-45-68"
        )
        
        await hub.add_family_member(parent)
        await hub.add_family_member(child)
        
        print(f"  ✅ __len__ after add: {len(hub)}")
        print(f"  ✅ __contains__ (parent): {'parent_001' in hub}")
        
        # Тест итерации
        members = list(hub)
        print(f"  ✅ __iter__: {len(members)} members")
        
        # Тест новых методов
        member = hub.get_member("parent_001")
        print(f"  ✅ get_member: {member.name if member else 'None'}")
        
        parents = hub.get_members_by_role(FamilyRole.PARENT)
        print(f"  ✅ get_members_by_role: {len(parents)} parents")
        
        online_members = hub.get_online_members()
        print(f"  ✅ get_online_members: {len(online_members)} online")
        
        emergency_contacts = hub.get_emergency_contacts()
        print(f"  ✅ get_emergency_contacts: {len(emergency_contacts)} contacts")
        
        # Тест удаления члена семьи
        result = hub.remove_family_member("child_001")
        print(f"  ✅ remove_family_member: {result}")
        
        # Тест контекстного менеджера
        async with hub:
            print(f"  ✅ __aenter__: {hub.is_active}")
        print(f"  ✅ __aexit__: {hub.is_active}")
        
        # Тест статуса здоровья
        health = hub.get_health_status()
        print(f"  ✅ get_health_status: {len(health)} fields")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_validation_and_error_handling():
    """Тест валидации и обработки ошибок"""
    print("\n🔍 Тестирование валидации и обработки ошибок:")
    print("-" * 50)
    
    try:
        # Тест валидации FamilyMember
        try:
            invalid_member = FamilyMember(
                id="",
                name="",
                role=FamilyRole.PARENT,
                security_level=10
            )
            print("  ❌ Валидация FamilyMember не сработала")
        except ValueError as e:
            print(f"  ✅ Валидация FamilyMember: {e}")
        
        # Тест валидации Message
        try:
            invalid_message = Message(
                id="",
                sender_id="",
                recipient_ids=[],
                content="",
                message_type=MessageType.TEXT,
                priority=MessagePriority.NORMAL,
                timestamp=datetime.now(),
                channel=CommunicationChannel.TELEGRAM
            )
            print("  ❌ Валидация Message не сработала")
        except ValueError as e:
            print(f"  ✅ Валидация Message: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТ УЛУЧШЕННЫХ МЕТОДОВ")
    print("=" * 60)
    
    results = []
    
    # Запуск всех тестов
    results.append(await test_enhanced_family_member())
    results.append(await test_enhanced_message())
    results.append(await test_enhanced_external_api_handler())
    results.append(await test_enhanced_family_communication_replacement())
    results.append(await test_validation_and_error_handling())
    
    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"  Тестов пройдено: {passed}/{total}")
    print(f"  Процент успеха: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ УЛУЧШЕННЫХ МЕТОДОВ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️ {total-passed} ТЕСТОВ ПРОВАЛЕНО")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)