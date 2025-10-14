#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер контактов экстренного реагирования
Применение Single Responsibility принципа
"""

import logging
from typing import Any, Dict, List, Optional

from .emergency_id_generator import EmergencyIDGenerator
from .emergency_models import EmergencyContact, EmergencyEvent
from .emergency_validators import EmailValidator, PhoneValidator


class EmergencyContactManager:
    """Менеджер контактов экстренного реагирования"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.contacts: Dict[str, EmergencyContact] = {}
        self.contact_groups: Dict[str, List[str]] = {}

    def add_contact(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        relationship: str = "family",
        priority: int = 1,
        is_available: bool = True,
    ) -> EmergencyContact:
        """
        Добавить новый контакт

        Args:
            name: Имя контакта
            phone: Номер телефона
            email: Email адрес
            relationship: Отношение к пользователю
            priority: Приоритет (1-5)
            is_available: Доступность контакта

        Returns:
            EmergencyContact: Созданный контакт
        """
        try:
            # Валидируем данные
            if not PhoneValidator.validate(phone):
                raise ValueError("Невалидный номер телефона")

            if email and not EmailValidator.validate(email):
                raise ValueError("Невалидный email адрес")

            # Создаем контакт
            contact = EmergencyContact(
                contact_id=EmergencyIDGenerator.create_contact_id(),
                name=name,
                phone=phone,
                email=email,
                relationship=relationship,
                priority=priority,
                is_available=is_available,
            )

            # Сохраняем контакт
            self.contacts[contact.contact_id] = contact

            self.logger.info(f"Добавлен контакт {contact.contact_id}: {name}")
            return contact

        except Exception as e:
            self.logger.error(f"Ошибка добавления контакта: {e}")
            raise

    def get_contact(self, contact_id: str) -> Optional[EmergencyContact]:
        """
        Получить контакт по ID

        Args:
            contact_id: ID контакта

        Returns:
            Optional[EmergencyContact]: Контакт или None
        """
        return self.contacts.get(contact_id)

    def update_contact(self, contact_id: str, **kwargs) -> bool:
        """
        Обновить контакт

        Args:
            contact_id: ID контакта
            **kwargs: Поля для обновления

        Returns:
            bool: True если обновлено успешно
        """
        try:
            contact = self.contacts.get(contact_id)
            if not contact:
                return False

            # Валидируем обновляемые поля
            if "phone" in kwargs and not PhoneValidator.validate(
                kwargs["phone"]
            ):
                raise ValueError("Невалидный номер телефона")

            if (
                "email" in kwargs
                and kwargs["email"]
                and not EmailValidator.validate(kwargs["email"])
            ):
                raise ValueError("Невалидный email адрес")

            # Обновляем поля
            for key, value in kwargs.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)

            self.logger.info(f"Контакт {contact_id} обновлен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления контакта: {e}")
            return False

    def delete_contact(self, contact_id: str) -> bool:
        """
        Удалить контакт

        Args:
            contact_id: ID контакта

        Returns:
            bool: True если удалено успешно
        """
        try:
            if contact_id in self.contacts:
                del self.contacts[contact_id]

                # Удаляем из групп
                for group_name, contact_list in self.contact_groups.items():
                    if contact_id in contact_list:
                        contact_list.remove(contact_id)

                self.logger.info(f"Контакт {contact_id} удален")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления контакта: {e}")
            return False

    def get_contacts_by_priority(
        self, priority: int
    ) -> List[EmergencyContact]:
        """
        Получить контакты по приоритету

        Args:
            priority: Приоритет контактов

        Returns:
            List[EmergencyContact]: Список контактов
        """
        return [
            contact
            for contact in self.contacts.values()
            if contact.priority == priority
        ]

    def get_available_contacts(self) -> List[EmergencyContact]:
        """
        Получить доступные контакты

        Returns:
            List[EmergencyContact]: Список доступных контактов
        """
        return [
            contact
            for contact in self.contacts.values()
            if contact.is_available
        ]

    def get_contacts_by_relationship(
        self, relationship: str
    ) -> List[EmergencyContact]:
        """
        Получить контакты по отношению

        Args:
            relationship: Отношение к пользователю

        Returns:
            List[EmergencyContact]: Список контактов
        """
        return [
            contact
            for contact in self.contacts.values()
            if contact.relationship == relationship
        ]

    def create_contact_group(
        self, group_name: str, contact_ids: List[str]
    ) -> bool:
        """
        Создать группу контактов

        Args:
            group_name: Название группы
            contact_ids: Список ID контактов

        Returns:
            bool: True если группа создана успешно
        """
        try:
            # Проверяем, что все контакты существуют
            valid_contacts = [
                cid for cid in contact_ids if cid in self.contacts
            ]

            if len(valid_contacts) != len(contact_ids):
                self.logger.warning("Некоторые контакты не найдены")

            self.contact_groups[group_name] = valid_contacts
            self.logger.info(f"Создана группа контактов {group_name}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания группы контактов: {e}")
            return False

    def get_contact_group(self, group_name: str) -> List[EmergencyContact]:
        """
        Получить контакты группы

        Args:
            group_name: Название группы

        Returns:
            List[EmergencyContact]: Список контактов группы
        """
        contact_ids = self.contact_groups.get(group_name, [])
        return [
            self.contacts[cid] for cid in contact_ids if cid in self.contacts
        ]

    def get_emergency_contacts(
        self, event: EmergencyEvent
    ) -> List[EmergencyContact]:
        """
        Получить контакты для экстренной ситуации

        Args:
            event: Экстренное событие

        Returns:
            List[EmergencyContact]: Список контактов для уведомления
        """
        try:
            # Получаем контакты по приоритету
            high_priority = self.get_contacts_by_priority(1)
            medium_priority = self.get_contacts_by_priority(2)

            # Фильтруем по доступности
            available_high = [c for c in high_priority if c.is_available]
            available_medium = [c for c in medium_priority if c.is_available]

            # Возвращаем контакты в порядке приоритета
            return available_high + available_medium

        except Exception as e:
            self.logger.error(f"Ошибка получения контактов для события: {e}")
            return []

    def get_contact_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику контактов

        Returns:
            Dict[str, Any]: Статистика контактов
        """
        try:
            total_contacts = len(self.contacts)
            available_contacts = len(self.get_available_contacts())

            # Статистика по приоритетам
            priority_stats = {}
            for contact in self.contacts.values():
                priority = contact.priority
                priority_stats[priority] = priority_stats.get(priority, 0) + 1

            # Статистика по отношениям
            relationship_stats = {}
            for contact in self.contacts.values():
                rel = contact.relationship
                relationship_stats[rel] = relationship_stats.get(rel, 0) + 1

            return {
                "total_contacts": total_contacts,
                "available_contacts": available_contacts,
                "unavailable_contacts": total_contacts - available_contacts,
                "priority_statistics": priority_stats,
                "relationship_statistics": relationship_stats,
                "contact_groups": len(self.contact_groups),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики контактов: {e}")
            return {}
