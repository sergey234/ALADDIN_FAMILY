# -*- coding: utf-8 -*-
"""
Монитор времени для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from security.bots.parental_control_bot import TimeLimitData, ActivityAlert


@dataclass
class TimeUsage:
    """Использование времени"""
    device_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    is_active: bool = True


@dataclass
class TimeStats:
    """Статистика времени"""
    total_usage_minutes: int = 0
    daily_usage: Dict[str, int] = None  # device_type -> minutes
    weekly_usage: Dict[str, int] = None  # device_type -> minutes
    violations_count: int = 0

    def __post_init__(self):
        if self.daily_usage is None:
            self.daily_usage = {}
        if self.weekly_usage is None:
            self.weekly_usage = {}


class TimeMonitor:
    """Монитор времени использования устройств"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.active_sessions: Dict[str, Dict[str, TimeUsage]] = {}  # child_id -> device_type -> TimeUsage
        self.time_limits: Dict[str, Dict[str, int]] = {}  # child_id -> device_type -> minutes
        self.daily_usage: Dict[str, Dict[str, int]] = {}  # child_id -> device_type -> minutes
        self.stats = TimeStats()
        self._lock = asyncio.Lock()

    async def start_session(self, child_id: str, device_type: str) -> bool:
        """Начало сессии использования устройства"""
        try:
            async with self._lock:
                if child_id not in self.active_sessions:
                    self.active_sessions[child_id] = {}

                if device_type in self.active_sessions[child_id]:
                    # Сессия уже активна
                    return False

                # Создание новой сессии
                session = TimeUsage(
                    device_type=device_type,
                    start_time=datetime.now(),
                    is_active=True
                )

                self.active_sessions[child_id][device_type] = session

                self.logger.info(f"Начата сессия {device_type} для {child_id}")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка начала сессии: {e}")
            return False

    async def end_session(self, child_id: str, device_type: str) -> Optional[int]:
        """Завершение сессии использования устройства"""
        try:
            async with self._lock:
                if (child_id not in self.active_sessions or
                        device_type not in self.active_sessions[child_id]):
                    return None

                session = self.active_sessions[child_id][device_type]
                session.end_time = datetime.now()
                session.is_active = False

                # Расчет продолжительности
                duration = session.end_time - session.start_time
                duration_minutes = int(duration.total_seconds() / 60)
                session.duration_minutes = duration_minutes

                # Обновление дневного использования
                await self._update_daily_usage(child_id, device_type, duration_minutes)

                # Удаление сессии
                del self.active_sessions[child_id][device_type]

                self.logger.info(f"Завершена сессия {device_type} для {child_id}: {duration_minutes}м")
                return duration_minutes

        except Exception as e:
            self.logger.error(f"Ошибка завершения сессии: {e}")
            return None

    async def set_time_limit(self, child_id: str, device_type: str, minutes: int) -> bool:
        """Установка лимита времени для устройства"""
        try:
            # Валидация данных
            time_data = TimeLimitData(device_type=device_type, minutes=minutes)

            async with self._lock:
                if child_id not in self.time_limits:
                    self.time_limits[child_id] = {}

                self.time_limits[child_id][device_type] = time_data.minutes

                self.logger.info(f"Установлен лимит {device_type}: {minutes}м для {child_id}")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка установки лимита времени: {e}")
            return False

    async def check_time_violation(self, child_id: str, device_type: str) -> Optional[ActivityAlert]:
        """Проверка нарушения лимита времени"""
        try:
            async with self._lock:
                # Получение текущего использования
                current_usage = await self.get_current_usage(child_id, device_type)
                limit = self.time_limits.get(child_id, {}).get(device_type, 0)

                if limit == 0:  # Лимит не установлен
                    return None

                if current_usage > limit:
                    # Создание алерта о нарушении
                    alert = ActivityAlert(
                        child_id=child_id,
                        alert_type="time_violation",
                        severity="medium",
                        message=f"Превышен лимит времени {device_type}: {current_usage}м > {limit}м",
                        timestamp=datetime.now(),
                        action_required=True,
                        data={
                            "device_type": device_type,
                            "current_usage": current_usage,
                            "limit": limit,
                        }
                    )

                    self.stats.violations_count += 1
                    self.logger.warning(f"Нарушение времени для {child_id}: {device_type}")
                    return alert

                return None

        except Exception as e:
            self.logger.error(f"Ошибка проверки нарушения времени: {e}")
            return None

    async def get_current_usage(self, child_id: str, device_type: str) -> int:
        """Получение текущего использования времени"""
        try:
            async with self._lock:
                # Проверка активной сессии
                if (child_id in self.active_sessions and
                        device_type in self.active_sessions[child_id]):
                    session = self.active_sessions[child_id][device_type]
                    if session.is_active:
                        current_duration = datetime.now() - session.start_time
                        return int(current_duration.total_seconds() / 60)

                # Возврат дневного использования
                return self.daily_usage.get(child_id, {}).get(device_type, 0)

        except Exception as e:
            self.logger.error(f"Ошибка получения текущего использования: {e}")
            return 0

    async def get_daily_usage(self, child_id: str) -> Dict[str, int]:
        """Получение дневного использования"""
        return self.daily_usage.get(child_id, {}).copy()

    async def get_weekly_usage(self, child_id: str) -> Dict[str, int]:
        """Получение недельного использования"""
        # Простая реализация - можно расширить с реальным хранением
        daily = await self.get_daily_usage(child_id)
        weekly = {}
        for device_type, minutes in daily.items():
            weekly[device_type] = minutes * 7  # Упрощенный расчет
        return weekly

    async def get_time_limits(self, child_id: str) -> Dict[str, int]:
        """Получение лимитов времени"""
        return self.time_limits.get(child_id, {}).copy()

    async def get_active_sessions(self, child_id: str) -> List[TimeUsage]:
        """Получение активных сессий"""
        if child_id not in self.active_sessions:
            return []

        return [
            session for session in self.active_sessions[child_id].values()
            if session.is_active
        ]

    async def _update_daily_usage(self, child_id: str, device_type: str, minutes: int):
        """Обновление дневного использования"""
        if child_id not in self.daily_usage:
            self.daily_usage[child_id] = {}

        current_usage = self.daily_usage[child_id].get(device_type, 0)
        self.daily_usage[child_id][device_type] = current_usage + minutes

        # Обновление общей статистики
        self.stats.total_usage_minutes += minutes
        self.stats.daily_usage[device_type] = \
            self.stats.daily_usage.get(device_type, 0) + minutes

    async def reset_daily_usage(self, child_id: str = None):
        """Сброс дневного использования"""
        async with self._lock:
            if child_id:
                if child_id in self.daily_usage:
                    del self.daily_usage[child_id]
            else:
                self.daily_usage.clear()

            self.logger.info(f"Сброшено дневное использование для {child_id or 'всех'}")

    async def get_stats(self) -> TimeStats:
        """Получение статистики"""
        return self.stats

    async def validate_time_limit_data(self, device_type: str, minutes: int) -> Tuple[bool, Optional[str]]:
        """Валидация данных лимита времени"""
        try:
            TimeLimitData(device_type=device_type, minutes=minutes)
            return True, None
        except Exception as e:
            return False, str(e)

    async def get_usage_report(self, child_id: str) -> Dict[str, Any]:
        """Получение отчета об использовании"""
        daily = await self.get_daily_usage(child_id)
        weekly = await self.get_weekly_usage(child_id)
        limits = await self.get_time_limits(child_id)
        active_sessions = await self.get_active_sessions(child_id)

        return {
            "child_id": child_id,
            "daily_usage": daily,
            "weekly_usage": weekly,
            "time_limits": limits,
            "active_sessions": len(active_sessions),
            "violations_today": self.stats.violations_count,
            "total_usage_minutes": sum(daily.values()),
            "timestamp": datetime.now().isoformat()
        }
