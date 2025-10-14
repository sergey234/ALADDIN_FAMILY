#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Interface Manager Main - Основной менеджер пользовательского интерфейса
"""

import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class InterfaceType(Enum):
    """Типы интерфейсов"""

    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    API = "api"
    DASHBOARD = "dashboard"


class EventType(Enum):
    """Типы событий"""

    LOGIN = "login"
    LOGOUT = "logout"
    NAVIGATION = "navigation"
    ACTION = "action"
    ERROR = "error"
    SECURITY = "security"


@dataclass
class InterfaceEvent:
    """Событие интерфейса"""

    id: str
    user_id: str
    interface_type: InterfaceType
    event_type: EventType
    event_data: Dict[str, Any]
    timestamp: datetime
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UserInterfaceManagerMain:
    """Основной менеджер пользовательского интерфейса"""

    def __init__(self):
        self.logger = logging.getLogger("ALADDIN.UserInterfaceManagerMain")
        self.events = {}
        self.user_sessions = {}
        self.interface_analytics = {}
        self.lock = threading.Lock()
        self.stats = {
            "total_events": 0,
            "active_sessions": 0,
            "interface_errors": 0,
            "security_events": 0,
        }
        self._init_analytics()

    def _init_analytics(self) -> None:
        """Инициализация аналитики"""
        try:
            self.interface_analytics = {
                "event_counts": {},
                "user_activity": {},
                "interface_performance": {},
                "error_patterns": {},
            }
            self.logger.info("Аналитика интерфейса инициализирована")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации аналитики: {e}")

    def log_event(self, event: InterfaceEvent) -> bool:
        """Логирование события интерфейса"""
        try:
            with self.lock:
                self.events[event.id] = event
                self.stats["total_events"] += 1

                # Обновление аналитики
                self._update_analytics(event)

                # Обновление сессии пользователя
                self._update_user_session(event)

                # Проверка на ошибки
                if event.event_type == EventType.ERROR:
                    self.stats["interface_errors"] += 1
                    self._analyze_error(event)

                # Проверка на события безопасности
                if event.event_type == EventType.SECURITY:
                    self.stats["security_events"] += 1
                    self._analyze_security_event(event)

            self.logger.info(
                f"Событие {event.event_type.value} залогировано для пользователя {event.user_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка логирования события: {e}")
            return False

    def _update_analytics(self, event: InterfaceEvent) -> None:
        """Обновление аналитики"""
        try:
            # Подсчет событий по типам
            event_key = (
                f"{event.interface_type.value}_{event.event_type.value}"
            )
            if event_key not in self.interface_analytics["event_counts"]:
                self.interface_analytics["event_counts"][event_key] = 0
            self.interface_analytics["event_counts"][event_key] += 1

            # Активность пользователя
            if event.user_id not in self.interface_analytics["user_activity"]:
                self.interface_analytics["user_activity"][event.user_id] = {
                    "total_events": 0,
                    "last_activity": event.timestamp,
                    "interface_types": set(),
                }

            user_activity = self.interface_analytics["user_activity"][
                event.user_id
            ]
            user_activity["total_events"] += 1
            user_activity["last_activity"] = event.timestamp
            user_activity["interface_types"].add(event.interface_type.value)

        except Exception as e:
            self.logger.error(f"Ошибка обновления аналитики: {e}")

    def _update_user_session(self, event: InterfaceEvent) -> None:
        """Обновление сессии пользователя"""
        try:
            if event.session_id:
                if event.session_id not in self.user_sessions:
                    self.user_sessions[event.session_id] = {
                        "user_id": event.user_id,
                        "start_time": event.timestamp,
                        "last_activity": event.timestamp,
                        "events": [],
                        "interface_type": event.interface_type.value,
                    }

                session = self.user_sessions[event.session_id]
                session["last_activity"] = event.timestamp
                session["events"].append(event.id)

                # Ограничение размера истории событий
                if len(session["events"]) > 1000:
                    session["events"].pop(0)

                self.stats["active_sessions"] = len(self.user_sessions)

        except Exception as e:
            self.logger.error(f"Ошибка обновления сессии: {e}")

    def _analyze_error(self, event: InterfaceEvent) -> None:
        """Анализ ошибки интерфейса"""
        try:
            error_data = event.event_data.get("error", {})
            error_type = error_data.get("type", "unknown")

            if error_type not in self.interface_analytics["error_patterns"]:
                self.interface_analytics["error_patterns"][error_type] = {
                    "count": 0,
                    "users": set(),
                    "interfaces": set(),
                }

            error_pattern = self.interface_analytics["error_patterns"][
                error_type
            ]
            error_pattern["count"] += 1
            error_pattern["users"].add(event.user_id)
            error_pattern["interfaces"].add(event.interface_type.value)

            self.logger.warning(
                f"Ошибка интерфейса: {error_type} для пользователя {event.user_id}"
            )

        except Exception as e:
            self.logger.error(f"Ошибка анализа ошибки: {e}")

    def _analyze_security_event(self, event: InterfaceEvent) -> None:
        """Анализ события безопасности"""
        try:
            security_data = event.event_data.get("security", {})
            threat_level = security_data.get("threat_level", "low")

            self.logger.warning(
                f"Событие безопасности: {threat_level} для пользователя {event.user_id}"
            )

            # Здесь должна быть дополнительная логика анализа безопасности

        except Exception as e:
            self.logger.error(f"Ошибка анализа события безопасности: {e}")

    def get_user_activity(self, user_id: str) -> Dict[str, Any]:
        """Получение активности пользователя"""
        try:
            if user_id not in self.interface_analytics["user_activity"]:
                return {"error": "Пользователь не найден"}

            user_activity = self.interface_analytics["user_activity"][user_id]

            # Получение сессий пользователя
            user_sessions = [
                session
                for session in self.user_sessions.values()
                if session["user_id"] == user_id
            ]

            return {
                "user_id": user_id,
                "total_events": user_activity["total_events"],
                "last_activity": user_activity["last_activity"].isoformat(),
                "interface_types": list(user_activity["interface_types"]),
                "active_sessions": len(user_sessions),
                "recent_sessions": [
                    {
                        "session_id": session["session_id"],
                        "start_time": session["start_time"].isoformat(),
                        "last_activity": session["last_activity"].isoformat(),
                        "interface_type": session["interface_type"],
                        "events_count": len(session["events"]),
                    }
                    for session in user_sessions[-5:]  # Последние 5 сессий
                ],
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения активности пользователя: {e}")
            return {"error": str(e)}

    def get_interface_analytics(self) -> Dict[str, Any]:
        """Получение аналитики интерфейса"""
        try:
            return {
                "event_counts": self.interface_analytics["event_counts"],
                "total_users": len(self.interface_analytics["user_activity"]),
                "error_patterns": {
                    error_type: {
                        "count": pattern["count"],
                        "affected_users": len(pattern["users"]),
                        "affected_interfaces": list(pattern["interfaces"]),
                    }
                    for error_type, pattern in self.interface_analytics[
                        "error_patterns"
                    ].items()
                },
                "stats": self.stats,
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения аналитики: {e}")
            return {"error": str(e)}

    def cleanup_old_events(self, max_age_hours: int = 24) -> int:
        """Очистка старых событий"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            events_to_remove = []

            with self.lock:
                for event_id, event in self.events.items():
                    if event.timestamp.timestamp() < cutoff_time:
                        events_to_remove.append(event_id)

                for event_id in events_to_remove:
                    del self.events[event_id]

            self.logger.info(f"Очищено {len(events_to_remove)} старых событий")
            return len(events_to_remove)

        except Exception as e:
            self.logger.error(f"Ошибка очистки старых событий: {e}")
            return 0

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера"""
        try:
            return {
                "total_events": self.stats["total_events"],
                "active_sessions": self.stats["active_sessions"],
                "interface_errors": self.stats["interface_errors"],
                "security_events": self.stats["security_events"],
                "unique_users": len(self.interface_analytics["user_activity"]),
                "status": "active",
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            with self.lock:
                self.events.clear()
                self.user_sessions.clear()
                self.interface_analytics = {
                    "event_counts": {},
                    "user_activity": {},
                    "interface_performance": {},
                    "error_patterns": {},
                }
                self.stats = {
                    "total_events": 0,
                    "active_sessions": 0,
                    "interface_errors": 0,
                    "security_events": 0,
                }
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")


# Глобальный экземпляр
user_interface_manager_main = UserInterfaceManagerMain()
