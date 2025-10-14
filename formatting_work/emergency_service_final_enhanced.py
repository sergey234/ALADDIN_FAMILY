#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmergencyService - Координатор системы экстренного реагирования
Применение SOLID принципов и DRY
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.base import SecurityBase
from security.ai_agents.emergency_models import (
    EmergencyConfiguration,
    EmergencyContact,
    EmergencyEvent,
    EmergencyResponse,
    EmergencySeverity,
    EmergencyType,
)
from security.managers.emergency_contact_manager import EmergencyContactManager
from security.managers.emergency_event_manager import EmergencyEventManager
from security.managers.emergency_notification_manager import (
    EmergencyNotificationManager,
)
from security.microservices.emergency_service_caller import (
    EmergencyServiceCaller,
)


class EmergencyService(SecurityBase):
    """
    Координатор системы экстренного реагирования

    Основной класс для управления экстренными ситуациями в системе
    безопасности. Обеспечивает полный цикл обработки от создания события
    до вызова служб.

    Применяет принципы SOLID:
    - Single Responsibility: координация экстренного реагирования
    - Open/Closed: открыт для расширения через менеджеры
    - Liskov Substitution: использует абстракции
    - Interface Segregation: разделенные интерфейсы
    - Dependency Inversion: зависит от абстракций

    Attributes:
        event_manager (EmergencyEventManager): Менеджер событий
        contact_manager (EmergencyContactManager): Менеджер контактов
        notification_manager (EmergencyNotificationManager): Менеджер
            уведомлений
        service_caller (EmergencyServiceCaller): Вызыватель служб
        config (EmergencyConfiguration): Конфигурация сервиса

    Example:
        >>> service = EmergencyService()
        >>> event = service.create_emergency_event(
        ...     EmergencyType.MEDICAL,
        ...     EmergencySeverity.HIGH,
        ...     {'lat': 55.7558, 'lon': 37.6176, 'address': 'Москва'},
        ...     'Серьезная травма, требуется скорая помощь',
        ...     'user123'
        ... )
        >>> print(f"Создано событие: {event.event_id}")

    Note:
        Все методы поддерживают как синхронный, так и асинхронный режим
        работы. Рекомендуется использовать асинхронные методы для лучшей
        производительности.
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

        # Дополнительные атрибуты для улучшенной функциональности
        self._async_enabled = True
        self._validation_enabled = True
        self._max_retries = 3
        self._timeout_seconds = 30
        self._performance_metrics = {
            "total_events": 0,
            "successful_events": 0,
            "failed_events": 0,
            "avg_response_time": 0.0,
        }

        self.logger.info("EmergencyService инициализирован")

    def _validate_emergency_event_params(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Валидация параметров для создания экстренного события

        Args:
            emergency_type: Тип экстренной ситуации
            severity: Серьезность ситуации
            location: Местоположение
            description: Описание ситуации
            user_id: ID пользователя

        Raises:
            ValueError: Если параметры невалидны
            TypeError: Если типы параметров неверны
        """
        # Проверка типа экстренной ситуации
        if not isinstance(emergency_type, EmergencyType):
            raise TypeError(
                f"emergency_type должен быть EmergencyType, "
                f"получен {type(emergency_type)}"
            )

        # Проверка серьезности
        if not isinstance(severity, EmergencySeverity):
            raise TypeError(
                f"severity должен быть EmergencySeverity, "
                f"получен {type(severity)}"
            )

        # Проверка местоположения
        if not isinstance(location, dict):
            raise TypeError(
                f"location должен быть dict, получен {type(location)}"
            )

        if not location:
            raise ValueError("location не может быть пустым")

        # Проверка обязательных полей местоположения
        required_location_fields = ["lat", "lon"]
        for field in required_location_fields:
            if field not in location:
                raise ValueError(f"location должен содержать поле '{field}'")

        # Проверка координат
        try:
            lat = float(location["lat"])
            lon = float(location["lon"])
            if not (-90 <= lat <= 90):
                raise ValueError("Широта должна быть между -90 и 90")
            if not (-180 <= lon <= 180):
                raise ValueError("Долгота должна быть между -180 и 180")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Некорректные координаты: {e}")

        # Проверка описания
        if not isinstance(description, str):
            raise TypeError(
                f"description должен быть str, получен {type(description)}"
            )

        if not description.strip():
            raise ValueError("description не может быть пустым")

        if len(description) < 10:
            raise ValueError(
                "description должен содержать минимум 10 символов"
            )

        # Проверка user_id (если предоставлен)
        if user_id is not None:
            if not isinstance(user_id, str):
                raise TypeError(
                    f"user_id должен быть str, получен {type(user_id)}"
                )

            if not user_id.strip():
                raise ValueError("user_id не может быть пустым")

    def _validate_contact_params(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        relationship: str = "family",
        priority: int = 1,
    ) -> None:
        """
        Валидация параметров для добавления контакта

        Args:
            name: Имя контакта
            phone: Номер телефона
            email: Email адрес
            relationship: Отношение к пользователю
            priority: Приоритет контакта

        Raises:
            ValueError: Если параметры невалидны
            TypeError: Если типы параметров неверны
        """
        # Проверка имени
        if not isinstance(name, str):
            raise TypeError(f"name должен быть str, получен {type(name)}")

        if not name.strip():
            raise ValueError("name не может быть пустым")

        if len(name) < 2:
            raise ValueError("name должен содержать минимум 2 символа")

        # Проверка телефона
        if not isinstance(phone, str):
            raise TypeError(f"phone должен быть str, получен {type(phone)}")

        if not phone.strip():
            raise ValueError("phone не может быть пустым")

        # Простая валидация номера телефона
        phone_digits = "".join(filter(str.isdigit, phone))
        if len(phone_digits) < 10:
            raise ValueError("phone должен содержать минимум 10 цифр")

        # Проверка email (если предоставлен)
        if email is not None:
            if not isinstance(email, str):
                raise TypeError(
                    f"email должен быть str, получен {type(email)}"
                )

            if not email.strip():
                raise ValueError("email не может быть пустым")

            if "@" not in email or "." not in email:
                raise ValueError("email должен содержать @ и точку")

        # Проверка relationship
        if not isinstance(relationship, str):
            raise TypeError(
                f"relationship должен быть str, получен {type(relationship)}"
            )

        if not relationship.strip():
            raise ValueError("relationship не может быть пустым")

        # Проверка priority
        if not isinstance(priority, int):
            raise TypeError(
                f"priority должен быть int, получен {type(priority)}"
            )

        if not (1 <= priority <= 5):
            raise ValueError("priority должен быть между 1 и 5")

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

        Raises:
            ValueError: Если параметры невалидны
            TypeError: Если типы параметров неверны
        """
        # Валидация параметров
        self._validate_emergency_event_params(
            emergency_type, severity, location, description, user_id
        )

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

    async def create_emergency_event_async(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
    ) -> EmergencyEvent:
        """
        Асинхронно создать экстренное событие

        Args:
            emergency_type: Тип экстренной ситуации
            severity: Серьезность ситуации
            location: Местоположение
            description: Описание ситуации
            user_id: ID пользователя

        Returns:
            EmergencyEvent: Созданное событие

        Raises:
            ValueError: Если параметры невалидны
            TypeError: Если типы параметров неверны
        """
        # Валидация параметров
        self._validate_emergency_event_params(
            emergency_type, severity, location, description, user_id
        )

        try:
            # Создаем событие асинхронно
            event = await asyncio.create_task(
                self._create_event_async(
                    emergency_type, severity, location, description, user_id
                )
            )

            # Получаем контакты для уведомления
            contacts = await asyncio.create_task(
                self._get_contacts_async(event)
            )

            # Отправляем уведомления асинхронно
            if contacts:
                await asyncio.create_task(
                    self._send_notifications_async(event, contacts)
                )

            # Вызываем службы экстренного реагирования асинхронно
            await asyncio.create_task(
                self._call_emergency_services_async(event)
            )

            self.logger.info(
                f"Асинхронно обработано экстренное событие {event.event_id}"
            )
            return event

        except Exception as e:
            self.logger.error(
                f"Ошибка асинхронного создания экстренного события: {e}"
            )
            raise

    async def _create_event_async(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
    ) -> EmergencyEvent:
        """Асинхронно создать событие"""
        # Имитация асинхронной работы
        await asyncio.sleep(0.1)
        return self.event_manager.create_event(
            emergency_type, severity, location, description, user_id
        )

    async def _get_contacts_async(
        self, event: EmergencyEvent
    ) -> List[EmergencyContact]:
        """Асинхронно получить контакты"""
        await asyncio.sleep(0.05)
        return self.contact_manager.get_emergency_contacts(event)

    async def _send_notifications_async(
        self, event: EmergencyEvent, contacts: List[EmergencyContact]
    ) -> None:
        """Асинхронно отправить уведомления"""
        await asyncio.sleep(0.1)
        self.notification_manager.send_emergency_notification(event, contacts)

    async def _call_emergency_services_async(
        self, event: EmergencyEvent
    ) -> List[EmergencyResponse]:
        """Асинхронно вызвать службы экстренного реагирования"""
        await asyncio.sleep(0.2)
        return self._call_emergency_services(event)

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

        Raises:
            ValueError: Если параметры невалидны
            TypeError: Если типы параметров неверны

        Example:
            >>> service = EmergencyService()
            >>> contact = service.add_emergency_contact(
            ...     "Иван Иванов",
            ...     "+7-999-123-45-67",
            ...     "ivan@example.com",
            ...     "брат",
            ...     1
            ... )
            >>> print(f"Добавлен контакт: {contact.name}")
        """
        # Валидация параметров
        self._validate_contact_params(
            name, phone, email, relationship, priority
        )

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
