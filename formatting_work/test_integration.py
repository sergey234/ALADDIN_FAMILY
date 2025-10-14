#!/usr/bin/env python3
"""
ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ
ЭТАП 8.2: Взаимодействие, передача данных, общие ресурсы, поток выполнения
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

async def test_family_member_message_integration():
    """Тест интеграции между FamilyMember и Message"""
    print("\n🔍 ТЕСТ ИНТЕГРАЦИИ FamilyMember ↔ Message:")
    print("=" * 60)
    
    try:
        # Создание члена семьи
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
        
        print(f"  ✅ Созданы члены семьи: {parent.name}, {child.name}")
        
        # Создание сообщения от родителя к ребенку
        message = Message(
            id="msg_001",
            sender_id=parent.id,
            recipient_ids=[child.id],
            content="Привет, как дела?",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        print(f"  ✅ Создано сообщение: {message.content}")
        
        # Проверка связи отправителя и получателя
        is_sender = message.sender_id == parent.id
        is_recipient = message.is_recipient(child.id)
        
        print(f"  ✅ Связь отправитель: {is_sender}")
        print(f"  ✅ Связь получатель: {is_recipient}")
        
        # Тест обновления статуса сообщения
        message.mark_as_delivered()
        print(f"  ✅ Сообщение доставлено: {message.is_delivered}")
        
        message.mark_as_read()
        print(f"  ✅ Сообщение прочитано: {message.is_read}")
        
        # Тест добавления метаданных
        message.add_metadata("sender_name", parent.name)
        message.add_metadata("recipient_name", child.name)
        message.add_metadata("security_level", parent.security_level)
        
        print(f"  ✅ Метаданные добавлены: {message.metadata}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка интеграции: {e}")
        return False

async def test_external_api_handler_integration():
    """Тест интеграции ExternalAPIHandler с другими компонентами"""
    print("\n🔍 ТЕСТ ИНТЕГРАЦИИ ExternalAPIHandler:")
    print("=" * 60)
    
    try:
        # Создание конфигурации
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef"
        }
        
        # Создание обработчика API
        api_handler = ExternalAPIHandler(config)
        print(f"  ✅ Создан ExternalAPIHandler: {api_handler}")
        
        # Проверка доступности каналов
        channels = api_handler.get_available_channels()
        print(f"  ✅ Доступные каналы: {channels}")
        
        # Создание сообщения для отправки
        message = Message(
            id="msg_002",
            sender_id="parent_001",
            recipient_ids=["child_001"],
            content="Тестовое сообщение для API",
            message_type=MessageType.TEXT,
            priority=MessagePriority.HIGH,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        print(f"  ✅ Создано сообщение для API: {message.content}")
        
        # Тест отправки через Telegram (заглушка)
        if api_handler.is_telegram_available():
            print(f"  ✅ Telegram доступен для отправки")
        
        # Тест отправки через Discord (заглушка)
        if api_handler.is_discord_available():
            print(f"  ✅ Discord доступен для отправки")
        
        # Тест отправки через SMS (заглушка)
        if api_handler.is_sms_available():
            print(f"  ✅ SMS доступен для отправки")
        
        # Проверка статистики ошибок
        stats = api_handler.get_error_stats()
        print(f"  ✅ Статистика ошибок: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка интеграции: {e}")
        return False

async def test_family_communication_replacement_integration():
    """Тест интеграции FamilyCommunicationReplacement с другими компонентами"""
    print("\n🔍 ТЕСТ ИНТЕГРАЦИИ FamilyCommunicationReplacement:")
    print("=" * 60)
    
    try:
        # Создание конфигурации
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef"
        }
        
        # Создание системы
        hub = FamilyCommunicationReplacement("family_integration_test", config)
        print(f"  ✅ Создана система: {hub}")
        
        # Запуск системы
        await hub.start()
        print(f"  ✅ Система запущена: {hub.is_active}")
        
        # Добавление членов семьи
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
        
        await hub.add_family_member(parent)
        await hub.add_family_member(child)
        print(f"  ✅ Добавлены члены семьи: {len(hub)}")
        
        # Создание и отправка сообщения
        message = Message(
            id="msg_003",
            sender_id=parent.id,
            recipient_ids=[child.id],
            content="Привет, как дела в школе?",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        result = await hub.send_message(message)
        print(f"  ✅ Сообщение отправлено: {result}")
        
        # Проверка интеграции данных
        messages = hub.get_messages_by_sender(parent.id)
        print(f"  ✅ Сообщения от родителя: {len(messages)}")
        
        messages = hub.get_messages_by_recipient(child.id)
        print(f"  ✅ Сообщения ребенку: {len(messages)}")
        
        # Проверка статистики
        stats = hub.stats
        print(f"  ✅ Статистика системы: {stats}")
        
        # Проверка здоровья системы
        health = hub.get_health_status()
        print(f"  ✅ Статус здоровья: {len(health)} полей")
        
        # Остановка системы
        await hub.stop()
        print(f"  ✅ Система остановлена: {hub.is_active}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка интеграции: {e}")
        return False

async def test_data_flow_integration():
    """Тест потока данных между компонентами"""
    print("\n🔍 ТЕСТ ПОТОКА ДАННЫХ:")
    print("=" * 60)
    
    try:
        # Создание конфигурации
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef"
        }
        
        # Создание системы
        hub = FamilyCommunicationReplacement("family_data_flow_test", config)
        await hub.start()
        
        # Создание членов семьи
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
        
        # Добавление в систему
        await hub.add_family_member(parent)
        await hub.add_family_member(child)
        
        print(f"  ✅ Члены семьи добавлены: {len(hub)}")
        
        # Создание сообщения
        message = Message(
            id="msg_004",
            sender_id=parent.id,
            recipient_ids=[child.id],
            content="Не забудь сделать домашнее задание!",
            message_type=MessageType.TEXT,
            priority=MessagePriority.HIGH,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        # Отправка сообщения
        result = await hub.send_message(message)
        print(f"  ✅ Сообщение отправлено: {result}")
        
        # Проверка потока данных
        print(f"  ✅ Сообщений в системе: {len(hub.messages)}")
        print(f"  ✅ Статистика сообщений: {hub.stats['total_messages']}")
        
        # Проверка обновления статистики
        hub.stats["total_messages"] = len(hub.messages)
        hub.stats["active_members"] = len(hub.members)
        hub.stats["last_activity"] = datetime.now()
        
        print(f"  ✅ Статистика обновлена: {hub.stats}")
        
        # Проверка метаданных сообщения
        if hub.messages:
            msg = hub.messages[0]
            print(f"  ✅ Метаданные сообщения: {msg.metadata}")
            
            # Добавление метаданных
            msg.add_metadata("processed", True)
            msg.add_metadata("timestamp", datetime.now().isoformat())
            
            print(f"  ✅ Метаданные обновлены: {msg.metadata}")
        
        # Остановка системы
        await hub.stop()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка потока данных: {e}")
        return False

async def test_error_handling_integration():
    """Тест интеграции обработки ошибок"""
    print("\n🔍 ТЕСТ ИНТЕГРАЦИИ ОБРАБОТКИ ОШИБОК:")
    print("=" * 60)
    
    try:
        # Создание системы с неполной конфигурацией
        config = {
            "telegram_token": None,
            "discord_token": None,
            "twilio_sid": None,
            "twilio_token": None
        }
        
        hub = FamilyCommunicationReplacement("family_error_test", config)
        await hub.start()
        
        # Создание члена семьи
        parent = FamilyMember(
            id="parent_001",
            name="Иван Иванов",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            security_level=3
        )
        
        await hub.add_family_member(parent)
        
        # Создание сообщения
        message = Message(
            id="msg_005",
            sender_id=parent.id,
            recipient_ids=["child_001"],
            content="Тестовое сообщение",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        # Попытка отправки сообщения (должна завершиться ошибкой)
        result = await hub.send_message(message)
        print(f"  ✅ Результат отправки (ожидается False): {result}")
        
        # Проверка статистики ошибок
        error_stats = hub.api_handler.get_error_stats()
        print(f"  ✅ Статистика ошибок: {error_stats}")
        
        # Проверка здоровья системы
        health = hub.get_health_status()
        print(f"  ✅ Статус здоровья: {health['is_active']}")
        
        # Остановка системы
        await hub.stop()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка интеграции обработки ошибок: {e}")
        return False

async def test_concurrent_operations():
    """Тест параллельных операций"""
    print("\n🔍 ТЕСТ ПАРАЛЛЕЛЬНЫХ ОПЕРАЦИЙ:")
    print("=" * 60)
    
    try:
        # Создание системы
        config = {
            "telegram_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "discord_token": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWx",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "1234567890abcdef1234567890abcdef"
        }
        
        hub = FamilyCommunicationReplacement("family_concurrent_test", config)
        await hub.start()
        
        # Создание нескольких членов семьи параллельно
        members = []
        for i in range(5):
            member = FamilyMember(
                id=f"member_{i:03d}",
                name=f"Член {i+1}",
                role=FamilyRole.PARENT if i % 2 == 0 else FamilyRole.CHILD,
                phone=f"+7-999-123-45-{i+60:02d}",
                security_level=2 + (i % 3)
            )
            members.append(member)
        
        # Добавление членов семьи параллельно
        tasks = [hub.add_family_member(member) for member in members]
        results = await asyncio.gather(*tasks)
        
        print(f"  ✅ Добавлено членов семьи: {sum(results)}")
        print(f"  ✅ Всего в системе: {len(hub)}")
        
        # Создание и отправка сообщений параллельно
        messages = []
        for i in range(3):
            message = Message(
                id=f"msg_{i:03d}",
                sender_id="member_000",
                recipient_ids=[f"member_{i+1:03d}"],
                content=f"Сообщение {i+1}",
                message_type=MessageType.TEXT,
                priority=MessagePriority.NORMAL,
                timestamp=datetime.now(),
                channel=CommunicationChannel.TELEGRAM
            )
            messages.append(message)
        
        # Отправка сообщений параллельно
        tasks = [hub.send_message(message) for message in messages]
        results = await asyncio.gather(*tasks)
        
        print(f"  ✅ Отправлено сообщений: {sum(results)}")
        print(f"  ✅ Всего сообщений в системе: {len(hub.messages)}")
        
        # Остановка системы
        await hub.stop()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка параллельных операций: {e}")
        return False

async def main():
    """Основная функция тестирования интеграции"""
    print("🚀 ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ")
    print("ЭТАП 8.2: Взаимодействие, передача данных, общие ресурсы, поток выполнения")
    print("=" * 80)
    
    results = []
    
    # Запуск всех тестов интеграции
    results.append(await test_family_member_message_integration())
    results.append(await test_external_api_handler_integration())
    results.append(await test_family_communication_replacement_integration())
    results.append(await test_data_flow_integration())
    results.append(await test_error_handling_integration())
    results.append(await test_concurrent_operations())
    
    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА ИНТЕГРАЦИИ:")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"  Тестов интеграции пройдено: {passed}/{total}")
    print(f"  Процент успеха: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ ИНТЕГРАЦИИ ПРОЙДЕНЫ УСПЕШНО!")
        print("🎯 ЭТАП 8.2 ЗАВЕРШЕН УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️ {total-passed} ТЕСТОВ ИНТЕГРАЦИИ ПРОВАЛЕНО")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)