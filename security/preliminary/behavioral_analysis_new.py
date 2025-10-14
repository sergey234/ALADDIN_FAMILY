# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Behavioral Analysis
Система поведенческого анализа пользователей
Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-10
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from core.base import SecurityBase


class BehaviorType(Enum):
    """Типы поведения"""

    NORMAL = "normal"  # Нормальное поведение
    SUSPICIOUS = "suspicious"  # Подозрительное поведение
    ANOMALOUS = "anomalous"  # Аномальное поведение
    MALICIOUS = "malicious"  # Вредоносное поведение


class RiskLevel(Enum):
    """Уровни риска"""

    LOW = "low"  # Низкий риск
    MEDIUM = "medium"  # Средний риск
    HIGH = "high"  # Высокий риск
    CRITICAL = "critical"  # Критический риск


class AnomalyType(Enum):
    """Типы аномалий"""

    TEMPORAL = "temporal"  # Временные аномалии
    FREQUENCY = "frequency"  # Частотные аномалии
    PATTERN = "pattern"  # Паттерн аномалии
    SEQUENCE = "sequence"  # Последовательные аномалии
    STATISTICAL = "statistical"  # Статистические аномалии


@dataclass
class BehaviorPattern:
    """Паттерн поведения"""

    pattern_id: str
    user_id: str
    behavior_type: BehaviorType
    features: Dict[str, float]
    confidence: float
    timestamp: datetime
    duration: int  # В минутах
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetection:
    """Обнаружение аномалий"""

    anomaly_id: str
    user_id: str
    anomaly_type: AnomalyType
    risk_level: RiskLevel
    score: float
    description: str
    timestamp: datetime
    features: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """Профиль пользователя"""

    user_id: str
    baseline_features: Dict[str, float]
    behavior_patterns: List[BehaviorPattern]
    anomaly_history: List[AnomalyDetection]
    risk_score: float
    last_activity: datetime
    total_sessions: int = 0
    suspicious_activities: int = 0


class BehavioralAnalysis(SecurityBase):
    """
    Система поведенческого анализа
    Анализ поведения пользователей и обнаружение аномалий
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("BehavioralAnalysis", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.user_profiles: Dict[str, UserProfile] = {}
        self.behavior_patterns: List[BehaviorPattern] = []
        self.anomaly_detections: List[AnomalyDetection] = []
        self.model_artifacts: Dict[str, Any] = {}

        # Модели машинного обучения
        self.isolation_forest = IsolationForest(
            contamination=0.1, random_state=42
        )
        self.one_class_svm = OneClassSVM(nu=0.1, kernel="rbf", gamma="scale")
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()

        # Конфигурация
        self.anomaly_threshold = 0.7
        self.learning_period_days = 30
        self.min_samples_for_analysis = 10
        self.auto_retrain = True

        # Инициализация
        self._initialize_default_profiles()

    def _initialize_default_profiles(self) -> None:
        """Инициализация профилей по умолчанию"""
        default_users = [
            {
                "user_id": "admin",
                "baseline_features": {
                    "login_frequency": 5.0,
                    "session_duration": 120.0,
                    "page_views": 25.0,
                    "click_rate": 0.15,
                    "navigation_speed": 2.5,
                },
            },
            {
                "user_id": "user_1",
                "baseline_features": {
                    "login_frequency": 3.0,
                    "session_duration": 90.0,
                    "page_views": 15.0,
                    "click_rate": 0.12,
                    "navigation_speed": 3.0,
                },
            },
        ]

        for user_data in default_users:
            self._create_user_profile(user_data)

    def _create_user_profile(self, user_data: Dict[str, Any]) -> None:
        """Создание профиля пользователя"""
        profile = UserProfile(
            user_id=user_data["user_id"],
            baseline_features=user_data["baseline_features"],
            behavior_patterns=[],
            anomaly_history=[],
            risk_score=0.0,
            last_activity=datetime.now(),
        )
        self.user_profiles[user_data["user_id"]] = profile

    def analyze_behavior(
        self, user_id: str, session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Анализ поведения пользователя"""
        if user_id not in self.user_profiles:
            self._create_user_profile(
                {
                    "user_id": user_id,
                    "baseline_features": self._extract_baseline_features(
                        session_data
                    ),
                }
            )

        profile = self.user_profiles[user_id]

        # Извлекаем признаки поведения
        features = self._extract_behavior_features(session_data)

        # Создаем паттерн поведения
        pattern = BehaviorPattern(
            pattern_id=f"pattern_{int(time.time())}",
            user_id=user_id,
            behavior_type=BehaviorType.NORMAL,
            features=features,
            confidence=1.0,
            timestamp=datetime.now(),
            duration=session_data.get("duration", 0),
        )

        # Анализируем на аномалии
        anomaly_result = self._detect_anomalies(user_id, features)

        # Обновляем профиль пользователя
        profile.behavior_patterns.append(pattern)
        profile.last_activity = datetime.now()
        profile.total_sessions += 1

        if anomaly_result["is_anomaly"]:
            profile.suspicious_activities += 1
            pattern.behavior_type = BehaviorType.SUSPICIOUS

        # Пересчитываем риск-скор
        profile.risk_score = self._calculate_risk_score(profile)

        return {
            "user_id": user_id,
            "pattern_id": pattern.pattern_id,
            "behavior_type": pattern.behavior_type.value,
            "anomaly_detected": anomaly_result["is_anomaly"],
            "anomaly_score": anomaly_result["score"],
            "risk_level": self._get_risk_level(profile.risk_score).value,
            "confidence": pattern.confidence,
            "recommendations": self._generate_recommendations(profile),
        }

    def _extract_behavior_features(
        self, session_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Извлечение признаков поведения"""
        features = {}

        # Временные признаки
        features["session_duration"] = session_data.get("duration", 0)
        features["login_time"] = session_data.get("login_hour", 12)
        features["day_of_week"] = session_data.get("day_of_week", 1)

        # Активность
        features["page_views"] = session_data.get("page_views", 0)
        features["clicks"] = session_data.get("clicks", 0)
        features["scrolls"] = session_data.get("scrolls", 0)
        features["keystrokes"] = session_data.get("keystrokes", 0)

        # Навигация
        features["unique_pages"] = session_data.get("unique_pages", 0)
        features["back_button_usage"] = session_data.get("back_usage", 0)
        features["search_queries"] = session_data.get("search_queries", 0)

        # Скорость и ритм
        features["avg_time_per_page"] = features["session_duration"] / max(
            features["page_views"], 1
        )
        features["click_rate"] = features["clicks"] / max(
            features["page_views"], 1
        )
        features["scroll_rate"] = features["scrolls"] / max(
            features["page_views"], 1
        )

        # Географические признаки
        features["location_changes"] = session_data.get("location_changes", 0)
        features["ip_changes"] = session_data.get("ip_changes", 0)

        return features

    def _extract_baseline_features(
        self, session_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Извлечение базовых признаков для нового пользователя"""
        return self._extract_behavior_features(session_data)

    def _detect_anomalies(
        self, user_id: str, features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Обнаружение аномалий в поведении"""
        profile = self.user_profiles[user_id]

        # Подготавливаем данные для анализа
        feature_vector = np.array(list(features.values())).reshape(1, -1)

        # Проверяем, достаточно ли данных для анализа
        if len(profile.behavior_patterns) < self.min_samples_for_analysis:
            return {
                "is_anomaly": False,
                "score": 0.0,
                "method": "insufficient_data",
            }

        # Получаем исторические данные
        historical_features = self._get_historical_features(profile)

        if len(historical_features) < self.min_samples_for_analysis:
            return {
                "is_anomaly": False,
                "score": 0.0,
                "method": "insufficient_history",
            }

        # Нормализуем данные
        scaler = StandardScaler()
        historical_scaled = scaler.fit_transform(historical_features)
        current_scaled = scaler.transform(feature_vector)

        # Применяем модели обнаружения аномалий
        anomaly_scores = []

        # Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        iso_forest.fit(historical_scaled)
        iso_score = iso_forest.decision_function(current_scaled)[0]
        anomaly_scores.append(abs(iso_score))

        # One-Class SVM
        one_class_svm = OneClassSVM(nu=0.1, kernel="rbf", gamma="scale")
        one_class_svm.fit(historical_scaled)
        svm_score = one_class_svm.decision_function(current_scaled)[0]
        anomaly_scores.append(abs(svm_score))

        # Статистический анализ
        stat_score = self._statistical_anomaly_score(
            historical_features, feature_vector
        )
        anomaly_scores.append(stat_score)

        # Усредняем оценки
        final_score = statistics.mean(anomaly_scores)
        is_anomaly = final_score > self.anomaly_threshold

        # Создаем запись об аномалии
        if is_anomaly:
            anomaly = AnomalyDetection(
                anomaly_id=f"anomaly_{int(time.time())}",
                user_id=user_id,
                anomaly_type=AnomalyType.STATISTICAL,
                risk_level=self._get_risk_level(final_score),
                score=final_score,
                description=(
                    f"Обнаружена аномалия в поведении пользователя {user_id}"
                ),
                timestamp=datetime.now(),
                features=features,
            )
            self.anomaly_detections.append(anomaly)
            profile.anomaly_history.append(anomaly)

        return {
            "is_anomaly": is_anomaly,
            "score": final_score,
            "method": "ensemble",
            "individual_scores": {
                "isolation_forest": anomaly_scores[0],
                "one_class_svm": anomaly_scores[1],
                "statistical": anomaly_scores[2],
            },
        }

    def _get_historical_features(self, profile: UserProfile) -> np.ndarray:
        """Получение исторических признаков пользователя"""
        if not profile.behavior_patterns:
            return np.array([])

        features_list = []
        for pattern in profile.behavior_patterns[
            -50:
        ]:  # Последние 50 паттернов
            features_list.append(list(pattern.features.values()))

        return np.array(features_list)

    def _statistical_anomaly_score(
        self, historical_data: np.ndarray, current_data: np.ndarray
    ) -> float:
        """Статистический анализ аномалий"""
        if len(historical_data) == 0:
            return 0.0

        # Вычисляем Z-скор для каждого признака
        z_scores = []
        for i in range(current_data.shape[1]):
            mean_val = np.mean(historical_data[:, i])
            std_val = np.std(historical_data[:, i])
            if std_val > 0:
                z_score = abs((current_data[0, i] - mean_val) / std_val)
                z_scores.append(z_score)

        # Возвращаем максимальный Z-скор
        return max(z_scores) if z_scores else 0.0

    def _calculate_risk_score(self, profile: UserProfile) -> float:
        """Расчет риск-скора пользователя"""
        base_score = 0.0

        # Фактор аномалий
        anomaly_factor = len(profile.anomaly_history) * 0.1
        base_score += min(anomaly_factor, 0.5)

        # Фактор подозрительной активности
        suspicious_factor = profile.suspicious_activities * 0.05
        base_score += min(suspicious_factor, 0.3)

        # Фактор частоты активности
        if profile.total_sessions > 0:
            recent_anomalies = len(
                [
                    a
                    for a in profile.anomaly_history
                    if a.timestamp > datetime.now() - timedelta(days=7)
                ]
            )
            frequency_factor = recent_anomalies / profile.total_sessions
            base_score += min(frequency_factor, 0.2)

        return min(base_score, 1.0)

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Определение уровня риска по скору"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendations(self, profile: UserProfile) -> List[str]:
        """Генерация рекомендаций для пользователя"""
        recommendations = []

        if profile.risk_score > 0.7:
            recommendations.append(
                "Высокий риск: рекомендуется дополнительная аутентификация"
            )

        if len(profile.anomaly_history) > 5:
            recommendations.append(
                "Много аномалий: рекомендуется мониторинг активности"
            )

        recent_anomalies = len(
            [
                a
                for a in profile.anomaly_history
                if a.timestamp > datetime.now() - timedelta(hours=24)
            ]
        )

        if recent_anomalies > 2:
            recommendations.append(
                "Недавние аномалии: рекомендуется проверка безопасности"
            )

        return recommendations

    def get_user_behavior_summary(self, user_id: str) -> Dict[str, Any]:
        """Получение сводки поведения пользователя"""
        if user_id not in self.user_profiles:
            return {"error": "Пользователь не найден"}

        profile = self.user_profiles[user_id]

        # Статистика за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)
        recent_patterns = [
            p for p in profile.behavior_patterns if p.timestamp > week_ago
        ]

        recent_anomalies = [
            a for a in profile.anomaly_history if a.timestamp > week_ago
        ]

        return {
            "user_id": user_id,
            "total_sessions": profile.total_sessions,
            "recent_sessions": len(recent_patterns),
            "total_anomalies": len(profile.anomaly_history),
            "recent_anomalies": len(recent_anomalies),
            "risk_score": profile.risk_score,
            "risk_level": self._get_risk_level(profile.risk_score).value,
            "last_activity": profile.last_activity.isoformat(),
            "behavior_trends": self._analyze_behavior_trends(profile),
            "recommendations": self._generate_recommendations(profile),
        }

    def _analyze_behavior_trends(self, profile: UserProfile) -> Dict[str, Any]:
        """Анализ трендов поведения"""
        if len(profile.behavior_patterns) < 2:
            return {"trend": "insufficient_data"}

        # Анализируем тренды по ключевым признакам
        patterns = profile.behavior_patterns[-10:]  # Последние 10 паттернов

        trends = {}
        for feature in ["session_duration", "page_views", "click_rate"]:
            values = [p.features.get(feature, 0) for p in patterns]
            if len(values) >= 2:
                trend = (
                    "increasing" if values[-1] > values[0] else "decreasing"
                )
                trends[feature] = {
                    "trend": trend,
                    "change_percent": (
                        (values[-1] - values[0]) / max(values[0], 1) * 100
                    ),
                }

        return trends

    def get_anomaly_report(
        self, user_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Any]:
        """Получение отчета об аномалиях"""
        cutoff_date = datetime.now() - timedelta(days=days)

        if user_id:
            anomalies = [
                a
                for a in self.anomaly_detections
                if a.user_id == user_id and a.timestamp > cutoff_date
            ]
        else:
            anomalies = [
                a for a in self.anomaly_detections if a.timestamp > cutoff_date
            ]

        # Группировка по типам аномалий
        by_type = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type.value
            if anomaly_type not in by_type:
                by_type[anomaly_type] = []
            by_type[anomaly_type].append(anomaly)

        # Группировка по уровням риска
        by_risk = {}
        for anomaly in anomalies:
            risk_level = anomaly.risk_level.value
            if risk_level not in by_risk:
                by_risk[risk_level] = []
            by_risk[risk_level].append(anomaly)

        return {
            "total_anomalies": len(anomalies),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_risk_level": {k: len(v) for k, v in by_risk.items()},
            "anomalies": [
                {
                    "anomaly_id": a.anomaly_id,
                    "user_id": a.user_id,
                    "type": a.anomaly_type.value,
                    "risk_level": a.risk_level.value,
                    "score": a.score,
                    "timestamp": a.timestamp.isoformat(),
                    "description": a.description,
                }
                for a in anomalies
            ],
        }

    def retrain_models(self) -> Dict[str, Any]:
        """Переобучение моделей машинного обучения"""
        if not self.behavior_patterns:
            return {"error": "Недостаточно данных для переобучения"}

        # Подготавливаем данные
        all_features = []
        for pattern in self.behavior_patterns:
            all_features.append(list(pattern.features.values()))

        X = np.array(all_features)

        if len(X) < self.min_samples_for_analysis:
            return {"error": "Недостаточно образцов для переобучения"}

        # Нормализуем данные
        X_scaled = self.scaler.fit_transform(X)

        # Переобучаем модели
        self.isolation_forest.fit(X_scaled)
        self.one_class_svm.fit(X_scaled)

        # Кластеризация
        self.dbscan.fit(X_scaled)
        self.kmeans.fit(X_scaled)

        # Сохраняем артефакты модели
        self.model_artifacts = {
            "last_retrain": datetime.now().isoformat(),
            "samples_count": len(X),
            "features_count": X.shape[1],
            "clusters_count": len(set(self.dbscan.labels_)),
        }

        return {
            "status": "success",
            "samples_used": len(X),
            "features_count": X.shape[1],
            "clusters_found": len(set(self.dbscan.labels_)),
            "retrain_time": datetime.now().isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "status": "active",
            "total_users": len(self.user_profiles),
            "total_patterns": len(self.behavior_patterns),
            "total_anomalies": len(self.anomaly_detections),
            "anomaly_threshold": self.anomaly_threshold,
            "learning_period_days": self.learning_period_days,
            "min_samples_for_analysis": self.min_samples_for_analysis,
            "auto_retrain": self.auto_retrain,
            "last_updated": datetime.now().isoformat(),
        }

    def get_analytics(self) -> Dict[str, Any]:
        """Получение аналитики системы"""
        if not self.user_profiles:
            return {"message": "Нет данных для анализа"}

        # Статистика по пользователям
        risk_distribution = {}
        for profile in self.user_profiles.values():
            risk_level = self._get_risk_level(profile.risk_score).value
            risk_distribution[risk_level] = (
                risk_distribution.get(risk_level, 0) + 1
            )

        # Статистика по аномалиям
        anomaly_types = {}
        for anomaly in self.anomaly_detections:
            anomaly_type = anomaly.anomaly_type.value
            anomaly_types[anomaly_type] = (
                anomaly_types.get(anomaly_type, 0) + 1
            )

        # Топ пользователей по риску
        high_risk_users = [
            {
                "user_id": profile.user_id,
                "risk_score": profile.risk_score,
                "anomalies_count": len(profile.anomaly_history),
            }
            for profile in self.user_profiles.values()
            if profile.risk_score > 0.5
        ]
        high_risk_users.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "total_users": len(self.user_profiles),
            "total_patterns": len(self.behavior_patterns),
            "total_anomalies": len(self.anomaly_detections),
            "risk_distribution": risk_distribution,
            "anomaly_types": anomaly_types,
            "high_risk_users": high_risk_users[:10],  # Топ 10
            "average_risk_score": statistics.mean(
                [p.risk_score for p in self.user_profiles.values()]
            ),
            "model_artifacts": self.model_artifacts,
        }
