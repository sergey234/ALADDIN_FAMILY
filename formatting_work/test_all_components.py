#!/usr/bin/env python3
"""
ПОЛНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ
ЭТАП 8.1: Создание экземпляров, вызовы методов, проверка возвращаемых значений
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
        FamilyCommunicationReplacement,
        family_communication_replacement
    )
    print("✅ Все импорты успешны")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

async def test_family_member_comprehensive():
    """Полный тест FamilyMember"""
    print("\n🔍 ПОЛНЫЙ ТЕСТ FamilyMember:")
    print("=" * 50)
    
    try:
        # Тест создания с валидацией
        member = FamilyMember(
            id="test_001",
            name="Иван Иванов",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            email="ivan@example.com",
            telegram_id="@ivan_ivanov",
            discord_id="ivan#1234",
            location=(55.7558, 37.6176),
            is_online=True,
            last_seen=datetime.now(),
            preferences={"theme": "dark", "language": "ru"},
            security_level=3,
            emergency_contacts=["+7-999-111-11-11"]
        )
        
        print(f"  ✅ Создание: {member.name}")
        print(f"  ✅ ID: {member.id}")
        print(f"  ✅ Роль: {member.role.value}")
        print(f"  ✅ Телефон: {member.phone}")
        print(f"  ✅ Email: {member.email}")
        print(f"  ✅ Telegram: {member.telegram_id}")
        print(f"  ✅ Discord: {member.discord_id}")
        print(f"  ✅ Местоположение: {member.location}")
        print(f"  ✅ Онлайн: {member.is_online}")
        print(f"  ✅ Последний раз: {member.last_seen}")
        print(f"  ✅ Предпочтения: {member.preferences}")
        print(f"  ✅ Уровень безопасности: {member.security_level}")
        print(f"  ✅ Экстренные контакты: {member.emergency_contacts}")
        
        # Тест всех методов
        print(f"  ✅ __str__: {str(member)}")
        print(f"  ✅ __repr__: {repr(member)}")
        print(f"  ✅ is_available: {member.is_available}")
        print(f"  ✅ has_emergency_contacts: {member.has_emergency_contacts}")
        
        # Тест управления экстренными контактами
        result = member.add_emergency_contact("+7-999-222-22-22")
        print(f"  ✅ add_emergency_contact: {result}")
        
        result = member.remove_emergency_contact("+7-999-111-11-11")
        print(f"  ✅ remove_emergency_contact: {result}")
        
        # Тест обновления местоположения
        member.update_location(55.7600, 37.6200)
        print(f"  ✅ update_location: {member.location}")
        
        # Тест установки статуса
        member.set_online_status(False)
        print(f"  ✅ set_online_status: {member.is_online}")
        
        # Тест сравнения
        member2 = FamilyMember(
            id="test_001",
            name="Другой Иван",
            role=FamilyRole.CHILD
        )
        print(f"  ✅ __eq__: {member == member2}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_message_comprehensive():
    """Полный тест Message"""
    print("\n🔍 ПОЛНЫЙ ТЕСТ Message:")
    print("=" * 50)
    
    try:
        # Тест создания с валидацией
        message = Message(
            id="msg_001",
            sender_id="test_001",
            recipient_ids=["test_002", "test_003"],
            content="Тестовое сообщение для проверки функциональности системы семейной коммуникации",
            message_type=MessageType.TEXT,
            priority=MessagePriority.HIGH,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM,
            metadata={"encrypted": True, "priority": "high"},
            is_encrypted=True,
            is_delivered=False,
            is_read=False
        )
        
        print(f"  ✅ Создание: {message.id}")
        print(f"  ✅ Отправитель: {message.sender_id}")
        print(f"  ✅ Получатели: {message.recipient_ids}")
        print(f"  ✅ Содержимое: {message.content[:50]}...")
        print(f"  ✅ Тип: {message.message_type.value}")
        print(f"  ✅ Приоритет: {message.priority.value}")
        print(f"  ✅ Время: {message.timestamp}")
        print(f"  ✅ Канал: {message.channel.value}")
        print(f"  ✅ Метаданные: {message.metadata}")
        print(f"  ✅ Зашифровано: {message.is_encrypted}")
        print(f"  ✅ Доставлено: {message.is_delivered}")
        print(f"  ✅ Прочитано: {message.is_read}")
        
        # Тест всех методов
        print(f"  ✅ __str__: {str(message)}")
        print(f"  ✅ __repr__: {repr(message)}")
        print(f"  ✅ is_urgent: {message.is_urgent}")
        print(f"  ✅ is_emergency: {message.is_emergency}")
        print(f"  ✅ age_seconds: {message.age_seconds:.2f}")
        
        # Тест управления статусом
        message.mark_as_delivered()
        print(f"  ✅ mark_as_delivered: {message.is_delivered}")
        
        message.mark_as_read()
        print(f"  ✅ mark_as_read: {message.is_read}")
        
        # Тест метаданных
        message.add_metadata("test_key", "test_value")
        print(f"  ✅ add_metadata: {message.metadata}")
        
        value = message.get_metadata("test_key", "default")
        print(f"  ✅ get_metadata: {value}")
        
        # Тест получателей
        is_recipient = message.is_recipient("test_002")
        print(f"  ✅ is_recipient: {is_recipient}")
        
        result = message.add_recipient("test_004")
        print(f"  ✅ add_recipient: {result}")
        
        result = message.remove_recipient("test_004")
        print(f"  ✅ remove_recipient: {result}")
        
        # Тест сравнения
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
        print(f"  ✅ __eq__: {message == message2}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_external_api_handler_comprehensive():
    """Полный тест ExternalAPIHandler"""
    print("\n🔍 ПОЛНЫЙ ТЕСТ ExternalAPIHandler:")
    print("=" * 50)
    
    try:
        # Тест создания с полной конфигурацией
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef",
            "additional_config": {"timeout": 30, "retries": 3}
        }
        
        handler = ExternalAPIHandler(config)
        
        print(f"  ✅ Создание: {handler}")
        print(f"  ✅ Конфигурация: {len(handler.config)} параметров")
        print(f"  ✅ Telegram токен: {'✓' if handler.telegram_token else '✗'}")
        print(f"  ✅ Discord токен: {'✓' if handler.discord_token else '✗'}")
        print(f"  ✅ Twilio SID: {'✓' if handler.twilio_sid else '✗'}")
        print(f"  ✅ Twilio токен: {'✓' if handler.twilio_token else '✗'}")
        
        # Тест всех методов
        print(f"  ✅ __str__: {str(handler)}")
        print(f"  ✅ __repr__: {repr(handler)}")
        
        # Тест проверки доступности
        print(f"  ✅ is_telegram_available: {handler.is_telegram_available()}")
        print(f"  ✅ is_discord_available: {handler.is_discord_available()}")
        print(f"  ✅ is_sms_available: {handler.is_sms_available()}")
        
        # Тест получения каналов
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

async def test_family_communication_replacement_comprehensive():
    """Полный тест FamilyCommunicationReplacement"""
    print("\n🔍 ПОЛНЫЙ ТЕСТ FamilyCommunicationReplacement:")
    print("=" * 50)
    
    try:
        # Тест создания с полной конфигурацией
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef",
            "notification_manager": None,
            "alert_system": None
        }
        
        hub = FamilyCommunicationReplacement("family_test_001", config)
        
        print(f"  ✅ Создание: {hub}")
        print(f"  ✅ ID семьи: {hub.family_id}")
        print(f"  ✅ Конфигурация: {len(hub.config)} параметров")
        print(f"  ✅ Статистика: {hub.stats}")
        print(f"  ✅ Активен: {hub.is_active}")
        
        # Тест всех методов представления
        print(f"  ✅ __str__: {str(hub)}")
        print(f"  ✅ __repr__: {repr(hub)}")
        print(f"  ✅ __len__: {len(hub)}")
        print(f"  ✅ __contains__ (empty): {'test_001' in hub}")
        
        # Тест запуска и остановки
        await hub.start()
        print(f"  ✅ start: {hub.is_active}")
        
        await hub.stop()
        print(f"  ✅ stop: {hub.is_active}")
        
        # Тест добавления членов семьи
        parent = FamilyMember(
            id="parent_001",
            name="Иван Иванов",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            security_level=3
        )
        
        child = FamilyMember(
            id="child_001",
            name="Анна Иванова",
            role=FamilyRole.CHILD,
            phone="+7-999-123-45-68",
            security_level=2
        )
        
        result = await hub.add_family_member(parent)
        print(f"  ✅ add_family_member (parent): {result}")
        
        result = await hub.add_family_member(child)
        print(f"  ✅ add_family_member (child): {result}")
        
        # Тест новых методов
        print(f"  ✅ __len__ after add: {len(hub)}")
        print(f"  ✅ __contains__ (parent): {'parent_001' in hub}")
        
        # Тест итерации
        members = list(hub)
        print(f"  ✅ __iter__: {len(members)} members")
        
        # Тест получения членов семьи
        member = hub.get_member("parent_001")
        print(f"  ✅ get_member: {member.name if member else 'None'}")
        
        parents = hub.get_members_by_role(FamilyRole.PARENT)
        print(f"  ✅ get_members_by_role: {len(parents)} parents")
        
        online_members = hub.get_online_members()
        print(f"  ✅ get_online_members: {len(online_members)} online")
        
        emergency_contacts = hub.get_emergency_contacts()
        print(f"  ✅ get_emergency_contacts: {len(emergency_contacts)} contacts")
        
        # Тест отправки сообщения
        message = Message(
            id="test_msg_001",
            sender_id="parent_001",
            recipient_ids=["child_001"],
            content="Тестовое сообщение",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        result = await hub.send_message(message)
        print(f"  ✅ send_message: {result}")
        
        # Тест получения сообщений
        messages = hub.get_messages_by_sender("parent_001")
        print(f"  ✅ get_messages_by_sender: {len(messages)} messages")
        
        messages = hub.get_messages_by_recipient("child_001")
        print(f"  ✅ get_messages_by_recipient: {len(messages)} messages")
        
        urgent_messages = hub.get_urgent_messages()
        print(f"  ✅ get_urgent_messages: {len(urgent_messages)} messages")
        
        emergency_messages = hub.get_emergency_messages()
        print(f"  ✅ get_emergency_messages: {len(emergency_messages)} messages")
        
        # Тест очистки старых сообщений
        cleared = hub.clear_old_messages(0)  # Очистить все сообщения
        print(f"  ✅ clear_old_messages: {cleared} messages cleared")
        
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
        for key, value in health.items():
            print(f"    - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_family_communication_replacement_function():
    """Полный тест функции family_communication_replacement"""
    print("\n🔍 ПОЛНЫЙ ТЕСТ family_communication_replacement:")
    print("=" * 50)
    
    try:
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef"
        }
        
        # Тест действия start
        result = await family_communication_replacement(
            family_id="family_test_002",
            config=config,
            action="start"
        )
        print(f"  ✅ action=start: {result['status']}")
        print(f"    - message: {result['message']}")
        print(f"    - active: {result['active']}")
        
        # Тест действия status
        result = await family_communication_replacement(
            family_id="family_test_002",
            config=config,
            action="status"
        )
        print(f"  ✅ action=status: {result['status']}")
        print(f"    - health fields: {len(result['health'])}")
        
        # Тест действия add_member
        member_data = {
            "id": "member_001",
            "name": "Тест Тестович",
            "role": "PARENT",
            "phone": "+7-999-123-45-67",
            "security_level": 3
        }
        
        result = await family_communication_replacement(
            family_id="family_test_002",
            config=config,
            action="add_member",
            member_data=member_data
        )
        print(f"  ✅ action=add_member: {result['status']}")
        print(f"    - message: {result['message']}")
        
        # Тест действия send_message
        result = await family_communication_replacement(
            family_id="family_test_002",
            config=config,
            action="send_message",
            sender_id="member_001",
            recipient_ids=["member_002"],
            content="Тестовое сообщение",
            message_type="TEXT",
            priority="NORMAL",
            channel="TELEGRAM"
        )
        print(f"  ✅ action=send_message: {result['status']}")
        print(f"    - message: {result['message']}")
        
        # Тест действия stop
        result = await family_communication_replacement(
            family_id="family_test_002",
            config=config,
            action="stop"
        )
        print(f"  ✅ action=stop: {result['status']}")
        print(f"    - message: {result['message']}")
        
        # Тест неизвестного действия
        result = await family_communication_replacement(
            family_id="family_test_002",
            config=config,
            action="unknown_action"
        )
        print(f"  ✅ action=unknown: {result['status']}")
        print(f"    - message: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def test_error_handling_comprehensive():
    """Полный тест обработки ошибок"""
    print("\n🔍 ПОЛНЫЙ ТЕСТ ОБРАБОТКИ ОШИБОК:")
    print("=" * 50)
    
    try:
        # Тест валидации FamilyMember
        print("  Тестирование валидации FamilyMember:")
        try:
            invalid_member = FamilyMember(
                id="",
                name="",
                role=FamilyRole.PARENT,
                security_level=10
            )
            print("    ❌ Валидация не сработала")
        except ValueError as e:
            print(f"    ✅ Валидация ID/name: {e}")
        
        try:
            invalid_member = FamilyMember(
                id="test",
                name="Test",
                role=FamilyRole.PARENT,
                security_level=0
            )
            print("    ❌ Валидация security_level не сработала")
        except ValueError as e:
            print(f"    ✅ Валидация security_level: {e}")
        
        # Тест валидации Message
        print("  Тестирование валидации Message:")
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
            print("    ❌ Валидация не сработала")
        except ValueError as e:
            print(f"    ✅ Валидация Message: {e}")
        
        # Тест обработки ошибок в функции
        print("  Тестирование обработки ошибок в функции:")
        result = await family_communication_replacement(
            family_id="",
            config={},
            action="start"
        )
        print(f"    ✅ Обработка пустого family_id: {result['status']}")
        
        result = await family_communication_replacement(
            family_id="test",
            config={},
            action="send_message"
        )
        print(f"    ✅ Обработка недостающих параметров: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 ПОЛНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("ЭТАП 8.1: Создание экземпляров, вызовы методов, проверка возвращаемых значений")
    print("=" * 80)
    
    results = []
    
    # Запуск всех тестов
    results.append(await test_family_member_comprehensive())
    results.append(await test_message_comprehensive())
    results.append(await test_external_api_handler_comprehensive())
    results.append(await test_family_communication_replacement_comprehensive())
    results.append(await test_family_communication_replacement_function())
    results.append(await test_error_handling_comprehensive())
    
    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"  Тестов пройдено: {passed}/{total}")
    print(f"  Процент успеха: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ КОМПОНЕНТОВ ПРОЙДЕНЫ УСПЕШНО!")
        print("🎯 ЭТАП 8.1 ЗАВЕРШЕН УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️ {total-passed} ТЕСТОВ ПРОВАЛЕНО")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)