#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmergencyService - Координатор системы экстренного реагирования
Применение SOLID принципов и DRY
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.base import SecurityBase
from security.managers.emergency_contact_manager import (
    EmergencyContactManager,
)
from security.managers.emergency_event_manager import EmergencyEventManager
from security.ai_agents.emergency_models import (
    EmergencyConfiguration,
    EmergencyContact,
    EmergencyEvent,
    EmergencyResponse,
    EmergencySeverity,
    EmergencyType,
)
from security.managers.emergency_notification_manager import (
    EmergencyNotificationManager,
)
from security.microservices.emergency_service_caller import (
    EmergencyServiceCaller,
)


class EmergencyService(SecurityBase):
    """
    Координатор системы экстренного реагирования

    Применяет принципы SOLID:
    - Single Responsibility: координация экстренного реагирования
    - Open/Closed: открыт для расширения через менеджеры
    - Liskov Substitution: использует абстракции
    - Interface Segregation: разделенные интерфейсы
    - Dependency Inversion: зависит от абстракций
    """

    def __init__(
        self,
        name: str = "EmergencyService",
        config: Optional[EmergencyConfiguration] = None,
    ):
        """
        Инициализация сервиса экстренного реагирования

        Args:
            name: Имя сервиса
            config: Конфигурация сервиса
        """
        super().__init__(name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or EmergencyConfiguration()

        # Инициализируем менеджеры
        self.event_manager = EmergencyEventManager()
        self.contact_manager = EmergencyContactManager()
        self.notification_manager = EmergencyNotificationManager()
        self.service_caller = EmergencyServiceCaller()

        self.logger.info("EmergencyService инициализирован")

    def create_emergency_event(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
    ) -> EmergencyEvent:
        """
        Создать экстренное событие

        Args:
            emergency_type: Тип экстренной ситуации
            severity: Серьезность ситуации
            location: Местоположение
            description: Описание ситуации
            user_id: ID пользователя

        Returns:
            EmergencyEvent: Созданное событие
        """
        try:
            # Создаем событие
            event = self.event_manager.create_event(
                emergency_type, severity, location, description, user_id
            )

            # Получаем контакты для уведомления
            contacts = self.contact_manager.get_emergency_contacts(event)

            # Отправляем уведомления
            if contacts:
                self.notification_manager.send_emergency_notification(
                    event, contacts
                )

            # Вызываем службы экстренного реагирования
            self._call_emergency_services(event)

            self.logger.info(f"Обработано экстренное событие {event.event_id}")
            return event

        except Exception as e:
            self.logger.error(f"Ошибка создания экстренного события: {e}")
            raise

    def _call_emergency_services(
        self, event: EmergencyEvent
    ) -> List[EmergencyResponse]:
        """
        Вызвать службы экстренного реагирования

        Args:
            event: Экстренное событие

        Returns:
            List[EmergencyResponse]: Список ответов служб
        """
        try:
            responses = []

            # Определяем тип службы на основе типа события
            service_mapping = {
                EmergencyType.MEDICAL: "medical",
                EmergencyType.FIRE: "fire",
                EmergencyType.POLICE: "police",
                EmergencyType.SECURITY: "security",
            }

            service_type = service_mapping.get(event.emergency_type)
            if service_type:
                # Получаем ближайшие службы
                nearest_services = self.service_caller.get_nearest_services(
                    event
                )

                # Вызываем первую доступную службу
                if nearest_services:
                    service_config = nearest_services[0]
                    response = self.service_caller.call_emergency_service(
                        event, service_config["service_type"]
                    )
                    responses.append(response)

            return responses

        except Exception as e:
            self.logger.error(f"Ошибка вызова служб: {e}")
            return []

    def add_emergency_contact(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        relationship: str = "family",
        priority: int = 1,
    ) -> EmergencyContact:
        """
        Добавить контакт экстренного реагирования

        Args:
            name: Имя контакта
            phone: Номер телефона
            email: Email адрес
            relationship: Отношение к пользователю
            priority: Приоритет (1-5)

        Returns:
            EmergencyContact: Созданный контакт
        """
        return self.contact_manager.add_contact(
            name, phone, email, relationship, priority
        )

    def get_emergency_events(self, hours: int = 24) -> List[EmergencyEvent]:
        """
        Получить экстренные события за период

        Args:
            hours: Количество часов назад

        Returns:
            List[EmergencyEvent]: Список событий
        """
        return self.event_manager.get_recent_events(hours)

    def get_emergency_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику экстренного реагирования

        Returns:
            Dict[str, Any]: Статистика
        """
        try:
            event_stats = self.event_manager.get_event_statistics()
            contact_stats = self.contact_manager.get_contact_statistics()
            notification_stats = (
                self.notification_manager.get_notification_statistics()
            )
            service_stats = self.service_caller.get_service_statistics()

            return {
                "events": event_stats,
                "contacts": contact_stats,
                "notifications": notification_stats,
                "services": service_stats,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def update_event_status(self, event_id: str, status: str) -> bool:
        """
        Обновить статус события

        Args:
            event_id: ID события
            status: Новый статус

        Returns:
            bool: True если обновлено успешно
        """
        return self.event_manager.update_event_status(event_id, status)

    def get_emergency_contacts(self) -> List[EmergencyContact]:
        """
        Получить контакты экстренного реагирования

        Returns:
            List[EmergencyContact]: Список контактов
        """
        return list(self.contact_manager.contacts.values())

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Очистить старые данные

        Args:
            days: Количество дней для хранения

        Returns:
            Dict[str, int]: Результат очистки
        """
        try:
            cleaned_events = self.event_manager.cleanup_old_events(days)

            return {
                "cleaned_events": cleaned_events,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка очистки данных: {e}")
            return {"error": str(e)}

    def get_system_health(self) -> Dict[str, Any]:
        """
        Получить состояние системы

        Returns:
            Dict[str, Any]: Состояние системы
        """
        try:
            stats = self.get_emergency_statistics()

            # Определяем общее состояние
            total_events = stats.get("events", {}).get("total_events", 0)
            resolution_rate = stats.get("events", {}).get("resolution_rate", 0)
            notification_success_rate = stats.get("notifications", {}).get(
                "success_rate", 0
            )

            if resolution_rate >= 90 and notification_success_rate >= 95:
                health_status = "excellent"
            elif resolution_rate >= 80 and notification_success_rate >= 90:
                health_status = "good"
            elif resolution_rate >= 70 and notification_success_rate >= 80:
                health_status = "fair"
            else:
                health_status = "poor"

            return {
                "health_status": health_status,
                "total_events": total_events,
                "resolution_rate": resolution_rate,
                "notification_success_rate": notification_success_rate,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения состояния системы: {e}")
            return {"health_status": "error", "error": str(e)}
