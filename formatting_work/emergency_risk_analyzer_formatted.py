#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор рисков для экстренных ситуаций
Применение Single Responsibility принципа
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .emergency_models import EmergencyEvent, EmergencySeverity, EmergencyType
from .emergency_time_utils import TimeBasedRiskAnalyzer, TimePeriodAnalyzer


class EmergencyRiskAnalyzer:
    """Анализатор рисков экстренных ситуаций"""

    def __init__(self):
        self.risk_factors = {
            "temporal": 0.3,
            "spatial": 0.2,
            "type": 0.2,
            "severity": 0.3,
        }

    def calculate_risk_score(self, event: EmergencyEvent) -> float:
        """
        Рассчитать оценку риска для события

        Args:
            event: Экстренное событие

        Returns:
            float: Оценка риска (0.0-1.0)
        """
        try:
            risk_score = 0.0

            # Временной фактор риска
            temporal_risk = self._calculate_temporal_risk(event)
            risk_score += temporal_risk * self.risk_factors["temporal"]

            # Пространственный фактор риска
            spatial_risk = self._calculate_spatial_risk(event)
            risk_score += spatial_risk * self.risk_factors["spatial"]

            # Типовой фактор риска
            type_risk = self._calculate_type_risk(event)
            risk_score += type_risk * self.risk_factors["type"]

            # Фактор серьезности
            severity_risk = self._calculate_severity_risk(event)
            risk_score += severity_risk * self.risk_factors["severity"]

            return min(risk_score, 1.0)

        except Exception:
            return 0.5  # Средний риск при ошибке

    def _calculate_temporal_risk(self, event: EmergencyEvent) -> float:
        """Рассчитать временной фактор риска"""
        try:
            now = datetime.now()
            hour = now.hour
            weekday = now.weekday()

            # Используем существующий анализатор времени
            return TimeBasedRiskAnalyzer.calculate_time_risk_factor(
                hour, weekday
            )
        except Exception:
            return 0.5

    def _calculate_spatial_risk(self, event: EmergencyEvent) -> float:
        """Рассчитать пространственный фактор риска"""
        try:
            location = event.location
            if not location or "coordinates" not in location:
                return 0.5

            coords = location["coordinates"]
            if not isinstance(coords, (list, tuple)) or len(coords) != 2:
                return 0.5

            lat, lon = coords

            # Проверяем на валидность координат
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return 0.8  # Высокий риск для невалидных координат

            # Анализируем близость к опасным зонам
            risk_zones = self._get_risk_zones()
            min_distance = min(
                [
                    self._calculate_distance(coords, zone["coordinates"])
                    for zone in risk_zones
                ]
            )

            # Чем ближе к опасной зоне, тем выше риск
            if min_distance < 1.0:  # 1 км
                return 0.9
            elif min_distance < 5.0:  # 5 км
                return 0.7
            elif min_distance < 10.0:  # 10 км
                return 0.5
            else:
                return 0.3

        except Exception:
            return 0.5

    def _calculate_type_risk(self, event: EmergencyEvent) -> float:
        """Рассчитать типовой фактор риска"""
        try:
            type_risk_scores = {
                EmergencyType.MEDICAL: 0.9,
                EmergencyType.FIRE: 0.8,
                EmergencyType.POLICE: 0.7,
                EmergencyType.SECURITY: 0.6,
                EmergencyType.ACCIDENT: 0.8,
                EmergencyType.NATURAL_DISASTER: 0.9,
                EmergencyType.TECHNICAL: 0.5,
                EmergencyType.PERSONAL: 0.4,
            }

            return type_risk_scores.get(event.emergency_type, 0.5)
        except Exception:
            return 0.5

    def _calculate_severity_risk(self, event: EmergencyEvent) -> float:
        """Рассчитать фактор риска по серьезности"""
        try:
            severity_risk_scores = {
                EmergencySeverity.LOW: 0.2,
                EmergencySeverity.MEDIUM: 0.5,
                EmergencySeverity.HIGH: 0.8,
                EmergencySeverity.CRITICAL: 0.95,
                EmergencySeverity.LIFE_THREATENING: 1.0,
            }

            return severity_risk_scores.get(event.severity, 0.5)
        except Exception:
            return 0.5

    def _get_risk_zones(self) -> List[Dict[str, Any]]:
        """Получить список опасных зон"""
        return [
            {
                "name": "Аэропорт",
                "coordinates": (55.7558, 37.6176),
                "risk_level": 0.8,
            },
            {
                "name": "Вокзал",
                "coordinates": (55.7558, 37.6176),
                "risk_level": 0.7,
            },
            {
                "name": "Метро",
                "coordinates": (55.7558, 37.6176),
                "risk_level": 0.6,
            },
            {
                "name": "Торговый центр",
                "coordinates": (55.7558, 37.6176),
                "risk_level": 0.5,
            },
        ]

    def _calculate_distance(
        self, coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> float:
        """Рассчитать расстояние между координатами в км"""
        try:
            import geopy.distance

            return geopy.distance.geodesic(coord1, coord2).kilometers
        except Exception:
            # Простое приближение для расстояния
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            return (
                np.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111
            )  # Примерно 111 км на градус

    def get_risk_level(self, risk_score: float) -> str:
        """
        Получить уровень риска по оценке

        Args:
            risk_score: Оценка риска (0.0-1.0)

        Returns:
            str: Уровень риска
        """
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def analyze_risk_trends(
        self, events: List[EmergencyEvent], days: int = 7
    ) -> Dict[str, Any]:
        """
        Анализировать тренды рисков

        Args:
            events: Список событий
            days: Количество дней для анализа

        Returns:
            Dict[str, Any]: Анализ трендов
        """
        try:
            if not events:
                return {}

            # Фильтруем события по времени
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_events = [e for e in events if e.timestamp >= cutoff_date]

            if not recent_events:
                return {}

            # Рассчитываем риски для всех событий
            risk_scores = [
                self.calculate_risk_score(event) for event in recent_events
            ]

            # Анализируем тренды
            avg_risk = np.mean(risk_scores)
            max_risk = np.max(risk_scores)
            min_risk = np.min(risk_scores)

            # Анализируем по дням
            daily_risks = {}
            for event in recent_events:
                day = event.timestamp.date()
                if day not in daily_risks:
                    daily_risks[day] = []
                daily_risks[day].append(self.calculate_risk_score(event))

            # Рассчитываем средние риски по дням
            daily_avg_risks = {
                str(day): np.mean(risks) for day, risks in daily_risks.items()
            }

            return {
                "average_risk": avg_risk,
                "max_risk": max_risk,
                "min_risk": min_risk,
                "total_events": len(recent_events),
                "daily_risks": daily_avg_risks,
                "risk_trend": self._calculate_risk_trend(
                    list(daily_avg_risks.values())
                ),
            }

        except Exception:
            return {}

    def _calculate_risk_trend(self, daily_risks: List[float]) -> str:
        """Рассчитать тренд рисков"""
        try:
            if len(daily_risks) < 2:
                return "stable"

            # Простой линейный тренд
            x = np.arange(len(daily_risks))
            y = np.array(daily_risks)

            # Вычисляем наклон
            slope = np.polyfit(x, y, 1)[0]

            if slope > 0.05:
                return "increasing"
            elif slope < -0.05:
                return "decreasing"
            else:
                return "stable"

        except Exception:
            return "unknown"

    def get_risk_recommendations(self, risk_score: float) -> List[str]:
        """
        Получить рекомендации по снижению риска

        Args:
            risk_score: Оценка риска

        Returns:
            List[str]: Список рекомендаций
        """
        recommendations = []

        if risk_score >= 0.8:
            recommendations.extend(
                [
                    "Немедленно вызвать экстренные службы",
                    "Эвакуировать людей из опасной зоны",
                    "Активировать план экстренного реагирования",
                ]
            )
        elif risk_score >= 0.6:
            recommendations.extend(
                [
                    "Усилить мониторинг ситуации",
                    "Подготовить резервные планы",
                    "Уведомить ответственные службы",
                ]
            )
        elif risk_score >= 0.4:
            recommendations.extend(
                [
                    "Продолжить наблюдение",
                    "Подготовить ресурсы",
                    "Информировать заинтересованные стороны",
                ]
            )
        else:
            recommendations.extend(
                ["Рутинный мониторинг", "Поддержание готовности"]
            )

        return recommendations
