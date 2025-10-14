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

    def __init__(self, max_events: int = 1000, auto_cleanup_days: int = 30):
        """
        Инициализация менеджера событий экстренного реагирования

        Args:
            max_events: Максимальное количество событий в памяти
            auto_cleanup_days: Количество дней для автоматической очистки
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.events: Dict[str, EmergencyEvent] = {}
        self.event_history: List[EmergencyEvent] = []
        
        # Дополнительные атрибуты для улучшенной функциональности
        self.max_events: int = max_events
        self.auto_cleanup_days: int = auto_cleanup_days
        self.export_format: str = "json"
        self.created_at: datetime = datetime.now()
        self.last_cleanup: Optional[datetime] = None

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

    def __str__(self) -> str:
        """
        Строковое представление объекта

        Returns:
            str: Информация о менеджере событий
        """
        return f"EmergencyEventManager(events={len(self.events)}, history={len(self.event_history)})"

    def __repr__(self) -> str:
        """
        Отладочное представление объекта

        Returns:
            str: Детальная информация о менеджере событий
        """
        return f"EmergencyEventManager(events={len(self.events)}, history={len(self.event_history)}, logger={self.logger.name})"

    def get_all_events(self) -> List[EmergencyEvent]:
        """
        Получить все события

        Returns:
            List[EmergencyEvent]: Список всех событий
        """
        return list(self.events.values())

    def get_events_by_user(self, user_id: str) -> List[EmergencyEvent]:
        """
        Получить события по пользователю

        Args:
            user_id: ID пользователя

        Returns:
            List[EmergencyEvent]: Список событий пользователя
        """
        return [
            event for event in self.events.values()
            if event.user_id == user_id
        ]

    def get_events_by_status(self, status: ResponseStatus) -> List[EmergencyEvent]:
        """
        Получить события по статусу

        Args:
            status: Статус события

        Returns:
            List[EmergencyEvent]: Список событий с указанным статусом
        """
        return [
            event for event in self.events.values()
            if event.status == status
        ]

    def get_events_count(self) -> int:
        """
        Получить количество событий

        Returns:
            int: Количество активных событий
        """
        return len(self.events)

    def is_empty(self) -> bool:
        """
        Проверить, пуст ли менеджер событий

        Returns:
            bool: True если нет активных событий
        """
        return len(self.events) == 0

    def clear_all_events(self) -> int:
        """
        Очистить все события

        Returns:
            int: Количество удаленных событий
        """
        try:
            count = len(self.events)
            self.events.clear()
            self.logger.info(f"Очищено {count} событий")
            return count
        except Exception as e:
            self.logger.error(f"Ошибка очистки всех событий: {e}")
            return 0

    def export_events(self, file_path: str) -> bool:
        """
        Экспортировать события в файл

        Args:
            file_path: Путь к файлу для экспорта

        Returns:
            bool: True если экспорт успешен
        """
        try:
            import json
            from datetime import datetime
            
            # Подготавливаем данные для экспорта
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_events": len(self.events),
                "events": []
            }
            
            for event in self.events.values():
                event_data = {
                    "event_id": event.event_id,
                    "emergency_type": event.emergency_type.value,
                    "severity": event.severity.value,
                    "location": event.location,
                    "description": event.description,
                    "user_id": event.user_id,
                    "timestamp": event.timestamp.isoformat(),
                    "status": event.status.value,
                    "resolved_at": event.resolved_at.isoformat() if event.resolved_at else None
                }
                export_data["events"].append(event_data)
            
            # Записываем в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Экспортировано {len(self.events)} событий в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта событий: {e}")
            return False

    def import_events(self, file_path: str) -> int:
        """
        Импортировать события из файла

        Args:
            file_path: Путь к файлу для импорта

        Returns:
            int: Количество импортированных событий
        """
        try:
            import json
            from datetime import datetime
            
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            for event_data in import_data.get("events", []):
                try:
                    # Создаем событие
                    event = EmergencyEvent(
                        event_id=event_data["event_id"],
                        emergency_type=EmergencyType(event_data["emergency_type"]),
                        severity=EmergencySeverity(event_data["severity"]),
                        location=event_data["location"],
                        description=event_data["description"],
                        user_id=event_data["user_id"],
                        timestamp=datetime.fromisoformat(event_data["timestamp"]),
                        status=ResponseStatus(event_data["status"]),
                        resolved_at=datetime.fromisoformat(event_data["resolved_at"]) if event_data["resolved_at"] else None
                    )
                    
                    # Добавляем в менеджер
                    self.events[event.event_id] = event
                    self.event_history.append(event)
                    imported_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Ошибка импорта события {event_data.get('event_id', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Импортировано {imported_count} событий из {file_path}")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта событий: {e}")
            return 0

    def get_max_events(self) -> int:
        """
        Получить максимальное количество событий

        Returns:
            int: Максимальное количество событий
        """
        return self.max_events

    def set_max_events(self, max_events: int) -> bool:
        """
        Установить максимальное количество событий

        Args:
            max_events: Новое максимальное количество событий

        Returns:
            bool: True если установлено успешно
        """
        try:
            if max_events > 0:
                self.max_events = max_events
                self.logger.info(f"Максимальное количество событий установлено: {max_events}")
                return True
            else:
                self.logger.warning("Максимальное количество событий должно быть больше 0")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка установки максимального количества событий: {e}")
            return False

    def get_auto_cleanup_days(self) -> int:
        """
        Получить количество дней для автоматической очистки

        Returns:
            int: Количество дней для автоматической очистки
        """
        return self.auto_cleanup_days

    def set_auto_cleanup_days(self, days: int) -> bool:
        """
        Установить количество дней для автоматической очистки

        Args:
            days: Количество дней для автоматической очистки

        Returns:
            bool: True если установлено успешно
        """
        try:
            if days > 0:
                self.auto_cleanup_days = days
                self.logger.info(f"Дни автоматической очистки установлены: {days}")
                return True
            else:
                self.logger.warning("Количество дней должно быть больше 0")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка установки дней автоматической очистки: {e}")
            return False

    def get_export_format(self) -> str:
        """
        Получить формат экспорта по умолчанию

        Returns:
            str: Формат экспорта
        """
        return self.export_format

    def set_export_format(self, format_type: str) -> bool:
        """
        Установить формат экспорта по умолчанию

        Args:
            format_type: Тип формата экспорта

        Returns:
            bool: True если установлено успешно
        """
        try:
            if format_type in ["json", "csv", "xml"]:
                self.export_format = format_type
                self.logger.info(f"Формат экспорта установлен: {format_type}")
                return True
            else:
                self.logger.warning(f"Неподдерживаемый формат: {format_type}")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка установки формата экспорта: {e}")
            return False

    def get_created_at(self) -> datetime:
        """
        Получить время создания менеджера

        Returns:
            datetime: Время создания менеджера
        """
        return self.created_at

    def get_last_cleanup(self) -> Optional[datetime]:
        """
        Получить время последней очистки

        Returns:
            Optional[datetime]: Время последней очистки или None
        """
        return self.last_cleanup

    def update_last_cleanup(self) -> None:
        """
        Обновить время последней очистки
        """
        self.last_cleanup = datetime.now()
        self.logger.debug("Время последней очистки обновлено")
