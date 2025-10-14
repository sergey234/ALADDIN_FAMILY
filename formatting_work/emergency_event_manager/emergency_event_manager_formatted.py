#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер событий экстренного реагирования
Применение Single Responsibility принципа
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from security.ai_agents.emergency_models import (
    EmergencyEvent,
    EmergencySeverity,
    EmergencyType,
    ResponseStatus,
)

from .emergency_id_generator import EmergencyIDGenerator
from .emergency_security_utils import EmergencySecurityUtils


class EmergencyEventManager:
    """Менеджер событий экстренного реагирования"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.events: Dict[str, EmergencyEvent] = {}
        self.event_history: List[EmergencyEvent] = []

    def create_event(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
    ) -> EmergencyEvent:
        """
        Создать новое экстренное событие

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
            # Валидируем входные данные
            if not EmergencySecurityUtils.validate_emergency_request(
                {
                    "emergency_type": emergency_type.value,
                    "description": description,
                    "location": location,
                }
            ):
                raise ValueError("Невалидные данные события")

            # Создаем событие
            event = EmergencyEvent(
                event_id=EmergencyIDGenerator.create_event_id(),
                emergency_type=emergency_type,
                severity=severity,
                location=location,
                description=description,
                user_id=user_id,
                timestamp=datetime.now(),
                status=ResponseStatus.PENDING,
            )

            # Сохраняем событие
            self.events[event.event_id] = event
            self.event_history.append(event)

            self.logger.info(f"Создано событие {event.event_id}")
            return event

        except Exception as e:
            self.logger.error(f"Ошибка создания события: {e}")
            raise

    def get_event(self, event_id: str) -> Optional[EmergencyEvent]:
        """
        Получить событие по ID

        Args:
            event_id: ID события

        Returns:
            Optional[EmergencyEvent]: Событие или None
        """
        return self.events.get(event_id)

    def update_event_status(
        self, event_id: str, status: ResponseStatus
    ) -> bool:
        """
        Обновить статус события

        Args:
            event_id: ID события
            status: Новый статус

        Returns:
            bool: True если обновлено успешно
        """
        try:
            event = self.events.get(event_id)
            if event:
                event.status = status
                if status == ResponseStatus.RESOLVED:
                    event.resolved_at = datetime.now()
                self.logger.info(
                    f"Статус события {event_id} обновлен на {status}"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка обновления статуса: {e}")
            return False

    def get_events_by_type(
        self, emergency_type: EmergencyType
    ) -> List[EmergencyEvent]:
        """
        Получить события по типу

        Args:
            emergency_type: Тип события

        Returns:
            List[EmergencyEvent]: Список событий
        """
        return [
            event
            for event in self.events.values()
            if event.emergency_type == emergency_type
        ]

    def get_events_by_severity(
        self, severity: EmergencySeverity
    ) -> List[EmergencyEvent]:
        """
        Получить события по серьезности

        Args:
            severity: Серьезность события

        Returns:
            List[EmergencyEvent]: Список событий
        """
        return [
            event
            for event in self.events.values()
            if event.severity == severity
        ]

    def get_recent_events(self, hours: int = 24) -> List[EmergencyEvent]:
        """
        Получить недавние события

        Args:
            hours: Количество часов назад

        Returns:
            List[EmergencyEvent]: Список событий
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event
            for event in self.events.values()
            if event.timestamp >= cutoff_time
        ]

    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику событий

        Returns:
            Dict[str, Any]: Статистика
        """
        try:
            total_events = len(self.events)
            resolved_events = len(
                [
                    e
                    for e in self.events.values()
                    if e.status == ResponseStatus.RESOLVED
                ]
            )
            pending_events = len(
                [
                    e
                    for e in self.events.values()
                    if e.status == ResponseStatus.PENDING
                ]
            )

            # Статистика по типам
            type_stats = {}
            for event in self.events.values():
                event_type = event.emergency_type.value
                type_stats[event_type] = type_stats.get(event_type, 0) + 1

            # Статистика по серьезности
            severity_stats = {}
            for event in self.events.values():
                severity = event.severity.value
                severity_stats[severity] = severity_stats.get(severity, 0) + 1

            return {
                "total_events": total_events,
                "resolved_events": resolved_events,
                "pending_events": pending_events,
                "resolution_rate": (resolved_events / max(total_events, 1))
                * 100,
                "type_statistics": type_stats,
                "severity_statistics": severity_stats,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def cleanup_old_events(self, days: int = 30) -> int:
        """
        Очистить старые события

        Args:
            days: Количество дней для хранения

        Returns:
            int: Количество удаленных событий
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            old_events = [
                event_id
                for event_id, event in self.events.items()
                if event.timestamp < cutoff_time
            ]

            for event_id in old_events:
                del self.events[event_id]

            self.logger.info(f"Удалено {len(old_events)} старых событий")
            return len(old_events)
        except Exception as e:
            self.logger.error(f"Ошибка очистки событий: {e}")
            return 0
