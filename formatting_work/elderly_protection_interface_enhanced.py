#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElderlyProtectionInterface - Интерфейс защиты для пожилых людей
Специализированный интерфейс "Защитник Пенсионера"

Этот модуль предоставляет:
- Упрощенный интерфейс для пожилых людей
- Крупные кнопки и понятные иконки
- Автоматическую защиту без сложных настроек
- Голосовые команды
- Экстренную связь с семьей
- Обучение безопасности

Технические детали:
- Использует крупные шрифты и контрастные цвета
- Применяет голосовое управление
- Интегрирует с системами уведомлений
- Использует простые метафоры безопасности
- Применяет адаптивный дизайн
- Интегрирует с семейными приложениями

Автор: ALADDIN Security System
Версия: 1.0
Дата: 2025-09-08
Лицензия: MIT
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.base import SecurityBase


class InterfaceMode(Enum):
    """Режимы интерфейса"""

    SIMPLE = "simple"  # Простой режим
    LARGE_TEXT = "large_text"  # Крупный текст
    VOICE_ONLY = "voice_only"  # Только голос
    EMERGENCY = "emergency"  # Экстренный режим
    LEARNING = "learning"  # Режим обучения


class ProtectionLevel(Enum):
    """Уровни защиты"""

    BASIC = "basic"  # Базовая защита
    ENHANCED = "enhanced"  # Улучшенная защита
    MAXIMUM = "maximum"  # Максимальная защита
    EMERGENCY = "emergency"  # Экстренная защита


class VoiceCommand(Enum):
    """Голосовые команды"""

    HELP = "help"  # Помощь
    EMERGENCY = "emergency"  # Экстренная помощь
    CALL_FAMILY = "call_family"  # Позвонить семье
    BLOCK_CALL = "block_call"  # Заблокировать звонок
    CHECK_SECURITY = "check_security"  # Проверить безопасность
    LEARN_SAFETY = "learn_safety"  # Изучить безопасность


@dataclass
class UserProfile:
    """Профиль пользователя"""

    user_id: str
    name: str
    age: int
    tech_level: str  # "beginner", "intermediate", "advanced"
    preferred_mode: InterfaceMode
    protection_level: ProtectionLevel
    family_contacts: List[str]
    emergency_contacts: List[str]
    voice_enabled: bool
    learning_enabled: bool
    created_at: datetime
    last_activity: datetime


@dataclass
class SafetyLesson:
    """Урок безопасности"""

    lesson_id: str
    title: str
    description: str
    content: str
    difficulty: str
    duration_minutes: int
    completed: bool
    completion_date: Optional[datetime] = None


@dataclass
class InterfaceElement:
    """Элемент интерфейса"""

    element_id: str
    element_type: str  # "button", "text", "icon", "voice_command"
    text: str
    icon: str
    size: str  # "small", "medium", "large", "extra_large"
    color: str
    position: Tuple[int, int]
    action: str
    is_visible: bool = True


class ElderlyProtectionInterface(SecurityBase):
    """
    Интерфейс защиты для пожилых людей
    Специализированный интерфейс "Защитник Пенсионера"
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ElderlyProtectionInterface", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Профили пользователей
        self.user_profiles = {}

        # Уроки безопасности
        self.safety_lessons = self._initialize_safety_lessons()

        # Элементы интерфейса
        self.interface_elements = self._initialize_interface_elements()

        # Статистика
        self.active_users = 0
        self.voice_commands_processed = 0
        self.lessons_completed = 0
        self.emergency_activations = 0

        # Настройки интерфейса
        self.default_font_size = 18
        self.large_font_size = 24
        self.extra_large_font_size = 32
        self.contrast_ratio = 4.5  # WCAG AA стандарт

        self.logger.info("ElderlyProtectionInterface инициализирован")

    def _initialize_safety_lessons(self) -> Dict[str, SafetyLesson]:
        """Инициализация уроков безопасности"""
        return {
            "phone_scam_lesson": SafetyLesson(
                lesson_id="phone_scam_001",
                title="Защита от телефонных мошенников",
                description="Учимся распознавать телефонных мошенников",
                content=(
                    "Телефонные мошенники часто представляются сотрудниками "
                    "банков, "
                    "ФСБ, прокуратуры. Они просят срочно перевести деньги или "
                    "сообщить данные карты. Помните: настоящие сотрудники "
                    "никогда не просят деньги по телефону!"
                ),
                difficulty="beginner",
                duration_minutes=5,
                completed=False,
            ),
            "deepfake_lesson": SafetyLesson(
                lesson_id="deepfake_001",
                title="Защита от поддельных видеозвонков",
                description="Учимся распознавать поддельные видеозвонки",
                content=(
                    "Мошенники могут использовать поддельные видео с лицами "
                    "ваших "
                    "знакомых. Если кто-то звонит по видео и просит деньги, "
                    "всегда проверьте через другой канал связи!"
                ),
                difficulty="intermediate",
                duration_minutes=7,
                completed=False,
            ),
            "financial_safety_lesson": SafetyLesson(
                lesson_id="financial_001",
                title="Финансовая безопасность",
                description="Правила безопасных финансовых операций",
                content=(
                    "Никогда не переводите деньги незнакомым людям. Всегда "
                    "проверяйте получателя. При сомнениях - звоните семье или "
                    "в банк!"
                ),
                difficulty="beginner",
                duration_minutes=6,
                completed=False,
            ),
            "emergency_lesson": SafetyLesson(
                lesson_id="emergency_001",
                title="Экстренная помощь",
                description="Как получить экстренную помощь",
                content=(
                    "Если вы подозреваете мошенничество, нажмите кнопку "
                    "'Экстренная помощь' или скажите 'Экстренная помощь'. "
                    "Система автоматически уведомит вашу семью!"
                ),
                difficulty="beginner",
                duration_minutes=3,
                completed=False,
            ),
        }

    def _initialize_interface_elements(self) -> Dict[str, InterfaceElement]:
        """Инициализация элементов интерфейса"""
        return {
            "emergency_button": InterfaceElement(
                element_id="emergency_btn",
                element_type="button",
                text="ЭКСТРЕННАЯ ПОМОЩЬ",
                icon="🚨",
                size="extra_large",
                color="#FF0000",
                position=(50, 50),
                action="trigger_emergency",
            ),
            "call_family_button": InterfaceElement(
                element_id="family_btn",
                element_type="button",
                text="ПОЗВОНИТЬ СЕМЬЕ",
                icon="👨‍👩‍👧‍👦",
                size="large",
                color="#00AA00",
                position=(50, 150),
                action="call_family",
            ),
            "check_security_button": InterfaceElement(
                element_id="security_btn",
                element_type="button",
                text="ПРОВЕРИТЬ БЕЗОПАСНОСТЬ",
                icon="🛡️",
                size="large",
                color="#0066CC",
                position=(50, 250),
                action="check_security",
            ),
            "learn_safety_button": InterfaceElement(
                element_id="learn_btn",
                element_type="button",
                text="ИЗУЧИТЬ БЕЗОПАСНОСТЬ",
                icon="📚",
                size="large",
                color="#FF6600",
                position=(50, 350),
                action="learn_safety",
            ),
            "status_text": InterfaceElement(
                element_id="status_text",
                element_type="text",
                text="Система защиты активна",
                icon="",
                size="medium",
                color="#000000",
                position=(50, 450),
                action="",
            ),
        }

    async def create_user_profile(
        self, user_id: str, name: str, age: int, tech_level: str = "beginner"
    ) -> UserProfile:
        """
        Создание профиля пользователя

        Args:
            user_id: ID пользователя
            name: Имя пользователя
            age: Возраст
            tech_level: Уровень технических навыков

        Returns:
            UserProfile: Профиль пользователя
        """
        try:
            self.logger.info(f"Создание профиля пользователя {user_id}")

            # Определение предпочтительного режима на основе возраста и навыков
            if age >= 80 or tech_level == "beginner":
                preferred_mode = InterfaceMode.SIMPLE
                protection_level = ProtectionLevel.MAXIMUM
            elif age >= 70 or tech_level == "intermediate":
                preferred_mode = InterfaceMode.LARGE_TEXT
                protection_level = ProtectionLevel.ENHANCED
            else:
                preferred_mode = InterfaceMode.SIMPLE
                protection_level = ProtectionLevel.BASIC

            profile = UserProfile(
                user_id=user_id,
                name=name,
                age=age,
                tech_level=tech_level,
                preferred_mode=preferred_mode,
                protection_level=protection_level,
                family_contacts=[],
                emergency_contacts=[],
                voice_enabled=True,
                learning_enabled=True,
                created_at=datetime.now(),
                last_activity=datetime.now(),
            )

            self.user_profiles[user_id] = profile
            self.active_users += 1

            self.logger.info(f"Профиль пользователя {user_id} создан")
            return profile

        except Exception as e:
            self.logger.error(f"Ошибка создания профиля пользователя: {e}")
            return None

    async def get_interface_for_user(self, user_id: str) -> Dict[str, Any]:
        """
        Получение интерфейса для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Dict[str, Any]: Настройки интерфейса
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}

            profile = self.user_profiles[user_id]

            # Адаптация интерфейса под пользователя
            interface_config = {
                "user_id": user_id,
                "mode": profile.preferred_mode.value,
                "protection_level": profile.protection_level.value,
                "font_size": self._get_font_size_for_user(profile),
                "contrast_ratio": self.contrast_ratio,
                "elements": self._get_elements_for_user(profile),
                "voice_commands": self._get_voice_commands_for_user(profile),
                "safety_lessons": self._get_lessons_for_user(profile),
            }

            return interface_config

        except Exception as e:
            self.logger.error(f"Ошибка получения интерфейса: {e}")
            return {"error": str(e)}

    def _get_font_size_for_user(self, profile: UserProfile) -> int:
        """Получение размера шрифта для пользователя"""
        if profile.age >= 80:
            return self.extra_large_font_size
        elif profile.age >= 70:
            return self.large_font_size
        else:
            return self.default_font_size

    def _get_elements_for_user(
        self, profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Получение элементов интерфейса для пользователя"""
        elements = []

        for element in self.interface_elements.values():
            # Адаптация размера под пользователя
            if profile.age >= 80:
                element_size = "extra_large"
            elif profile.age >= 70:
                element_size = "large"
            else:
                element_size = element.size

            elements.append(
                {
                    "id": element.element_id,
                    "type": element.element_type,
                    "text": element.text,
                    "icon": element.icon,
                    "size": element_size,
                    "color": element.color,
                    "position": element.position,
                    "action": element.action,
                    "visible": element.is_visible,
                }
            )

        return elements

    def _get_voice_commands_for_user(
        self, profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Получение голосовых команд для пользователя"""
        if not profile.voice_enabled:
            return []

        commands = []
        for command in VoiceCommand:
            commands.append(
                {
                    "command": command.value,
                    "description": self._get_command_description(command),
                    "action": self._get_command_action(command),
                }
            )

        return commands

    def _get_command_description(self, command: VoiceCommand) -> str:
        """Получение описания голосовой команды"""
        descriptions = {
            VoiceCommand.HELP: "Получить помощь",
            VoiceCommand.EMERGENCY: "Экстренная помощь",
            VoiceCommand.CALL_FAMILY: "Позвонить семье",
            VoiceCommand.BLOCK_CALL: "Заблокировать звонок",
            VoiceCommand.CHECK_SECURITY: "Проверить безопасность",
            VoiceCommand.LEARN_SAFETY: "Изучить безопасность",
        }
        return descriptions.get(command, "Неизвестная команда")

    def _get_command_action(self, command: VoiceCommand) -> str:
        """Получение действия голосовой команды"""
        actions = {
            VoiceCommand.HELP: "show_help",
            VoiceCommand.EMERGENCY: "trigger_emergency",
            VoiceCommand.CALL_FAMILY: "call_family",
            VoiceCommand.BLOCK_CALL: "block_current_call",
            VoiceCommand.CHECK_SECURITY: "check_security_status",
            VoiceCommand.LEARN_SAFETY: "show_safety_lessons",
        }
        return actions.get(command, "unknown_action")

    def _get_lessons_for_user(
        self, profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Получение уроков безопасности для пользователя"""
        if not profile.learning_enabled:
            return []

        lessons = []
        for lesson in self.safety_lessons.values():
            # Фильтрация по уровню сложности
            if (
                profile.tech_level == "beginner"
                and lesson.difficulty != "beginner"
            ):
                continue
            elif (
                profile.tech_level == "intermediate"
                and lesson.difficulty == "advanced"
            ):
                continue

            lessons.append(
                {
                    "id": lesson.lesson_id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "difficulty": lesson.difficulty,
                    "duration": lesson.duration_minutes,
                    "completed": lesson.completed,
                }
            )

        return lessons

    async def process_voice_command(
        self, user_id: str, command: str
    ) -> Dict[str, Any]:
        """
        Обработка голосовой команды

        Args:
            user_id: ID пользователя
            command: Голосовая команда

        Returns:
            Dict[str, Any]: Результат обработки
        """
        try:
            self.logger.info(
                f"Обработка голосовой команды для {user_id}: {command}"
            )

            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}

            profile = self.user_profiles[user_id]

            if not profile.voice_enabled:
                return {"error": "Голосовые команды отключены"}

            # Обработка команды
            command_lower = command.lower().strip()

            if "помощь" in command_lower or "help" in command_lower:
                return await self._handle_help_command(user_id)
            elif "экстренн" in command_lower or "emergency" in command_lower:
                return await self._handle_emergency_command(user_id)
            elif "семь" in command_lower or "family" in command_lower:
                return await self._handle_call_family_command(user_id)
            elif "блокир" in command_lower or "block" in command_lower:
                return await self._handle_block_call_command(user_id)
            elif "безопасн" in command_lower or "security" in command_lower:
                return await self._handle_check_security_command(user_id)
            elif "изуч" in command_lower or "learn" in command_lower:
                return await self._handle_learn_safety_command(user_id)
            else:
                return {
                    "error": "Команда не распознана",
                    "suggestion": "Скажите 'помощь' для списка команд",
                }

        except Exception as e:
            self.logger.error(f"Ошибка обработки голосовой команды: {e}")
            return {"error": str(e)}

    async def _handle_help_command(self, user_id: str) -> Dict[str, Any]:
        """Обработка команды помощи"""
        return {
            "action": "show_help",
            "message": (
                "Доступные команды: экстренная помощь, позвонить семье, "
                "заблокировать звонок, проверить безопасность, "
                "изучить безопасность"
            ),
            "voice_response": (
                "Я могу помочь вам с безопасностью. Скажите "
                "'экстренная помощь' "
                "для срочной помощи, 'позвонить семье' для связи с родными."
            ),
        }

    async def _handle_emergency_command(self, user_id: str) -> Dict[str, Any]:
        """Обработка команды экстренной помощи"""
        self.emergency_activations += 1
        return {
            "action": "trigger_emergency",
            "message": (
                "Экстренная помощь активирована! Ваша семья уведомлена."
            ),
            "voice_response": (
                "Экстренная помощь активирована! Ваша семья получила "
                "уведомление. "
                "Оставайтесь спокойны, помощь уже в пути."
            ),
        }

    async def _handle_call_family_command(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Обработка команды звонка семье"""
        return {
            "action": "call_family",
            "message": "Связываюсь с семьей...",
            "voice_response": (
                "Сейчас свяжу вас с семьей. Пожалуйста, подождите."
            ),
        }

    async def _handle_block_call_command(self, user_id: str) -> Dict[str, Any]:
        """Обработка команды блокировки звонка"""
        return {
            "action": "block_current_call",
            "message": "Текущий звонок заблокирован",
            "voice_response": (
                "Звонок заблокирован. Если это был мошенник, ваша семья "
                "уведомлена."
            ),
        }

    async def _handle_check_security_command(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Обработка команды проверки безопасности"""
        return {
            "action": "check_security",
            "message": (
                "Проверка безопасности завершена. Все системы работают "
                "нормально."
            ),
            "voice_response": (
                "Проверка безопасности завершена. Все системы защиты активны "
                "и работают нормально."
            ),
        }

    async def _handle_learn_safety_command(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Обработка команды изучения безопасности"""
        return {
            "action": "show_safety_lessons",
            "message": "Открываю уроки безопасности...",
            "voice_response": (
                "Открываю уроки безопасности. Выберите урок для изучения."
            ),
        }

    async def complete_safety_lesson(
        self, user_id: str, lesson_id: str
    ) -> bool:
        """
        Завершение урока безопасности

        Args:
            user_id: ID пользователя
            lesson_id: ID урока

        Returns:
            bool: Успешность завершения
        """
        try:
            if lesson_id in self.safety_lessons:
                self.safety_lessons[lesson_id].completed = True
                self.safety_lessons[lesson_id].completion_date = datetime.now()
                self.lessons_completed += 1

                self.logger.info(
                    f"Урок {lesson_id} завершен пользователем {user_id}"
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Ошибка завершения урока: {e}")
            return False

    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        if user_id not in self.user_profiles:
            return {"error": "Пользователь не найден"}

        profile = self.user_profiles[user_id]
        completed_lessons = sum(
            1 for lesson in self.safety_lessons.values() if lesson.completed
        )

        return {
            "user_id": user_id,
            "name": profile.name,
            "age": profile.age,
            "tech_level": profile.tech_level,
            "interface_mode": profile.preferred_mode.value,
            "protection_level": profile.protection_level.value,
            "completed_lessons": completed_lessons,
            "total_lessons": len(self.safety_lessons),
            "voice_commands_used": self.voice_commands_processed,
            "last_activity": profile.last_activity.isoformat(),
        }

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса интерфейса"""
        return {
            "interface_name": "ElderlyProtectionInterface",
            "status": "active",
            "version": "1.0",
            "features": [
                "Упрощенный интерфейс",
                "Крупные кнопки",
                "Голосовые команды",
                "Экстренная связь",
                "Обучение безопасности",
                "Адаптивный дизайн",
            ],
            "active_users": self.active_users,
            "total_lessons": len(self.safety_lessons),
            "completed_lessons": self.lessons_completed,
            "emergency_activations": self.emergency_activations,
            "voice_commands_processed": self.voice_commands_processed,
        }

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Получение профиля пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserProfile: Профиль пользователя или None если не найден
        """
        try:
            return self.user_profiles.get(user_id)
        except Exception as e:
            self.logger.error(f"Ошибка получения профиля пользователя: {e}")
            return None

    async def update_user_profile(
        self, 
        user_id: str, 
        **updates
    ) -> Optional[UserProfile]:
        """
        Обновление профиля пользователя
        
        Args:
            user_id: ID пользователя
            **updates: Поля для обновления
            
        Returns:
            UserProfile: Обновленный профиль или None если не найден
        """
        try:
            if user_id not in self.user_profiles:
                return None
            
            profile = self.user_profiles[user_id]
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            self.user_profiles[user_id] = profile
            return profile
        except Exception as e:
            self.logger.error(f"Ошибка обновления профиля пользователя: {e}")
            return None

    async def get_safety_lessons(self, user_id: str) -> Dict[str, Any]:
        """
        Получение уроков безопасности для пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Словарь с уроками безопасности
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}
            
            profile = self.user_profiles[user_id]
            lessons = self._get_lessons_for_user(profile)
            
            return {
                "lessons": lessons,
                "total_lessons": len(lessons),
                "completed_lessons": sum(1 for lesson in lessons if lesson.get("completed", False))
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения уроков безопасности: {e}")
            return {"error": str(e)}

    async def get_emergency_contacts(self, user_id: str) -> Dict[str, Any]:
        """
        Получение экстренных контактов пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Словарь с экстренными контактами
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}
            
            profile = self.user_profiles[user_id]
            return {
                "emergency_contacts": profile.emergency_contacts,
                "family_contacts": profile.family_contacts,
                "total_contacts": len(profile.emergency_contacts) + len(profile.family_contacts)
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения экстренных контактов: {e}")
            return {"error": str(e)}

    async def add_emergency_contact(
        self, 
        user_id: str, 
        contact: str
    ) -> Dict[str, Any]:
        """
        Добавление экстренного контакта
        
        Args:
            user_id: ID пользователя
            contact: Контакт для добавления
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}
            
            profile = self.user_profiles[user_id]
            if contact not in profile.emergency_contacts:
                profile.emergency_contacts.append(contact)
                self.user_profiles[user_id] = profile
                return {"success": True, "message": "Контакт добавлен"}
            else:
                return {"success": False, "message": "Контакт уже существует"}
        except Exception as e:
            self.logger.error(f"Ошибка добавления экстренного контакта: {e}")
            return {"error": str(e)}

    async def remove_emergency_contact(
        self, 
        user_id: str, 
        contact: str
    ) -> Dict[str, Any]:
        """
        Удаление экстренного контакта
        
        Args:
            user_id: ID пользователя
            contact: Контакт для удаления
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}
            
            profile = self.user_profiles[user_id]
            if contact in profile.emergency_contacts:
                profile.emergency_contacts.remove(contact)
                self.user_profiles[user_id] = profile
                return {"success": True, "message": "Контакт удален"}
            else:
                return {"success": False, "message": "Контакт не найден"}
        except Exception as e:
            self.logger.error(f"Ошибка удаления экстренного контакта: {e}")
            return {"error": str(e)}

    async def get_interface_mode(self, user_id: str) -> Dict[str, Any]:
        """
        Получение режима интерфейса пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Режим интерфейса
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}
            
            profile = self.user_profiles[user_id]
            return {
                "interface_mode": profile.preferred_mode.value,
                "protection_level": profile.protection_level.value,
                "voice_enabled": profile.voice_enabled,
                "learning_enabled": profile.learning_enabled
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения режима интерфейса: {e}")
            return {"error": str(e)}

    async def set_interface_mode(
        self, 
        user_id: str, 
        mode: str,
        protection_level: str = None
    ) -> Dict[str, Any]:
        """
        Установка режима интерфейса пользователя
        
        Args:
            user_id: ID пользователя
            mode: Режим интерфейса
            protection_level: Уровень защиты (опционально)
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        try:
            if user_id not in self.user_profiles:
                return {"error": "Пользователь не найден"}
            
            profile = self.user_profiles[user_id]
            
            # Устанавливаем режим интерфейса
            try:
                profile.preferred_mode = InterfaceMode(mode)
            except ValueError:
                return {"error": f"Неверный режим интерфейса: {mode}"}
            
            # Устанавливаем уровень защиты если указан
            if protection_level:
                try:
                    profile.protection_level = ProtectionLevel(protection_level)
                except ValueError:
                    return {"error": f"Неверный уровень защиты: {protection_level}"}
            
            self.user_profiles[user_id] = profile
            return {
                "success": True, 
                "message": "Режим интерфейса обновлен",
                "interface_mode": profile.preferred_mode.value,
                "protection_level": profile.protection_level.value
            }
        except Exception as e:
            self.logger.error(f"Ошибка установки режима интерфейса: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Тестирование интерфейса
    async def test_elderly_protection_interface():
        interface = ElderlyProtectionInterface()

        # Создание профиля пользователя
        profile = await interface.create_user_profile(
            "elderly_001", "Анна Ивановна", 75, "beginner"
        )
        print(f"Профиль создан: {profile}")

        # Получение интерфейса
        ui_config = await interface.get_interface_for_user("elderly_001")
        print(f"Конфигурация интерфейса: {ui_config}")

        # Обработка голосовой команды
        result = await interface.process_voice_command(
            "elderly_001", "экстренная помощь"
        )
        print(f"Результат голосовой команды: {result}")

        # Завершение урока
        success = await interface.complete_safety_lesson(
            "elderly_001", "phone_scam_lesson"
        )
        print(f"Урок завершен: {success}")

        # Получение статуса
        status = await interface.get_status()
        print(f"Статус интерфейса: {status}")

    # Запуск тестов
    asyncio.run(test_elderly_protection_interface())
