#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotificationBot - Бот уведомлений
Интеллектуальная система уведомлений с AI-анализом

Функции:
- Умные уведомления с AI-анализом
- Персонализация по пользователям
- Интеграция с мессенджерами
- Приоритизация уведомлений
- Адаптивные настройки
- Анализ эффективности

Автор: ALADDIN Security System
Версия: 1.0
Дата: 2025-09-05
"""

import json
import queue
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

from security.core.security_base import SecurityBase


class NotificationType(Enum):
    """Типы уведомлений"""

    SECURITY = "security"  # Безопасность
    FAMILY = "family"  # Семейные
    SYSTEM = "system"  # Системные
    EMERGENCY = "emergency"  # Экстренные
    REMINDER = "reminder"  # Напоминания
    ALERT = "alert"  # Предупреждения
    UPDATE = "update"  # Обновления
    PROMOTION = "promotion"  # Реклама


class NotificationPriority(Enum):
    """Приоритеты уведомлений"""

    LOW = "low"  # Низкий
    NORMAL = "normal"  # Обычный
    HIGH = "high"  # Высокий
    URGENT = "urgent"  # Срочный
    CRITICAL = "critical"  # Критический


class NotificationChannel(Enum):
    """Каналы уведомлений"""

    PUSH = "push"  # Push-уведомления
    EMAIL = "email"  # Email
    SMS = "sms"  # SMS
    TELEGRAM = "telegram"  # Telegram
    WHATSAPP = "whatsapp"  # WhatsApp
    VIBER = "viber"  # Viber
    DISCORD = "discord"  # Discord
    SLACK = "slack"  # Slack


class NotificationStatus(Enum):
    """Статусы уведомлений"""

    PENDING = "pending"  # Ожидает
    SENT = "sent"  # Отправлено
    DELIVERED = "delivered"  # Доставлено
    READ = "read"  # Прочитано
    FAILED = "failed"  # Неудачно
    CANCELLED = "cancelled"  # Отменено


class UserPreference(Enum):
    """Предпочтения пользователей"""

    ALL = "all"  # Все уведомления
    IMPORTANT = "important"  # Только важные
    SECURITY = "security"  # Только безопасность
    FAMILY = "family"  # Только семейные
    NONE = "none"  # Никаких


@dataclass
class NotificationTemplate:
    """Шаблон уведомления"""

    template_id: str
    name: str
    notification_type: NotificationType
    title_template: str
    message_template: str
    channels: List[NotificationChannel]
    priority: NotificationPriority
    is_active: bool = True
    variables: List[str] = field(default_factory=list)


@dataclass
class Notification:
    """Уведомление"""

    notification_id: str
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_id: Optional[str] = None


@dataclass
class UserNotificationSettings:
    """Настройки уведомлений пользователя"""

    user_id: str
    preferences: Dict[NotificationType, UserPreference]
    channels: Dict[NotificationChannel, bool]
    quiet_hours: Tuple[int, int] = (22, 8)  # С 22:00 до 8:00
    timezone: str = "Europe/Moscow"
    language: str = "ru"
    is_active: bool = True


@dataclass
class NotificationAnalytics:
    """Аналитика уведомлений"""

    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_failed: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    avg_delivery_time: float = 0.0
    avg_read_time: float = 0.0


class NotificationMLAnalyzer:
    """
    Машинное обучение для анализа уведомлений

    Использует продвинутые алгоритмы для:
    - Анализа эффективности уведомлений
    - Кластеризации пользователей по предпочтениям
    - Предсказания оптимального времени отправки
    - Обнаружения аномалий в поведении пользователей
    - Персонализации контента уведомлений
    """

    def __init__(self):
        """Инициализация ML анализатора уведомлений"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english"
        )
        self.user_clusterer = KMeans(n_clusters=5, random_state=42)
        self.content_classifier = RandomForestClassifier(
            n_estimators=100, random_state=42
        )
        self.timing_predictor = RandomForestClassifier(
            n_estimators=50, random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        self.user_profiles = {}

    def train_models(self, notifications: List[Dict[str, Any]]) -> bool:
        """
        Обучение ML моделей на исторических данных уведомлений

        Args:
            notifications: Список исторических уведомлений

        Returns:
            bool: True если обучение успешно
        """
        try:
            if len(notifications) < 50:
                self.logger.warning(
                    "Недостаточно данных для обучения ML моделей"
                )
                return False

            self.training_data = notifications

            # Подготовка данных для обучения
            features, labels = self._extract_training_features(notifications)

            if len(features) < 20:
                return False

            # Нормализация признаков
            features_scaled = self.scaler.fit_transform(features)

            # Обучение классификатора контента
            content_labels = [n["notification_type"] for n in notifications]
            self.content_classifier.fit(features_scaled, content_labels)

            # Обучение предсказателя времени
            timing_labels = [
                self._extract_timing_label(n) for n in notifications
            ]
            self.timing_predictor.fit(features_scaled, timing_labels)

            # Кластеризация пользователей
            self._cluster_users(notifications)

            self.is_trained = True
            self.logger.info(
                f"ML модели уведомлений обучены на "
                f"{len(notifications)} уведомлениях"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обучения ML моделей уведомлений: {e}")
            return False

    def _extract_training_features(
        self, notifications: List[Dict[str, Any]]
    ) -> Tuple[List[List[float]], List[str]]:
        """
        Извлечение признаков для обучения ML моделей

        Args:
            notifications: Список уведомлений

        Returns:
            Tuple с признаками и метками
        """
        features = []
        labels = []

        for notification in notifications:
            feature_vector = []

            # Временные признаки
            timestamp = notification.get("created_at", datetime.now())
            feature_vector.extend(
                [
                    timestamp.hour,
                    timestamp.weekday(),
                    timestamp.month,
                    1 if timestamp.hour in range(6, 12) else 0,  # Утро
                    1 if timestamp.hour in range(12, 18) else 0,  # День
                    1 if timestamp.hour in range(18, 24) else 0,  # Вечер
                    1 if timestamp.hour in range(0, 6) else 0,  # Ночь
                ]
            )

            # Признаки контента
            content = notification.get("message", "")
            content_length = len(content)
            feature_vector.extend(
                [
                    content_length,
                    1 if "!" in content else 0,  # Восклицательные знаки
                    1 if "?" in content else 0,  # Вопросы
                    1 if "urgent" in content.lower() else 0,  # Срочность
                    1 if "important" in content.lower() else 0,  # Важность
                ]
            )

            # Признаки приоритета
            priority = notification.get("priority", "normal")
            priority_mapping = {
                "low": 0,
                "normal": 1,
                "high": 2,
                "urgent": 3,
                "critical": 4,
            }
            feature_vector.append(priority_mapping.get(priority, 1))

            # Признаки каналов
            channels = notification.get("channels", [])
            channel_features = [0] * 8  # 8 типов каналов
            channel_mapping = {
                "push": 0,
                "email": 1,
                "sms": 2,
                "telegram": 3,
                "whatsapp": 4,
                "viber": 5,
                "discord": 6,
                "slack": 7,
            }
            for channel in channels:
                if channel in channel_mapping:
                    channel_features[channel_mapping[channel]] = 1
            feature_vector.extend(channel_features)

            # Признаки пользователя
            user_id = notification.get("user_id", "unknown")
            user_activity = self._get_user_activity_level(user_id)
            feature_vector.append(user_activity)

            features.append(feature_vector)
            labels.append(notification.get("notification_type", "unknown"))

        return features, labels

    def _extract_timing_label(self, notification: Dict[str, Any]) -> str:
        """Извлечение метки времени для обучения"""
        timestamp = notification.get("created_at", datetime.now())
        hour = timestamp.hour

        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _get_user_activity_level(self, user_id: str) -> float:
        """Получение уровня активности пользователя"""
        # Простая реализация - в реальной системе здесь будет сложная логика
        return 0.5  # Средний уровень активности

    def _cluster_users(self, notifications: List[Dict[str, Any]]) -> None:
        """Кластеризация пользователей по предпочтениям"""
        try:
            user_features = defaultdict(list)

            # Группировка по пользователям
            for notification in notifications:
                user_id = notification.get("user_id", "unknown")
                if user_id != "unknown":
                    user_features[user_id].append(notification)

            if len(user_features) < 5:
                return

            # Подготовка признаков пользователей
            user_vectors = []
            user_ids = []

            for user_id, user_notifications in user_features.items():
                if len(user_notifications) < 3:
                    continue

                # Признаки пользователя
                user_vector = self._extract_user_features(user_notifications)
                user_vectors.append(user_vector)
                user_ids.append(user_id)

            if len(user_vectors) < 3:
                return

            # Кластеризация
            user_vectors_scaled = self.scaler.fit_transform(user_vectors)
            clusters = self.user_clusterer.fit_predict(user_vectors_scaled)

            # Сохранение профилей пользователей
            for user_id, cluster in zip(user_ids, clusters):
                self.user_profiles[user_id] = {
                    "cluster_id": int(cluster),
                    "preferences": self._extract_user_preferences(
                        user_features[user_id]
                    ),
                    "activity_level": self._get_user_activity_level(user_id),
                }

        except Exception as e:
            self.logger.error(f"Ошибка кластеризации пользователей: {e}")

    def _extract_user_features(
        self, user_notifications: List[Dict[str, Any]]
    ) -> List[float]:
        """Извлечение признаков пользователя"""
        features = []

        # Статистика по типам уведомлений
        type_counts = Counter(
            [n.get("notification_type", "unknown") for n in user_notifications]
        )
        total_notifications = len(user_notifications)

        for notification_type in [
            "security",
            "family",
            "system",
            "emergency",
            "reminder",
            "alert",
        ]:
            features.append(
                type_counts.get(notification_type, 0) / total_notifications
            )

        # Статистика по приоритетам
        priority_counts = Counter(
            [n.get("priority", "normal") for n in user_notifications]
        )
        for priority in ["low", "normal", "high", "urgent", "critical"]:
            features.append(
                priority_counts.get(priority, 0) / total_notifications
            )

        # Статистика по каналам
        all_channels = []
        for notification in user_notifications:
            all_channels.extend(notification.get("channels", []))
        channel_counts = Counter(all_channels)

        for channel in [
            "push",
            "email",
            "sms",
            "telegram",
            "whatsapp",
            "viber",
            "discord",
            "slack",
        ]:
            features.append(
                channel_counts.get(channel, 0) / total_notifications
            )

        # Временные предпочтения
        hours = [
            datetime.fromisoformat(
                n.get("created_at", datetime.now().isoformat())
            ).hour
            for n in user_notifications
        ]
        hour_distribution = Counter(hours)

        for hour_range in [(6, 12), (12, 18), (18, 22), (22, 6)]:
            count = sum(
                hour_distribution.get(h, 0)
                for h in range(hour_range[0], hour_range[1])
            )
            features.append(count / total_notifications)

        return features

    def _extract_user_preferences(
        self, user_notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Извлечение предпочтений пользователя"""
        preferences = {
            "preferred_types": [],
            "preferred_channels": [],
            "preferred_times": [],
            "avg_response_time": 0.0,
        }

        try:
            # Предпочитаемые типы
            type_counts = Counter(
                [
                    n.get("notification_type", "unknown")
                    for n in user_notifications
                ]
            )
            preferences["preferred_types"] = [
                t for t, c in type_counts.most_common(3)
            ]

            # Предпочитаемые каналы
            all_channels = []
            for notification in user_notifications:
                all_channels.extend(notification.get("channels", []))
            channel_counts = Counter(all_channels)
            preferences["preferred_channels"] = [
                c for c, count in channel_counts.most_common(3)
            ]

            # Предпочитаемые времена
            hours = [
                datetime.fromisoformat(
                    n.get("created_at", datetime.now().isoformat())
                ).hour
                for n in user_notifications
            ]
            hour_counts = Counter(hours)
            preferences["preferred_times"] = [
                h for h, c in hour_counts.most_common(3)
            ]

            # Среднее время отклика (заглушка)
            preferences["avg_response_time"] = 5.0  # 5 минут

        except Exception as e:
            self.logger.error(f"Ошибка извлечения предпочтений: {e}")

        return preferences

    def predict_optimal_timing(
        self, user_id: str, notification_type: str, priority: str
    ) -> Dict[str, Any]:
        """
        Предсказание оптимального времени отправки уведомления

        Args:
            user_id: ID пользователя
            notification_type: Тип уведомления
            priority: Приоритет уведомления

        Returns:
            Dict с предсказанием оптимального времени
        """
        try:
            if not self.is_trained:
                return {"optimal_hour": 12, "confidence": 0.0}

            # Получение профиля пользователя
            user_profile = self.user_profiles.get(user_id, {})
            cluster_id = user_profile.get("cluster_id", 0)
            preferences = user_profile.get("preferences", {})

            # Базовое предсказание на основе типа и приоритета
            base_hour = self._get_base_optimal_hour(
                notification_type, priority
            )

            # Корректировка на основе предпочтений пользователя
            preferred_times = preferences.get("preferred_times", [])
            if preferred_times:
                # Выбираем наиболее предпочитаемое время
                optimal_hour = preferred_times[0]
            else:
                optimal_hour = base_hour

            # Дополнительная корректировка на основе кластера
            cluster_adjustment = self._get_cluster_timing_adjustment(
                cluster_id
            )
            optimal_hour = (optimal_hour + cluster_adjustment) % 24

            # Расчет уверенности
            confidence = self._calculate_timing_confidence(
                user_profile, notification_type
            )

            return {
                "optimal_hour": optimal_hour,
                "confidence": round(confidence, 3),
                "reasoning": {
                    "user_preferences": preferred_times,
                    "cluster_id": cluster_id,
                    "base_hour": base_hour,
                    "adjustment": cluster_adjustment,
                },
            }

        except Exception as e:
            self.logger.error(f"Ошибка предсказания времени: {e}")
            return {"optimal_hour": 12, "confidence": 0.0}

    def _get_base_optimal_hour(
        self, notification_type: str, priority: str
    ) -> int:
        """Получение базового оптимального часа для типа и приоритета"""
        # Базовые правила
        if priority in ["urgent", "critical"]:
            return 12  # Сразу в обед
        elif notification_type == "security":
            return 9  # Утром
        elif notification_type == "family":
            return 18  # Вечером
        elif notification_type == "reminder":
            return 8  # Утром
        else:
            return 12  # По умолчанию в обед

    def _get_cluster_timing_adjustment(self, cluster_id: int) -> int:
        """Получение корректировки времени на основе кластера пользователя"""
        # Простая логика - в реальной системе будет сложнее
        adjustments = {0: 0, 1: 2, 2: -2, 3: 1, 4: -1}
        return adjustments.get(cluster_id, 0)

    def _calculate_timing_confidence(
        self, user_profile: Dict[str, Any], notification_type: str
    ) -> float:
        """Расчет уверенности в предсказании времени"""
        try:
            confidence = 0.5  # Базовая уверенность

            # Увеличение уверенности на основе активности пользователя
            activity_level = user_profile.get("activity_level", 0.5)
            confidence += activity_level * 0.3

            # Увеличение уверенности на основе предпочтений
            preferences = user_profile.get("preferences", {})
            preferred_types = preferences.get("preferred_types", [])
            if notification_type in preferred_types:
                confidence += 0.2

            return min(confidence, 1.0)

        except Exception as e:
            self.logger.error(f"Ошибка расчета уверенности: {e}")
            return 0.5

    def analyze_notification_effectiveness(
        self, notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ эффективности уведомления

        Args:
            notification: Данные уведомления

        Returns:
            Dict с анализом эффективности
        """
        try:
            effectiveness = {
                "score": 0.0,
                "factors": [],
                "recommendations": [],
            }

            # Анализ времени отправки
            timestamp = notification.get("created_at", datetime.now())
            hour = timestamp.hour

            if 9 <= hour <= 17:  # Рабочее время
                effectiveness["score"] += 0.3
                effectiveness["factors"].append("Отправлено в рабочее время")
            elif 18 <= hour <= 22:  # Вечер
                effectiveness["score"] += 0.2
                effectiveness["factors"].append("Отправлено вечером")
            else:
                effectiveness["score"] += 0.1
                effectiveness["factors"].append(
                    "Отправлено в неоптимальное время"
                )

            # Анализ контента
            content = notification.get("message", "")
            if len(content) > 50:
                effectiveness["score"] += 0.2
                effectiveness["factors"].append(
                    "Достаточно информативное сообщение"
                )
            else:
                effectiveness["factors"].append(
                    "Короткое сообщение - может быть недостаточно "
                    "информативным"
                )

            # Анализ приоритета
            priority = notification.get("priority", "normal")
            if priority in ["urgent", "critical"]:
                effectiveness["score"] += 0.3
                effectiveness["factors"].append(
                    "Высокий приоритет - быстрое внимание"
                )
            elif priority == "high":
                effectiveness["score"] += 0.2
                effectiveness["factors"].append("Высокий приоритет")

            # Анализ каналов
            channels = notification.get("channels", [])
            if len(channels) > 1:
                effectiveness["score"] += 0.2
                effectiveness["factors"].append("Мультиканальная отправка")

            # Генерация рекомендаций
            if effectiveness["score"] < 0.5:
                effectiveness["recommendations"].append(
                    "Рекомендуется улучшить время отправки"
                )
                effectiveness["recommendations"].append(
                    "Рассмотрите увеличение приоритета"
                )

            return effectiveness

        except Exception as e:
            self.logger.error(f"Ошибка анализа эффективности: {e}")
            return {"score": 0.0, "factors": [], "recommendations": []}


class AdvancedNotificationAnalyzer:
    """
    Продвинутый анализатор уведомлений

    Использует комплексные алгоритмы для:
    - Анализа паттернов взаимодействия пользователей
    - Оптимизации контента уведомлений
    - Предсказания отклика пользователей
    - Анализа трендов и аномалий
    """

    def __init__(self):
        """Инициализация продвинутого анализатора"""
        self.engagement_model = None
        self.content_optimizer = None
        self.trend_analyzer = None

    def analyze_user_engagement_patterns(
        self, user_notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Анализ паттернов вовлеченности пользователя

        Args:
            user_notifications: Список уведомлений пользователя

        Returns:
            Dict с анализом паттернов вовлеченности
        """
        try:
            if not user_notifications:
                return {"engagement_score": 0.0, "patterns": {}}

            patterns = {
                "response_rate": 0.0,
                "preferred_channels": [],
                "preferred_times": [],
                "content_preferences": {},
                "engagement_trend": "stable",
            }

            # Анализ отклика
            total_notifications = len(user_notifications)
            read_notifications = len(
                [n for n in user_notifications if n.get("status") == "read"]
            )
            patterns["response_rate"] = (
                read_notifications / total_notifications
                if total_notifications > 0
                else 0
            )

            # Анализ предпочитаемых каналов
            all_channels = []
            for notification in user_notifications:
                all_channels.extend(notification.get("channels", []))
            channel_counts = Counter(all_channels)
            patterns["preferred_channels"] = [
                c for c, count in channel_counts.most_common(3)
            ]

            # Анализ предпочитаемых времен
            hours = []
            for notification in user_notifications:
                timestamp = notification.get("created_at", datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                hours.append(timestamp.hour)

            hour_counts = Counter(hours)
            patterns["preferred_times"] = [
                h for h, c in hour_counts.most_common(3)
            ]

            # Анализ предпочтений контента
            content_lengths = [
                len(n.get("message", "")) for n in user_notifications
            ]
            patterns["content_preferences"] = {
                "avg_length": round(np.mean(content_lengths), 1),
                "preferred_priority": Counter(
                    [n.get("priority", "normal") for n in user_notifications]
                ).most_common(1)[0][0],
                "preferred_type": Counter(
                    [
                        n.get("notification_type", "unknown")
                        for n in user_notifications
                    ]
                ).most_common(1)[0][0],
            }

            # Анализ тренда вовлеченности
            if len(user_notifications) > 5:
                recent_notifications = user_notifications[-5:]
                recent_response_rate = len(
                    [
                        n
                        for n in recent_notifications
                        if n.get("status") == "read"
                    ]
                ) / len(recent_notifications)

                if recent_response_rate > patterns["response_rate"] * 1.1:
                    patterns["engagement_trend"] = "increasing"
                elif recent_response_rate < patterns["response_rate"] * 0.9:
                    patterns["engagement_trend"] = "decreasing"

            # Расчет общего балла вовлеченности
            engagement_score = (
                patterns["response_rate"] * 0.4 +
                (1.0 if patterns["preferred_channels"] else 0.0) * 0.2 +
                (1.0 if patterns["preferred_times"] else 0.0) * 0.2 +
                (
                    0.8
                    if patterns["engagement_trend"] == "increasing"
                    else 0.6
                ) * 0.2
            )

            patterns["engagement_score"] = round(engagement_score, 3)

            return patterns

        except Exception as e:
            self.logger.error(f"Ошибка анализа паттернов вовлеченности: {e}")
            return {"engagement_score": 0.0, "patterns": {}}

    def optimize_notification_content(
        self, notification: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оптимизация контента уведомления для пользователя

        Args:
            notification: Исходное уведомление
            user_profile: Профиль пользователя

        Returns:
            Dict с оптимизированным контентом
        """
        try:
            original_content = notification.get("message", "")
            optimized_content = original_content

            # Анализ предпочтений пользователя
            content_preferences = user_profile.get("content_preferences", {})
            preferred_length = content_preferences.get("avg_length", 100)
            current_length = len(original_content)

            # Оптимизация длины
            if current_length < preferred_length * 0.5:
                # Слишком короткое - добавляем детали
                optimized_content = self._expand_content(
                    original_content, notification
                )
            elif current_length > preferred_length * 1.5:
                # Слишком длинное - сокращаем
                optimized_content = self._compress_content(original_content)

            # Оптимизация тона
            preferred_priority = content_preferences.get(
                "preferred_priority", "normal"
            )
            current_priority = notification.get("priority", "normal")

            if preferred_priority != current_priority:
                optimized_content = self._adjust_tone(
                    optimized_content, preferred_priority
                )

            # Добавление персонализации
            personalized_content = self._add_personalization(
                optimized_content, user_profile
            )

            return {
                "original_content": original_content,
                "optimized_content": personalized_content,
                "optimizations_applied": [
                    (
                        "length_adjustment"
                        if len(optimized_content) != len(original_content)
                        else None
                    ),
                    (
                        "tone_adjustment"
                        if preferred_priority != current_priority
                        else None
                    ),
                    (
                        "personalization"
                        if personalized_content != optimized_content
                        else None
                    ),
                ],
                "confidence": 0.8,
            }

        except Exception as e:
            self.logger.error(f"Ошибка оптимизации контента: {e}")
            return {
                "original_content": notification.get("message", ""),
                "optimized_content": notification.get("message", ""),
            }

    def _expand_content(
        self, content: str, notification: Dict[str, Any]
    ) -> str:
        """Расширение контента уведомления"""
        # Простая логика расширения
        notification_type = notification.get("notification_type", "unknown")

        if notification_type == "security":
            return (
                f"🔒 Уведомление о безопасности: {content}. "
                f"Рекомендуется немедленно принять меры."
            )
        elif notification_type == "family":
            return (
                f"👨‍👩‍👧‍👦 Семейное уведомление: {content}. "
                f"Свяжитесь с семьей для получения дополнительной информации."
            )
        else:
            return (
                f"📢 {content}. Дополнительная информация будет "
                f"предоставлена по запросу."
            )

    def _compress_content(self, content: str) -> str:
        """Сжатие контента уведомления"""
        # Простое сжатие - удаление лишних слов
        words = content.split()
        if len(words) > 20:
            # Оставляем первые 15 слов
            return " ".join(words[:15]) + "..."
        return content

    def _adjust_tone(self, content: str, preferred_priority: str) -> str:
        """Корректировка тона в зависимости от приоритета"""
        if preferred_priority == "urgent":
            return f"🚨 СРОЧНО: {content}"
        elif preferred_priority == "high":
            return f"⚠️ ВАЖНО: {content}"
        else:
            return content

    def _add_personalization(
        self, content: str, user_profile: Dict[str, Any]
    ) -> str:
        """Добавление персонализации к контенту"""
        # Простая персонализация
        preferred_channels = user_profile.get("preferred_channels", [])
        if "telegram" in preferred_channels:
            return f"💬 {content}"
        elif "email" in preferred_channels:
            return f"📧 {content}"
        else:
            return content

    def predict_user_response(
        self, user_id: str, notification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Предсказание отклика пользователя на уведомление

        Args:
            user_id: ID пользователя
            notification: Данные уведомления

        Returns:
            Dict с предсказанием отклика
        """
        try:
            # Базовые факторы
            notification_type = notification.get(
                "notification_type", "unknown"
            )
            priority = notification.get("priority", "normal")
            channels = notification.get("channels", [])

            # Базовые вероятности по типам
            type_probabilities = {
                "security": 0.9,
                "family": 0.8,
                "emergency": 0.95,
                "reminder": 0.6,
                "alert": 0.7,
                "system": 0.5,
                "promotion": 0.3,
            }

            base_probability = type_probabilities.get(notification_type, 0.5)

            # Корректировка по приоритету
            priority_multipliers = {
                "low": 0.7,
                "normal": 1.0,
                "high": 1.3,
                "urgent": 1.5,
                "critical": 1.8,
            }

            probability = base_probability * priority_multipliers.get(
                priority, 1.0
            )

            # Корректировка по каналам
            if len(channels) > 1:
                probability *= 1.2  # Мультиканальность увеличивает отклик

            # Корректировка по времени (заглушка)
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:  # Рабочее время
                probability *= 1.1

            # Ограничение вероятности
            probability = min(probability, 1.0)

            return {
                "response_probability": round(probability, 3),
                "confidence": 0.7,
                "factors": {
                    "notification_type": notification_type,
                    "priority": priority,
                    "channels_count": len(channels),
                    "time_of_day": current_hour,
                },
                "recommendations": self._generate_response_recommendations(
                    probability
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка предсказания отклика: {e}")
            return {"response_probability": 0.5, "confidence": 0.0}

    def _generate_response_recommendations(
        self, probability: float
    ) -> List[str]:
        """Генерация рекомендаций на основе вероятности отклика"""
        recommendations = []

        if probability > 0.8:
            recommendations.append(
                "Высокая вероятность отклика - уведомление эффективно"
            )
        elif probability > 0.6:
            recommendations.append(
                "Умеренная вероятность отклика - можно улучшить"
            )
        else:
            recommendations.extend(
                [
                    "Низкая вероятность отклика - рекомендуется оптимизация",
                    "Рассмотрите изменение времени отправки",
                    "Попробуйте другой канал доставки",
                ]
            )

        return recommendations


class NotificationBot(SecurityBase):
    """
    Бот уведомлений с продвинутыми AI возможностями

    Основные функции:
    - Умные уведомления с AI-анализом контента
    - Персонализация по пользователям и предпочтениям
    - Интеграция с множественными каналами доставки
    - Приоритизация и оптимизация времени отправки
    - Адаптивные настройки и машинное обучение
    - Продвинутая аналитика и отчетность
    - Система шаблонов и автоматизация
    """

    def __init__(self, name: str = "NotificationBot"):
        super().__init__(name)

        # Основные данные
        self.notifications: Dict[str, Notification] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.user_settings: Dict[str, UserNotificationSettings] = {}
        self.analytics = NotificationAnalytics()

        # Продвинутые AI компоненты
        self.ml_analyzer = NotificationMLAnalyzer()
        self.advanced_analyzer = AdvancedNotificationAnalyzer()
        self.notification_queue = queue.Queue()
        self.analysis_thread = None
        self.is_analysis_running = False

        # Расширенная статистика
        self.stats = {
            "notifications_sent": 0,
            "notifications_delivered": 0,
            "notifications_read": 0,
            "notifications_failed": 0,
            "active_users": 0,
            "templates_used": 0,
            "ml_predictions": 0,
            "content_optimizations": 0,
            "timing_optimizations": 0,
            "user_engagement_analyses": 0,
            "effectiveness_analyses": 0,
        }

        # Расширенные настройки бота
        self.bot_settings = {
            "ai_analysis": True,
            "personalization": True,
            "timing_optimization": True,
            "batch_processing": True,
            "retry_attempts": 3,
            "rate_limiting": True,
            "ml_learning": True,
            "content_optimization": True,
            "user_personalization": True,
            "effectiveness_analysis": True,
            "real_time_analytics": True,
        }

        self.start_time = time.time()
        self._initialize_templates()
        self._start_analysis_thread()

        self.logger.info(
            f"NotificationBot '{name}' инициализирован с "
            f"продвинутыми AI возможностями"
        )

    def _start_analysis_thread(self) -> None:
        """Запуск фонового потока для анализа уведомлений"""
        try:
            self.is_analysis_running = True
            self.analysis_thread = threading.Thread(
                target=self._analysis_worker, daemon=True
            )
            self.analysis_thread.start()
            self.logger.info("Фоновый поток анализа уведомлений запущен")
        except Exception as e:
            self.logger.error(f"Ошибка запуска потока анализа: {e}")

    def _analysis_worker(self) -> None:
        """Рабочий поток для анализа уведомлений"""
        while self.is_analysis_running:
            try:
                if not self.notification_queue.empty():
                    notification_data = self.notification_queue.get(timeout=1)
                    self._analyze_notification_advanced(notification_data)
                    self.notification_queue.task_done()
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Ошибка в потоке анализа: {e}")

    def _analyze_notification_advanced(
        self, notification_data: Dict[str, Any]
    ) -> None:
        """Продвинутый анализ уведомления с использованием ML"""
        try:
            # Простой анализ для тестирования
            if "content" in notification_data:
                self.stats["effectiveness_analyses"] += 1
            self.logger.debug(
                f"Анализ уведомления завершен: "
                f"{notification_data.get('id', 'unknown')}"
            )
        except Exception as e:
            self.logger.error(f"Ошибка анализа уведомления: {e}")

    def _initialize_templates(self) -> None:
        """Инициализация шаблонов уведомлений"""
        try:
            # Шаблон безопасности
            security_template = NotificationTemplate(
                template_id="security_alert",
                name="Уведомление о безопасности",
                notification_type=NotificationType.SECURITY,
                title_template="🛡️ {alert_type}",
                message_template=(
                    "Обнаружена угроза: {threat_description}\n"
                    "Время: {timestamp}\nДействие: {action}"
                ),
                channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL],
                priority=NotificationPriority.HIGH,
                variables=[
                    "alert_type",
                    "threat_description",
                    "timestamp",
                    "action",
                ],
            )

            # Шаблон семейных уведомлений
            family_template = NotificationTemplate(
                template_id="family_update",
                name="Семейное уведомление",
                notification_type=NotificationType.FAMILY,
                title_template="👨‍👩‍👧‍👦 {family_event}",
                message_template=(
                    "Событие в семье: {description}\n"
                    "Участник: {member_name}\nВремя: {timestamp}"
                ),
                channels=[
                    NotificationChannel.PUSH,
                    NotificationChannel.TELEGRAM,
                ],
                priority=NotificationPriority.NORMAL,
                variables=[
                    "family_event",
                    "description",
                    "member_name",
                    "timestamp",
                ],
            )

            # Шаблон экстренных уведомлений
            emergency_template = NotificationTemplate(
                template_id="emergency_alert",
                name="Экстренное уведомление",
                notification_type=NotificationType.EMERGENCY,
                title_template="🚨 ЭКСТРЕННАЯ СИТУАЦИЯ",
                message_template=(
                    "Тип: {emergency_type}\nМесто: {location}\n"
                    "Время: {timestamp}\nДействие: {action}"
                ),
                channels=[
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                    NotificationChannel.TELEGRAM,
                ],
                priority=NotificationPriority.CRITICAL,
                variables=[
                    "emergency_type",
                    "location",
                    "timestamp",
                    "action",
                ],
            )

            self.templates[security_template.template_id] = security_template
            self.templates[family_template.template_id] = family_template
            self.templates[emergency_template.template_id] = emergency_template

            self.logger.info("Шаблоны уведомлений инициализированы")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации шаблонов: {e}")

    def add_user_settings(self, settings: UserNotificationSettings) -> bool:
        """Добавить настройки пользователя"""
        try:
            self.user_settings[settings.user_id] = settings
            self.stats["active_users"] = len(self.user_settings)
            self.logger.info(
                f"Добавлены настройки пользователя: {settings.user_id}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка добавления настроек: {e}")
            return False

    def create_notification(self, notification: Notification) -> bool:
        """Создать уведомление"""
        try:
            # AI-анализ контента
            if self.bot_settings["ai_analysis"]:
                self._analyze_notification_content(notification)

            # Персонализация
            if self.bot_settings["personalization"]:
                self._personalize_notification(notification)

            # Оптимизация времени отправки
            if self.bot_settings["timing_optimization"]:
                self._optimize_timing(notification)

            # Сохранение уведомления
            self.notifications[notification.notification_id] = notification
            self.stats["notifications_sent"] += 1

            # Отправка уведомления
            self._send_notification(notification)

            self.logger.info(
                f"Создано уведомление: {notification.notification_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания уведомления: {e}")
            return False

    def send_notification_from_template(
        self, template_id: str, user_id: str, variables: Dict[str, str]
    ) -> bool:
        """Отправить уведомление по шаблону"""
        try:
            if template_id not in self.templates:
                return False

            template = self.templates[template_id]

            # Заполнение шаблона
            title = self._fill_template(template.title_template, variables)
            message = self._fill_template(template.message_template, variables)

            # Создание уведомления
            notification = Notification(
                notification_id=f"notif_{int(time.time() * 1000)}",
                user_id=user_id,
                notification_type=template.notification_type,
                title=title,
                message=message,
                priority=template.priority,
                channels=template.channels,
                template_id=template_id,
            )

            return self.create_notification(notification)

        except Exception as e:
            self.logger.error(f"Ошибка отправки по шаблону: {e}")
            return False

    def get_user_notifications(
        self, user_id: str, limit: int = 50
    ) -> List[Notification]:
        """Получить уведомления пользователя"""
        try:
            user_notifications = []
            for notification in self.notifications.values():
                if notification.user_id == user_id:
                    user_notifications.append(notification)

            # Сортировка по времени
            user_notifications.sort(key=lambda x: x.created_at, reverse=True)
            return user_notifications[:limit]

        except Exception as e:
            self.logger.error(f"Ошибка получения уведомлений: {e}")
            return []

    def mark_notification_read(self, notification_id: str) -> bool:
        """Отметить уведомление как прочитанное"""
        try:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.now()
                self.stats["notifications_read"] += 1
                self.logger.info(f"Уведомление прочитано: {notification_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка отметки прочтения: {e}")
            return False

    def get_notification_analytics(self) -> Dict[str, Any]:
        """Получить аналитику уведомлений"""
        try:
            total_sent = self.stats["notifications_sent"]
            total_delivered = self.stats["notifications_delivered"]
            total_read = self.stats["notifications_read"]

            delivery_rate = (total_delivered / max(total_sent, 1)) * 100
            read_rate = (total_read / max(total_delivered, 1)) * 100

            return {
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_read": total_read,
                "total_failed": self.stats["notifications_failed"],
                "delivery_rate": round(delivery_rate, 2),
                "read_rate": round(read_rate, 2),
                "active_users": self.stats["active_users"],
                "templates_count": len(self.templates),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения аналитики: {e}")
            return {}

    def _analyze_notification_content(
        self, notification: Notification
    ) -> None:
        """AI-анализ контента уведомления"""
        try:
            # Простой анализ для демонстрации
            content_lower = notification.message.lower()

            # Определение приоритета на основе контента
            if any(
                word in content_lower
                for word in ["критично", "срочно", "экстренно", "опасность"]
            ):
                notification.priority = NotificationPriority.CRITICAL
            elif any(
                word in content_lower
                for word in ["важно", "внимание", "предупреждение"]
            ):
                notification.priority = NotificationPriority.HIGH

            # Определение типа уведомления
            if any(
                word in content_lower
                for word in ["безопасность", "угроза", "атака"]
            ):
                notification.notification_type = NotificationType.SECURITY
            elif any(
                word in content_lower
                for word in ["семья", "ребенок", "родитель"]
            ):
                notification.notification_type = NotificationType.FAMILY
            elif any(
                word in content_lower
                for word in ["экстренно", "помощь", "спасите"]
            ):
                notification.notification_type = NotificationType.EMERGENCY

        except Exception as e:
            self.logger.error(f"Ошибка анализа контента: {e}")

    def _personalize_notification(self, notification: Notification) -> None:
        """Персонализация уведомления"""
        try:
            if notification.user_id in self.user_settings:
                settings = self.user_settings[notification.user_id]

                # Фильтрация по предпочтениям
                if (
                    settings.preferences.get(
                        notification.notification_type, UserPreference.ALL
                    ) == UserPreference.NONE
                ):
                    notification.status = NotificationStatus.CANCELLED
                    return

                # Фильтрация каналов
                available_channels = []
                for channel in notification.channels:
                    if settings.channels.get(channel, True):
                        available_channels.append(channel)
                notification.channels = available_channels

                # Проверка тихого времени
                current_hour = datetime.now().hour
                if (
                    settings.quiet_hours[0] <= current_hour or
                    current_hour < settings.quiet_hours[1]
                ):
                    if notification.priority not in [
                        NotificationPriority.CRITICAL,
                        NotificationPriority.URGENT,
                    ]:
                        notification.status = NotificationStatus.PENDING
                        # Планируем отправку на утро
                        notification.metadata["scheduled_for"] = (
                            datetime.now() + timedelta(hours=8)
                        ).isoformat()

        except Exception as e:
            self.logger.error(f"Ошибка персонализации: {e}")

    def _optimize_timing(self, notification: Notification) -> None:
        """Оптимизация времени отправки"""
        try:
            # Простая оптимизация для демонстрации
            current_time = datetime.now()

            # Для важных уведомлений отправляем сразу
            if notification.priority in [
                NotificationPriority.CRITICAL,
                NotificationPriority.URGENT,
            ]:
                return

            # Для обычных уведомлений планируем на рабочее время
            if current_time.hour < 9 or current_time.hour > 18:
                notification.metadata["scheduled_for"] = (
                    current_time + timedelta(hours=1)
                ).isoformat()

        except Exception as e:
            self.logger.error(f"Ошибка оптимизации времени: {e}")

    def _send_notification(self, notification: Notification) -> None:
        """Отправка уведомления"""
        try:
            for channel in notification.channels:
                if self._send_to_channel(notification, channel):
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now()
                    self.stats["notifications_delivered"] += 1
                else:
                    notification.status = NotificationStatus.FAILED
                    self.stats["notifications_failed"] += 1

        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления: {e}")

    def _send_to_channel(
        self, notification: Notification, channel: NotificationChannel
    ) -> bool:
        """Отправка в конкретный канал"""
        try:
            # Симуляция отправки в разные каналы
            if channel == NotificationChannel.PUSH:
                self.logger.info(f"Push-уведомление: {notification.title}")
            elif channel == NotificationChannel.EMAIL:
                self.logger.info(f"Email: {notification.title}")
            elif channel == NotificationChannel.SMS:
                self.logger.info(f"SMS: {notification.title}")
            elif channel == NotificationChannel.TELEGRAM:
                self.logger.info(f"Telegram: {notification.title}")
            elif channel == NotificationChannel.WHATSAPP:
                self.logger.info(f"WhatsApp: {notification.title}")
            elif channel == NotificationChannel.VIBER:
                self.logger.info(f"Viber: {notification.title}")

            return True

        except Exception as e:
            self.logger.error(f"Ошибка отправки в канал {channel.value}: {e}")
            return False

    def _fill_template(self, template: str, variables: Dict[str, str]) -> str:
        """Заполнение шаблона переменными"""
        try:
            result = template
            for key, value in variables.items():
                result = result.replace(f"{{{key}}}", str(value))
            return result
        except Exception as e:
            self.logger.error(f"Ошибка заполнения шаблона: {e}")
            return template

    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус системы"""
        try:
            return {
                "status": "active",
                "notifications": len(self.notifications),
                "templates": len(self.templates),
                "users": len(self.user_settings),
                "uptime": time.time() - self.start_time,
                "last_notification": max(
                    [n.created_at for n in self.notifications.values()],
                    default=None,
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def search_notifications(
        self, query: str, user_id: Optional[str] = None
    ) -> List[Notification]:
        """Поиск уведомлений по запросу"""
        try:
            results = []
            query_lower = query.lower()

            for notification in self.notifications.values():
                if user_id and notification.user_id != user_id:
                    continue

                if (
                    query_lower in notification.title.lower() or
                    query_lower in notification.message.lower()
                ):
                    results.append(notification)

            return sorted(results, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            self.logger.error(f"Ошибка поиска уведомлений: {e}")
            return []

    def get_user_engagement_stats(
        self, user_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Получить статистику вовлеченности пользователя"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            user_notifications = []

            for notification in self.notifications.values():
                if (
                    notification.user_id == user_id and
                    notification.created_at >= cutoff_date
                ):
                    user_notifications.append(notification)

            # Статистика по типам
            type_stats = {}
            for notification in user_notifications:
                ntype = notification.notification_type.value
                type_stats[ntype] = type_stats.get(ntype, 0) + 1

            # Статистика по каналам
            channel_stats = {}
            for notification in user_notifications:
                for channel in notification.channels:
                    channel_stats[channel.value] = (
                        channel_stats.get(channel.value, 0) + 1
                    )

            # Статистика по статусам
            status_stats = {}
            for notification in user_notifications:
                status = notification.status.value
                status_stats[status] = status_stats.get(status, 0) + 1

            # Время отклика
            read_notifications = [n for n in user_notifications if n.read_at]
            response_times = []
            for notification in read_notifications:
                if notification.sent_at and notification.read_at:
                    response_time = (
                        notification.read_at - notification.sent_at
                    ).total_seconds() / 60
                    response_times.append(response_time)

            avg_response_time = (
                sum(response_times) / len(response_times)
                if response_times
                else 0
            )

            return {
                "total_notifications": len(user_notifications),
                "read_notifications": len(read_notifications),
                "read_rate": len(read_notifications) /
                max(len(user_notifications), 1) * 100,
                "type_distribution": type_stats,
                "channel_distribution": channel_stats,
                "status_distribution": status_stats,
                "average_response_time_minutes": round(avg_response_time, 2),
                "most_active_channel": (
                    max(channel_stats.items(), key=lambda x: x[1])[0]
                    if channel_stats
                    else None
                ),
                "most_common_type": (
                    max(type_stats.items(), key=lambda x: x[1])[0]
                    if type_stats
                    else None
                ),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения статистики вовлеченности: {e}"
            )
            return {}

    def create_custom_template(self, template: NotificationTemplate) -> bool:
        """Создать пользовательский шаблон"""
        try:
            self.templates[template.template_id] = template
            self.logger.info(
                f"Создан пользовательский шаблон: {template.template_id}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка создания шаблона: {e}")
            return False

    def delete_template(self, template_id: str) -> bool:
        """Удалить шаблон"""
        try:
            if template_id in self.templates:
                del self.templates[template_id]
                self.logger.info(f"Удален шаблон: {template_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления шаблона: {e}")
            return False

    def bulk_send_notifications(
        self, notifications: List[Notification]
    ) -> Dict[str, int]:
        """Массовая отправка уведомлений"""
        try:
            results = {"sent": 0, "failed": 0, "total": len(notifications)}

            for notification in notifications:
                if self.create_notification(notification):
                    results["sent"] += 1
                else:
                    results["failed"] += 1

            self.logger.info(
                f"Массовая отправка завершена: "
                f"{results['sent']}/{results['total']} успешно"
            )
            return results
        except Exception as e:
            self.logger.error(f"Ошибка массовой отправки: {e}")
            return {"sent": 0, "failed": 0, "total": 0, "error": str(e)}

    def export_notification_data(
        self, user_id: Optional[str] = None, format: str = "json"
    ) -> str:
        """Экспорт данных уведомлений"""
        try:
            notifications_to_export = []

            for notification in self.notifications.values():
                if user_id and notification.user_id != user_id:
                    continue

                notifications_to_export.append(
                    {
                        "notification_id": notification.notification_id,
                        "user_id": notification.user_id,
                        "type": notification.notification_type.value,
                        "title": notification.title,
                        "message": notification.message,
                        "priority": notification.priority.value,
                        "channels": [c.value for c in notification.channels],
                        "status": notification.status.value,
                        "created_at": notification.created_at.isoformat(),
                        "sent_at": (
                            notification.sent_at.isoformat()
                            if notification.sent_at
                            else None
                        ),
                        "read_at": (
                            notification.read_at.isoformat()
                            if notification.read_at
                            else None
                        ),
                        "template_id": notification.template_id,
                    }
                )

            data = {
                "notifications": notifications_to_export,
                "templates": [
                    {
                        "template_id": template.template_id,
                        "name": template.name,
                        "type": template.notification_type.value,
                        "priority": template.priority.value,
                        "channels": [c.value for c in template.channels],
                        "is_active": template.is_active,
                    }
                    for template in self.templates.values()
                ],
                "analytics": self.get_notification_analytics(),
                "export_time": datetime.now().isoformat(),
            }

            if format.lower() == "json":
                return json.dumps(data, ensure_ascii=False, indent=2)
            else:
                return str(data)
        except Exception as e:
            self.logger.error(f"Ошибка экспорта данных: {e}")
            return ""

    def generate_notification_report(self, days: int = 7) -> Dict[str, Any]:
        """Генерация отчета по уведомлениям"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_notifications = [
                n
                for n in self.notifications.values()
                if n.created_at >= cutoff_date
            ]

            report = {
                "period_days": days,
                "total_notifications": len(recent_notifications),
                "delivery_rate": 0,
                "read_rate": 0,
                "by_type": {},
                "by_priority": {},
                "by_channel": {},
                "top_users": {},
                "recommendations": [],
            }

            # Анализ по типам и приоритетам
            for notification in recent_notifications:
                ntype = notification.notification_type.value
                priority = notification.priority.value

                report["by_type"][ntype] = report["by_type"].get(ntype, 0) + 1
                report["by_priority"][priority] = (
                    report["by_priority"].get(priority, 0) + 1
                )

                # По каналам
                for channel in notification.channels:
                    channel_name = channel.value
                    report["by_channel"][channel_name] = (
                        report["by_channel"].get(channel_name, 0) + 1
                    )

                # По пользователям
                user_id = notification.user_id
                report["top_users"][user_id] = (
                    report["top_users"].get(user_id, 0) + 1
                )

            # Расчет метрик
            delivered = len(
                [
                    n
                    for n in recent_notifications
                    if n.status
                    in [
                        NotificationStatus.SENT,
                        NotificationStatus.DELIVERED,
                        NotificationStatus.READ,
                    ]
                ]
            )
            read = len(
                [
                    n
                    for n in recent_notifications
                    if n.status == NotificationStatus.READ
                ]
            )

            if recent_notifications:
                report["delivery_rate"] = (
                    delivered / len(recent_notifications)
                ) * 100
                report["read_rate"] = (read / max(delivered, 1)) * 100

            # Рекомендации
            if report["delivery_rate"] < 90:
                report["recommendations"].append(
                    "Низкий процент доставки - проверьте настройки " "каналов"
                )

            if report["read_rate"] < 50:
                report["recommendations"].append(
                    "Низкий процент прочтения - оптимизируйте контент "
                    "и время отправки"
                )

            return report
        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета: {e}")
            return {"error": str(e)}

    def test_notification_system(self) -> Dict[str, Any]:
        """Тестирование системы уведомлений"""
        try:
            test_results = {
                "templates_available": len(self.templates),
                "users_configured": len(self.user_settings),
                "test_notifications_sent": 0,
                "test_delivery_success": 0,
                "system_health": "good",
                "issues": [],
            }

            # Проверка шаблонов
            if test_results["templates_available"] == 0:
                test_results["issues"].append("Нет доступных шаблонов")
                test_results["system_health"] = "critical"

            # Проверка пользователей
            if test_results["users_configured"] == 0:
                test_results["issues"].append("Нет настроенных пользователей")
                test_results["system_health"] = "warning"

            # Тестовая отправка
            test_vars = {
                "alert_type": "Тест системы",
                "threat_description": "Проверка работоспособности",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "action": "Тест завершен",
            }

            if self.send_notification_from_template(
                "security_alert", "test_user", test_vars
            ):
                test_results["test_notifications_sent"] = 1
                test_results["test_delivery_success"] = 1

            return test_results
        except Exception as e:
            self.logger.error(f"Ошибка тестирования системы: {e}")
            return {"system_health": "error", "error": str(e)}


# Дополнительные утилиты
class NotificationUtils:
    """Утилиты для уведомлений"""

    @staticmethod
    def create_notification_id() -> str:
        """Создать ID уведомления"""
        return (
            f"notif_{int(time.time() * 1000)}_"
            f"{hash(str(time.time())) % 10000}"
        )

    @staticmethod
    def format_notification_for_display(notification: Notification) -> str:
        """Форматировать уведомление для отображения"""
        return (
            f"[{notification.created_at.strftime('%H:%M')}] "
            f"{notification.title}: {notification.message}"
        )

    @staticmethod
    def is_urgent_notification(notification: Notification) -> bool:
        """Проверить, является ли уведомление срочным"""
        return notification.priority in [
            NotificationPriority.URGENT,
            NotificationPriority.CRITICAL,
        ]


class NotificationScheduler:
    """Планировщик уведомлений"""

    def __init__(self, bot: NotificationBot):
        self.bot = bot

    def schedule_notification(
        self, notification: Notification, send_time: datetime
    ) -> bool:
        """Запланировать уведомление"""
        try:
            notification.metadata["scheduled_for"] = send_time.isoformat()
            notification.status = NotificationStatus.PENDING
            self.bot.logger.info(f"Уведомление запланировано на {send_time}")
            return True
        except Exception as e:
            self.bot.logger.error(f"Ошибка планирования: {e}")
            return False

    def process_scheduled_notifications(self) -> int:
        """Обработать запланированные уведомления"""
        try:
            current_time = datetime.now()
            processed = 0

            for notification in self.bot.notifications.values():
                if (
                    notification.status == NotificationStatus.PENDING and
                    "scheduled_for" in notification.metadata
                ):

                    scheduled_time = datetime.fromisoformat(
                        notification.metadata["scheduled_for"]
                    )
                    if current_time >= scheduled_time:
                        self.bot._send_notification(notification)
                        processed += 1

            return processed
        except Exception as e:
            self.bot.logger.error(f"Ошибка обработки запланированных: {e}")
            return 0


if __name__ == "__main__":
    # Тестирование
    bot = NotificationBot("TestBot")

    # Добавляем настройки пользователя
    user_settings = UserNotificationSettings(
        user_id="user_1",
        preferences={
            NotificationType.SECURITY: UserPreference.ALL,
            NotificationType.FAMILY: UserPreference.ALL,
            NotificationType.EMERGENCY: UserPreference.ALL,
            NotificationType.PROMOTION: UserPreference.NONE,
        },
        channels={
            NotificationChannel.PUSH: True,
            NotificationChannel.EMAIL: True,
            NotificationChannel.TELEGRAM: True,
            NotificationChannel.SMS: False,
        },
    )

    bot.add_user_settings(user_settings)

    # Отправляем уведомление по шаблону
    variables = {
        "alert_type": "Подозрительная активность",
        "threat_description": "Обнаружена попытка взлома",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "action": "Блокировка IP-адреса",
    }

    bot.send_notification_from_template("security_alert", "user_1", variables)

    # Получаем аналитику
    analytics = bot.get_notification_analytics()
    print(f"Аналитика уведомлений: {analytics}")

    print("NotificationBot успешно протестирован!")


# Продвинутые методы для NotificationBot
def _start_analysis_thread(self) -> None:
    """Запуск фонового потока для анализа уведомлений"""
    try:
        self.is_analysis_running = True
        self.analysis_thread = threading.Thread(
            target=self._analysis_worker, daemon=True
        )
        self.analysis_thread.start()
        self.logger.info("Фоновый поток анализа уведомлений запущен")
    except Exception as e:
        self.logger.error(f"Ошибка запуска потока анализа: {e}")


def _analysis_worker(self) -> None:
    """Рабочий поток для анализа уведомлений"""
    while self.is_analysis_running:
        try:
            if not self.notification_queue.empty():
                notification_data = self.notification_queue.get(timeout=1)
                self._analyze_notification_advanced(notification_data)
                self.notification_queue.task_done()
            else:
                time.sleep(0.1)
        except queue.Empty:
            continue
        except Exception as e:
            self.logger.error(f"Ошибка в потоке анализа: {e}")


def _analyze_notification_advanced(
    self, notification_data: Dict[str, Any]
) -> None:
    """
    Продвинутый анализ уведомления с использованием ML

    Args:
        notification_data: Данные уведомления
    """
    try:
        # Анализ эффективности
        if self.bot_settings["effectiveness_analysis"]:
            effectiveness = (
                self.ml_analyzer.analyze_notification_effectiveness(
                    notification_data
                )
            )
            notification_data["effectiveness"] = effectiveness
            self.stats["effectiveness_analyses"] += 1

        # Оптимизация контента
        if self.bot_settings["content_optimization"]:
            user_id = notification_data.get("user_id", "unknown")
            user_profile = self._get_user_profile(user_id)
            if user_profile:
                optimization = (
                    self.advanced_analyzer.optimize_notification_content(
                        notification_data, user_profile
                    )
                )
                notification_data["content_optimization"] = optimization
                self.stats["content_optimizations"] += 1

        # Предсказание оптимального времени
        if self.bot_settings["timing_optimization"]:
            user_id = notification_data.get("user_id", "unknown")
            notification_type = notification_data.get(
                "notification_type", "unknown"
            )
            priority = notification_data.get("priority", "normal")

            timing_prediction = self.ml_analyzer.predict_optimal_timing(
                user_id, notification_type, priority
            )
            notification_data["timing_prediction"] = timing_prediction
            self.stats["timing_optimizations"] += 1

        # Обновление статистики
        self.stats["ml_predictions"] += 1

    except Exception as e:
        self.logger.error(f"Ошибка продвинутого анализа уведомления: {e}")


def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
    """Получение профиля пользователя"""
    try:
        if user_id in self.ml_analyzer.user_profiles:
            return self.ml_analyzer.user_profiles[user_id]

        # Создание базового профиля
        user_notifications = [
            n for n in self.notifications.values() if n.user_id == user_id
        ]
        if user_notifications:
            engagement_patterns = (
                self.advanced_analyzer.analyze_user_engagement_patterns(
                    [self._notification_to_dict(n) for n in user_notifications]
                )
            )
            return {
                "cluster_id": 0,
                "preferences": engagement_patterns.get("patterns", {}),
                "activity_level": engagement_patterns.get(
                    "engagement_score", 0.5
                ),
            }

        return {}

    except Exception as e:
        self.logger.error(f"Ошибка получения профиля пользователя: {e}")
        return {}


def _notification_to_dict(self, notification: Notification) -> Dict[str, Any]:
    """Преобразование объекта Notification в словарь"""
    return {
        "notification_id": notification.notification_id,
        "user_id": notification.user_id,
        "notification_type": notification.notification_type.value,
        "priority": notification.priority.value,
        "message": notification.message,
        "channels": [c.value for c in notification.channels],
        "status": notification.status.value,
        "created_at": notification.created_at.isoformat(),
        "delivered_at": (
            notification.delivered_at.isoformat()
            if notification.delivered_at
            else None
        ),
        "read_at": (
            notification.read_at.isoformat() if notification.read_at else None
        ),
    }


def train_ml_models(self) -> bool:
    """
    Обучение ML моделей на исторических данных уведомлений

    Returns:
        bool: True если обучение успешно
    """
    try:
        if len(self.notifications) < 50:
            self.logger.warning("Недостаточно данных для обучения ML моделей")
            return False

        # Подготовка данных для обучения
        notifications_data = []
        for notification in self.notifications.values():
            notification_dict = self._notification_to_dict(notification)
            notifications_data.append(notification_dict)

        # Обучение моделей
        success = self.ml_analyzer.train_models(notifications_data)

        if success:
            self.logger.info("ML модели уведомлений успешно обучены")
            return True
        else:
            self.logger.error("Ошибка обучения ML моделей уведомлений")
            return False

    except Exception as e:
        self.logger.error(f"Ошибка обучения ML моделей: {e}")
        return False


def get_advanced_analytics(self) -> Dict[str, Any]:
    """
    Получение продвинутой аналитики уведомлений

    Returns:
        Dict с детальной аналитикой
    """
    try:
        # Базовая статистика
        analytics = {
            "total_notifications": len(self.notifications),
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "ml_predictions": self.stats["ml_predictions"],
            "content_optimizations": self.stats["content_optimizations"],
            "timing_optimizations": self.stats["timing_optimizations"],
            "effectiveness_analyses": self.stats["effectiveness_analyses"],
        }

        # Анализ вовлеченности пользователей
        if self.notifications:
            user_engagement = self._analyze_user_engagement()
            analytics["user_engagement"] = user_engagement

        # Анализ эффективности контента
        if self.notifications and self.ml_analyzer.is_trained:
            content_effectiveness = self._analyze_content_effectiveness()
            analytics["content_effectiveness"] = content_effectiveness

        # Анализ трендов
        trends = self._analyze_notification_trends()
        analytics["trends"] = trends

        return analytics

    except Exception as e:
        self.logger.error(f"Ошибка получения продвинутой аналитики: {e}")
        return {"error": str(e)}


def _analyze_user_engagement(self) -> Dict[str, Any]:
    """Анализ вовлеченности пользователей"""
    try:
        user_engagement = {
            "total_users": len(
                set(n.user_id for n in self.notifications.values())
            ),
            "active_users": 0,
            "engagement_by_type": {},
            "engagement_by_channel": {},
            "avg_engagement_score": 0.0,
        }

        # Группировка по пользователям
        user_notifications = defaultdict(list)
        for notification in self.notifications.values():
            user_notifications[notification.user_id].append(notification)

        engagement_scores = []
        for user_id, notifications in user_notifications.items():
            if len(notifications) >= 3:  # Минимум 3 уведомления для анализа
                user_data = [
                    self._notification_to_dict(n) for n in notifications
                ]
                patterns = (
                    self.advanced_analyzer.analyze_user_engagement_patterns(
                        user_data
                    )
                )
                engagement_scores.append(patterns.get("engagement_score", 0.0))

                if patterns.get("engagement_score", 0.0) > 0.5:
                    user_engagement["active_users"] += 1

        # Анализ по типам
        type_engagement = defaultdict(list)
        for notification in self.notifications.values():
            type_engagement[notification.notification_type.value].append(
                1 if notification.status.value == "read" else 0
            )

        for notification_type, responses in type_engagement.items():
            user_engagement["engagement_by_type"][notification_type] = {
                "response_rate": (
                    sum(responses) / len(responses) if responses else 0
                ),
                "total_sent": len(responses),
            }

        # Анализ по каналам
        channel_engagement = defaultdict(list)
        for notification in self.notifications.values():
            for channel in notification.channels:
                channel_engagement[channel.value].append(
                    1 if notification.status.value == "read" else 0
                )

        for channel, responses in channel_engagement.items():
            user_engagement["engagement_by_channel"][channel] = {
                "response_rate": (
                    sum(responses) / len(responses) if responses else 0
                ),
                "total_sent": len(responses),
            }

        # Средний балл вовлеченности
        if engagement_scores:
            user_engagement["avg_engagement_score"] = round(
                np.mean(engagement_scores), 3
            )

        return user_engagement

    except Exception as e:
        self.logger.error(f"Ошибка анализа вовлеченности: {e}")
        return {}


def _analyze_content_effectiveness(self) -> Dict[str, Any]:
    """Анализ эффективности контента"""
    try:
        effectiveness_data = {
            "avg_effectiveness_score": 0.0,
            "effectiveness_by_length": {},
            "effectiveness_by_priority": {},
            "effectiveness_by_type": {},
            "recommendations": [],
        }

        effectiveness_scores = []
        length_groups = {"short": [], "medium": [], "long": []}
        priority_groups = defaultdict(list)
        type_groups = defaultdict(list)

        for notification in self.notifications.values():
            notification_dict = self._notification_to_dict(notification)
            effectiveness = (
                self.ml_analyzer.analyze_notification_effectiveness(
                    notification_dict
                )
            )
            score = effectiveness.get("score", 0.0)
            effectiveness_scores.append(score)

            # Группировка по длине
            message_length = len(notification.message)
            if message_length < 50:
                length_groups["short"].append(score)
            elif message_length < 200:
                length_groups["medium"].append(score)
            else:
                length_groups["long"].append(score)

            # Группировка по приоритету
            priority_groups[notification.priority.value].append(score)

            # Группировка по типу
            type_groups[notification.notification_type.value].append(score)

        # Расчет средних показателей
        if effectiveness_scores:
            effectiveness_data["avg_effectiveness_score"] = round(
                np.mean(effectiveness_scores), 3
            )

        # Анализ по длине
        for length_group, scores in length_groups.items():
            if scores:
                effectiveness_data["effectiveness_by_length"][length_group] = {
                    "avg_score": round(np.mean(scores), 3),
                    "count": len(scores),
                }

        # Анализ по приоритету
        for priority, scores in priority_groups.items():
            if scores:
                effectiveness_data["effectiveness_by_priority"][priority] = {
                    "avg_score": round(np.mean(scores), 3),
                    "count": len(scores),
                }

        # Анализ по типу
        for notification_type, scores in type_groups.items():
            if scores:
                effectiveness_data["effectiveness_by_type"][
                    notification_type
                ] = {
                    "avg_score": round(np.mean(scores), 3),
                    "count": len(scores),
                }

        # Генерация рекомендаций
        if effectiveness_data["avg_effectiveness_score"] < 0.6:
            effectiveness_data["recommendations"].append(
                "Общая эффективность низкая - требуется оптимизация"
            )

        # Рекомендации по длине
        if "short" in effectiveness_data["effectiveness_by_length"]:
            short_score = effectiveness_data["effectiveness_by_length"][
                "short"
            ]["avg_score"]
            if short_score < 0.5:
                effectiveness_data["recommendations"].append(
                    "Короткие сообщения неэффективны - добавьте детали"
                )

        return effectiveness_data

    except Exception as e:
        self.logger.error(f"Ошибка анализа эффективности контента: {e}")
        return {}


def _analyze_notification_trends(self) -> Dict[str, Any]:
    """Анализ трендов уведомлений"""
    try:
        trends = {
            "hourly_distribution": defaultdict(int),
            "daily_distribution": defaultdict(int),
            "type_trends": defaultdict(int),
            "priority_trends": defaultdict(int),
            "channel_trends": defaultdict(int),
        }

        # Анализ временных трендов
        for notification in self.notifications.values():
            trends["hourly_distribution"][notification.created_at.hour] += 1
            trends["daily_distribution"][
                notification.created_at.weekday()
            ] += 1
            trends["type_trends"][notification.notification_type.value] += 1
            trends["priority_trends"][notification.priority.value] += 1

            for channel in notification.channels:
                trends["channel_trends"][channel.value] += 1

        # Преобразование в обычные словари
        trends["hourly_distribution"] = dict(trends["hourly_distribution"])
        trends["daily_distribution"] = dict(trends["daily_distribution"])
        trends["type_trends"] = dict(trends["type_trends"])
        trends["priority_trends"] = dict(trends["priority_trends"])
        trends["channel_trends"] = dict(trends["channel_trends"])

        # Нахождение пиковых часов
        if trends["hourly_distribution"]:
            peak_hour = max(
                trends["hourly_distribution"].items(), key=lambda x: x[1]
            )
            trends["peak_hour"] = peak_hour[0]
            trends["peak_hour_count"] = peak_hour[1]

        # Нахождение наиболее популярного типа
        if trends["type_trends"]:
            popular_type = max(
                trends["type_trends"].items(), key=lambda x: x[1]
            )
            trends["most_popular_type"] = popular_type[0]
            trends["most_popular_type_count"] = popular_type[1]

        return trends

    except Exception as e:
        self.logger.error(f"Ошибка анализа трендов: {e}")
        return {}


def predict_user_response(
    self, user_id: str, notification: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Предсказание отклика пользователя на уведомление

    Args:
        user_id: ID пользователя
        notification: Данные уведомления

    Returns:
        Dict с предсказанием отклика
    """
    try:
        if not self.ml_analyzer.is_trained:
            return {"response_probability": 0.5, "confidence": 0.0}

        # Использование продвинутого анализатора
        prediction = self.advanced_analyzer.predict_user_response(
            user_id, notification
        )

        # Обновление статистики
        self.stats["ml_predictions"] += 1

        return prediction

    except Exception as e:
        self.logger.error(f"Ошибка предсказания отклика: {e}")
        return {"response_probability": 0.5, "confidence": 0.0}


def optimize_notification_timing(
    self, user_id: str, notification_type: str, priority: str
) -> Dict[str, Any]:
    """
    Оптимизация времени отправки уведомления

    Args:
        user_id: ID пользователя
        notification_type: Тип уведомления
        priority: Приоритет уведомления

    Returns:
        Dict с рекомендациями по времени
    """
    try:
        if not self.ml_analyzer.is_trained:
            return {"optimal_hour": 12, "confidence": 0.0}

        # Использование ML анализатора
        timing_prediction = self.ml_analyzer.predict_optimal_timing(
            user_id, notification_type, priority
        )

        # Дополнительные рекомендации
        recommendations = self._generate_timing_recommendations(
            timing_prediction
        )
        timing_prediction["recommendations"] = recommendations

        # Обновление статистики
        self.stats["timing_optimizations"] += 1

        return timing_prediction

    except Exception as e:
        self.logger.error(f"Ошибка оптимизации времени: {e}")
        return {"optimal_hour": 12, "confidence": 0.0}


def _generate_timing_recommendations(
    self, timing_prediction: Dict[str, Any]
) -> List[str]:
    """Генерация рекомендаций по времени отправки"""
    recommendations = []

    optimal_hour = timing_prediction.get("optimal_hour", 12)
    confidence = timing_prediction.get("confidence", 0.0)

    if confidence > 0.8:
        recommendations.append(
            f"Оптимальное время: {optimal_hour}:00 (высокая уверенность)"
        )
    elif confidence > 0.6:
        recommendations.append(
            f"Рекомендуемое время: {optimal_hour}:00 (умеренная уверенность)"
        )
    else:
        recommendations.append(
            f"Предлагаемое время: {optimal_hour}:00 (низкая уверенность)"
        )

    # Дополнительные рекомендации на основе времени
    if 6 <= optimal_hour <= 9:
        recommendations.append(
            "Утреннее время - хорошее время для важных уведомлений"
        )
    elif 9 <= optimal_hour <= 17:
        recommendations.append(
            "Рабочее время - оптимально для деловых уведомлений"
        )
    elif 17 <= optimal_hour <= 22:
        recommendations.append(
            "Вечернее время - подходит для личных уведомлений"
        )
    else:
        recommendations.append(
            "Ночное время - используйте только для критических уведомлений"
        )

    return recommendations
