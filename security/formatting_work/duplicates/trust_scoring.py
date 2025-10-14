# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Trust Scoring
Система оценки доверия для семей
Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-10
"""

import logging
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

from core.base import SecurityBase
from core.security_base import SecurityEvent, IncidentSeverity

class TrustLevel(Enum):
    """Уровни доверия"""
    CRITICAL = "critical"  # Критический (0.0-0.2)
    LOW = "low"  # Низкий (0.2-0.4)
    MEDIUM = "medium"  # Средний (0.4-0.6)
    HIGH = "high"  # Высокий (0.6-0.8)
    EXCELLENT = "excellent"  # Отличный (0.8-1.0)

@dataclass
class TrustProfile:
    """Профиль доверия пользователя"""
    user_id: str
    initial_score: float
    current_score: float
    risk_factors: List[str]
    trust_indicators: List[str]
    last_updated: datetime
    trust_level: TrustLevel
    security_events: List[SecurityEvent] = field(default_factory=list)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrustEvent:
    """Событие, влияющее на доверие"""
    event_id: str
    user_id: str
    event_type: str
    severity: IncidentSeverity
    timestamp: datetime
    description: str
    impact_score: float
    resolved: bool = False

@dataclass
class TrustScore:
    """Оценка доверия"""
    user_id: str
    score: float
    trust_level: TrustLevel
    calculated_at: datetime
    factors: Dict[str, float]
    confidence: float

class TrustScoring(SecurityBase):
    """
    Система оценки доверия для семей
    Комплексная оценка уровня доверия пользователей и устройств
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("TrustScoring", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.trust_profiles: Dict[str, TrustProfile] = {}
        self.trust_events: List[TrustEvent] = []
        self.trust_scores: List[TrustScore] = []

        # Конфигурация
        self.min_trust_score = 0.0
        self.max_trust_score = 1.0
        self.risk_threshold = 0.3
        self.trust_threshold = 0.7

        # Инициализация
        self._initialize_default_profiles()

    def _initialize_default_profiles(self) -> None:
        """Инициализация профилей по умолчанию"""
        default_users: List[Dict[str, Any]] = [
            {
                "user_id": "admin",
                "initial_score": 0.9,
                "risk_factors": [],
                "trust_indicators": [
                    "mfa_enabled", "strong_password", "regular_updates"
                ]
            },
            {
                "user_id": "parent",
                "initial_score": 0.8,
                "risk_factors": [],
                "trust_indicators": ["mfa_enabled", "secure_network"]
            },
            {
                "user_id": "teen",
                "initial_score": 0.6,
                "risk_factors": ["limited_security_awareness"],
                "trust_indicators": [
                    "parental_controls", "content_filtering"
                ]
            },
            {
                "user_id": "elderly",
                "initial_score": 0.7,
                "risk_factors": ["vulnerable_to_scams"],
                "trust_indicators": [
                    "family_monitoring", "simplified_interface"
                ]
            }
        ]

        for user_data in default_users:
            self._create_trust_profile(user_data)

    def _create_trust_profile(self, user_data: Dict[str, Any]) -> None:
        """Создание профиля доверия"""
        trust_level = self._calculate_trust_level(user_data["initial_score"])

        profile = TrustProfile(
            user_id=user_data["user_id"],
            initial_score=user_data["initial_score"],
            current_score=user_data["initial_score"],
            risk_factors=user_data["risk_factors"],
            trust_indicators=user_data["trust_indicators"],
            last_updated=datetime.now(),
            trust_level=trust_level
        )

        self.trust_profiles[user_data["user_id"]] = profile

    def _calculate_trust_level(self, score: float) -> TrustLevel:
        """Расчет уровня доверия"""
        if score >= 0.8:
            return TrustLevel.EXCELLENT
        elif score >= 0.6:
            return TrustLevel.HIGH
        elif score >= 0.4:
            return TrustLevel.MEDIUM
        elif score >= 0.2:
            return TrustLevel.LOW
        else:
            return TrustLevel.CRITICAL

    def calculate_trust_score(
        self,
        user_id: str,
        events: List[SecurityEvent]
    ) -> TrustScore:
        """Расчет оценки доверия для пользователя"""
        if user_id not in self.trust_profiles:
            raise ValueError(f"Пользователь {user_id} не найден")

        profile = self.trust_profiles[user_id]
        base_score = profile.initial_score

        # Факторы влияния
        factors = {
            "base_score": base_score,
            "security_events": 0.0,
            "behavior_patterns": 0.0,
            "risk_factors": 0.0,
            "trust_indicators": 0.0
        }

        # Анализ событий безопасности
        security_impact = self._analyze_security_events(events)
        factors["security_events"] = security_impact

        # Анализ поведенческих паттернов
        behavior_impact = self._analyze_behavior_patterns(profile)
        factors["behavior_patterns"] = behavior_impact

        # Анализ факторов риска
        risk_impact = self._analyze_risk_factors(profile.risk_factors)
        factors["risk_factors"] = risk_impact

        # Анализ индикаторов доверия
        trust_impact = self._analyze_trust_indicators(profile.trust_indicators)
        factors["trust_indicators"] = trust_impact

        # Итоговый расчет
        final_score = self._calculate_final_score(factors)
        final_score = max(self.min_trust_score,
                         min(self.max_trust_score, final_score))

        # Создание оценки
        trust_score = TrustScore(
            user_id=user_id,
            score=final_score,
            trust_level=self._calculate_trust_level(final_score),
            calculated_at=datetime.now(),
            factors=factors,
            confidence=self._calculate_confidence(factors)
        )

        # Обновление профиля
        profile.current_score = final_score
        profile.trust_level = trust_score.trust_level
        profile.last_updated = datetime.now()

        # Сохранение оценки
        self.trust_scores.append(trust_score)

        return trust_score

    def _analyze_security_events(
        self,
        events: List[SecurityEvent]
    ) -> float:
        """Анализ событий безопасности"""
        if not events:
            return 0.0

        total_impact = 0.0
        for event in events:
            if event.severity == IncidentSeverity.CRITICAL:
                total_impact -= 0.3
            elif event.severity == IncidentSeverity.HIGH:
                total_impact -= 0.2
            elif event.severity == IncidentSeverity.MEDIUM:
                total_impact -= 0.1
            elif event.severity == IncidentSeverity.LOW:
                total_impact -= 0.05

        return total_impact

    def _analyze_behavior_patterns(
        self,
        profile: TrustProfile
    ) -> float:
        """Анализ поведенческих паттернов"""
        if not profile.behavior_patterns:
            return 0.0

        positive_patterns = 0
        negative_patterns = 0

        for pattern, value in profile.behavior_patterns.items():
            if pattern in ["regular_login", "secure_browsing", "timely_updates"]:
                if value:
                    positive_patterns += 1
            elif pattern in ["suspicious_activity", "failed_logins", "unusual_hours"]:
                if value:
                    negative_patterns += 1

        if positive_patterns + negative_patterns == 0:
            return 0.0

        return (positive_patterns - negative_patterns) * 0.1

    def _analyze_risk_factors(self, risk_factors: List[str]) -> float:
        """Анализ факторов риска"""
        if not risk_factors:
            return 0.0

        risk_weights = {
            "limited_security_awareness": -0.1,
            "vulnerable_to_scams": -0.15,
            "weak_passwords": -0.2,
            "no_mfa": -0.1,
            "outdated_software": -0.1
        }

        total_impact = 0.0
        for factor in risk_factors:
            total_impact += risk_weights.get(factor, -0.05)

        return total_impact

    def _analyze_trust_indicators(self, trust_indicators: List[str]) -> float:
        """Анализ индикаторов доверия"""
        if not trust_indicators:
            return 0.0

        trust_weights = {
            "mfa_enabled": 0.15,
            "strong_password": 0.1,
            "regular_updates": 0.1,
            "secure_network": 0.05,
            "parental_controls": 0.05,
            "content_filtering": 0.05,
            "family_monitoring": 0.1,
            "simplified_interface": 0.05
        }

        total_impact = 0.0
        for indicator in trust_indicators:
            total_impact += trust_weights.get(indicator, 0.02)

        return total_impact

    def _calculate_final_score(self, factors: Dict[str, float]) -> float:
        """Расчет итогового балла"""
        base_score = factors["base_score"]
        adjustments = sum([
            factors["security_events"],
            factors["behavior_patterns"],
            factors["risk_factors"],
            factors["trust_indicators"]
        ])

        return base_score + adjustments

    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Расчет уверенности в оценке"""
        # Базовая уверенность
        confidence = 0.5

        # Увеличение уверенности при наличии данных
        if factors["security_events"] != 0:
            confidence += 0.2
        if factors["behavior_patterns"] != 0:
            confidence += 0.2
        if factors["risk_factors"] != 0:
            confidence += 0.1
        if factors["trust_indicators"] != 0:
            confidence += 0.1

        return min(1.0, confidence)

    def get_trust_report(self, user_id: str) -> Dict[str, Any]:
        """Получение отчета о доверии"""
        if user_id not in self.trust_profiles:
            raise ValueError(f"Пользователь {user_id} не найден")

        profile = self.trust_profiles[user_id]
        recent_scores = [
            score for score in self.trust_scores
            if score.user_id == user_id
        ][-10:]  # Последние 10 оценок

        return {
            "user_id": user_id,
            "current_score": profile.current_score,
            "trust_level": profile.trust_level.value,
            "last_updated": profile.last_updated.isoformat(),
            "risk_factors": profile.risk_factors,
            "trust_indicators": profile.trust_indicators,
            "recent_scores": [score.score for score in recent_scores],
            "trend": self._calculate_trend(recent_scores),
            "recommendations": self._generate_recommendations(profile)
        }

    def _calculate_trend(self, scores: List[TrustScore]) -> str:
        """Расчет тренда оценок"""
        if len(scores) < 2:
            return "insufficient_data"

        recent_avg = statistics.mean([s.score for s in scores[-3:]])
        older_avg = statistics.mean([s.score for s in scores[:-3]])

        if recent_avg > older_avg + 0.05:
            return "improving"
        elif recent_avg < older_avg - 0.05:
            return "declining"
        else:
            return "stable"

    def _generate_recommendations(self, profile: TrustProfile) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        if profile.current_score < 0.5:
            recommendations.append("Критически низкий уровень доверия")
            recommendations.append("Рекомендуется усилить меры безопасности")
        elif profile.current_score < 0.7:
            recommendations.append("Низкий уровень доверия")
            recommendations.append("Рекомендуется улучшить безопасность")

        if "limited_security_awareness" in profile.risk_factors:
            recommendations.append("Провести обучение по безопасности")

        if "no_mfa" in profile.risk_factors:
            recommendations.append("Включить двухфакторную аутентификацию")

        if "weak_passwords" in profile.risk_factors:
            recommendations.append("Усилить пароли")

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        total_users = len(self.trust_profiles)
        avg_score = statistics.mean([
            profile.current_score
            for profile in self.trust_profiles.values()
        ]) if self.trust_profiles else 0.0

        return {
            "status": "active",
            "total_users": total_users,
            "average_trust_score": round(avg_score, 3),
            "total_events": len(self.trust_events),
            "total_scores": len(self.trust_scores),
            "last_updated": datetime.now().isoformat()
        }

    def reset_user_trust(self, user_id: str) -> bool:
        """Сброс доверия пользователя к начальному уровню"""
        if user_id not in self.trust_profiles:
            return False

        profile = self.trust_profiles[user_id]
        profile.current_score = profile.initial_score
        profile.trust_level = self._calculate_trust_level(profile.initial_score)
        profile.last_updated = datetime.now()

        return True

    def update_trust_indicators(
        self,
        user_id: str,
        indicators: List[str]
    ) -> bool:
        """Обновление индикаторов доверия"""
        if user_id not in self.trust_profiles:
            return False

        profile = self.trust_profiles[user_id]
        profile.trust_indicators = indicators
        profile.last_updated = datetime.now()

        return True

    def add_risk_factor(self, user_id: str, factor: str) -> bool:
        """Добавление фактора риска"""
        if user_id not in self.trust_profiles:
            return False

        profile = self.trust_profiles[user_id]
        if factor not in profile.risk_factors:
            profile.risk_factors.append(factor)
            profile.last_updated = datetime.now()

        return True

    def remove_risk_factor(self, user_id: str, factor: str) -> bool:
        """Удаление фактора риска"""
        if user_id not in self.trust_profiles:
            return False

        profile = self.trust_profiles[user_id]
        if factor in profile.risk_factors:
            profile.risk_factors.remove(factor)
            profile.last_updated = datetime.now()

        return True
