#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Behavioral Analytics Engine Main - Основной движок поведенческой аналитики
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

# Уровни риска
LOW = "low"  # Низкий риск
MEDIUM = "medium"  # Средний риск
HIGH = "high"  # Высокий риск
CRITICAL = "critical"  # Критический риск


@dataclass
class UserBehavior:
    """Поведение пользователя"""

    user_id: str
    action_type: str
    timestamp: datetime
    risk_score: float
    metadata: Dict[str, Any]


class BehavioralAnalyticsEngineMain:
    """Основной движок поведенческой аналитики"""

    def __init__(self):
        self.logger = logging.getLogger(
            "ALADDIN.BehavioralAnalyticsEngineMain"
        )
        self.user_behaviors = {}
        self.risk_patterns = {}
        self.anomaly_threshold = 0.7
        self.stats = {
            "behaviors_analyzed": 0,
            "anomalies_detected": 0,
            "false_positives": 0,
        }
        self._init_risk_patterns()

    def _init_risk_patterns(self) -> None:
        """Инициализация паттернов риска"""
        try:
            self.risk_patterns = {
                "suspicious_login": {
                    "pattern": "unusual_time",
                    "weight": 0.8,
                    "description": "Подозрительное время входа",
                },
                "rapid_actions": {
                    "pattern": "high_frequency",
                    "weight": 0.6,
                    "description": "Высокая частота действий",
                },
                "unusual_location": {
                    "pattern": "geographic_anomaly",
                    "weight": 0.9,
                    "description": "Необычное географическое расположение",
                },
            }
            self.logger.info("Паттерны риска инициализированы")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации паттернов риска: {e}")

    def analyze_behavior(self, behavior: UserBehavior) -> Dict[str, Any]:
        """Анализ поведения пользователя"""
        try:
            self.stats["behaviors_analyzed"] += 1

            # Анализ аномалий
            anomaly_score = self._detect_anomalies(behavior)

            # Анализ рисков
            risk_analysis = self._analyze_risks(behavior)

            # Определение уровня риска
            risk_level = self._determine_risk_level(
                anomaly_score, risk_analysis
            )

            # Генерация рекомендаций
            recommendations = self._generate_recommendations(
                risk_level, behavior
            )

            result = {
                "user_id": behavior.user_id,
                "anomaly_score": anomaly_score,
                "risk_analysis": risk_analysis,
                "risk_level": risk_level,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
            }

            # Обновление статистики
            if anomaly_score > self.anomaly_threshold:
                self.stats["anomalies_detected"] += 1

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа поведения: {e}")
            return {"error": str(e)}

    def _detect_anomalies(self, behavior: UserBehavior) -> float:
        """Обнаружение аномалий"""
        try:
            user_id = behavior.user_id

            # Получение истории поведения пользователя
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = []

            user_history = self.user_behaviors[user_id]

            # Анализ временных паттернов
            time_anomaly = self._analyze_time_patterns(behavior, user_history)

            # Анализ частоты действий
            frequency_anomaly = self._analyze_frequency_patterns(
                behavior, user_history
            )

            # Анализ географических паттернов
            location_anomaly = self._analyze_location_patterns(
                behavior, user_history
            )

            # Итоговый скор аномалии
            anomaly_score = (
                time_anomaly + frequency_anomaly + location_anomaly
            ) / 3

            # Добавление поведения в историю
            user_history.append(behavior)

            # Ограничение размера истории
            if len(user_history) > 1000:
                user_history.pop(0)

            return min(max(anomaly_score, 0.0), 1.0)

        except Exception as e:
            self.logger.error(f"Ошибка обнаружения аномалий: {e}")
            return 0.5

    def _analyze_time_patterns(
        self, behavior: UserBehavior, history: List[UserBehavior]
    ) -> float:
        """Анализ временных паттернов"""
        try:
            if not history:
                return 0.0

            current_hour = behavior.timestamp.hour

            # Анализ обычного времени активности
            usual_hours = [
                b.timestamp.hour for b in history[-100:]
            ]  # Последние 100 действий

            if not usual_hours:
                return 0.0

            # Проверка на необычное время
            if current_hour not in usual_hours:
                return 0.8  # Высокий риск необычного времени

            return 0.2  # Низкий риск

        except Exception as e:
            self.logger.error(f"Ошибка анализа временных паттернов: {e}")
            return 0.5

    def _analyze_frequency_patterns(
        self, behavior: UserBehavior, history: List[UserBehavior]
    ) -> float:
        """Анализ паттернов частоты"""
        try:
            if not history:
                return 0.0

            # Анализ частоты за последний час
            recent_actions = [
                b
                for b in history
                if (behavior.timestamp - b.timestamp).total_seconds() < 3600
            ]

            if len(recent_actions) > 10:  # Более 10 действий за час
                return 0.7  # Высокий риск высокой частоты

            return 0.1  # Низкий риск

        except Exception as e:
            self.logger.error(f"Ошибка анализа частоты: {e}")
            return 0.5

    def _analyze_location_patterns(
        self, behavior: UserBehavior, history: List[UserBehavior]
    ) -> float:
        """Анализ географических паттернов"""
        try:
            # Здесь должна быть логика анализа местоположения
            # Пока возвращаем нейтральное значение
            return 0.3

        except Exception as e:
            self.logger.error(f"Ошибка анализа местоположения: {e}")
            return 0.5

    def _analyze_risks(self, behavior: UserBehavior) -> Dict[str, Any]:
        """Анализ рисков"""
        try:
            risks = {}

            for risk_name, risk_config in self.risk_patterns.items():
                # Проверка соответствия паттерну
                if self._matches_pattern(behavior, risk_config):
                    risks[risk_name] = {
                        "weight": risk_config["weight"],
                        "description": risk_config["description"],
                        "detected": True,
                    }
                else:
                    risks[risk_name] = {
                        "weight": 0.0,
                        "description": risk_config["description"],
                        "detected": False,
                    }

            return risks

        except Exception as e:
            self.logger.error(f"Ошибка анализа рисков: {e}")
            return {}

    def _matches_pattern(
        self, behavior: UserBehavior, pattern_config: Dict[str, Any]
    ) -> bool:
        """Проверка соответствия паттерну"""
        try:
            pattern_type = pattern_config["pattern"]

            if pattern_type == "unusual_time":
                return (
                    behavior.timestamp.hour < 6 or behavior.timestamp.hour > 22
                )
            elif pattern_type == "high_frequency":
                # Логика проверки высокой частоты
                return False
            elif pattern_type == "geographic_anomaly":
                # Логика проверки географических аномалий
                return False

            return False

        except Exception as e:
            self.logger.error(f"Ошибка проверки паттерна: {e}")
            return False

    def _determine_risk_level(
        self, anomaly_score: float, risk_analysis: Dict[str, Any]
    ) -> str:
        """Определение уровня риска"""
        try:
            # Расчет общего скора риска
            total_risk = anomaly_score

            # Добавление весов из анализа рисков
            for risk_name, risk_data in risk_analysis.items():
                if risk_data.get("detected", False):
                    total_risk += risk_data["weight"] * 0.1

            # Нормализация
            total_risk = min(max(total_risk, 0.0), 1.0)

            # Определение уровня
            if total_risk >= 0.8:
                return CRITICAL
            elif total_risk >= 0.6:
                return HIGH
            elif total_risk >= 0.4:
                return MEDIUM
            else:
                return LOW

        except Exception as e:
            self.logger.error(f"Ошибка определения уровня риска: {e}")
            return MEDIUM

    def _generate_recommendations(
        self, risk_level: str, behavior: UserBehavior
    ) -> List[str]:
        """Генерация рекомендаций"""
        try:
            recommendations = []

            if risk_level == CRITICAL:
                recommendations.extend(
                    [
                        "Немедленно заблокировать пользователя",
                        "Уведомить администратора безопасности",
                        "Провести дополнительную проверку",
                    ]
                )
            elif risk_level == HIGH:
                recommendations.extend(
                    [
                        "Усилить мониторинг пользователя",
                        "Запросить дополнительную аутентификацию",
                        "Уведомить пользователя о подозрительной активности",
                    ]
                )
            elif risk_level == MEDIUM:
                recommendations.extend(
                    [
                        "Продолжить мониторинг",
                        "Собрать дополнительную информацию",
                    ]
                )
            else:
                recommendations.append("Продолжить обычный мониторинг")

            return recommendations

        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")
            return ["Ошибка анализа"]

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса движка"""
        try:
            return {
                "behaviors_analyzed": self.stats["behaviors_analyzed"],
                "anomalies_detected": self.stats["anomalies_detected"],
                "false_positives": self.stats["false_positives"],
                "active_users": len(self.user_behaviors),
                "risk_patterns_count": len(self.risk_patterns),
                "status": "active",
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            self.user_behaviors.clear()
            self.risk_patterns.clear()
            self.stats = {
                "behaviors_analyzed": 0,
                "anomalies_detected": 0,
                "false_positives": 0,
            }
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")


# Глобальный экземпляр
behavioral_analytics_engine_main = BehavioralAnalyticsEngineMain()
