#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Форматировщики сообщений для системы экстренного реагирования
Применение Single Responsibility принципа
"""


from security.ai_agents.emergency_models import (
    EmergencyContact,
    EmergencyEvent,
)


class EmergencyMessageFormatter:
    """Форматировщик сообщений для экстренных ситуаций"""

    SEVERITY_EMOJIS = {
        "low": "🟡",
        "medium": "🟠",
        "high": "🔴",
        "critical": "🚨",
        "life": "💀",
    }

    def __init__(self):
        """Инициализация форматировщика сообщений"""
        pass

    @staticmethod
    def format_emergency_message(event: EmergencyEvent) -> str:
        """
        Форматировать сообщение об экстренной ситуации

        Args:
            event: Экстренное событие

        Returns:
            str: Отформатированное сообщение
        """
        emoji = EmergencyMessageFormatter.SEVERITY_EMOJIS.get(
            event.severity.value, "⚠️"
        )

        message = f"{emoji} ЭКСТРЕННАЯ СИТУАЦИЯ\n"
        message += f"Тип: {event.emergency_type.value.upper()}\n"
        message += f"Серьезность: {event.severity.value.upper()}\n"
        message += f"Место: {event.location.address}\n"
        message += f"Описание: {event.description}\n"
        message += f"Время: {event.timestamp.strftime('%H:%M:%S %d.%m.%Y')}"

        return message

    @staticmethod
    def format_contact_notification(
        contact: EmergencyContact, event: EmergencyEvent
    ) -> str:
        """
        Форматировать уведомление для контакта

        Args:
            contact: Контакт для уведомления
            event: Экстренное событие

        Returns:
            str: Отформатированное уведомление
        """
        message = f"Уведомление для {contact.name}:\n\n"
        message += EmergencyMessageFormatter.format_emergency_message(event)
        message += (
            f"\n\nСвяжитесь с {contact.name} по телефону: {contact.phone}"
        )

        return message

    @staticmethod
    def format_service_call_message(
        service: str, event: EmergencyEvent
    ) -> str:
        """
        Форматировать сообщение для вызова службы

        Args:
            service: Название службы
            event: Экстренное событие

        Returns:
            str: Отформатированное сообщение
        """
        message = f"Вызов службы {service.upper()}:\n\n"
        message += f"ID события: {event.event_id}\n"
        message += f"Тип: {event.emergency_type.value}\n"
        message += f"Место: {event.location.get('address', 'Не указано')}\n"
        message += (
            f"Координаты: {event.location.get('coordinates', 'Не указаны')}\n"
        )
        message += f"Описание: {event.description}\n"
        message += f"Время: {event.timestamp.strftime('%H:%M:%S %d.%m.%Y')}"

        return message


class EmergencyDataFormatter:
    """Форматировщик данных для экспорта"""

    def __init__(self):
        """Инициализация форматировщика данных"""
        pass

    @staticmethod
    def format_events_for_json(events: list) -> str:
        """
        Форматировать события для JSON экспорта

        Args:
            events: Список событий

        Returns:
            str: JSON строка
        """
        import json

        try:
            events_data = []
            for event in events:
                event_data = {
                    "event_id": event.event_id,
                    "emergency_type": event.emergency_type.value,
                    "severity": event.severity.value,
                    "location": {
                        "address": event.location.address,
                        "coordinates": event.location.coordinates,
                        "description": event.location.description,
                    },
                    "description": event.description,
                    "timestamp": event.timestamp.isoformat(),
                    "status": event.status.value,
                    "resolved_at": (
                        event.resolved_at.isoformat()
                        if event.resolved_at
                        else None
                    ),
                }
                events_data.append(event_data)

            return json.dumps(events_data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Ошибка экспорта: {str(e)}"

    @staticmethod
    def format_contacts_for_csv(contacts: list) -> str:
        """
        Форматировать контакты для CSV экспорта

        Args:
            contacts: Список контактов

        Returns:
            str: CSV строка
        """
        try:
            csv_lines = [
                "contact_id,name,phone,email,relationship,priority,"
                "is_available"
            ]

            for contact in contacts:
                line = f"{contact.contact_id},{contact.name},{contact.phone},"
                line += f"{contact.email or ''},{contact.relationship},"
                line += f"{contact.priority},{contact.is_available}"
                csv_lines.append(line)

            return "\n".join(csv_lines)
        except Exception as e:
            return f"Ошибка экспорта: {str(e)}"
