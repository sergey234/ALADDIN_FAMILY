#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Psychological Support Agent
Система психологической поддержки для детей, родителей и пожилых людей

Автор: ALADDIN Security Team
Версия: 2.5
Дата: 2025-01-26
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.base import SecurityBase
from core.security_base import SecurityEvent, IncidentSeverity


class EmotionalState(Enum):
    """Эмоциональные состояния"""
    HAPPY = "happy"  # Счастливый
    CALM = "calm"  # Спокойный
    ANXIOUS = "anxious"  # Тревожный
    SAD = "sad"  # Грустный
    ANGRY = "angry"  # Злой
    STRESSED = "stressed"  # Стресс
    CONFUSED = "confused"  # Запутанный
    LONELY = "lonely"  # Одинокий


class SupportType(Enum):
    """Типы психологической поддержки"""
    EMOTIONAL = "emotional"  # Эмоциональная поддержка
    BEHAVIORAL = "behavioral"  # Поведенческая поддержка
    EDUCATIONAL = "educational"  # Образовательная поддержка
    SOCIAL = "social"  # Социальная поддержка
    CRISIS = "crisis"  # Кризисная поддержка


class AgeGroup(Enum):
    """Возрастные группы"""
    CHILD_3_6 = "child_3_6"  # 3-6 лет
    CHILD_7_12 = "child_7_12"  # 7-12 лет
    TEEN_13_17 = "teen_13_17"  # 13-17 лет
    ADULT_18_65 = "adult_18_65"  # 18-65 лет
    ELDERLY_65_PLUS = "elderly_65_plus"  # 65+ лет


class PsychologicalSupportAgent(SecurityBase):
    """
    Агент психологической поддержки
    Обеспечивает психологическую помощь для всех возрастных групп
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("PsychologicalSupportAgent", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.emotional_history: Dict[str, List[Dict[str, Any]]] = {}
        self.support_sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.crisis_alerts: List[Dict[str, Any]] = []

        # Конфигурация
        self.crisis_threshold = 0.8  # Порог кризиса
        self.support_cooldown = 300  # Кулдаун поддержки (секунды)
        self.max_sessions_per_day = 10  # Максимум сессий в день

        # Инициализация
        self._initialize_support_resources()
        self._initialize_crisis_protocols()

    def _initialize_support_resources(self) -> None:
        """Инициализация ресурсов поддержки"""
        self.support_resources = {
            "emotional_support": {
                "child_3_6": [
                    "Ты молодец! Ты справишься!",
                    "Мама и папа любят тебя очень сильно!",
                    "Давай поиграем в твою любимую игру!",
                    "Ты очень умный и талантливый!"
                ],
                "child_7_12": [
                    "Я понимаю, что тебе трудно. Это нормально.",
                    "Ты можешь рассказать мне, что тебя беспокоит?",
                    "Помни, что ошибки - это часть обучения.",
                    "Ты делаешь отличные успехи!"
                ],
                "teen_13_17": [
                    "Подростковый возраст - это сложное время, но ты справишься.",
                    "Твои чувства важны и имеют значение.",
                    "Не бойся просить помощи, когда она нужна.",
                    "Ты уникальная личность с большим потенциалом."
                ],
                "adult_18_65": [
                    "Взрослая жизнь полна вызовов, но у тебя есть силы их преодолеть.",
                    "Помни о своих достижениях и сильных сторонах.",
                    "Не стесняйтесь обращаться за поддержкой.",
                    "Каждый день - это новая возможность для роста."
                ],
                "elderly_65_plus": [
                    "Ваш жизненный опыт - это огромное богатство.",
                    "Вы заслуживаете уважения и заботы.",
                    "Не стесняйтесь просить помощи, когда она нужна.",
                    "Ваша мудрость помогает другим."
                ]
            },
            "crisis_interventions": {
                "immediate": [
                    "Сейчас с вами свяжется специалист.",
                    "Вы не одни. Помощь уже в пути.",
                    "Дышите глубоко. Вы в безопасности.",
                    "Кризис временный. Вы справитесь."
                ],
                "follow_up": [
                    "Как вы себя чувствуете сейчас?",
                    "Что помогает вам справляться?",
                    "Нужна ли дополнительная поддержка?",
                    "Помните, что помощь всегда доступна."
                ]
            }
        }

    def _initialize_crisis_protocols(self) -> None:
        """Инициализация протоколов кризиса"""
        self.crisis_protocols = {
            "suicidal_ideation": {
                "severity": "critical",
                "immediate_actions": [
                    "Немедленно связаться с кризисной службой",
                    "Уведомить семью",
                    "Обеспечить постоянное наблюдение"
                ],
                "support_actions": [
                    "Предоставить эмоциональную поддержку",
                    "Направить к специалисту",
                    "Обеспечить безопасность"
                ]
            },
            "severe_depression": {
                "severity": "high",
                "immediate_actions": [
                    "Связаться с психологом",
                    "Уведомить семью",
                    "Предложить экстренную поддержку"
                ],
                "support_actions": [
                    "Предоставить эмоциональную поддержку",
                    "Направить к специалисту",
                    "Мониторить состояние"
                ]
            },
            "anxiety_attack": {
                "severity": "medium",
                "immediate_actions": [
                    "Применить техники релаксации",
                    "Обеспечить спокойную обстановку",
                    "Предложить поддержку"
                ],
                "support_actions": [
                    "Дыхательные упражнения",
                    "Медитация",
                    "Эмоциональная поддержка"
                ]
            }
        }

    def analyze_emotional_state(
        self,
        user_id: str,
        text_input: str,
        behavior_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Анализ эмоционального состояния пользователя"""
        try:
            # Простой анализ текста (в реальной системе будет использоваться ML)
            emotional_indicators = {
                "happy": ["рад", "счастлив", "отлично", "хорошо", "ура", "круто"],
                "sad": ["грустно", "печально", "плохо", "ужасно", "депрессия"],
                "angry": ["злой", "злюсь", "бешенство", "ярость", "ненавижу"],
                "anxious": ["тревожно", "волнуюсь", "боюсь", "страшно", "паника"],
                "stressed": ["стресс", "устал", "напряжение", "давление", "перегрузка"],
                "lonely": ["одиноко", "один", "никого", "пустота", "изоляция"]
            }

            text_lower = text_input.lower()
            emotional_scores = {}

            for emotion, indicators in emotional_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text_lower)
                emotional_scores[emotion] = score

            # Определяем доминирующую эмоцию
            dominant_emotion = max(emotional_scores, key=emotional_scores.get)
            confidence = emotional_scores[dominant_emotion] / len(text_input.split())

            # Анализ поведения
            behavior_analysis = self._analyze_behavior_patterns(
                user_id, behavior_data
            )

            # Определяем уровень риска
            risk_level = self._assess_risk_level(
                dominant_emotion, confidence, behavior_analysis
            )

            result = {
                "user_id": user_id,
                "dominant_emotion": dominant_emotion,
                "confidence": confidence,
                "emotional_scores": emotional_scores,
                "risk_level": risk_level,
                "behavior_analysis": behavior_analysis,
                "timestamp": datetime.now().isoformat(),
                "recommendations": self._generate_recommendations(
                    dominant_emotion, risk_level, user_id
                )
            }

            # Сохраняем в историю
            self._save_emotional_analysis(user_id, result)

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа эмоционального состояния: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_behavior_patterns(
        self, user_id: str, behavior_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Анализ поведенческих паттернов"""
        if not behavior_data:
            return {"patterns": [], "risk_indicators": []}

        patterns = []
        risk_indicators = []

        # Анализ активности
        if behavior_data.get("activity_level", 0) < 0.3:
            patterns.append("low_activity")
            risk_indicators.append("social_withdrawal")

        # Анализ социального взаимодействия
        if behavior_data.get("social_interactions", 0) < 0.2:
            patterns.append("social_isolation")
            risk_indicators.append("loneliness")

        # Анализ сна
        if behavior_data.get("sleep_quality", 0) < 0.4:
            patterns.append("sleep_disturbance")
            risk_indicators.append("stress")

        return {
            "patterns": patterns,
            "risk_indicators": risk_indicators,
            "analysis_confidence": 0.8
        }

    def _assess_risk_level(
        self,
        dominant_emotion: str,
        confidence: float,
        behavior_analysis: Dict[str, Any]
    ) -> str:
        """Оценка уровня риска"""
        risk_score = 0

        # Эмоциональные факторы
        if dominant_emotion in ["sad", "angry", "anxious", "stressed", "lonely"]:
            risk_score += 0.3

        # Поведенческие факторы
        risk_indicators = behavior_analysis.get("risk_indicators", [])
        risk_score += len(risk_indicators) * 0.2

        # Уровень уверенности
        if confidence > 0.7:
            risk_score += 0.2

        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self, dominant_emotion: str, risk_level: str, user_id: str
    ) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        # Базовые рекомендации по эмоциям
        if dominant_emotion == "sad":
            recommendations.append("Попробуйте заняться любимым делом")
            recommendations.append("Свяжитесь с близкими людьми")
        elif dominant_emotion == "anxious":
            recommendations.append("Попробуйте дыхательные упражнения")
            recommendations.append("Займитесь медитацией или йогой")
        elif dominant_emotion == "angry":
            recommendations.append("Попробуйте физические упражнения")
            recommendations.append("Сделайте паузу и подышите")
        elif dominant_emotion == "lonely":
            recommendations.append("Свяжитесь с друзьями или семьей")
            recommendations.append("Присоединитесь к группе по интересам")

        # Рекомендации по уровню риска
        if risk_level == "critical":
            recommendations.append("Немедленно обратитесь к специалисту")
            recommendations.append("Свяжитесь с кризисной службой")
        elif risk_level == "high":
            recommendations.append("Рекомендуется консультация психолога")
            recommendations.append("Обратитесь за поддержкой к близким")

        return recommendations

    def provide_emotional_support(
        self,
        user_id: str,
        age_group: AgeGroup,
        emotional_state: EmotionalState,
        support_type: SupportType = SupportType.EMOTIONAL
    ) -> Dict[str, Any]:
        """Предоставление эмоциональной поддержки"""
        try:
            # Получаем возрастную группу
            age_key = age_group.value

            # Выбираем подходящие сообщения поддержки
            support_messages = self.support_resources.get(
                "emotional_support", {}
            ).get(age_key, [])

            if not support_messages:
                support_messages = [
                    "Я здесь, чтобы поддержать вас.",
                    "Вы не одни в этом.",
                    "Помощь всегда доступна."
                ]

            # Выбираем случайное сообщение
            selected_message = random.choice(support_messages)

            # Создаем сессию поддержки
            session = {
                "session_id": f"support_{int(time.time())}",
                "user_id": user_id,
                "age_group": age_group.value,
                "emotional_state": emotional_state.value,
                "support_type": support_type.value,
                "message": selected_message,
                "timestamp": datetime.now().isoformat(),
                "effectiveness": None  # Будет оценено позже
            }

            # Сохраняем сессию
            if user_id not in self.support_sessions:
                self.support_sessions[user_id] = []
            self.support_sessions[user_id].append(session)

            # Проверяем на кризис
            if emotional_state in [EmotionalState.SAD, EmotionalState.ANXIOUS]:
                self._check_crisis_indicators(user_id, emotional_state)

            return {
                "success": True,
                "session_id": session["session_id"],
                "message": selected_message,
                "support_type": support_type.value,
                "timestamp": session["timestamp"]
            }

        except Exception as e:
            self.logger.error(f"Ошибка предоставления поддержки: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _check_crisis_indicators(
        self, user_id: str, emotional_state: EmotionalState
    ) -> None:
        """Проверка индикаторов кризиса"""
        # Анализируем историю эмоций
        if user_id in self.emotional_history:
            recent_emotions = self.emotional_history[user_id][-10:]  # Последние 10 записей
            
            # Подсчитываем негативные эмоции
            negative_emotions = [
                EmotionalState.SAD.value,
                EmotionalState.ANXIOUS.value,
                EmotionalState.ANGRY.value,
                EmotionalState.STRESSED.value,
                EmotionalState.LONELY.value
            ]
            
            negative_count = sum(
                1 for record in recent_emotions
                if record.get("dominant_emotion") in negative_emotions
            )
            
            # Если много негативных эмоций подряд
            if negative_count >= 7:
                self._trigger_crisis_alert(user_id, "emotional_distress")

    def _trigger_crisis_alert(self, user_id: str, crisis_type: str) -> None:
        """Активация кризисного алерта"""
        alert = {
            "alert_id": f"crisis_{int(time.time())}",
            "user_id": user_id,
            "crisis_type": crisis_type,
            "severity": "high",
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "status": "active"
        }

        self.crisis_alerts.append(alert)

        # Создаем событие безопасности
        event = SecurityEvent(
            event_type="psychological_crisis_alert",
            severity=IncidentSeverity.HIGH,
            description=f"Кризисный алерт для пользователя {user_id}: {crisis_type}",
            source="PsychologicalSupportAgent",
            timestamp=datetime.now()
        )

        self.logger.warning(f"Кризисный алерт: {alert}")

    def get_user_psychological_profile(self, user_id: str) -> Dict[str, Any]:
        """Получение психологического профиля пользователя"""
        if user_id not in self.user_profiles:
            return {"error": "Профиль не найден"}

        profile = self.user_profiles[user_id]
        emotional_history = self.emotional_history.get(user_id, [])
        support_sessions = self.support_sessions.get(user_id, [])

        # Анализ трендов
        recent_emotions = emotional_history[-30:] if emotional_history else []
        emotional_trends = self._analyze_emotional_trends(recent_emotions)

        return {
            "user_id": user_id,
            "profile": profile,
            "emotional_trends": emotional_trends,
            "recent_sessions": support_sessions[-5:],
            "crisis_alerts": [
                alert for alert in self.crisis_alerts
                if alert["user_id"] == user_id
            ],
            "recommendations": self._generate_profile_recommendations(
                emotional_trends, support_sessions
            )
        }

    def _analyze_emotional_trends(
        self, emotional_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Анализ эмоциональных трендов"""
        if not emotional_history:
            return {"trend": "stable", "confidence": 0.0}

        # Подсчитываем эмоции
        emotion_counts = {}
        for record in emotional_history:
            emotion = record.get("dominant_emotion", "unknown")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Определяем тренд
        total_records = len(emotional_history)
        positive_emotions = ["happy", "calm"]
        negative_emotions = ["sad", "anxious", "angry", "stressed", "lonely"]

        positive_ratio = sum(
            emotion_counts.get(emotion, 0) for emotion in positive_emotions
        ) / total_records

        negative_ratio = sum(
            emotion_counts.get(emotion, 0) for emotion in negative_emotions
        ) / total_records

        if positive_ratio > 0.6:
            trend = "positive"
        elif negative_ratio > 0.6:
            trend = "negative"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "confidence": min(total_records / 10, 1.0),
            "emotion_distribution": emotion_counts
        }

    def _generate_profile_recommendations(
        self,
        emotional_trends: Dict[str, Any],
        support_sessions: List[Dict[str, Any]]
    ) -> List[str]:
        """Генерация рекомендаций на основе профиля"""
        recommendations = []

        trend = emotional_trends.get("trend", "stable")

        if trend == "negative":
            recommendations.append("Рекомендуется регулярная психологическая поддержка")
            recommendations.append("Рассмотрите возможность консультации специалиста")
        elif trend == "positive":
            recommendations.append("Отличный эмоциональный баланс!")
            recommendations.append("Продолжайте поддерживать позитивный настрой")
        else:
            recommendations.append("Стабильное эмоциональное состояние")
            recommendations.append("Продолжайте мониторить свое состояние")

        # Рекомендации на основе сессий поддержки
        if len(support_sessions) > 5:
            recommendations.append("Рассмотрите возможность профилактических сессий")

        return recommendations

    def _save_emotional_analysis(
        self, user_id: str, analysis: Dict[str, Any]
    ) -> None:
        """Сохранение анализа эмоций"""
        if user_id not in self.emotional_history:
            self.emotional_history[user_id] = []

        self.emotional_history[user_id].append(analysis)

        # Ограничиваем историю (последние 100 записей)
        if len(self.emotional_history[user_id]) > 100:
            self.emotional_history[user_id] = self.emotional_history[user_id][-100:]

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "status": "active",
            "total_users": len(self.user_profiles),
            "active_sessions": sum(
                len(sessions) for sessions in self.support_sessions.values()
            ),
            "crisis_alerts": len(self.crisis_alerts),
            "support_resources_loaded": len(self.support_resources),
            "crisis_protocols_loaded": len(self.crisis_protocols),
            "last_updated": datetime.now().isoformat()
        }

    def create_user_profile(
        self,
        user_id: str,
        name: str,
        age: int,
        preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Создание профиля пользователя"""
        try:
            # Определяем возрастную группу
            if age <= 6:
                age_group = AgeGroup.CHILD_3_6
            elif age <= 12:
                age_group = AgeGroup.CHILD_7_12
            elif age <= 17:
                age_group = AgeGroup.TEEN_13_17
            elif age <= 65:
                age_group = AgeGroup.ADULT_18_65
            else:
                age_group = AgeGroup.ELDERLY_65_PLUS

            profile = {
                "user_id": user_id,
                "name": name,
                "age": age,
                "age_group": age_group.value,
                "preferences": preferences or {},
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "support_sessions_count": 0,
                "emotional_state": EmotionalState.CALM.value
            }

            self.user_profiles[user_id] = profile
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания профиля: {e}")
            return False

    def emergency_support(self, user_id: str, crisis_type: str) -> Dict[str, Any]:
        """Экстренная психологическая поддержка"""
        try:
            # Активируем кризисный протокол
            self._trigger_crisis_alert(user_id, crisis_type)

            # Получаем кризисные сообщения
            crisis_messages = self.support_resources.get(
                "crisis_interventions", {}
            ).get("immediate", [])

            if not crisis_messages:
                crisis_messages = [
                    "Сейчас с вами свяжется специалист.",
                    "Вы не одни. Помощь уже в пути.",
                    "Дышите глубоко. Вы в безопасности."
                ]

            selected_message = random.choice(crisis_messages)

            return {
                "success": True,
                "message": selected_message,
                "crisis_type": crisis_type,
                "immediate_actions": self.crisis_protocols.get(
                    crisis_type, {}
                ).get("immediate_actions", []),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка экстренной поддержки: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }