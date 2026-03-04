#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер событий экстренного реагирования
Применение Single Responsibility принципа
"""

import asyncio
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional

from security.ai_agents.emergency_models import (
    EmergencyEvent,
    EmergencySeverity,
    EmergencyType,
    ResponseStatus,
)

from security.ai_agents.emergency_id_generator import EmergencyIDGenerator
from security.ai_agents.emergency_security_utils import EmergencySecurityUtils


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

        # Кэширование
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}
        self._default_cache_ttl: int = 300  # 5 минут

        # Rate limiting
        self._rate_limits: Dict[str, List[datetime]] = {}
        self._default_rate_limit: int = 10  # 10 запросов в минуту
        self._rate_limit_window: int = 60  # 1 минута

        # Performance metrics
        self._operation_count: int = 0
        self._total_response_time: float = 0.0
        self._cache_hits: int = 0
        self._cache_requests: int = 0
        self._error_count: int = 0
        self._start_time: datetime = datetime.now()

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
        return (
            f"EmergencyEventManager(events={len(self.events)}, "
            f"history={len(self.event_history)})"
        )

    def __repr__(self) -> str:
        """
        Отладочное представление объекта

        Returns:
            str: Детальная информация о менеджере событий
        """
        return (
            f"EmergencyEventManager(events={len(self.events)}, "
            f"history={len(self.event_history)}, logger={self.logger.name})"
        )

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
            event for event in self.events.values() if event.user_id == user_id
        ]

    def get_events_by_status(
        self, status: ResponseStatus
    ) -> List[EmergencyEvent]:
        """
        Получить события по статусу

        Args:
            status: Статус события

        Returns:
            List[EmergencyEvent]: Список событий с указанным статусом
        """
        return [
            event for event in self.events.values() if event.status == status
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
                "events": [],
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
                    "resolved_at": (
                        event.resolved_at.isoformat()
                        if event.resolved_at
                        else None
                    ),
                }
                export_data["events"].append(event_data)

            # Записываем в файл
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.logger.info(
                f"Экспортировано {len(self.events)} событий в {file_path}"
            )
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

            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            imported_count = 0

            for event_data in import_data.get("events", []):
                try:
                    # Создаем событие
                    event = EmergencyEvent(
                        event_id=event_data["event_id"],
                        emergency_type=EmergencyType(
                            event_data["emergency_type"]
                        ),
                        severity=EmergencySeverity(event_data["severity"]),
                        location=event_data["location"],
                        description=event_data["description"],
                        user_id=event_data["user_id"],
                        timestamp=datetime.fromisoformat(
                            event_data["timestamp"]
                        ),
                        status=ResponseStatus(event_data["status"]),
                        resolved_at=(
                            datetime.fromisoformat(event_data["resolved_at"])
                            if event_data["resolved_at"]
                            else None
                        ),
                    )

                    # Добавляем в менеджер
                    self.events[event.event_id] = event
                    self.event_history.append(event)
                    imported_count += 1

                except Exception as e:
                    self.logger.warning(
                        f"Ошибка импорта события "
                        f"{event_data.get('event_id', 'unknown')}: {e}"
                    )
                    continue

            self.logger.info(
                f"Импортировано {imported_count} событий из {file_path}"
            )
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
                self.logger.info(
                    f"Максимальное количество событий установлено: "
                    f"{max_events}"
                )
                return True
            else:
                self.logger.warning(
                    "Максимальное количество событий должно быть больше 0"
                )
                return False
        except Exception as e:
            self.logger.error(
                f"Ошибка установки максимального количества событий: {e}"
            )
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
                self.logger.info(
                    f"Дни автоматической очистки установлены: {days}"
                )
                return True
            else:
                self.logger.warning("Количество дней должно быть больше 0")
                return False
        except Exception as e:
            self.logger.error(
                f"Ошибка установки дней автоматической очистки: {e}"
            )
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

    # ==================== VALIDATION METHODS ====================

    def _validate_event_data(self, data: Dict[str, Any]) -> bool:
        """
        Валидация данных события

        Args:
            data: Данные для валидации

        Returns:
            bool: True если данные валидны
        """
        try:
            required_fields = ["emergency_type", "description", "location"]
            for field in required_fields:
                if field not in data:
                    self.logger.warning(
                        f"Отсутствует обязательное поле: {field}"
                    )
                    return False

            # Валидация типа события
            if not isinstance(data["emergency_type"], str):
                self.logger.warning("emergency_type должен быть строкой")
                return False

            # Валидация описания
            if (
                not isinstance(data["description"], str)
                or len(data["description"]) < 5
            ):
                self.logger.warning(
                    "description должен быть строкой длиной >= 5"
                )
                return False

            # Валидация местоположения
            if not isinstance(data["location"], dict):
                self.logger.warning("location должен быть словарем")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации данных: {e}")
            return False

    def _validate_user_id(self, user_id: str) -> bool:
        """
        Валидация ID пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если ID валиден
        """
        try:
            if not isinstance(user_id, str):
                return False
            if len(user_id) < 3 or len(user_id) > 50:
                return False
            if not user_id.replace("_", "").replace("-", "").isalnum():
                return False
            return True
        except Exception:
            return False

    def _validate_location(self, location: Dict[str, Any]) -> bool:
        """
        Валидация местоположения

        Args:
            location: Данные местоположения

        Returns:
            bool: True если местоположение валидно
        """
        try:
            if not isinstance(location, dict):
                return False

            # Проверяем наличие координат
            if "lat" in location and "lon" in location:
                lat = location["lat"]
                lon = location["lon"]
                if not isinstance(lat, (int, float)) or not isinstance(
                    lon, (int, float)
                ):
                    return False
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    return False

            # Проверяем адрес
            if "address" in location:
                if not isinstance(location["address"], str):
                    return False
                if len(location["address"]) < 5:
                    return False

            return True
        except Exception:
            return False

    def _validate_emergency_type(self, emergency_type: EmergencyType) -> bool:
        """
        Валидация типа экстренной ситуации

        Args:
            emergency_type: Тип экстренной ситуации

        Returns:
            bool: True если тип валиден
        """
        try:
            return isinstance(emergency_type, EmergencyType)
        except Exception:
            return False

    def _validate_severity(self, severity: EmergencySeverity) -> bool:
        """
        Валидация серьезности события

        Args:
            severity: Серьезность события

        Returns:
            bool: True если серьезность валидна
        """
        try:
            return isinstance(severity, EmergencySeverity)
        except Exception:
            return False

    def _validate_status(self, status: ResponseStatus) -> bool:
        """
        Валидация статуса события

        Args:
            status: Статус события

        Returns:
            bool: True если статус валиден
        """
        try:
            return isinstance(status, ResponseStatus)
        except Exception:
            return False

    # ==================== ADVANCED ANALYTICS ====================

    def get_advanced_analytics(self) -> Dict[str, Any]:
        """
        Получить расширенную аналитику событий

        Returns:
            Dict[str, Any]: Расширенная аналитика
        """
        try:
            if not self.events:
                return {
                    "trends": {},
                    "hotspots": [],
                    "response_times": {},
                    "user_activity": {},
                    "severity_distribution": {},
                    "time_patterns": {},
                    "geographic_distribution": {},
                }

            # Анализ трендов
            trends = self._analyze_trends()

            # Анализ горячих точек
            hotspots = self._find_hotspots()

            # Анализ времени отклика
            response_times = self._analyze_response_times()

            # Анализ активности пользователей
            user_activity = self._analyze_user_activity()

            # Распределение по серьезности
            severity_distribution = self._analyze_severity_distribution()

            # Временные паттерны
            time_patterns = self._analyze_time_patterns()

            # Географическое распределение
            geographic_distribution = self._analyze_geographic_distribution()

            return {
                "trends": trends,
                "hotspots": hotspots,
                "response_times": response_times,
                "user_activity": user_activity,
                "severity_distribution": severity_distribution,
                "time_patterns": time_patterns,
                "geographic_distribution": geographic_distribution,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения расширенной аналитики: {e}")
            return {}

    def _analyze_trends(self) -> Dict[str, Any]:
        """Анализ трендов событий"""
        try:
            events_by_hour = {}
            events_by_day = {}
            events_by_type = {}

            for event in self.events.values():
                hour = event.timestamp.hour
                day = event.timestamp.strftime("%Y-%m-%d")
                event_type = event.emergency_type.value

                events_by_hour[hour] = events_by_hour.get(hour, 0) + 1
                events_by_day[day] = events_by_day.get(day, 0) + 1
                events_by_type[event_type] = (
                    events_by_type.get(event_type, 0) + 1
                )

            return {
                "hourly_distribution": events_by_hour,
                "daily_distribution": events_by_day,
                "type_distribution": events_by_type,
            }
        except Exception as e:
            self.logger.error(f"Ошибка анализа трендов: {e}")
            return {}

    def _find_hotspots(self) -> List[Dict[str, Any]]:
        """Поиск горячих точек (мест с высокой концентрацией событий)"""
        try:
            location_counts = {}
            for event in self.events.values():
                if "lat" in event.location and "lon" in event.location:
                    lat = round(event.location["lat"], 2)
                    lon = round(event.location["lon"], 2)
                    key = f"{lat},{lon}"
                    location_counts[key] = location_counts.get(key, 0) + 1

            # Сортируем по количеству событий
            hotspots = []
            for location, count in sorted(
                location_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                lat, lon = location.split(",")
                hotspots.append(
                    {
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "event_count": count,
                    }
                )

            return hotspots
        except Exception as e:
            self.logger.error(f"Ошибка поиска горячих точек: {e}")
            return []

    def _analyze_response_times(self) -> Dict[str, Any]:
        """Анализ времени отклика на события"""
        try:
            response_times = []
            for event in self.events.values():
                if (
                    event.resolved_at
                    and event.status == ResponseStatus.RESOLVED
                ):
                    response_time = (
                        event.resolved_at - event.timestamp
                    ).total_seconds()
                    response_times.append(response_time)

            if not response_times:
                return {"average": 0, "min": 0, "max": 0, "median": 0}

            response_times.sort()
            return {
                "average": sum(response_times) / len(response_times),
                "min": min(response_times),
                "max": max(response_times),
                "median": response_times[len(response_times) // 2],
            }
        except Exception as e:
            self.logger.error(f"Ошибка анализа времени отклика: {e}")
            return {}

    def _analyze_user_activity(self) -> Dict[str, Any]:
        """Анализ активности пользователей"""
        try:
            user_activity = {}
            for event in self.events.values():
                if event.user_id:
                    user_activity[event.user_id] = (
                        user_activity.get(event.user_id, 0) + 1
                    )

            # Сортируем пользователей по активности
            top_users = sorted(
                user_activity.items(), key=lambda x: x[1], reverse=True
            )[:10]

            return {
                "total_users": len(user_activity),
                "top_users": [
                    {"user_id": uid, "event_count": count}
                    for uid, count in top_users
                ],
                "user_distribution": user_activity,
            }
        except Exception as e:
            self.logger.error(f"Ошибка анализа активности пользователей: {e}")
            return {}

    def _analyze_severity_distribution(self) -> Dict[str, Any]:
        """Анализ распределения по серьезности"""
        try:
            severity_counts = {}
            for event in self.events.values():
                severity = event.severity.value
                severity_counts[severity] = (
                    severity_counts.get(severity, 0) + 1
                )

            total = sum(severity_counts.values())
            distribution = {
                severity: (count / total * 100) if total > 0 else 0
                for severity, count in severity_counts.items()
            }

            return {
                "counts": severity_counts,
                "percentages": distribution,
            }
        except Exception as e:
            self.logger.error(f"Ошибка анализа распределения серьезности: {e}")
            return {}

    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Анализ временных паттернов"""
        try:
            weekday_counts = {}
            hour_counts = {}
            month_counts = {}

            for event in self.events.values():
                weekday = event.timestamp.strftime("%A")
                hour = event.timestamp.hour
                month = event.timestamp.strftime("%Y-%m")

                weekday_counts[weekday] = weekday_counts.get(weekday, 0) + 1
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
                month_counts[month] = month_counts.get(month, 0) + 1

            return {
                "weekday_distribution": weekday_counts,
                "hour_distribution": hour_counts,
                "monthly_distribution": month_counts,
            }
        except Exception as e:
            self.logger.error(f"Ошибка анализа временных паттернов: {e}")
            return {}

    def _analyze_geographic_distribution(self) -> Dict[str, Any]:
        """Анализ географического распределения"""
        try:
            countries = {}
            regions = {}
            cities = {}

            for event in self.events.values():
                location = event.location
                if "country" in location:
                    country = location["country"]
                    countries[country] = countries.get(country, 0) + 1

                if "region" in location:
                    region = location["region"]
                    regions[region] = regions.get(region, 0) + 1

                if "city" in location:
                    city = location["city"]
                    cities[city] = cities.get(city, 0) + 1

            return {
                "countries": countries,
                "regions": regions,
                "cities": cities,
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка анализа географического распределения: {e}"
            )
            return {}

    # ==================== CACHING METHODS ====================

    def _get_cache_key(self, method_name: str, *args, **kwargs) -> str:
        """
        Генерация ключа кэша

        Args:
            method_name: Имя метода
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы

        Returns:
            str: Ключ кэша
        """
        key_parts = [method_name]
        for arg in args:
            if hasattr(arg, "value"):
                key_parts.append(str(arg.value))
            else:
                key_parts.append(str(arg))
        for k, v in sorted(kwargs.items()):
            if hasattr(v, "value"):
                key_parts.append(f"{k}={v.value}")
            else:
                key_parts.append(f"{k}={v}")
        return "|".join(key_parts)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Проверка валидности кэша

        Args:
            cache_key: Ключ кэша

        Returns:
            bool: True если кэш валиден
        """
        if cache_key not in self._cache:
            return False
        if cache_key not in self._cache_ttl:
            return False
        return datetime.now() < self._cache_ttl[cache_key]

    def _set_cache(
        self, cache_key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """
        Установка значения в кэш

        Args:
            cache_key: Ключ кэша
            value: Значение для кэширования
            ttl: Время жизни кэша в секундах
        """
        ttl = ttl or self._default_cache_ttl
        self._cache[cache_key] = value
        self._cache_ttl[cache_key] = datetime.now() + timedelta(seconds=ttl)

    def _get_cache(self, cache_key: str) -> Any:
        """
        Получение значения из кэша

        Args:
            cache_key: Ключ кэша

        Returns:
            Any: Значение из кэша или None
        """
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        return None

    def _invalidate_cache(self, pattern: Optional[str] = None) -> None:
        """
        Инвалидация кэша

        Args:
            pattern: Паттерн для инвалидации (если None - очистить весь кэш)
        """
        if pattern is None:
            self._cache.clear()
            self._cache_ttl.clear()
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._cache_ttl.pop(key, None)

    @lru_cache(maxsize=128)
    def get_cached_events_by_type(
        self, emergency_type: EmergencyType
    ) -> List[EmergencyEvent]:
        """
        Кэшированное получение событий по типу

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

    @lru_cache(maxsize=128)
    def get_cached_events_by_severity(
        self, severity: EmergencySeverity
    ) -> List[EmergencyEvent]:
        """
        Кэшированное получение событий по серьезности

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

    def get_cached_event_statistics(self) -> Dict[str, Any]:
        """
        Кэшированное получение статистики событий

        Returns:
            Dict[str, Any]: Статистика
        """
        cache_key = self._get_cache_key("get_event_statistics")
        cached_result = self._get_cache(cache_key)

        if cached_result is not None:
            self.logger.debug("Статистика получена из кэша")
            return cached_result

        # Вычисляем статистику
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

            result = {
                "total_events": total_events,
                "resolved_events": resolved_events,
                "pending_events": pending_events,
                "resolution_rate": (resolved_events / max(total_events, 1))
                * 100,
                "type_statistics": type_stats,
                "severity_statistics": severity_stats,
            }

            # Кэшируем результат
            self._set_cache(cache_key, result, ttl=60)  # 1 минута
            return result

        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Получить информацию о кэше

        Returns:
            Dict[str, Any]: Информация о кэше
        """
        now = datetime.now()
        valid_entries = sum(1 for ttl in self._cache_ttl.values() if now < ttl)
        expired_entries = len(self._cache) - valid_entries

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_hit_rate": getattr(self, "_cache_hits", 0)
            / max(getattr(self, "_cache_requests", 1), 1)
            * 100,
            "memory_usage": sum(len(str(v)) for v in self._cache.values()),
        }

    def clear_cache(self) -> int:
        """
        Очистить кэш

        Returns:
            int: Количество очищенных записей
        """
        count = len(self._cache)
        self._cache.clear()
        self._cache_ttl.clear()
        self.logger.info(f"Очищено {count} записей из кэша")
        return count

    # ==================== RATE LIMITING METHODS ====================

    def _check_rate_limit(
        self, user_id: str, limit: Optional[int] = None
    ) -> bool:
        """
        Проверка лимита запросов для пользователя

        Args:
            user_id: ID пользователя
            limit: Лимит запросов (если None - используется по умолчанию)

        Returns:
            bool: True если лимит не превышен
        """
        try:
            limit = limit or self._default_rate_limit
            now = datetime.now()
            window_start = now - timedelta(seconds=self._rate_limit_window)

            # Очищаем старые записи
            if user_id in self._rate_limits:
                self._rate_limits[user_id] = [
                    timestamp
                    for timestamp in self._rate_limits[user_id]
                    if timestamp > window_start
                ]
            else:
                self._rate_limits[user_id] = []

            # Проверяем лимит
            if len(self._rate_limits[user_id]) >= limit:
                self.logger.warning(
                    f"Rate limit превышен для пользователя {user_id}"
                )
                return False

            # Добавляем текущий запрос
            self._rate_limits[user_id].append(now)
            return True

        except Exception as e:
            self.logger.error(f"Ошибка проверки rate limit: {e}")
            return True  # В случае ошибки разрешаем запрос

    def create_event_with_rate_limit(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
        rate_limit: Optional[int] = None,
    ) -> EmergencyEvent:
        """
        Создание события с проверкой rate limit

        Args:
            emergency_type: Тип экстренной ситуации
            severity: Серьезность ситуации
            location: Местоположение
            description: Описание ситуации
            user_id: ID пользователя
            rate_limit: Лимит запросов

        Returns:
            EmergencyEvent: Созданное событие

        Raises:
            ValueError: Если превышен rate limit
        """
        if user_id and not self._check_rate_limit(user_id, rate_limit):
            raise ValueError(f"Rate limit превышен для пользователя {user_id}")

        return self.create_event(
            emergency_type=emergency_type,
            severity=severity,
            location=location,
            description=description,
            user_id=user_id,
        )

    def get_rate_limit_info(self, user_id: str) -> Dict[str, Any]:
        """
        Получить информацию о rate limit для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Dict[str, Any]: Информация о rate limit
        """
        try:
            now = datetime.now()
            window_start = now - timedelta(seconds=self._rate_limit_window)

            if user_id in self._rate_limits:
                # Очищаем старые записи
                self._rate_limits[user_id] = [
                    timestamp
                    for timestamp in self._rate_limits[user_id]
                    if timestamp > window_start
                ]
                current_requests = len(self._rate_limits[user_id])
            else:
                current_requests = 0

            return {
                "user_id": user_id,
                "current_requests": current_requests,
                "rate_limit": self._default_rate_limit,
                "window_seconds": self._rate_limit_window,
                "remaining_requests": max(
                    0, self._default_rate_limit - current_requests
                ),
                "reset_time": window_start
                + timedelta(seconds=self._rate_limit_window),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о rate limit: {e}")
            return {}

    def set_rate_limit(self, user_id: str, limit: int) -> bool:
        """
        Установить rate limit для пользователя

        Args:
            user_id: ID пользователя
            limit: Новый лимит

        Returns:
            bool: True если установлено успешно
        """
        try:
            if limit > 0:
                self._rate_limits[user_id] = []
                self.logger.info(
                    f"Rate limit установлен для {user_id}: {limit}"
                )
                return True
            else:
                self.logger.warning("Rate limit должен быть больше 0")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка установки rate limit: {e}")
            return False

    def clear_rate_limits(self) -> int:
        """
        Очистить все rate limits

        Returns:
            int: Количество очищенных записей
        """
        count = len(self._rate_limits)
        self._rate_limits.clear()
        self.logger.info(f"Очищено {count} rate limit записей")
        return count

    # ==================== PERFORMANCE METRICS ====================

    def _record_operation(
        self, operation_name: str, start_time: datetime, success: bool = True
    ) -> None:
        """
        Записать метрику операции

        Args:
            operation_name: Название операции
            start_time: Время начала операции
            success: Успешность операции
        """
        try:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            self._operation_count += 1
            self._total_response_time += response_time

            if not success:
                self._error_count += 1

            self.logger.debug(
                f"Операция {operation_name}: {response_time:.3f}s, "
                f"успех: {success}"
            )
        except Exception as e:
            self.logger.error(f"Ошибка записи метрики: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики производительности

        Returns:
            Dict[str, Any]: Метрики производительности
        """
        try:
            uptime = (datetime.now() - self._start_time).total_seconds()
            avg_response_time = self._total_response_time / max(
                self._operation_count, 1
            )
            error_rate = (
                self._error_count / max(self._operation_count, 1)
            ) * 100
            cache_hit_rate = (
                self._cache_hits / max(self._cache_requests, 1)
            ) * 100

            return {
                "uptime_seconds": uptime,
                "total_operations": self._operation_count,
                "average_response_time": avg_response_time,
                "total_response_time": self._total_response_time,
                "error_count": self._error_count,
                "error_rate_percent": error_rate,
                "cache_hits": self._cache_hits,
                "cache_requests": self._cache_requests,
                "cache_hit_rate_percent": cache_hit_rate,
                "operations_per_second": self._operation_count
                / max(uptime, 1),
                "memory_usage": self._get_memory_usage(),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения метрик производительности: {e}"
            )
            return {}

    def _get_memory_usage(self) -> Dict[str, int]:
        """
        Получить информацию об использовании памяти

        Returns:
            Dict[str, int]: Информация о памяти
        """
        try:
            events_memory = sum(
                len(str(event)) for event in self.events.values()
            )
            history_memory = sum(
                len(str(event)) for event in self.event_history
            )
            cache_memory = sum(len(str(v)) for v in self._cache.values())

            return {
                "events_memory_bytes": events_memory,
                "history_memory_bytes": history_memory,
                "cache_memory_bytes": cache_memory,
                "total_memory_bytes": events_memory
                + history_memory
                + cache_memory,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о памяти: {e}")
            return {}

    def reset_performance_metrics(self) -> None:
        """
        Сбросить метрики производительности
        """
        try:
            self._operation_count = 0
            self._total_response_time = 0.0
            self._cache_hits = 0
            self._cache_requests = 0
            self._error_count = 0
            self._start_time = datetime.now()
            self.logger.info("Метрики производительности сброшены")
        except Exception as e:
            self.logger.error(f"Ошибка сброса метрик: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """
        Получить состояние системы

        Returns:
            Dict[str, Any]: Состояние системы
        """
        try:
            metrics = self.get_performance_metrics()

            # Определяем статус здоровья
            health_score = 100
            if metrics.get("error_rate_percent", 0) > 10:
                health_score -= 30
            if metrics.get("average_response_time", 0) > 1.0:
                health_score -= 20
            if metrics.get("cache_hit_rate_percent", 0) < 50:
                health_score -= 10
            if len(self.events) > self.max_events * 0.9:
                health_score -= 20

            health_status = (
                "excellent"
                if health_score >= 90
                else (
                    "good"
                    if health_score >= 70
                    else "warning" if health_score >= 50 else "critical"
                )
            )

            return {
                "health_score": max(0, health_score),
                "health_status": health_status,
                "uptime_hours": metrics.get("uptime_seconds", 0) / 3600,
                "total_events": len(self.events),
                "max_events": self.max_events,
                "memory_usage_percent": (
                    len(self.events) / max(self.max_events, 1)
                )
                * 100,
                "performance_metrics": metrics,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения состояния системы: {e}")
            return {"health_score": 0, "health_status": "error"}

    # ==================== REST API METHODS ====================

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать менеджер в словарь для API

        Returns:
            Dict[str, Any]: Словарь с данными менеджера
        """
        try:
            return {
                "manager_id": id(self),
                "max_events": self.max_events,
                "auto_cleanup_days": self.auto_cleanup_days,
                "export_format": self.export_format,
                "created_at": self.created_at.isoformat(),
                "last_cleanup": (
                    self.last_cleanup.isoformat()
                    if self.last_cleanup
                    else None
                ),
                "total_events": len(self.events),
                "total_history": len(self.event_history),
                "performance_metrics": self.get_performance_metrics(),
                "system_health": self.get_system_health(),
            }
        except Exception as e:
            self.logger.error(f"Ошибка преобразования в словарь: {e}")
            return {}

    def from_dict(self, data: Dict[str, Any]) -> bool:
        """
        Восстановить менеджер из словаря

        Args:
            data: Словарь с данными

        Returns:
            bool: True если восстановление успешно
        """
        try:
            if "max_events" in data:
                self.max_events = data["max_events"]
            if "auto_cleanup_days" in data:
                self.auto_cleanup_days = data["auto_cleanup_days"]
            if "export_format" in data:
                self.export_format = data["export_format"]
            if "created_at" in data:
                self.created_at = datetime.fromisoformat(data["created_at"])
            if "last_cleanup" in data and data["last_cleanup"]:
                self.last_cleanup = datetime.fromisoformat(
                    data["last_cleanup"]
                )

            self.logger.info("Менеджер восстановлен из словаря")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка восстановления из словаря: {e}")
            return False

    def get_api_summary(self) -> Dict[str, Any]:
        """
        Получить краткую сводку для API

        Returns:
            Dict[str, Any]: Краткая сводка
        """
        try:
            return {
                "status": "active",
                "version": "2.5",
                "total_events": len(self.events),
                "health_status": self.get_system_health().get(
                    "health_status", "unknown"
                ),
                "last_updated": datetime.now().isoformat(),
                "endpoints": [
                    "GET /events",
                    "POST /events",
                    "GET /events/{id}",
                    "PUT /events/{id}",
                    "DELETE /events/{id}",
                    "GET /events/stats",
                    "GET /events/analytics",
                    "GET /health",
                ],
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки API: {e}")
            return {}

    def get_events_for_api(
        self, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить события для API

        Args:
            limit: Максимальное количество событий
            offset: Смещение

        Returns:
            Dict[str, Any]: События в формате API
        """
        try:
            events_list = list(self.events.values())
            total = len(events_list)

            # Применяем пагинацию
            start = offset
            end = min(offset + limit, total)
            paginated_events = events_list[start:end]

            # Преобразуем события в словари
            events_data = []
            for event in paginated_events:
                event_dict = {
                    "event_id": event.event_id,
                    "emergency_type": event.emergency_type.value,
                    "severity": event.severity.value,
                    "location": event.location,
                    "description": event.description,
                    "user_id": event.user_id,
                    "timestamp": event.timestamp.isoformat(),
                    "status": event.status.value,
                    "resolved_at": (
                        event.resolved_at.isoformat()
                        if event.resolved_at
                        else None
                    ),
                }
                events_data.append(event_dict)

            return {
                "events": events_data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": end < total,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения событий для API: {e}")
            return {"events": [], "total": 0, "error": str(e)}

    def create_event_from_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать событие из API данных

        Args:
            data: Данные события из API

        Returns:
            Dict[str, Any]: Результат создания
        """
        try:
            # Валидируем обязательные поля
            required_fields = [
                "emergency_type",
                "severity",
                "location",
                "description",
            ]
            for field in required_fields:
                if field not in data:
                    return {
                        "success": False,
                        "error": f"Отсутствует поле: {field}",
                    }

            # Преобразуем строки в enum
            try:
                emergency_type = EmergencyType(data["emergency_type"])
                severity = EmergencySeverity(data["severity"])
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Неверный тип или серьезность: {e}",
                }

            # Создаем событие
            event = self.create_event(
                emergency_type=emergency_type,
                severity=severity,
                location=data["location"],
                description=data["description"],
                user_id=data.get("user_id"),
            )

            return {
                "success": True,
                "event_id": event.event_id,
                "message": "Событие создано успешно",
            }
        except Exception as e:
            self.logger.error(f"Ошибка создания события из API: {e}")
            return {"success": False, "error": str(e)}

    def update_event_from_api(
        self, event_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить событие из API данных

        Args:
            event_id: ID события
            data: Данные для обновления

        Returns:
            Dict[str, Any]: Результат обновления
        """
        try:
            event = self.events.get(event_id)
            if not event:
                return {"success": False, "error": "Событие не найдено"}

            # Обновляем поля
            if "status" in data:
                try:
                    status = ResponseStatus(data["status"])
                    self.update_event_status(event_id, status)
                except ValueError:
                    return {"success": False, "error": "Неверный статус"}

            if "description" in data:
                event.description = data["description"]

            if "location" in data:
                event.location = data["location"]

            return {
                "success": True,
                "event_id": event_id,
                "message": "Событие обновлено успешно",
            }
        except Exception as e:
            self.logger.error(f"Ошибка обновления события из API: {e}")
            return {"success": False, "error": str(e)}

    def delete_event_from_api(self, event_id: str) -> Dict[str, Any]:
        """
        Удалить событие из API

        Args:
            event_id: ID события

        Returns:
            Dict[str, Any]: Результат удаления
        """
        try:
            if event_id not in self.events:
                return {"success": False, "error": "Событие не найдено"}

            del self.events[event_id]
            self.logger.info(f"Событие {event_id} удалено через API")

            return {
                "success": True,
                "event_id": event_id,
                "message": "Событие удалено успешно",
            }
        except Exception as e:
            self.logger.error(f"Ошибка удаления события из API: {e}")
            return {"success": False, "error": str(e)}

    # ==================== ASYNC VERSIONS ====================

    async def create_event_async(
        self,
        emergency_type: EmergencyType,
        severity: EmergencySeverity,
        location: Dict[str, Any],
        description: str,
        user_id: Optional[str] = None,
    ) -> EmergencyEvent:
        """
        Асинхронное создание нового экстренного события

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

    async def get_event_async(self, event_id: str) -> Optional[EmergencyEvent]:
        """
        Асинхронное получение события по ID

        Args:
            event_id: ID события

        Returns:
            Optional[EmergencyEvent]: Событие или None
        """
        await asyncio.sleep(0)  # Имитация асинхронной операции
        return self.events.get(event_id)

    async def update_event_status_async(
        self, event_id: str, status: ResponseStatus
    ) -> bool:
        """
        Асинхронное обновление статуса события

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

    async def get_events_by_type_async(
        self, emergency_type: EmergencyType
    ) -> List[EmergencyEvent]:
        """
        Асинхронное получение событий по типу

        Args:
            emergency_type: Тип события

        Returns:
            List[EmergencyEvent]: Список событий
        """
        await asyncio.sleep(0)  # Имитация асинхронной операции
        return [
            event
            for event in self.events.values()
            if event.emergency_type == emergency_type
        ]

    async def get_events_by_severity_async(
        self, severity: EmergencySeverity
    ) -> List[EmergencyEvent]:
        """
        Асинхронное получение событий по серьезности

        Args:
            severity: Серьезность события

        Returns:
            List[EmergencyEvent]: Список событий
        """
        await asyncio.sleep(0)  # Имитация асинхронной операции
        return [
            event
            for event in self.events.values()
            if event.severity == severity
        ]

    async def get_recent_events_async(
        self, hours: int = 24
    ) -> List[EmergencyEvent]:
        """
        Асинхронное получение недавних событий

        Args:
            hours: Количество часов назад

        Returns:
            List[EmergencyEvent]: Список событий
        """
        await asyncio.sleep(0)  # Имитация асинхронной операции
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event
            for event in self.events.values()
            if event.timestamp >= cutoff_time
        ]

    async def get_event_statistics_async(self) -> Dict[str, Any]:
        """
        Асинхронное получение статистики событий

        Returns:
            Dict[str, Any]: Статистика
        """
        try:
            await asyncio.sleep(0)  # Имитация асинхронной операции
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

    async def cleanup_old_events_async(self, days: int = 30) -> int:
        """
        Асинхронная очистка старых событий

        Args:
            days: Количество дней для хранения

        Returns:
            int: Количество удаленных событий
        """
        try:
            await asyncio.sleep(0)  # Имитация асинхронной операции
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
