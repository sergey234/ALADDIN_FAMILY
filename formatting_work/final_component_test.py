#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ
Полный тест всех классов, методов и функций
"""

import asyncio
import sys
import os
from datetime import datetime
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

class ComponentTestResult:
    """Результат тестирования компонента"""
    def __init__(self, name: str):
        self.name = name
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        self.warnings = []
    
    def add_success(self, test_name: str):
        self.tests_passed += 1
        print(f"  ✅ {test_name}")
    
    def add_failure(self, test_name: str, error: str):
        self.tests_failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"  ❌ {test_name}: {error}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append(f"{test_name}: {warning}")
        print(f"  ⚠️ {test_name}: {warning}")
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "total_tests": self.tests_passed + self.tests_failed,
            "success_rate": (self.tests_passed / (self.tests_passed + self.tests_failed)) * 100 if (self.tests_passed + self.tests_failed) > 0 else 0,
            "errors": self.errors,
            "warnings": self.warnings
        }

async def test_enum_classes():
    """Тест Enum классов"""
    result = ComponentTestResult("Enum Classes")
    
    print("\n🔍 Тестирование Enum классов:")
    print("-" * 40)
    
    # Тест FamilyRole
    try:
        assert FamilyRole.PARENT.value == "parent"
        assert FamilyRole.CHILD.value == "child"
        assert FamilyRole.ELDERLY.value == "elderly"
        assert FamilyRole.GUARDIAN.value == "guardian"
        result.add_success("FamilyRole values")
    except Exception as e:
        result.add_failure("FamilyRole values", str(e))
    
    # Тест MessageType
    try:
        assert MessageType.TEXT.value == "text"
        assert MessageType.VOICE.value == "voice"
        assert MessageType.IMAGE.value == "image"
        assert MessageType.VIDEO.value == "video"
        assert MessageType.EMERGENCY.value == "emergency"
        assert MessageType.LOCATION.value == "location"
        result.add_success("MessageType values")
    except Exception as e:
        result.add_failure("MessageType values", str(e))
    
    # Тест MessagePriority
    try:
        assert MessagePriority.LOW.value == "low"
        assert MessagePriority.NORMAL.value == "normal"
        assert MessagePriority.HIGH.value == "high"
        assert MessagePriority.URGENT.value == "urgent"
        assert MessagePriority.EMERGENCY.value == "emergency"
        result.add_success("MessagePriority values")
    except Exception as e:
        result.add_failure("MessagePriority values", str(e))
    
    # Тест CommunicationChannel
    try:
        assert CommunicationChannel.INTERNAL.value == "internal"
        assert CommunicationChannel.TELEGRAM.value == "telegram"
        assert CommunicationChannel.DISCORD.value == "discord"
        assert CommunicationChannel.SMS.value == "sms"
        assert CommunicationChannel.EMAIL.value == "email"
        assert CommunicationChannel.PUSH.value == "push"
        assert CommunicationChannel.VOICE_CALL.value == "voice_call"
        assert CommunicationChannel.VIDEO_CALL.value == "video_call"
        result.add_success("CommunicationChannel values")
    except Exception as e:
        result.add_failure("CommunicationChannel values", str(e))
    
    return result

async def test_dataclass_classes():
    """Тест Dataclass классов"""
    result = ComponentTestResult("Dataclass Classes")
    
    print("\n🔍 Тестирование Dataclass классов:")
    print("-" * 40)
    
    # Тест FamilyMember
    try:
        member = FamilyMember(
            id="test_001",
            name="Тест Тестович",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            email="test@example.com",
            telegram_id="123456789",
            discord_id="987654321",
            location=(55.7558, 37.6176),
            is_online=True,
            last_seen=datetime.now(),
            preferences={"theme": "dark", "language": "ru"},
            security_level=3,
            emergency_contacts=["+7-999-111-11-11", "+7-999-222-22-22"]
        )
        
        assert member.id == "test_001"
        assert member.name == "Тест Тестович"
        assert member.role == FamilyRole.PARENT
        assert member.phone == "+7-999-123-45-67"
        assert member.email == "test@example.com"
        assert member.telegram_id == "123456789"
        assert member.discord_id == "987654321"
        assert member.location == (55.7558, 37.6176)
        assert member.is_online == True
        assert member.last_seen is not None
        assert member.preferences == {"theme": "dark", "language": "ru"}
        assert member.security_level == 3
        assert member.emergency_contacts == ["+7-999-111-11-11", "+7-999-222-22-22"]
        
        result.add_success("FamilyMember creation and attributes")
    except Exception as e:
        result.add_failure("FamilyMember creation and attributes", str(e))
    
    # Тест Message
    try:
        message = Message(
            id="msg_001",
            sender_id="test_001",
            recipient_ids=["test_002", "test_003"],
            content="Тестовое сообщение",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM,
            metadata={"encrypted": True, "priority": "normal"},
            is_encrypted=True,
            is_delivered=False,
            is_read=False
        )
        
        assert message.id == "msg_001"
        assert message.sender_id == "test_001"
        assert message.recipient_ids == ["test_002", "test_003"]
        assert message.content == "Тестовое сообщение"
        assert message.message_type == MessageType.TEXT
        assert message.priority == MessagePriority.NORMAL
        assert message.timestamp is not None
        assert message.channel == CommunicationChannel.TELEGRAM
        assert message.metadata == {"encrypted": True, "priority": "normal"}
        assert message.is_encrypted == True
        assert message.is_delivered == False
        assert message.is_read == False
        
        result.add_success("Message creation and attributes")
    except Exception as e:
        result.add_failure("Message creation and attributes", str(e))
    
    return result

async def test_external_api_handler():
    """Тест ExternalAPIHandler"""
    result = ComponentTestResult("ExternalAPIHandler")
    
    print("\n🔍 Тестирование ExternalAPIHandler:")
    print("-" * 40)
    
    # Тест создания
    try:
        config = {
            "telegram_token": "test_telegram_token",
            "discord_token": "test_discord_token",
            "twilio_sid": "test_twilio_sid",
            "twilio_token": "test_twilio_token",
            "twilio_from_number": "+1234567890"
        }
        
        handler = ExternalAPIHandler(config)
        
        assert handler.config == config
        assert handler.telegram_token == "test_telegram_token"
        assert handler.discord_token == "test_discord_token"
        assert handler.twilio_sid == "test_twilio_sid"
        assert handler.twilio_token == "test_twilio_token"
        assert handler.logger is not None
        
        result.add_success("ExternalAPIHandler creation")
    except Exception as e:
        result.add_failure("ExternalAPIHandler creation", str(e))
    
    # Тест методов (без реальной отправки)
    try:
        # Тест send_telegram_message
        success = await handler.send_telegram_message("test_chat_id", "test message")
        assert isinstance(success, bool)
        result.add_success("send_telegram_message method")
    except Exception as e:
        result.add_failure("send_telegram_message method", str(e))
    
    try:
        # Тест send_discord_message
        success = await handler.send_discord_message("test_channel_id", "test message")
        assert isinstance(success, bool)
        result.add_success("send_discord_message method")
    except Exception as e:
        result.add_failure("send_discord_message method", str(e))
    
    try:
        # Тест send_sms
        success = await handler.send_sms("+1234567890", "test message")
        assert isinstance(success, bool)
        result.add_success("send_sms method")
    except Exception as e:
        result.add_failure("send_sms method", str(e))
    
    return result

async def test_family_communication_replacement():
    """Тест FamilyCommunicationReplacement"""
    result = ComponentTestResult("FamilyCommunicationReplacement")
    
    print("\n🔍 Тестирование FamilyCommunicationReplacement:")
    print("-" * 40)
    
    # Тест создания
    try:
        config = {
            "telegram_token": "test_telegram_token",
            "discord_token": "test_discord_token",
            "twilio_sid": "test_twilio_sid",
            "twilio_token": "test_twilio_token",
            "twilio_from_number": "+1234567890"
        }
        
        hub = FamilyCommunicationReplacement("family_test", config)
        
        assert hub.family_id == "family_test"
        assert hub.config == config
        assert hub.members == {}
        assert hub.messages == []
        assert hub.is_active == False
        assert hub.stats is not None
        assert hub.api_handler is not None
        assert hub.logger is not None
        
        result.add_success("FamilyCommunicationReplacement creation")
    except Exception as e:
        result.add_failure("FamilyCommunicationReplacement creation", str(e))
    
    # Тест методов
    try:
        # Тест add_family_member
        member = FamilyMember(
            id="test_member_001",
            name="Тест Тестович",
            role=FamilyRole.PARENT
        )
        
        success = await hub.add_family_member(member)
        assert isinstance(success, bool)
        assert hub.members["test_member_001"] == member
        
        result.add_success("add_family_member method")
    except Exception as e:
        result.add_failure("add_family_member method", str(e))
    
    try:
        # Тест send_message
        message = Message(
            id="msg_001",
            sender_id="test_member_001",
            recipient_ids=["test_member_002"],
            content="Тестовое сообщение",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        success = await hub.send_message(message)
        assert isinstance(success, bool)
        
        result.add_success("send_message method")
    except Exception as e:
        result.add_failure("send_message method", str(e))
    
    try:
        # Тест get_family_statistics
        stats = await hub.get_family_statistics()
        assert isinstance(stats, dict)
        assert "family_id" in stats
        assert "total_members" in stats
        assert "active_members" in stats
        assert "total_messages" in stats
        assert "is_active" in stats
        
        result.add_success("get_family_statistics method")
    except Exception as e:
        result.add_failure("get_family_statistics method", str(e))
    
    try:
        # Тест start/stop
        await hub.start()
        assert hub.is_active == True
        
        await hub.stop()
        assert hub.is_active == False
        
        result.add_success("start/stop methods")
    except Exception as e:
        result.add_failure("start/stop methods", str(e))
    
    return result

async def test_integration():
    """Тест интеграции между компонентами"""
    result = ComponentTestResult("Integration")
    
    print("\n🔍 Тестирование интеграции между компонентами:")
    print("-" * 40)
    
    try:
        # Создание полной системы
        config = {
            "telegram_token": "test_telegram_token",
            "discord_token": "test_discord_token",
            "twilio_sid": "test_twilio_sid",
            "twilio_token": "test_twilio_token",
            "twilio_from_number": "+1234567890"
        }
        
        hub = FamilyCommunicationReplacement("family_integration_test", config)
        
        # Добавление нескольких членов семьи
        parent = FamilyMember(
            id="parent_001",
            name="Иван Иванов",
            role=FamilyRole.PARENT,
            phone="+7-999-123-45-67",
            telegram_id="123456789"
        )
        
        child = FamilyMember(
            id="child_001",
            name="Анна Иванова",
            role=FamilyRole.CHILD,
            phone="+7-999-123-45-68",
            telegram_id="123456790"
        )
        
        await hub.add_family_member(parent)
        await hub.add_family_member(child)
        
        # Отправка сообщения
        message = Message(
            id="integration_msg_001",
            sender_id="parent_001",
            recipient_ids=["child_001"],
            content="Привет, как дела?",
            message_type=MessageType.TEXT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            channel=CommunicationChannel.TELEGRAM
        )
        
        success = await hub.send_message(message)
        
        # Получение статистики
        stats = await hub.get_family_statistics()
        
        # Проверка результатов
        assert len(hub.members) == 2
        assert len(hub.messages) == 1
        assert stats["total_members"] == 2
        assert stats["total_messages"] == 1
        
        result.add_success("Full integration test")
    except Exception as e:
        result.add_failure("Full integration test", str(e))
    
    return result

async def main():
    """Основная функция тестирования"""
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    results = []
    
    # Запуск всех тестов
    results.append(await test_enum_classes())
    results.append(await test_dataclass_classes())
    results.append(await test_external_api_handler())
    results.append(await test_family_communication_replacement())
    results.append(await test_integration())
    
    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for result in results:
        summary = result.get_summary()
        total_passed += summary["tests_passed"]
        total_failed += summary["tests_failed"]
        total_tests += summary["total_tests"]
        
        print(f"\n{summary['name']}:")
        print(f"  Тестов пройдено: {summary['tests_passed']}")
        print(f"  Тестов провалено: {summary['tests_failed']}")
        print(f"  Процент успеха: {summary['success_rate']:.1f}%")
        
        if summary["errors"]:
            print("  Ошибки:")
            for error in summary["errors"]:
                print(f"    - {error}")
        
        if summary["warnings"]:
            print("  Предупреждения:")
            for warning in summary["warnings"]:
                print(f"    - {warning}")
    
    print(f"\n🎯 ОБЩИЕ РЕЗУЛЬТАТЫ:")
    print(f"  Всего тестов: {total_tests}")
    print(f"  Пройдено: {total_passed}")
    print(f"  Провалено: {total_failed}")
    print(f"  Процент успеха: {(total_passed/total_tests)*100:.1f}%")
    
    if total_failed == 0:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️ {total_failed} ТЕСТОВ ПРОВАЛЕНО")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)