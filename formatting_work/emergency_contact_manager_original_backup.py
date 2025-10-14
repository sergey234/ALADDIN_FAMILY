#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер контактов экстренного реагирования
Применение Single Responsibility принципа
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import lru_cache

from security.ai_agents.emergency_id_generator import EmergencyIDGenerator
from security.ai_agents.emergency_models import EmergencyContact, EmergencyEvent
from security.ai_agents.emergency_validators import EmailValidator, PhoneValidator


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

    def __str__(self) -> str:
        """
        Строковое представление менеджера контактов

        Returns:
            str: Информация о количестве контактов
        """
        return (
            f"EmergencyContactManager(contacts={len(self.contacts)}, "
            f"groups={len(self.contact_groups)})"
        )

    def __repr__(self) -> str:
        """
        Представление для отладки

        Returns:
            str: Детальная информация о менеджере
        """
        return (
            f"EmergencyContactManager(contacts={self.contacts}, "
            f"groups={self.contact_groups})"
        )

    def __len__(self) -> int:
        """
        Количество контактов в менеджере

        Returns:
            int: Количество контактов
        """
        return len(self.contacts)

    def __contains__(self, contact_id: str) -> bool:
        """
        Проверка наличия контакта по ID

        Args:
            contact_id: ID контакта

        Returns:
            bool: True если контакт существует
        """
        return contact_id in self.contacts

    def clear_contacts(self) -> bool:
        """
        Очистить все контакты и группы

        Returns:
            bool: True если очистка прошла успешно
        """
        try:
            self.contacts.clear()
            self.contact_groups.clear()
            self.logger.info("Все контакты и группы очищены")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка очистки контактов: {e}")
            return False

    def search_contacts(self, query: str) -> List[EmergencyContact]:
        """
        Поиск контактов по имени или телефону

        Args:
            query: Поисковый запрос

        Returns:
            List[EmergencyContact]: Найденные контакты
        """
        try:
            query_lower = query.lower()
            results = []

            for contact in self.contacts.values():
                if (
                    query_lower in contact.name.lower()
                    or query_lower in contact.phone.lower()
                    or (contact.email and query_lower in contact.email.lower())
                ):
                    results.append(contact)

            self.logger.info(
                f"Найдено {len(results)} контактов по запросу '{query}'"
            )
            return results

        except Exception as e:
            self.logger.error(f"Ошибка поиска контактов: {e}")
            return []

    def validate_contact(self, contact_id: str) -> bool:
        """
        Валидация существующего контакта

        Args:
            contact_id: ID контакта

        Returns:
            bool: True если контакт валиден
        """
        try:
            contact = self.contacts.get(contact_id)
            if not contact:
                return False

            # Проверяем валидность телефона
            if not PhoneValidator.validate(contact.phone):
                return False

            # Проверяем валидность email если есть
            if contact.email and not EmailValidator.validate(contact.email):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка валидации контакта: {e}")
            return False

    def export_contacts(self, filepath: str) -> bool:
        """
        Экспорт контактов в JSON файл

        Args:
            filepath: Путь к файлу для экспорта

        Returns:
            bool: True если экспорт успешен
        """
        try:
            export_data = {
                "contacts": [],
                "groups": self.contact_groups,
            }

            for contact in self.contacts.values():
                contact_data = {
                    "contact_id": contact.contact_id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "email": contact.email,
                    "relationship": contact.relationship,
                    "priority": contact.priority,
                    "is_available": contact.is_available,
                }
                export_data["contacts"].append(contact_data)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Контакты экспортированы в {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка экспорта контактов: {e}")
            return False

    def import_contacts(self, filepath: str) -> bool:
        """
        Импорт контактов из JSON файла

        Args:
            filepath: Путь к файлу для импорта

        Returns:
            bool: True если импорт успешен
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            imported_count = 0
            for contact_data in import_data.get("contacts", []):
                try:
                    contact = EmergencyContact(
                        contact_id=contact_data["contact_id"],
                        name=contact_data["name"],
                        phone=contact_data["phone"],
                        email=contact_data.get("email"),
                        relationship=contact_data.get(
                            "relationship", "family"
                        ),
                        priority=contact_data.get("priority", 1),
                        is_available=contact_data.get("is_available", True),
                    )
                    self.contacts[contact.contact_id] = contact
                    imported_count += 1
                except Exception as e:
                    self.logger.warning(f"Ошибка импорта контакта: {e}")
                    continue

            # Импортируем группы
            self.contact_groups.update(import_data.get("groups", {}))

            self.logger.info(
                f"Импортировано {imported_count} контактов из {filepath}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка импорта контактов: {e}")
            return False

    def backup_contacts(self) -> Dict[str, Any]:
        """
        Создание резервной копии контактов

        Returns:
            Dict[str, Any]: Резервная копия данных
        """
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "contacts": {},
                "groups": self.contact_groups.copy(),
            }

            for contact_id, contact in self.contacts.items():
                backup_data["contacts"][contact_id] = {
                    "contact_id": contact.contact_id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "email": contact.email,
                    "relationship": contact.relationship,
                    "priority": contact.priority,
                    "is_available": contact.is_available,
                }

            self.logger.info("Создана резервная копия контактов")
            return backup_data

        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            return {}

    # ============================================================================
    # АСИНХРОННЫЕ МЕТОДЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
    # ============================================================================

    async def add_contact_async(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        relationship: str = "family",
        priority: int = 1,
        is_available: bool = True,
    ) -> EmergencyContact:
        """
        Асинхронное добавление нового контакта с расширенной валидацией.

        Этот метод создает новый контакт с полной валидацией данных и
        автоматической генерацией уникального ID. Контакт сразу становится
        доступным для использования в экстренных ситуациях.

        Args:
            name (str): Полное имя контакта (минимум 2 символа, максимум 100)
            phone (str): Номер телефона в международном формате
            email (Optional[str], optional): Email адрес. Defaults to None.
            relationship (str, optional): Отношение к пользователю. Defaults to "family".
            priority (int, optional): Приоритет контакта (1-5). Defaults to 1.
            is_available (bool, optional): Доступность контакта. Defaults to True.

        Returns:
            EmergencyContact: Созданный объект контакта с уникальным ID

        Raises:
            ValueError: При невалидных данных (телефон, email, имя)
            Exception: При ошибках создания контакта

        Example:
            >>> manager = EmergencyContactManager()
            >>> contact = await manager.add_contact_async("Иван Иванов", "+1234567890")
            >>> print(contact.contact_id)
            contact_1234567890

        Note:
            Приоритет 1 - наивысший, 5 - наименьший
            Валидация телефона использует PhoneValidator
            Валидация email использует EmailValidator
            Метод выполняется асинхронно
        """
        try:
            # Расширенная валидация параметров
            await self._validate_contact_data_async(
                name, phone, email, relationship, priority
            )

            # Создаем контакт
            contact = EmergencyContact(
                contact_id=EmergencyIDGenerator.create_contact_id(),
                name=name.strip(),
                phone=phone.strip(),
                email=email.strip() if email else None,
                relationship=relationship.strip(),
                priority=priority,
                is_available=is_available,
            )

            # Сохраняем контакт
            self.contacts[contact.contact_id] = contact

            # Асинхронное логирование
            await self._log_async(
                "info", f"Добавлен контакт {contact.contact_id}: {name}"
            )
            return contact

        except Exception as e:
            await self._log_async("error", f"Ошибка добавления контакта: {e}")
            raise

    async def get_contacts_async(
        self,
        priority: Optional[int] = None,
        relationship: Optional[str] = None,
        is_available: Optional[bool] = None,
    ) -> List[EmergencyContact]:
        """
        Асинхронное получение контактов с фильтрацией.

        Args:
            priority (Optional[int], optional): Фильтр по приоритету. Defaults to None.
            relationship (Optional[str], optional): Фильтр по отношению. Defaults to None.
            is_available (Optional[bool], optional): Фильтр по доступности. Defaults to None.

        Returns:
            List[EmergencyContact]: Отфильтрованный список контактов
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной операции

            results = []
            for contact in self.contacts.values():
                if priority is not None and contact.priority != priority:
                    continue
                if (
                    relationship is not None
                    and contact.relationship != relationship
                ):
                    continue
                if (
                    is_available is not None
                    and contact.is_available != is_available
                ):
                    continue
                results.append(contact)

            await self._log_async(
                "info", f"Найдено {len(results)} контактов с фильтрацией"
            )
            return results

        except Exception as e:
            await self._log_async("error", f"Ошибка получения контактов: {e}")
            return []

    async def search_contacts_async(
        self, query: str
    ) -> List[EmergencyContact]:
        """
        Асинхронный поиск контактов по имени, телефону или email.

        Args:
            query (str): Поисковый запрос (минимум 2 символа)

        Returns:
            List[EmergencyContact]: Найденные контакты
        """
        try:
            if len(query.strip()) < 2:
                raise ValueError(
                    "Поисковый запрос должен содержать минимум 2 символа"
                )

            await asyncio.sleep(0.001)  # Имитация асинхронной операции

            query_lower = query.lower().strip()
            results = []

            for contact in self.contacts.values():
                if (
                    query_lower in contact.name.lower()
                    or query_lower in contact.phone.lower()
                    or (contact.email and query_lower in contact.email.lower())
                ):
                    results.append(contact)

            await self._log_async(
                "info",
                f"Найдено {len(results)} контактов по запросу '{query}'",
            )
            return results

        except Exception as e:
            await self._log_async("error", f"Ошибка поиска контактов: {e}")
            return []

    async def export_contacts_async(self, filepath: str) -> bool:
        """
        Асинхронный экспорт контактов в JSON файл.

        Args:
            filepath (str): Путь к файлу для экспорта

        Returns:
            bool: True если экспорт успешен
        """
        try:
            await asyncio.sleep(0.001)  # Имитация асинхронной операции

            export_data = {
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
                "contacts": [],
                "groups": self.contact_groups,
            }

            for contact in self.contacts.values():
                contact_data = {
                    "contact_id": contact.contact_id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "email": contact.email,
                    "relationship": contact.relationship,
                    "priority": contact.priority,
                    "is_available": contact.is_available,
                }
                export_data["contacts"].append(contact_data)

            # Асинхронная запись файла
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._write_json_file, filepath, export_data
            )

            await self._log_async(
                "info", f"Контакты экспортированы в {filepath}"
            )
            return True

        except Exception as e:
            await self._log_async("error", f"Ошибка экспорта контактов: {e}")
            return False

    # ============================================================================
    # ВСПОМОГАТЕЛЬНЫЕ АСИНХРОННЫЕ МЕТОДЫ
    # ============================================================================

    async def _validate_contact_data_async(
        self,
        name: str,
        phone: str,
        email: Optional[str],
        relationship: str,
        priority: int,
    ) -> None:
        """Асинхронная валидация данных контакта."""
        if not name or len(name.strip()) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        if len(name.strip()) > 100:
            raise ValueError("Имя не должно превышать 100 символов")

        if not phone or not PhoneValidator.validate(phone.strip()):
            raise ValueError("Невалидный номер телефона")

        if email and not EmailValidator.validate(email.strip()):
            raise ValueError("Невалидный email адрес")

        if relationship not in [
            "family",
            "friend",
            "colleague",
            "emergency",
            "other",
        ]:
            raise ValueError("Невалидное отношение к пользователю")

        if not isinstance(priority, int) or priority < 1 or priority > 5:
            raise ValueError("Приоритет должен быть числом от 1 до 5")

    async def _log_async(self, level: str, message: str) -> None:
        """Асинхронное логирование."""
        await asyncio.sleep(0.0001)  # Имитация асинхронной операции
        getattr(self.logger, level)(message)

    def _write_json_file(self, filepath: str, data: Dict[str, Any]) -> None:
        """Синхронная запись JSON файла для использования в executor."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ============================================================================
    # КЭШИРОВАНИЕ ДЛЯ ЧАСТО ИСПОЛЬЗУЕМЫХ ОПЕРАЦИЙ
    # ============================================================================

    @lru_cache(maxsize=128)
    def get_contact_by_id_cached(
        self, contact_id: str
    ) -> Optional[EmergencyContact]:
        """
        Кэшированное получение контакта по ID.

        Args:
            contact_id (str): ID контакта

        Returns:
            Optional[EmergencyContact]: Контакт или None
        """
        return self.contacts.get(contact_id)

    @lru_cache(maxsize=64)
    def get_contacts_by_priority_cached(
        self, priority: int
    ) -> List[EmergencyContact]:
        """
        Кэшированное получение контактов по приоритету.

        Args:
            priority (int): Приоритет контактов

        Returns:
            List[EmergencyContact]: Список контактов
        """
        return [
            contact
            for contact in self.contacts.values()
            if contact.priority == priority
        ]

    def clear_cache(self) -> None:
        """Очистка кэша."""
        self.get_contact_by_id_cached.cache_clear()
        self.get_contacts_by_priority_cached.cache_clear()
        self.logger.info("Кэш очищен")

    # ============================================================================
    # РАСШИРЕННОЕ ЛОГИРОВАНИЕ С УРОВНЯМИ
    # ============================================================================

    def log_contact_operation(
        self,
        operation: str,
        contact_id: str,
        success: bool,
        details: Optional[str] = None,
    ) -> None:
        """
        Расширенное логирование операций с контактами.

        Args:
            operation (str): Тип операции (add, update, delete, search)
            contact_id (str): ID контакта
            success (bool): Успешность операции
            details (Optional[str]): Дополнительные детали
        """
        level = "info" if success else "error"
        message = f"Операция '{operation}' для контакта {contact_id}: {'УСПЕХ' if success else 'ОШИБКА'}"
        if details:
            message += f" - {details}"

        getattr(self.logger, level)(message)

    def log_performance_metric(
        self, operation: str, duration: float, record_count: int
    ) -> None:
        """
        Логирование метрик производительности.

        Args:
            operation (str): Операция
            duration (float): Время выполнения в секундах
            record_count (int): Количество обработанных записей
        """
        self.logger.info(
            f"PERF: {operation} - {duration:.3f}s, {record_count} записей, "
            f"{record_count/duration:.1f} записей/сек"
        )
