#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для работы со временем в экстренных ситуациях
Применение Single Responsibility принципа
"""

from datetime import datetime
from typing import Any, Dict


class TimePeriodAnalyzer:
    """Анализатор временных периодов"""

    PEAK_HOURS = set(range(8, 11)) | set(range(17, 20))  # 8-10, 17-19
    NIGHT_HOURS = set(range(22, 24)) | set(range(0, 6))  # 22-23, 0-5
    WEEKEND_DAYS = {5, 6}  # Суббота, воскресенье

    def __init__(self):
        """Инициализация анализатора временных периодов"""
        pass

    @staticmethod
    def is_peak_hours(hour: int) -> bool:
        """
        Проверить, являются ли часы пиковыми

        Args:
            hour: Час дня (0-23)

        Returns:
            bool: True если часы пиковые
        """
        return hour in TimePeriodAnalyzer.PEAK_HOURS

    @staticmethod
    def is_night_time(hour: int) -> bool:
        """
        Проверить, является ли время ночным

        Args:
            hour: Час дня (0-23)

        Returns:
            bool: True если время ночное
        """
        return hour in TimePeriodAnalyzer.NIGHT_HOURS

    @staticmethod
    def is_weekend(weekday: int) -> bool:
        """
        Проверить, является ли день выходным

        Args:
            weekday: День недели (0-6)

        Returns:
            bool: True если день выходной
        """
        return weekday in TimePeriodAnalyzer.WEEKEND_DAYS

    @staticmethod
    def get_time_period(hour: int) -> str:
        """
        Получить период времени

        Args:
            hour: Час дня (0-23)

        Returns:
            str: Период времени
        """
        if 0 <= hour < 6:
            return "night"
        elif 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        else:
            return "evening"


class ResponseTimeCalculator:
    """Калькулятор времени реагирования"""

    def __init__(self):
        """Инициализация калькулятора времени реагирования"""
        pass

    @staticmethod
    def calculate_response_time(
        start_time: datetime, end_time: datetime
    ) -> float:
        """
        Рассчитать время реагирования в минутах

        Args:
            start_time: Время начала
            end_time: Время окончания

        Returns:
            float: Время в минутах
        """
        try:
            delta = end_time - start_time
            return delta.total_seconds() / 60
        except Exception:
            return 0.0

    @staticmethod
    def calculate_average_response_time(times: list) -> float:
        """
        Рассчитать среднее время реагирования

        Args:
            times: Список времен в минутах

        Returns:
            float: Среднее время
        """
        try:
            if not times:
                return 0.0
            return sum(times) / len(times)
        except Exception:
            return 0.0

    @staticmethod
    def is_response_time_acceptable(
        response_time: float, max_acceptable: float = 30.0
    ) -> bool:
        """
        Проверить, приемлемо ли время реагирования

        Args:
            response_time: Время реагирования в минутах
            max_acceptable: Максимально приемлемое время

        Returns:
            bool: True если время приемлемо
        """
        return response_time <= max_acceptable


class TimeBasedRiskAnalyzer:
    """Анализатор рисков на основе времени"""

    def __init__(self):
        """Инициализация анализатора рисков на основе времени"""
        pass

    @staticmethod
    def calculate_time_risk_factor(hour: int, weekday: int) -> float:
        """
        Рассчитать фактор риска на основе времени

        Args:
            hour: Час дня (0-23)
            weekday: День недели (0-6)

        Returns:
            float: Фактор риска (0.0-1.0)
        """
        risk_factor = 0.0

        # Ночное время - повышенный риск
        if TimePeriodAnalyzer.is_night_time(hour):
            risk_factor += 0.3

        # Пиковое время - высокая активность
        if TimePeriodAnalyzer.is_peak_hours(hour):
            risk_factor += 0.2

        # Выходные - повышенная активность
        if TimePeriodAnalyzer.is_weekend(weekday):
            risk_factor += 0.1

        return min(risk_factor, 1.0)

    @staticmethod
    def get_risk_level(risk_factor: float) -> str:
        """
        Получить уровень риска

        Args:
            risk_factor: Фактор риска (0.0-1.0)

        Returns:
            str: Уровень риска
        """
        if risk_factor >= 0.7:
            return "high"
        elif risk_factor >= 0.4:
            return "medium"
        else:
            return "low"


class EmergencyTimeUtils:
    """Основные утилиты для работы со временем"""

    def __init__(self):
        """Инициализация утилит для работы со временем"""
        pass

    @staticmethod
    def get_current_time_info() -> Dict[str, Any]:
        """
        Получить информацию о текущем времени

        Returns:
            Dict: Информация о времени
        """
        now = datetime.now()

        return {
            "hour": now.hour,
            "weekday": now.weekday(),
            "is_peak": TimePeriodAnalyzer.is_peak_hours(now.hour),
            "is_night": TimePeriodAnalyzer.is_night_time(now.hour),
            "is_weekend": TimePeriodAnalyzer.is_weekend(now.weekday()),
            "time_period": TimePeriodAnalyzer.get_time_period(now.hour),
            "risk_factor": TimeBasedRiskAnalyzer.calculate_time_risk_factor(
                now.hour, now.weekday()
            ),
        }

    @staticmethod
    def format_timestamp(
        timestamp: datetime, format_str: str = "%H:%M:%S %d.%m.%Y"
    ) -> str:
        """
        Форматировать временную метку

        Args:
            timestamp: Временная метка
            format_str: Формат строки

        Returns:
            str: Отформатированная строка
        """
        try:
            return timestamp.strftime(format_str)
        except Exception:
            return str(timestamp)
