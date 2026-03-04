#!/usr/bin/env python3
"""
FAMILY COMMUNICATION REPLACEMENT
Замена FamilyCommunicationHub на SmartNotificationManager + внешние API
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp


class FamilyRole(Enum):
    """Роли в семье"""

    PARENT = "parent"
    CHILD = "child"
    ELDERLY = "elderly"
    GUARDIAN = "guardian"


class MessageType(Enum):
    """Типы сообщений"""

    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    EMERGENCY = "emergency"
    LOCATION = "location"


class MessagePriority(Enum):
    """Приоритеты сообщений"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class CommunicationChannel(Enum):
    """Каналы связи"""

    INTERNAL = "internal"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    VOICE_CALL = "voice_call"
    VIDEO_CALL = "video_call"


@dataclass
class FamilyMember:
    """Член семьи"""

    id: str
    name: str
    role: FamilyRole
    phone: Optional[str] = None
    email: Optional[str] = None
    telegram_id: Optional[str] = None
    discord_id: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    is_online: bool = False
    last_seen: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    security_level: int = 1
    emergency_contacts: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Валидация после инициализации"""
        if not self.id:
            raise ValueError("ID не может быть пустым")
        if not self.name:
            raise ValueError("Имя не может быть пустым")
        if self.security_level < 1 or self.security_level > 5:
            raise ValueError("Уровень безопасности должен быть от 1 до 5")

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return f"FamilyMember(name='{self.name}', role={self.role.value})"

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"FamilyMember(id='{self.id}', name='{self.name}', "
            f"role={self.role})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение членов семьи по ID"""
        if not isinstance(other, FamilyMember):
            return False
        return self.id == other.id

    @property
    def is_available(self) -> bool:
        """Доступен ли член семьи для связи"""
        return self.is_online and self.last_seen is not None

    @property
    def has_emergency_contacts(self) -> bool:
        """Есть ли экстренные контакты"""
        return len(self.emergency_contacts) > 0

    def add_emergency_contact(self, contact: str) -> bool:
        """Добавление экстренного контакта"""
        if contact and contact not in self.emergency_contacts:
            self.emergency_contacts.append(contact)
            return True
        return False

    def remove_emergency_contact(self, contact: str) -> bool:
        """Удаление экстренного контакта"""
        if contact in self.emergency_contacts:
            self.emergency_contacts.remove(contact)
            return True
        return False

    def update_location(self, latitude: float, longitude: float) -> None:
        """Обновление местоположения"""
        self.location = (latitude, longitude)
        self.last_seen = datetime.now()

    def set_online_status(self, status: bool) -> None:
        """Установка статуса онлайн/офлайн"""
        self.is_online = status
        if status:
            self.last_seen = datetime.now()


@dataclass
class Message:
    """Сообщение"""

    id: str
    sender_id: str
    recipient_ids: List[str]
    content: str
    message_type: MessageType
    priority: MessagePriority
    timestamp: datetime
    channel: CommunicationChannel
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_encrypted: bool = True
    is_delivered: bool = False
    is_read: bool = False

    def __post_init__(self):
        """Валидация после инициализации"""
        if not self.id:
            raise ValueError("ID сообщения не может быть пустым")
        if not self.sender_id:
            raise ValueError("ID отправителя не может быть пустым")
        if not self.recipient_ids:
            raise ValueError("Список получателей не может быть пустым")
        if not self.content:
            raise ValueError("Содержимое сообщения не может быть пустым")

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50
            else self.content
        )
        return (
            f"Message(id='{self.id}', from={self.sender_id}, "
            f"content='{content_preview}')"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"Message(id='{self.id}', sender_id='{self.sender_id}', "
            f"type={self.message_type})"
        )

    def __eq__(self, other) -> bool:
        """Сравнение сообщений по ID"""
        if not isinstance(other, Message):
            return False
        return self.id == other.id

    @property
    def is_urgent(self) -> bool:
        """Является ли сообщение срочным"""
        return self.priority in [
            MessagePriority.URGENT,
            MessagePriority.EMERGENCY
        ]

    @property
    def is_emergency(self) -> bool:
        """Является ли сообщение экстренным"""
        return self.priority == MessagePriority.EMERGENCY

    @property
    def age_seconds(self) -> float:
        """Возраст сообщения в секундах"""
        return (datetime.now() - self.timestamp).total_seconds()

    def mark_as_delivered(self) -> None:
        """Отметить сообщение как доставленное"""
        self.is_delivered = True

    def mark_as_read(self) -> None:
        """Отметить сообщение как прочитанное"""
        self.is_read = True
        self.is_delivered = True

    def add_metadata(self, key: str, value: Any) -> None:
        """Добавление метаданных"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Получение метаданных"""
        return self.metadata.get(key, default)

    def is_recipient(self, user_id: str) -> bool:
        """Проверка, является ли пользователь получателем"""
        return user_id in self.recipient_ids

    def add_recipient(self, user_id: str) -> bool:
        """Добавление получателя"""
        if user_id not in self.recipient_ids:
            self.recipient_ids.append(user_id)
            return True
        return False

    def remove_recipient(self, user_id: str) -> bool:
        """Удаление получателя"""
        if user_id in self.recipient_ids:
            self.recipient_ids.remove(user_id)
            return True
        return False


class ExternalAPIHandler:
    """Обработчик внешних API"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Инициализация обработчика внешних API

        Args:
            config: Конфигурация API
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.telegram_token = config.get("telegram_token")
        self.discord_token = config.get("discord_token")
        self.twilio_sid = config.get("twilio_sid")
        self.twilio_token = config.get("twilio_token")
        self.error_stats = {
            "total_errors": 0,
            "error_types": {},
            "last_error": None,
            "error_rate": 0.0
        }

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        telegram_status = "✓" if self.telegram_token else "✗"
        discord_status = "✓" if self.discord_token else "✗"
        sms_status = "✓" if self.twilio_sid and self.twilio_token else "✗"
        return (
            f"ExternalAPIHandler(telegram={telegram_status}, "
            f"discord={discord_status}, sms={sms_status})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return f"ExternalAPIHandler(config_keys={list(self.config.keys())})"

    def _log_error(self, error_type: str, error: Exception) -> None:
        """Логирование ошибки с метриками"""
        self.error_stats["total_errors"] += 1
        error_types = self.error_stats["error_types"]
        error_types[error_type] = error_types.get(error_type, 0) + 1
        self.error_stats["last_error"] = str(error)
        self.logger.error(f"[{error_type}] {error}")

    def get_error_stats(self) -> Dict[str, Any]:
        """Получение статистики ошибок"""
        return self.error_stats.copy()

    def reset_error_stats(self) -> None:
        """Сброс статистики ошибок"""
        self.error_stats = {
            "total_errors": 0,
            "error_types": {},
            "last_error": None,
            "error_rate": 0.0
        }

    def is_telegram_available(self) -> bool:
        """Проверка доступности Telegram API"""
        return self.telegram_token is not None

    def is_discord_available(self) -> bool:
        """Проверка доступности Discord API"""
        return self.discord_token is not None

    def is_sms_available(self) -> bool:
        """Проверка доступности SMS API"""
        return self.twilio_sid is not None and self.twilio_token is not None

    def get_available_channels(self) -> List[str]:
        """Получение списка доступных каналов"""
        channels = []
        if self.is_telegram_available():
            channels.append("telegram")
        if self.is_discord_available():
            channels.append("discord")
        if self.is_sms_available():
            channels.append("sms")
        return channels

    async def send_telegram_message(
        self, chat_id: str, text: str, parse_mode: str = "HTML"
    ) -> bool:
        """
        Отправка сообщения в Telegram

        Args:
            chat_id: ID чата
            text: Текст сообщения
            parse_mode: Режим парсинга

        Returns:
            bool: True если успешно отправлено
        """
        try:
            if not self.telegram_token:
                self.logger.warning("Telegram token не настроен")
                return False

            url = (
                f"https://api.telegram.org/bot"
                f"{self.telegram_token}/sendMessage"
            )
            data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        self.logger.info(
                            f"Telegram сообщение отправлено в {chat_id}"
                        )
                        return True
                    else:
                        self.logger.error(
                            f"Ошибка отправки Telegram: {response.status}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки Telegram сообщения: {e}")
            return False

    async def send_discord_message(
        self, channel_id: str, content: str, embed: Optional[Dict] = None
    ) -> bool:
        """
        Отправка сообщения в Discord

        Args:
            channel_id: ID канала
            content: Содержимое сообщения
            embed: Вложение (опционально)

        Returns:
            bool: True если успешно отправлено
        """
        try:
            if not self.discord_token:
                self.logger.warning("Discord token не настроен")
                return False

            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            headers = {
                "Authorization": f"Bot {self.discord_token}",
                "Content-Type": "application/json",
            }

            data = {"content": content}
            if embed:
                data["embeds"] = [embed]

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=data, headers=headers
                ) as response:
                    if response.status == 200:
                        self.logger.info(
                            f"Discord сообщение отправлено в {channel_id}"
                        )
                        return True
                    else:
                        self.logger.error(
                            f"Ошибка отправки Discord: {response.status}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки Discord сообщения: {e}")
            return False

    async def send_sms(self, phone: str, message: str) -> bool:
        """
        Отправка SMS через Twilio

        Args:
            phone: Номер телефона
            message: Текст сообщения

        Returns:
            bool: True если успешно отправлено
        """
        try:
            if not self.twilio_sid or not self.twilio_token:
                self.logger.warning("Twilio credentials не настроены")
                return False

            url = (
                f"https://api.twilio.com/2010-04-01/Accounts/"
                f"{self.twilio_sid}/Messages.json"
            )
            auth = (self.twilio_sid, self.twilio_token)
            data = {
                "From": self.config.get("twilio_from_number"),
                "To": phone,
                "Body": message,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, auth=auth) as response:
                    if response.status == 201:
                        self.logger.info(f"SMS отправлено на {phone}")
                        return True
                    else:
                        self.logger.error(
                            f"Ошибка отправки SMS: {response.status}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"Ошибка отправки SMS: {e}")
            return False


class FamilyCommunicationReplacement:
    """Замена FamilyCommunicationHub с использованием
    SmartNotificationManager + внешние API"""

    def __init__(self, family_id: str, config: Dict[str, Any]) -> None:
        """
        Инициализация замены семейного коммуникационного центра

        Args:
            family_id: Уникальный идентификатор семьи
            config: Конфигурация внешних API
        """
        self.family_id = family_id
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.members: Dict[str, FamilyMember] = {}
        self.messages: List[Message] = []
        self.api_handler = ExternalAPIHandler(config)
        self.is_active = False
        self.stats: Dict[str, Any] = {
            "total_messages": 0,
            "active_members": 0,
            "last_activity": None,
            "api_success_rate": 0.0,
        }

        # Импорт SmartNotificationManager
        try:
            from security.managers.smart_notification_manager import (
                SmartNotificationManager,
            )

            self.notification_manager = SmartNotificationManager()
            self.logger.info("SmartNotificationManager успешно импортирован")
        except ImportError as e:
            self.logger.error(f"Ошибка импорта SmartNotificationManager: {e}")
            self.notification_manager = None

        # Импорт ContextualAlertSystem
        try:
            from security.ai_agents.contextual_alert_system import (
                ContextualAlertSystem,
            )

            self.alert_system = ContextualAlertSystem()
            self.logger.info("ContextualAlertSystem успешно импортирован")
        except ImportError as e:
            self.logger.error(f"Ошибка импорта ContextualAlertSystem: {e}")
            self.alert_system = None

    async def add_family_member(self, member: FamilyMember) -> bool:
        """
        Добавление члена семьи

        Args:
            member: Член семьи

        Returns:
            bool: True если успешно добавлен
        """
        try:
            self.members[member.id] = member
            self.stats["active_members"] = len(self.members)
            self.logger.info(f"Добавлен член семьи: {member.name}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка добавления члена семьи: {e}")
            return False

    async def send_message(self, message: Message) -> bool:
        """
        Отправка сообщения через внешние API

        Args:
            message: Сообщение для отправки

        Returns:
            bool: True если успешно отправлено
        """
        try:
            success_count = 0
            total_attempts = 0

            # Отправка через SmartNotificationManager
            if self.notification_manager:
                try:
                    await self.notification_manager.send_notification(
                        user_id=message.sender_id,
                        message=message.content,
                        priority=message.priority.value,
                        channel=message.channel.value,
                    )
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Ошибка SmartNotificationManager: {e}")
            total_attempts += 1

            # Отправка через ContextualAlertSystem для экстренных сообщений
            if (
                message.priority == MessagePriority.EMERGENCY
                and self.alert_system
            ):
                try:
                    await self.alert_system.send_alert(
                        alert_type="emergency",
                        message=message.content,
                        recipients=message.recipient_ids,
                    )
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Ошибка ContextualAlertSystem: {e}")
            total_attempts += 1

            # Отправка через внешние API
            for recipient_id in message.recipient_ids:
                recipient = self.members.get(recipient_id)
                if not recipient:
                    continue

                # Telegram
                if (
                    message.channel == CommunicationChannel.TELEGRAM
                    and recipient.telegram_id
                ):
                    if await self.api_handler.send_telegram_message(
                        recipient.telegram_id, message.content
                    ):
                        success_count += 1
                    total_attempts += 1

                # Discord
                elif (
                    message.channel == CommunicationChannel.DISCORD
                    and recipient.discord_id
                ):
                    if await self.api_handler.send_discord_message(
                        recipient.discord_id, message.content
                    ):
                        success_count += 1
                    total_attempts += 1

                # SMS
                elif (
                    message.channel == CommunicationChannel.SMS
                    and recipient.phone
                ):
                    if await self.api_handler.send_sms(
                        recipient.phone, message.content
                    ):
                        success_count += 1
                    total_attempts += 1

            # Обновление статистики
            self.messages.append(message)
            self.stats["total_messages"] += 1
            self.stats["last_activity"] = datetime.now()
            self.stats["api_success_rate"] = (
                (success_count / total_attempts) * 100
                if total_attempts > 0
                else 0
            )

            message.is_delivered = success_count > 0
            self.logger.info(
                f"Сообщение {message.id} отправлено через "
                f"{success_count}/{total_attempts} каналов"
            )
            return success_count > 0

        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    async def get_family_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики семьи

        Returns:
            Dict с статистикой
        """
        return {
            "family_id": self.family_id,
            "total_members": len(self.members),
            "active_members": self.stats["active_members"],
            "total_messages": self.stats["total_messages"],
            "last_activity": self.stats["last_activity"],
            "api_success_rate": self.stats["api_success_rate"],
            "is_active": self.is_active,
            "notification_manager_available": self.notification_manager
            is not None,
            "alert_system_available": self.alert_system is not None,
        }

    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return (
            f"FamilyCommunicationReplacement(family_id='{self.family_id}', "
            f"members={len(self.members)}, active={self.is_active})"
        )

    def __repr__(self) -> str:
        """Строковое представление для разработчика"""
        return (
            f"FamilyCommunicationReplacement(family_id='{self.family_id}', "
            f"members={len(self.members)})"
        )

    def __len__(self) -> int:
        """Количество членов семьи"""
        return len(self.members)

    def __iter__(self):
        """Итерация по членам семьи"""
        return iter(self.members.values())

    def __contains__(self, member_id: str) -> bool:
        """Проверка наличия члена семьи"""
        return member_id in self.members

    async def __aenter__(self):
        """Асинхронный вход в контекст"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный выход из контекста"""
        await self.stop()

    def get_member(self, member_id: str) -> Optional[FamilyMember]:
        """Получение члена семьи по ID"""
        return self.members.get(member_id)

    def get_members_by_role(self, role: FamilyRole) -> List[FamilyMember]:
        """Получение членов семьи по роли"""
        return [
            member for member in self.members.values()
            if member.role == role
        ]

    def get_online_members(self) -> List[FamilyMember]:
        """Получение онлайн членов семьи"""
        return [member for member in self.members.values() if member.is_online]

    def get_emergency_contacts(self) -> List[str]:
        """Получение всех экстренных контактов"""
        contacts = set()
        for member in self.members.values():
            contacts.update(member.emergency_contacts)
        return list(contacts)

    def remove_family_member(self, member_id: str) -> bool:
        """Удаление члена семьи"""
        try:
            if member_id in self.members:
                del self.members[member_id]
                self.stats["active_members"] = len(self.members)
                self.logger.info(f"Удален член семьи: {member_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления члена семьи: {e}")
            return False

    def get_messages_by_sender(self, sender_id: str) -> List[Message]:
        """Получение сообщений по отправителю"""
        return [msg for msg in self.messages if msg.sender_id == sender_id]

    def get_messages_by_recipient(self, recipient_id: str) -> List[Message]:
        """Получение сообщений по получателю"""
        return [
            msg for msg in self.messages
            if recipient_id in msg.recipient_ids
        ]

    def get_urgent_messages(self) -> List[Message]:
        """Получение срочных сообщений"""
        return [msg for msg in self.messages if msg.is_urgent]

    def get_emergency_messages(self) -> List[Message]:
        """Получение экстренных сообщений"""
        return [msg for msg in self.messages if msg.is_emergency]

    def clear_old_messages(self, days: int = 30) -> int:
        """Очистка старых сообщений"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            old_messages = [
                msg for msg in self.messages
                if msg.timestamp < cutoff_date
            ]
            self.messages = [
                msg for msg in self.messages
                if msg.timestamp >= cutoff_date
            ]
            self.logger.info(f"Удалено {len(old_messages)} старых сообщений")
            return len(old_messages)
        except Exception as e:
            self.logger.error(f"Ошибка очистки старых сообщений: {e}")
            return 0

    def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья системы"""
        return {
            "is_active": self.is_active,
            "total_members": len(self.members),
            "online_members": len(self.get_online_members()),
            "total_messages": len(self.messages),
            "urgent_messages": len(self.get_urgent_messages()),
            "emergency_messages": len(self.get_emergency_messages()),
            "api_handler_status": str(self.api_handler),
            "notification_manager_available": (
                self.notification_manager is not None
            ),
            "alert_system_available": self.alert_system is not None,
            "error_stats": (
                self.api_handler.get_error_stats()
                if self.api_handler else {}
            )
        }

    async def start(self) -> None:
        """Запуск сервиса"""
        self.is_active = True
        self.logger.info("FamilyCommunicationReplacement запущен")

    async def stop(self) -> None:
        """Остановка сервиса"""
        self.is_active = False
        self.logger.info("FamilyCommunicationReplacement остановлен")


# Тестирование
async def main() -> None:
    """Основная функция для тестирования"""
    # Конфигурация внешних API
    config = {
        "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "discord_token": "YOUR_DISCORD_BOT_TOKEN",
        "twilio_sid": "YOUR_TWILIO_SID",
        "twilio_token": "YOUR_TWILIO_TOKEN",
        "twilio_from_number": "+1234567890",
    }

    # Создание экземпляра
    hub = FamilyCommunicationReplacement("family_001", config)
    await hub.start()

    # Добавление членов семьи
    parent = FamilyMember(
        id="parent_001",
        name="Иван Иванов",
        role=FamilyRole.PARENT,
        phone="+7-999-123-45-67",
        email="ivan@example.com",
        telegram_id="123456789",
        discord_id="987654321",
    )

    child = FamilyMember(
        id="child_001",
        name="Анна Иванова",
        role=FamilyRole.CHILD,
        phone="+7-999-123-45-68",
        telegram_id="123456790",
    )

    await hub.add_family_member(parent)
    await hub.add_family_member(child)

    # Отправка сообщения через Telegram
    message = Message(
        id=str(uuid.uuid4()),
        sender_id="parent_001",
        recipient_ids=["child_001"],
        content="Привет, как дела?",
        message_type=MessageType.TEXT,
        priority=MessagePriority.NORMAL,
        timestamp=datetime.now(),
        channel=CommunicationChannel.TELEGRAM,
    )

    await hub.send_message(message)

    # Получение статистики
    stats = await hub.get_family_statistics()
    print(f"Статистика семьи: {stats}")

    # Остановка
    await hub.stop()


async def family_communication_replacement(
    family_id: str,
    config: Dict[str, Any],
    action: str = "start",
    **kwargs
) -> Dict[str, Any]:
    """
    AI агент для замены FamilyCommunicationHub

    Args:
        family_id: ID семьи
        config: Конфигурация системы
        action: Действие (start, stop, status, send_message, add_member)
        **kwargs: Дополнительные параметры

    Returns:
        Результат выполнения действия
    """
    try:
        # Создание экземпляра системы
        hub = FamilyCommunicationReplacement(family_id, config)

        if action == "start":
            await hub.start()
            return {
                "status": "success",
                "message": "Система семейной коммуникации запущена",
                "family_id": family_id,
                "active": hub.is_active
            }

        elif action == "stop":
            await hub.stop()
            return {
                "status": "success",
                "message": "Система семейной коммуникации остановлена",
                "family_id": family_id,
                "active": hub.is_active
            }

        elif action == "status":
            health = hub.get_health_status()
            return {
                "status": "success",
                "health": health,
                "family_id": family_id
            }

        elif action == "send_message":
            sender_id = kwargs.get("sender_id")
            recipient_ids = kwargs.get("recipient_ids", [])
            content = kwargs.get("content", "")
            message_type_str = kwargs.get("message_type", "TEXT")
            priority_str = kwargs.get("priority", "NORMAL")
            channel_str = kwargs.get("channel", "TELEGRAM")

            if not sender_id or not recipient_ids or not content:
                return {
                    "status": "error",
                    "message": "Недостаточно параметров для отправки сообщения"
                }

            # Преобразование строк в enum
            message_type = MessageType[message_type_str]
            priority = MessagePriority[priority_str]
            channel = CommunicationChannel[channel_str]

            # Создание объекта Message
            message = Message(
                id=f"msg_{datetime.now().timestamp()}",
                sender_id=sender_id,
                recipient_ids=recipient_ids,
                content=content,
                message_type=message_type,
                priority=priority,
                timestamp=datetime.now(),
                channel=channel
            )

            result = await hub.send_message(message)

            return {
                "status": "success" if result else "error",
                "message": (
                    "Сообщение отправлено" if result else "Ошибка отправки"
                ),
                "result": result
            }

        elif action == "add_member":
            member_data = kwargs.get("member_data")
            if not member_data:
                return {
                    "status": "error",
                    "message": "Данные члена семьи не предоставлены"
                }

            # Преобразование строки в FamilyRole
            role_str = member_data.get("role", "PARENT")
            if isinstance(role_str, str):
                role = FamilyRole[role_str]
            else:
                role = role_str

            member = FamilyMember(
                id=member_data.get("id"),
                name=member_data.get("name"),
                role=role,
                phone=member_data.get("phone"),
                email=member_data.get("email"),
                telegram_id=member_data.get("telegram_id"),
                discord_id=member_data.get("discord_id"),
                security_level=member_data.get("security_level", 1)
            )

            result = await hub.add_family_member(member)

            return {
                "status": "success" if result else "error",
                "message": (
                    "Член семьи добавлен" if result else "Ошибка добавления"
                ),
                "result": result
            }

        else:
            return {
                "status": "error",
                "message": f"Неизвестное действие: {action}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка выполнения: {str(e)}",
            "error_type": type(e).__name__
        }


if __name__ == "__main__":
    asyncio.run(main())
