#!/usr/bin/env python3
"""
FamilyIntegrationLayer - Слой интеграции семейных компонентов
Обеспечивает полную интеграцию между всеми семейными функциями

Этот файл является центральным интеграционным слоем,
который объединяет все семейные компоненты в единую систему
"""

import logging
from typing import Any, Dict, List, Optional

from core.base import ComponentStatus, SecurityBase

from ..ai_agents.family_communication_hub_a_plus import (
    CommunicationAnalysis,
    FamilyCommunicationHubAPlus,
)

# Импорты компонентов
from .family_profile_manager_enhanced import (
    CommunicationChannel,
    FamilyGroup,
    FamilyMember,
    FamilyProfile,
    FamilyProfileManagerEnhanced,
    FamilyRole,
    MessagePriority,
    MessageType,
)


class FamilyIntegrationLayer(SecurityBase):
    """
    Слой интеграции семейных компонентов

    Объединяет:
    - FamilyProfileManagerEnhanced (управление профилями и группами)
    - FamilyCommunicationHubAPlus (AI коммуникация)
    - Обеспечивает единый API для всех операций
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FamilyIntegrationLayer", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Основные компоненты
        self.profile_manager: Optional[FamilyProfileManagerEnhanced] = None
        self.communication_hub: Optional[FamilyCommunicationHubAPlus] = None

        # Статус интеграции
        self.is_integrated = False
        self.integration_stats = {
            "total_families": 0,
            "total_members": 0,
            "total_groups": 0,
            "total_messages": 0,
            "ai_analyses": 0,
        }

    def initialize(self) -> bool:
        """Инициализация интеграционного слоя"""
        try:
            self.log_activity("Инициализация FamilyIntegrationLayer")
            self.status = ComponentStatus.INITIALIZING

            # Создание профильного менеджера
            self.profile_manager = FamilyProfileManagerEnhanced(self.config)
            if not self.profile_manager.initialize():
                raise Exception("Ошибка инициализации профильного менеджера")

            # Создание коммуникационного хаба
            self.communication_hub = FamilyCommunicationHubAPlus(self.config)
            if not self.communication_hub.initialize():
                raise Exception("Ошибка инициализации коммуникационного хаба")

            # Интеграция компонентов
            self.communication_hub.set_profile_manager(self.profile_manager)

            # Обновление статистики
            self._update_integration_stats()

            self.is_integrated = True
            self.status = ComponentStatus.RUNNING
            self.start_time = self.profile_manager.start_time

            self.log_activity("FamilyIntegrationLayer успешно инициализирован")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    def _update_integration_stats(self):
        """Обновление статистики интеграции"""
        try:
            if self.profile_manager:
                stats = self.profile_manager.get_system_statistics()
                self.integration_stats.update(
                    {
                        "total_families": stats.get("total_families", 0),
                        "total_members": stats.get("total_members", 0),
                        "total_groups": stats.get("total_groups", 0),
                        "total_messages": stats.get("total_messages", 0),
                    }
                )

            if self.communication_hub:
                self.integration_stats["ai_analyses"] = len(
                    self.communication_hub.communication_analyses
                )

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    # ==================== УПРАВЛЕНИЕ СЕМЬЯМИ ====================

    def create_family(
        self,
        family_id: str,
        family_name: str,
        security_settings: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Создание новой семьи"""
        if not self.is_integrated:
            return False

        result = self.profile_manager.create_family(
            family_id, family_name, security_settings
        )
        if result:
            self._update_integration_stats()
        return result

    def add_family_member(
        self,
        family_id: str,
        member_id: str,
        name: str,
        age: int,
        role: Optional[FamilyRole] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> bool:
        """Добавление члена семьи"""
        if not self.is_integrated:
            return False

        result = self.profile_manager.add_family_member(
            family_id, member_id, name, age, role, email, phone
        )
        if result:
            self._update_integration_stats()
        return result

    def get_family(self, family_id: str) -> Optional[FamilyProfile]:
        """Получение семьи"""
        if not self.is_integrated:
            return None
        return self.profile_manager.families.get(family_id)

    def get_family_member(
        self, family_id: str, member_id: str
    ) -> Optional[FamilyMember]:
        """Получение члена семьи"""
        if not self.is_integrated:
            return None

        family = self.get_family(family_id)
        if not family:
            return None
        return family.members.get(member_id)

    # ==================== УПРАВЛЕНИЕ ГРУППАМИ ====================

    def create_family_group(
        self,
        family_id: str,
        group_id: str,
        group_name: str,
        description: Optional[str] = None,
        max_members: int = 20,
    ) -> bool:
        """Создание семейной группы"""
        if not self.is_integrated:
            return False

        result = self.profile_manager.create_family_group(
            family_id, group_id, group_name, description, max_members
        )
        if result:
            self._update_integration_stats()
        return result

    def add_member_to_group(
        self, family_id: str, group_id: str, member_id: str
    ) -> bool:
        """Добавление члена семьи в группу"""
        if not self.is_integrated:
            return False

        result = self.profile_manager.add_member_to_group(
            family_id, group_id, member_id
        )
        if result:
            self._update_integration_stats()
        return result

    def get_family_groups(self, family_id: str) -> List[FamilyGroup]:
        """Получение групп семьи"""
        if not self.is_integrated:
            return []
        return self.profile_manager.get_family_groups(family_id)

    # ==================== КОММУНИКАЦИЯ ====================

    def send_message(
        self,
        sender_id: str,
        recipient_ids: List[str],
        content: str,
        message_type: MessageType = MessageType.TEXT,
        priority: MessagePriority = MessagePriority.NORMAL,
        channel: CommunicationChannel = CommunicationChannel.INTERNAL,
        family_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> Optional[str]:
        """Отправка сообщения с AI анализом"""
        if not self.is_integrated:
            return None

        # Отправка сообщения через профильный менеджер
        message_id = self.profile_manager.send_message(
            sender_id,
            recipient_ids,
            content,
            message_type,
            priority,
            channel,
            family_id,
            group_id,
        )

        if message_id and self.communication_hub:
            # AI анализ сообщения
            message = self.profile_manager.messages.get(message_id)
            if message:
                analysis = self.communication_hub.analyze_message(message)
                if analysis:
                    self._update_integration_stats()

        return message_id

    def get_message_analysis(
        self, message_id: str
    ) -> Optional[CommunicationAnalysis]:
        """Получение AI анализа сообщения"""
        if not self.is_integrated or not self.communication_hub:
            return None
        return self.communication_hub.get_analysis_for_message(message_id)

    def get_communication_statistics(self) -> Optional[Dict[str, Any]]:
        """Получение статистики коммуникации"""
        if not self.is_integrated or not self.communication_hub:
            return None
        return self.communication_hub.get_communication_statistics()

    # ==================== АНАЛИТИКА И СТАТИСТИКА ====================

    def get_family_statistics(
        self, family_id: str
    ) -> Optional[Dict[str, Any]]:
        """Получение статистики семьи"""
        if not self.is_integrated:
            return None
        return self.profile_manager.get_family_statistics(family_id)

    def get_system_statistics(self) -> Dict[str, Any]:
        """Получение системной статистики"""
        if not self.is_integrated:
            return {}

        # Базовая статистика
        stats = self.profile_manager.get_system_statistics()

        # Добавляем статистику интеграции
        stats.update(
            {
                "integration_status": self.is_integrated,
                "ai_analyses": self.integration_stats["ai_analyses"],
                "communication_hub_active": self.communication_hub is not None,
            }
        )

        return stats

    def get_integration_health(self) -> Dict[str, Any]:
        """Получение состояния интеграции"""
        return {
            "is_integrated": self.is_integrated,
            "profile_manager_status": (
                self.profile_manager.status.value
                if self.profile_manager
                else "not_initialized"
            ),
            "communication_hub_status": (
                self.communication_hub.status.value
                if self.communication_hub
                else "not_initialized"
            ),
            "integration_stats": self.integration_stats,
            "uptime": (
                (
                    self.profile_manager.start_time - self.start_time
                ).total_seconds()
                if self.profile_manager and self.start_time
                else 0
            ),
        }

    # ==================== БЕЗОПАСНОСТЬ ====================

    def update_member_security_level(
        self, family_id: str, member_id: str, security_level: int
    ) -> bool:
        """Обновление уровня безопасности члена семьи"""
        if not self.is_integrated:
            return False
        return self.profile_manager.update_member_security_level(
            family_id, member_id, security_level
        )

    def get_family_members_by_role(
        self, family_id: str, role: FamilyRole
    ) -> List[FamilyMember]:
        """Получение членов семьи по роли"""
        if not self.is_integrated:
            return []
        return self.profile_manager.get_family_members_by_role(family_id, role)

    # ==================== УПРАВЛЕНИЕ ЖИЗНЕННЫМ ЦИКЛОМ ====================

    def shutdown(self) -> bool:
        """Корректное завершение работы"""
        try:
            self.log_activity("Завершение работы FamilyIntegrationLayer")
            self.status = ComponentStatus.STOPPING

            # Завершение компонентов
            if self.communication_hub:
                self.communication_hub.shutdown()

            if self.profile_manager:
                self.profile_manager.shutdown()

            self.is_integrated = False
            self.status = ComponentStatus.STOPPED

            self.log_activity("FamilyIntegrationLayer остановлен")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")
            return False

    def restart(self) -> bool:
        """Перезапуск интеграционного слоя"""
        try:
            self.log_activity("Перезапуск FamilyIntegrationLayer")

            # Завершение текущих компонентов
            self.shutdown()

            # Повторная инициализация
            return self.initialize()

        except Exception as e:
            self.logger.error(f"Ошибка перезапуска: {e}")
            return False


# ==================== ФАБРИКА ====================


def create_family_integration_layer(
    config: Optional[Dict[str, Any]] = None
) -> FamilyIntegrationLayer:
    """Фабрика для создания FamilyIntegrationLayer"""
    layer = FamilyIntegrationLayer(config)
    layer.initialize()
    return layer


# ==================== ТЕСТИРОВАНИЕ ====================

if __name__ == "__main__":
    # Тестирование интеграционного слоя
    integration = create_family_integration_layer()

    # Создание семьи
    family_id = "test_integration_family"
    integration.create_family(family_id, "Тестовая семья (Интеграция)")

    # Добавление членов
    integration.add_family_member(
        family_id, "parent_001", "Иван Петров", 35, FamilyRole.PARENT
    )
    integration.add_family_member(
        family_id, "child_001", "Мария Петрова", 10, FamilyRole.CHILD
    )

    # Создание группы
    integration.create_family_group(family_id, "parents_group", "Родители")
    integration.add_member_to_group(family_id, "parents_group", "parent_001")

    # Отправка сообщения с AI анализом
    message_id = integration.send_message(
        "parent_001",
        ["child_001"],
        "Привет, как дела?",
        MessageType.TEXT,
        MessagePriority.NORMAL,
        CommunicationChannel.INTERNAL,
        family_id,
        "parents_group",
    )

    # Получение анализа
    if message_id:
        analysis = integration.get_message_analysis(message_id)
        if analysis:
            print(f"AI анализ: {analysis.sentiment.value}")
            print(f"Срочность: {analysis.urgency_score}")
            print(f"Рекомендации: {analysis.recommendations}")

    # Статистика
    family_stats = integration.get_family_statistics(family_id)
    system_stats = integration.get_system_statistics()
    health = integration.get_integration_health()

    print(f"Статистика семьи: {family_stats}")
    print(f"Системная статистика: {system_stats}")
    print(f"Состояние интеграции: {health}")

    print("FamilyIntegrationLayer успешно протестирован!")
