from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple

import asyncio
import hashlib
import json
import math
import os
import sqlite3
import statistics
import time
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Behavioral Analytics для ALADDIN Security System
Расширенная система анализа поведения пользователей и сущностей

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-27
Качество: A+
"""

class BehaviorType(Enum):
    """Типы поведения"""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    ANOMALOUS = "anomalous"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"

class EntityType(Enum):
    """Типы сущностей"""
    USER = "user"
    DEVICE = "device"
    APPLICATION = "application"
    SERVICE = "service"
    NETWORK = "network"
    API_ENDPOINT = "api_endpoint"

class RiskLevel(Enum):
    """Уровни риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnomalyType(Enum):
    """Типы аномалий"""
    TEMPORAL = "temporal"  # Временные аномалии
    FREQUENCY = "frequency"  # Частотные аномалии
    LOCATION = "location"  # Локальные аномалии
    DEVICE = "device"  # Аномалии устройств
    VELOCITY = "velocity"  # Скоростные аномалии
    PATTERN = "pattern"  # Паттерновые аномалии
    BEHAVIORAL = "behavioral"  # Поведенческие аномалии
    CONTEXTUAL = "contextual"  # Контекстные аномалии

@dataclass
class UserBehaviorProfile:
    """Профиль поведения пользователя"""
    user_id: str
    baseline_patterns: Dict[str, Any]
    activity_times: Dict[str, int]  # час -> количество активностей
    locations: Dict[str, int]  # локация -> количество посещений
    devices: Dict[str, int]  # устройство -> количество использований
    applications: Dict[str, int]  # приложение -> количество использований
    session_durations: List[float]  # длительности сессий
    login_frequency: Dict[str, int]  # день недели -> количество входов
    data_access_patterns: Dict[str, Any]
    communication_patterns: Dict[str, Any]
    risk_score: float
    last_updated: datetime
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data

@dataclass
class EntityBehaviorProfile:
    """Профиль поведения сущности"""
    entity_id: str
    entity_type: EntityType
    baseline_metrics: Dict[str, float]
    performance_patterns: Dict[str, List[float]]
    resource_usage: Dict[str, List[float]]
    interaction_patterns: Dict[str, Any]
    error_patterns: Dict[str, List[float]]
    availability_patterns: Dict[str, float]
    risk_score: float
    last_updated: datetime
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['entity_type'] = self.entity_type.value
        data['last_updated'] = self.last_updated.isoformat()
        return data

@dataclass
class AdvancedAnomaly:
    """Расширенная аномалия"""
    anomaly_id: str
    entity_id: str
    entity_type: EntityType
    anomaly_type: AnomalyType
    severity: RiskLevel
    confidence: float
    description: str
    detected_at: datetime
    baseline_value: float
    actual_value: float
    deviation_percentage: float
    context: Dict[str, Any]
    recommendations: List[str]
    false_positive_probability: float
    related_anomalies: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['entity_type'] = self.entity_type.value
        data['anomaly_type'] = self.anomaly_type.value
        data['severity'] = self.severity.value
        data['detected_at'] = self.detected_at.isoformat()
        return data

@dataclass
class RiskAssessment:
    """Оценка риска"""
    entity_id: str
    entity_type: EntityType
    overall_risk_score: float  # 0-100
    risk_factors: Dict[str, float]
    risk_trend: str  # increasing, decreasing, stable
    confidence: float
    recommendations: List[str]
    assessed_at: datetime
    valid_until: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['entity_type'] = self.entity_type.value
        data['assessed_at'] = self.assessed_at.isoformat()
        data['valid_until'] = self.valid_until.isoformat()
        return data

class AdvancedBehavioralAnalytics:
    """Расширенная система анализа поведения"""

    def __init__(self, db_path: str = "advanced_behavioral_analytics.db"):
        self.db_path = db_path
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        self.entity_profiles: Dict[str, EntityBehaviorProfile] = {}
        self.anomalies: List[AdvancedAnomaly] = []
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица профилей пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior_profiles (
                user_id TEXT PRIMARY KEY,
                baseline_patterns TEXT,
                activity_times TEXT,
                locations TEXT,
                devices TEXT,
                applications TEXT,
                session_durations TEXT,
                login_frequency TEXT,
                data_access_patterns TEXT,
                communication_patterns TEXT,
                risk_score REAL,
                last_updated DATETIME,
                confidence REAL
            )
        ''')

        # Таблица профилей сущностей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entity_behavior_profiles (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                baseline_metrics TEXT,
                performance_patterns TEXT,
                resource_usage TEXT,
                interaction_patterns TEXT,
                error_patterns TEXT,
                availability_patterns TEXT,
                risk_score REAL,
                last_updated DATETIME,
                confidence REAL
            )
        ''')

        # Таблица аномалий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                anomaly_id TEXT PRIMARY KEY,
                entity_id TEXT,
                entity_type TEXT,
                anomaly_type TEXT,
                severity TEXT,
                confidence REAL,
                description TEXT,
                detected_at DATETIME,
                baseline_value REAL,
                actual_value REAL,
                deviation_percentage REAL,
                context TEXT,
                recommendations TEXT,
                false_positive_probability REAL,
                related_anomalies TEXT
            )
        ''')

        # Таблица оценок рисков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessments (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                overall_risk_score REAL,
                risk_factors TEXT,
                risk_trend TEXT,
                confidence REAL,
                recommendations TEXT,
                assessed_at DATETIME,
                valid_until DATETIME
            )
        ''')

        conn.commit()
        conn.close()

    async def analyze_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> UserBehaviorProfile:
        """Анализ поведения пользователя"""
        # Получаем существующий профиль или создаем новый
        profile = await self._get_user_profile(user_id)

        if profile is None:
            profile = UserBehaviorProfile(
                user_id=user_id,
                baseline_patterns={},
                activity_times={},
                locations={},
                devices={},
                applications={},
                session_durations=[],
                login_frequency={},
                data_access_patterns={},
                communication_patterns={},
                risk_score=0.0,
                last_updated=datetime.now(),
                confidence=0.0
            )

        # Обновляем профиль на основе новых данных
        await self._update_user_profile(profile, behavior_data)

        # Сохраняем профиль
        await self._save_user_profile(profile)

        return profile

    async def analyze_entity_behavior(self, entity_id: str, entity_type: EntityType,
                                    behavior_data: Dict[str, Any]) -> EntityBehaviorProfile:
        """Анализ поведения сущности"""
        # Получаем существующий профиль или создаем новый
        profile = await self._get_entity_profile(entity_id)

        if profile is None:
            profile = EntityBehaviorProfile(
                entity_id=entity_id,
                entity_type=entity_type,
                baseline_metrics={},
                performance_patterns={},
                resource_usage={},
                interaction_patterns={},
                error_patterns={},
                availability_patterns={},
                risk_score=0.0,
                last_updated=datetime.now(),
                confidence=0.0
            )

        # Обновляем профиль на основе новых данных
        await self._update_entity_profile(profile, behavior_data)

        # Сохраняем профиль
        await self._save_entity_profile(profile)

        return profile

    async def detect_anomalies(self, entity_id: str, entity_type: EntityType,
                             current_data: Dict[str, Any]) -> List[AdvancedAnomaly]:
        """Обнаружение аномалий"""
        anomalies = []

        if entity_type == EntityType.USER:
            profile = await self._get_user_profile(entity_id)
            if profile:
                anomalies.extend(await self._detect_user_anomalies(profile, current_data))
        else:
            profile = await self._get_entity_profile(entity_id)
            if profile:
                anomalies.extend(await self._detect_entity_anomalies(profile, current_data))

        # Сохраняем обнаруженные аномалии
        for anomaly in anomalies:
            await self._save_anomaly(anomaly)

        return anomalies

    async def _detect_user_anomalies(self, profile: UserBehaviorProfile,
                                   current_data: Dict[str, Any]) -> List[AdvancedAnomaly]:
        """Обнаружение аномалий пользователя"""
        anomalies = []

        # Временные аномалии
        current_hour = datetime.now().hour
        expected_activity = profile.activity_times.get(str(current_hour), 0)
        current_activity = current_data.get("activity_count", 0)

        if expected_activity > 0:
            deviation = abs(current_activity - expected_activity) / expected_activity
            if deviation > 2.0:  # 200% отклонение
                anomaly = AdvancedAnomaly(
                    anomaly_id=f"temp_{profile.user_id}_{int(time.time())}",
                    entity_id=profile.user_id,
                    entity_type=EntityType.USER,
                    anomaly_type=AnomalyType.TEMPORAL,
                    severity=RiskLevel.HIGH if deviation > 5.0 else RiskLevel.MEDIUM,
                    confidence=min(95.0, deviation * 20),
                    description=f"Необычная активность в {current_hour}:00. Ожидалось: {expected_activity}, получено: {current_activity}",
                    detected_at=datetime.now(),
                    baseline_value=expected_activity,
                    actual_value=current_activity,
                    deviation_percentage=deviation * 100,
                    context={"hour": current_hour, "expected": expected_activity, "actual": current_activity},
                    recommendations=["Проверить активность пользователя", "Уведомить администратора"],
                    false_positive_probability=10.0,
                    related_anomalies=[]
                )
                anomalies.append(anomaly)

        # Локальные аномалии
        current_location = current_data.get("location", "unknown")
        if current_location != "unknown":
            expected_location_visits = profile.locations.get(current_location, 0)
            if expected_location_visits < 5:  # Редко посещаемое место
                anomaly = AdvancedAnomaly(
                    anomaly_id=f"loc_{profile.user_id}_{int(time.time())}",
                    entity_id=profile.user_id,
                    entity_type=EntityType.USER,
                    anomaly_type=AnomalyType.LOCATION,
                    severity=RiskLevel.MEDIUM,
                    confidence=75.0,
                    description=f"Вход из необычного места: {current_location}",
                    detected_at=datetime.now(),
                    baseline_value=expected_location_visits,
                    actual_value=1,
                    deviation_percentage=100.0,
                    context={"location": current_location, "previous_visits": expected_location_visits},
                    recommendations=["Запросить подтверждение личности", "Включить дополнительную аутентификацию"],
                    false_positive_probability=25.0,
                    related_anomalies=[]
                )
                anomalies.append(anomaly)

        # Поведенческие аномалии
        session_duration = current_data.get("session_duration", 0)
        if session_duration > 0 and profile.session_durations:
            avg_duration = statistics.mean(profile.session_durations)
            if session_duration > avg_duration * 3:  # В 3 раза дольше обычного
                anomaly = AdvancedAnomaly(
                    anomaly_id=f"behav_{profile.user_id}_{int(time.time())}",
                    entity_id=profile.user_id,
                    entity_type=EntityType.USER,
                    anomaly_type=AnomalyType.BEHAVIORAL,
                    severity=RiskLevel.MEDIUM,
                    confidence=70.0,
                    description=f"Необычно долгая сессия: {session_duration} минут (среднее: {avg_duration:.1f})",
                    detected_at=datetime.now(),
                    baseline_value=avg_duration,
                    actual_value=session_duration,
                    deviation_percentage=(session_duration / avg_duration - 1) * 100,
                    context={"session_duration": session_duration, "average_duration": avg_duration},
                    recommendations=["Мониторить активность", "Проверить на признаки компрометации"],
                    false_positive_probability=30.0,
                    related_anomalies=[]
                )
                anomalies.append(anomaly)

        return anomalies

    async def _detect_entity_anomalies(self, profile: EntityBehaviorProfile,
                                     current_data: Dict[str, Any]) -> List[AdvancedAnomaly]:
        """Обнаружение аномалий сущности"""
        anomalies = []

        # Аномалии производительности
        current_performance = current_data.get("performance_metrics", {})
        for metric_name, current_value in current_performance.items():
            if metric_name in profile.baseline_metrics:
                baseline_value = profile.baseline_metrics[metric_name]
                if baseline_value > 0:
                    deviation = abs(current_value - baseline_value) / baseline_value
                    if deviation > 0.5:  # 50% отклонение
                        anomaly = AdvancedAnomaly(
                            anomaly_id=f"perf_{profile.entity_id}_{metric_name}_{int(time.time())}",
                            entity_id=profile.entity_id,
                            entity_type=profile.entity_type,
                            anomaly_type=AnomalyType.PATTERN,
                            severity=RiskLevel.HIGH if deviation > 1.0 else RiskLevel.MEDIUM,
                            confidence=min(90.0, deviation * 60),
                            description=f"Аномалия производительности {metric_name}: {current_value} (базовое: {baseline_value})",
                            detected_at=datetime.now(),
                            baseline_value=baseline_value,
                            actual_value=current_value,
                            deviation_percentage=deviation * 100,
                            context={"metric": metric_name, "baseline": baseline_value, "current": current_value},
                            recommendations=["Проверить состояние системы", "Мониторить ресурсы"],
                            false_positive_probability=15.0,
                            related_anomalies=[]
                        )
                        anomalies.append(anomaly)

        # Аномалии ошибок
        current_errors = current_data.get("error_count", 0)
        if current_errors > 0 and profile.error_patterns:
            avg_errors = statistics.mean(
                [sum(errors) for errors in profile.error_patterns.values() if errors]
            )
            if current_errors > avg_errors * 2:  # В 2 раза больше ошибок
                anomaly = AdvancedAnomaly(
                    anomaly_id=f"error_{profile.entity_id}_{int(time.time())}",
                    entity_id=profile.entity_id,
                    entity_type=profile.entity_type,
                    anomaly_type=AnomalyType.PATTERN,
                    severity=RiskLevel.HIGH,
                    confidence=85.0,
                    description=f"Увеличение ошибок: {current_errors} (среднее: {avg_errors:.1f})",
                    detected_at=datetime.now(),
                    baseline_value=avg_errors,
                    actual_value=current_errors,
                    deviation_percentage=(current_errors / avg_errors - 1) * 100,
                    context={"error_count": current_errors, "average_errors": avg_errors},
                    recommendations=["Проверить логи ошибок", "Устранить проблемы"],
                    false_positive_probability=5.0,
                    related_anomalies=[]
                )
                anomalies.append(anomaly)

        return anomalies

    async def calculate_risk_score(self, entity_id: str, entity_type: EntityType) -> RiskAssessment:
        """Расчет оценки риска"""
        # Получаем профиль
        if entity_type == EntityType.USER:
            profile = await self._get_user_profile(entity_id)
        else:
            profile = await self._get_entity_profile(entity_id)

        if profile is None:
            return RiskAssessment(
                entity_id=entity_id,
                entity_type=entity_type,
                overall_risk_score=50.0,  # Средний риск для новых сущностей
                risk_factors={},
                risk_trend="stable",
                confidence=0.0,
                recommendations=["Собрать больше данных для анализа"],
                assessed_at=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=24)
            )

        # Анализируем недавние аномалии
        recent_anomalies = [
            a for a in self.anomalies
            if a.entity_id == entity_id and
            a.detected_at > datetime.now() - timedelta(hours=24)
        ]

        # Рассчитываем факторы риска
        risk_factors = {}

        # Фактор аномалий
        anomaly_risk = min(100.0, len(recent_anomalies) * 15)
        risk_factors["anomalies"] = anomaly_risk

        # Фактор серьезности аномалий
        if recent_anomalies:
            critical_anomalies = len([a for a in recent_anomalies if a.severity == RiskLevel.CRITICAL])
            high_anomalies = len([a for a in recent_anomalies if a.severity == RiskLevel.HIGH])
            severity_risk = min(100.0, critical_anomalies * 25 + high_anomalies * 15)
            risk_factors["severity"] = severity_risk
        else:
            risk_factors["severity"] = 0.0

        # Фактор отклонения от базовых паттернов
        if hasattr(profile, 'risk_score'):
            pattern_risk = profile.risk_score
            risk_factors["patterns"] = pattern_risk

        # Общий риск
        overall_risk = statistics.mean(risk_factors.values()) if risk_factors else 0.0

        # Тренд риска
        risk_trend = "stable"
        if len(recent_anomalies) > 3:
            risk_trend = "increasing"
        elif len(recent_anomalies) == 0:
            risk_trend = "decreasing"

        # Рекомендации
        recommendations = []
        if overall_risk > 70:
            recommendations.append("Критический уровень риска - немедленное вмешательство")
        elif overall_risk > 50:
            recommendations.append("Высокий уровень риска - усиленный мониторинг")
        elif overall_risk > 30:
            recommendations.append("Средний уровень риска - регулярный мониторинг")
        else:
            recommendations.append("Низкий уровень риска - стандартный мониторинг")

        risk_assessment = RiskAssessment(
            entity_id=entity_id,
            entity_type=entity_type,
            overall_risk_score=overall_risk,
            risk_factors=risk_factors,
            risk_trend=risk_trend,
            confidence=min(95.0, len(recent_anomalies) * 10 + 50),
            recommendations=recommendations,
            assessed_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=24)
        )

        # Сохраняем оценку риска
        await self._save_risk_assessment(risk_assessment)

        return risk_assessment

    async def _update_user_profile(self, profile: UserBehaviorProfile, behavior_data: Dict[str, Any]):
        """Обновление профиля пользователя"""
        # Обновляем время активности
        current_hour = datetime.now().hour
        profile.activity_times[str(current_hour)] = profile.activity_times.get(str(current_hour), 0) + 1

        # Обновляем локации
        location = behavior_data.get("location", "unknown")
        if location != "unknown":
            profile.locations[location] = profile.locations.get(location, 0) + 1

        # Обновляем устройства
        device = behavior_data.get("device", "unknown")
        if device != "unknown":
            profile.devices[device] = profile.devices.get(device, 0) + 1

        # Обновляем приложения
        application = behavior_data.get("application", "unknown")
        if application != "unknown":
            profile.applications[application] = profile.applications.get(application, 0) + 1

        # Обновляем длительности сессий
        session_duration = behavior_data.get("session_duration", 0)
        if session_duration > 0:
            profile.session_durations.append(session_duration)
            # Ограничиваем историю до 100 записей
            if len(profile.session_durations) > 100:
                profile.session_durations = profile.session_durations[-100:]

        # Обновляем частоту входов
        day_of_week = datetime.now().strftime("%A")
        profile.login_frequency[day_of_week] = profile.login_frequency.get(day_of_week, 0) + 1

        # Обновляем время последнего обновления
        profile.last_updated = datetime.now()

        # Рассчитываем уверенность на основе количества данных
        data_points = (len(profile.activity_times) + len(profile.locations) +
                      len(profile.devices) + len(profile.applications))
        profile.confidence = min(95.0, data_points * 2)

    async def _update_entity_profile(self, profile: EntityBehaviorProfile, behavior_data: Dict[str, Any]):
        """Обновление профиля сущности"""
        # Обновляем базовые метрики
        performance_metrics = behavior_data.get("performance_metrics", {})
        for metric_name, value in performance_metrics.items():
            if metric_name in profile.baseline_metrics:
                # Скользящее среднее
                profile.baseline_metrics[metric_name] = (
                    profile.baseline_metrics[metric_name] * 0.9 + value * 0.1
                )
            else:
                profile.baseline_metrics[metric_name] = value

        # Обновляем паттерны производительности
        for metric_name, value in performance_metrics.items():
            if metric_name not in profile.performance_patterns:
                profile.performance_patterns[metric_name] = []
            profile.performance_patterns[metric_name].append(value)
            # Ограничиваем историю до 100 записей
            if len(profile.performance_patterns[metric_name]) > 100:
                profile.performance_patterns[metric_name] = profile.performance_patterns[metric_name][-100:]

        # Обновляем использование ресурсов
        resource_usage = behavior_data.get("resource_usage", {})
        for resource_name, usage in resource_usage.items():
            if resource_name not in profile.resource_usage:
                profile.resource_usage[resource_name] = []
            profile.resource_usage[resource_name].append(usage)
            # Ограничиваем историю до 100 записей
            if len(profile.resource_usage[resource_name]) > 100:
                profile.resource_usage[resource_name] = profile.resource_usage[resource_name][-100:]

        # Обновляем паттерны ошибок
        error_count = behavior_data.get("error_count", 0)
        current_hour = datetime.now().hour
        hour_key = str(current_hour)
        if hour_key not in profile.error_patterns:
            profile.error_patterns[hour_key] = []
        profile.error_patterns[hour_key].append(error_count)

        # Обновляем время последнего обновления
        profile.last_updated = datetime.now()

        # Рассчитываем уверенность
        data_points = len(profile.baseline_metrics) + len(profile.performance_patterns)
        profile.confidence = min(95.0, data_points * 5)

    async def _get_user_profile(self, user_id: str) -> Optional[UserBehaviorProfile]:
        """Получение профиля пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_behavior_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return UserBehaviorProfile(
                user_id=row[0],
                baseline_patterns=json.loads(row[1]),
                activity_times=json.loads(row[2]),
                locations=json.loads(row[3]),
                devices=json.loads(row[4]),
                applications=json.loads(row[5]),
                session_durations=json.loads(row[6]),
                login_frequency=json.loads(row[7]),
                data_access_patterns=json.loads(row[8]),
                communication_patterns=json.loads(row[9]),
                risk_score=row[10],
                last_updated=datetime.fromisoformat(row[11]),
                confidence=row[12]
            )

        return None

    async def _get_entity_profile(self, entity_id: str) -> Optional[EntityBehaviorProfile]:
        """Получение профиля сущности"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM entity_behavior_profiles WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return EntityBehaviorProfile(
                entity_id=row[0],
                entity_type=EntityType(row[1]),
                baseline_metrics=json.loads(row[2]),
                performance_patterns=json.loads(row[3]),
                resource_usage=json.loads(row[4]),
                interaction_patterns=json.loads(row[5]),
                error_patterns=json.loads(row[6]),
                availability_patterns=json.loads(row[7]),
                risk_score=row[8],
                last_updated=datetime.fromisoformat(row[9]),
                confidence=row[10]
            )

        return None

    async def _save_user_profile(self, profile: UserBehaviorProfile):
        """Сохранение профиля пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO user_behavior_profiles
            (user_id, baseline_patterns, activity_times, locations, devices,
             applications, session_durations, login_frequency, data_access_patterns,
             communication_patterns, risk_score, last_updated, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.user_id,
            json.dumps(profile.baseline_patterns),
            json.dumps(profile.activity_times),
            json.dumps(profile.locations),
            json.dumps(profile.devices),
            json.dumps(profile.applications),
            json.dumps(profile.session_durations),
            json.dumps(profile.login_frequency),
            json.dumps(profile.data_access_patterns),
            json.dumps(profile.communication_patterns),
            profile.risk_score,
            profile.last_updated.isoformat(),
            profile.confidence
        ))

        conn.commit()
        conn.close()

    async def _save_entity_profile(self, profile: EntityBehaviorProfile):
        """Сохранение профиля сущности"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO entity_behavior_profiles
            (entity_id, entity_type, baseline_metrics, performance_patterns,
             resource_usage, interaction_patterns, error_patterns, availability_patterns,
             risk_score, last_updated, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.entity_id,
            profile.entity_type.value,
            json.dumps(profile.baseline_metrics),
            json.dumps(profile.performance_patterns),
            json.dumps(profile.resource_usage),
            json.dumps(profile.interaction_patterns),
            json.dumps(profile.error_patterns),
            json.dumps(profile.availability_patterns),
            profile.risk_score,
            profile.last_updated.isoformat(),
            profile.confidence
        ))

        conn.commit()
        conn.close()

    async def _save_anomaly(self, anomaly: AdvancedAnomaly):
        """Сохранение аномалии"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO anomalies
            (anomaly_id, entity_id, entity_type, anomaly_type, severity, confidence,
             description, detected_at, baseline_value, actual_value, deviation_percentage,
             context, recommendations, false_positive_probability, related_anomalies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            anomaly.anomaly_id,
            anomaly.entity_id,
            anomaly.entity_type.value,
            anomaly.anomaly_type.value,
            anomaly.severity.value,
            anomaly.confidence,
            anomaly.description,
            anomaly.detected_at.isoformat(),
            anomaly.baseline_value,
            anomaly.actual_value,
            anomaly.deviation_percentage,
            json.dumps(anomaly.context),
            json.dumps(anomaly.recommendations),
            anomaly.false_positive_probability,
            json.dumps(anomaly.related_anomalies)
        ))

        conn.commit()
        conn.close()

    async def _save_risk_assessment(self, assessment: RiskAssessment):
        """Сохранение оценки риска"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO risk_assessments
            (entity_id, entity_type, overall_risk_score, risk_factors, risk_trend,
             confidence, recommendations, assessed_at, valid_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assessment.entity_id,
            assessment.entity_type.value,
            assessment.overall_risk_score,
            json.dumps(assessment.risk_factors),
            assessment.risk_trend,
            assessment.confidence,
            json.dumps(assessment.recommendations),
            assessment.assessed_at.isoformat(),
            assessment.valid_until.isoformat()
        ))

        conn.commit()
        conn.close()

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Получение сводки аналитики"""
        return {
            "user_profiles": len(self.user_profiles),
            "entity_profiles": len(self.entity_profiles),
            "total_anomalies": len(self.anomalies),
            "risk_assessments": len(self.risk_assessments),
            "anomalies_by_type": {},
            "anomalies_by_severity": {},
            "last_updated": datetime.now().isoformat()
        }

# Пример использования
async def main():
    """Основная функция"""
    analytics = AdvancedBehavioralAnalytics()

    # Анализ поведения пользователя
    user_data = {
        "location": "Moscow",
        "device": "iPhone",
        "application": "ALADDIN Mobile",
        "session_duration": 45,
        "activity_count": 15
    }

    user_profile = await analytics.analyze_user_behavior("user_123", user_data)
    print(f"User profile: {user_profile.to_dict()}")

    # Обнаружение аномалий
    anomalies = await analytics.detect_anomalies("user_123", EntityType.USER, user_data)
    print(f"Anomalies detected: {len(anomalies)}")

    # Оценка риска
    risk_assessment = await analytics.calculate_risk_score("user_123", EntityType.USER)
    print(f"Risk assessment: {risk_assessment.to_dict()}")

    # Сводка
    summary = await analytics.get_analytics_summary()
    print(f"Analytics summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
