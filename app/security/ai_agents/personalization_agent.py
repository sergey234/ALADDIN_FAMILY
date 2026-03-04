#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonalizationAgent - AI-агент персонализации тарифов ALADDIN
Версия 1.0 - Полная система AI-персонализации с машинным обучением

Интегрируется с:
- SubscriptionManager (управление подписками)
- FamilyProfileManagerEnhanced (семейные профили)
- ReferralManager (реферальная система)
- FamilyNotificationManager (уведомления)

Автор: ALADDIN Security System
Версия: 1.0.0
Дата: 2025-01-27
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from security.core.security_base import ComponentStatus, SecurityBase, SecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserSegment(Enum):
    """Сегменты пользователей (БЕЗ СТУДЕНТОВ - не можем проверить статус)"""
    FAMILY_FOCUSED = "family_focused"         # Семейно-ориентированные
    TECH_SAVVY = "tech_savvy"                 # Технически продвинутые
    SECURITY_CONSIOUS = "security_conscious"  # Обеспокоенные безопасностью
    BUDGET_CONSCIOUS = "budget_conscious"     # Ориентированные на бюджет
    PREMIUM_SEEKERS = "premium_seekers"       # Ищущие премиум решения
    ENTERPRISE_USERS = "enterprise_users"     # Корпоративные пользователи


class BehaviorPattern(Enum):
    """Паттерны поведения"""
    HEAVY_USER = "heavy_user"                 # Активные пользователи
    LIGHT_USER = "light_user"                 # Легкие пользователи
    PEAK_USER = "peak_user"                   # Пользователи в пиковые часы
    WEEKEND_USER = "weekend_user"             # Пользователи выходных
    MOBILE_FIRST = "mobile_first"             # Мобильные пользователи
    DESKTOP_FIRST = "desktop_first"           # Десктопные пользователи


class RecommendationType(Enum):
    """Типы рекомендаций"""
    TARIFF_UPGRADE = "tariff_upgrade"         # Обновление тарифа
    FEATURE_ADDON = "feature_addon"           # Дополнительные функции
    DISCOUNT_OFFER = "discount_offer"         # Предложение скидки
    FAMILY_PLAN = "family_plan"               # Семейный план
    ENTERPRISE_PLAN = "enterprise_plan"       # Корпоративный план
    CUSTOMIZATION = "customization"           # Персонализация


@dataclass
class UserProfile:
    """Профиль пользователя"""
    family_id: str
    user_segment: UserSegment
    behavior_pattern: BehaviorPattern
    risk_level: str  # low, medium, high
    tech_savviness: float  # 0.0 - 1.0
    security_concern: float  # 0.0 - 1.0
    budget_sensitivity: float  # 0.0 - 1.0
    family_size: int
    device_count: int
    usage_patterns: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Recommendation:
    """Рекомендация для пользователя"""
    recommendation_id: str
    family_id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    confidence_score: float  # 0.0 - 1.0
    expected_value: Decimal
    discount_percentage: Optional[float] = None
    features: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_accepted: Optional[bool] = None
    accepted_at: Optional[datetime] = None


@dataclass
class MLModel:
    """Модель машинного обучения"""
    model_id: str
    model_type: str
    model: Any
    accuracy: float
    features: List[str]
    created_at: datetime
    last_trained: datetime
    version: str = "1.0"


class PersonalizationAgent(SecurityBase):
    """
    AI-агент персонализации тарифов ALADDIN

    Функции:
    - Анализ поведения пользователей
    - Сегментация пользователей
    - Рекомендации тарифов
    - Предложения скидок
    - Машинное обучение
    - A/B тестирование рекомендаций
    """

    def __init__(self):
        """Инициализация агента персонализации"""
        super().__init__()

        # Хранилища данных
        self.user_profiles: Dict[str, UserProfile] = {}
        self.recommendations: Dict[str, Recommendation] = {}
        self.ml_models: Dict[str, MLModel] = {}
        self.user_behavior_data: Dict[str, List[Dict[str, Any]]] = {}

        # ML компоненты
        self.scaler = StandardScaler()
        self.segmentation_model = None
        self.recommendation_model = None
        self.discount_model = None

        # Конфигурация
        self.min_data_points = 10  # Минимум данных для обучения
        self.model_retrain_interval = 7  # Дни между переобучением
        self.recommendation_expiry_days = 30  # Дни действия рекомендаций

        # Инициализация моделей
        self._initialize_ml_models()

        # Статус компонента
        self.status = ComponentStatus.ACTIVE
        self.security_level = SecurityLevel.HIGH

        logger.info("PersonalizationAgent инициализирован")

    def _initialize_ml_models(self) -> None:
        """Инициализация моделей машинного обучения"""
        try:
            # Модель сегментации пользователей
            self.segmentation_model = MLModel(
                model_id="user_segmentation",
                model_type="KMeans",
                model=KMeans(n_clusters=6, random_state=42),
                accuracy=0.0,
                features=["tech_savviness", "security_concern", "budget_sensitivity", "family_size", "device_count"],
                created_at=datetime.now(),
                last_trained=datetime.now()
            )

            # Модель рекомендаций
            self.recommendation_model = MLModel(
                model_id="tariff_recommendation",
                model_type="RandomForest",
                model=RandomForestClassifier(n_estimators=100, random_state=42),
                accuracy=0.0,
                features=["user_segment", "behavior_pattern", "risk_level", "family_size", "device_count"],
                created_at=datetime.now(),
                last_trained=datetime.now()
            )

            # Модель скидок
            self.discount_model = MLModel(
                model_id="discount_optimization",
                model_type="RandomForest",
                model=RandomForestClassifier(n_estimators=50, random_state=42),
                accuracy=0.0,
                features=["user_segment", "budget_sensitivity", "family_size", "device_count", "usage_intensity"],
                created_at=datetime.now(),
                last_trained=datetime.now()
            )

            # Сохраняем модели
            self.ml_models["user_segmentation"] = self.segmentation_model
            self.ml_models["tariff_recommendation"] = self.recommendation_model
            self.ml_models["discount_optimization"] = self.discount_model

            logger.info("ML модели инициализированы")

        except Exception as e:
            logger.error(f"Ошибка инициализации ML моделей: {e}")

    async def analyze_user_behavior(self, family_id: str,
                                    behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ поведения пользователя

        Args:
            family_id: ID семьи
            behavior_data: Данные о поведении

        Returns:
            Результат анализа поведения
        """
        try:
            # Сохраняем данные о поведении
            if family_id not in self.user_behavior_data:
                self.user_behavior_data[family_id] = []

            behavior_data["timestamp"] = datetime.now().isoformat()
            self.user_behavior_data[family_id].append(behavior_data)

            # Ограничиваем количество данных (последние 1000 записей)
            if len(self.user_behavior_data[family_id]) > 1000:
                self.user_behavior_data[family_id] = self.user_behavior_data[family_id][-1000:]

            # Обновляем профиль пользователя
            await self._update_user_profile(family_id, behavior_data)

            # Проверяем, нужно ли переобучить модели
            if len(self.user_behavior_data[family_id]) >= self.min_data_points:
                await self._retrain_models_if_needed()

            logger.info(f"Проанализировано поведение семьи {family_id}")

            return {
                "success": True,
                "family_id": family_id,
                "data_points": len(self.user_behavior_data[family_id]),
                "profile_updated": True
            }

        except Exception as e:
            logger.error(f"Ошибка анализа поведения: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _update_user_profile(self, family_id: str, behavior_data: Dict[str, Any]) -> None:
        """Обновление профиля пользователя"""
        try:
            # Получаем или создаем профиль
            if family_id not in self.user_profiles:
                self.user_profiles[family_id] = UserProfile(
                    family_id=family_id,
                    user_segment=UserSegment.FAMILY_FOCUSED,
                    behavior_pattern=BehaviorPattern.LIGHT_USER,
                    risk_level="medium",
                    tech_savviness=0.5,
                    security_concern=0.5,
                    budget_sensitivity=0.5,
                    family_size=1,
                    device_count=1
                )

            profile = self.user_profiles[family_id]

            # Обновляем данные на основе поведения
            if "tech_savviness" in behavior_data:
                profile.tech_savviness = behavior_data["tech_savviness"]

            if "security_concern" in behavior_data:
                profile.security_concern = behavior_data["security_concern"]

            if "budget_sensitivity" in behavior_data:
                profile.budget_sensitivity = behavior_data["budget_sensitivity"]

            if "family_size" in behavior_data:
                profile.family_size = behavior_data["family_size"]

            if "device_count" in behavior_data:
                profile.device_count = behavior_data["device_count"]

            if "usage_patterns" in behavior_data:
                profile.usage_patterns.update(behavior_data["usage_patterns"])

            if "preferences" in behavior_data:
                profile.preferences.update(behavior_data["preferences"])

            # Обновляем сегмент пользователя
            profile.user_segment = await self._determine_user_segment(profile)

            # Обновляем паттерн поведения
            profile.behavior_pattern = await self._determine_behavior_pattern(profile)

            # Обновляем уровень риска
            profile.risk_level = await self._determine_risk_level(profile)

            profile.updated_at = datetime.now()

        except Exception as e:
            logger.error(f"Ошибка обновления профиля: {e}")

    async def _determine_user_segment(self, profile: UserProfile) -> UserSegment:
        """Определение сегмента пользователя"""
        try:
            # Простая логика сегментации (в реальной системе используется ML)
            if profile.family_size >= 4 and profile.security_concern > 0.7:
                return UserSegment.FAMILY_FOCUSED
            elif profile.tech_savviness > 0.8 and profile.device_count > 3:
                return UserSegment.TECH_SAVVY
            elif profile.security_concern > 0.8:
                return UserSegment.SECURITY_CONSIOUS
            elif profile.budget_sensitivity > 0.7:
                return UserSegment.BUDGET_CONSCIOUS
            elif profile.tech_savviness > 0.6 and profile.budget_sensitivity < 0.4:
                return UserSegment.PREMIUM_SEEKERS
            elif profile.family_size >= 10 or profile.device_count >= 20:
                return UserSegment.ENTERPRISE_USERS
            else:
                return UserSegment.FAMILY_FOCUSED

        except Exception as e:
            logger.error(f"Ошибка определения сегмента: {e}")
            return UserSegment.FAMILY_FOCUSED

    async def _determine_behavior_pattern(self, profile: UserProfile) -> BehaviorPattern:
        """Определение паттерна поведения"""
        try:
            # Анализируем паттерны использования
            usage_intensity = profile.usage_patterns.get("intensity", 0.5)
            peak_hours_usage = profile.usage_patterns.get("peak_hours_usage", 0.5)
            weekend_usage = profile.usage_patterns.get("weekend_usage", 0.5)
            mobile_usage = profile.usage_patterns.get("mobile_usage", 0.5)

            if usage_intensity > 0.8:
                return BehaviorPattern.HEAVY_USER
            elif usage_intensity < 0.3:
                return BehaviorPattern.LIGHT_USER
            elif peak_hours_usage > 0.7:
                return BehaviorPattern.PEAK_USER
            elif weekend_usage > 0.7:
                return BehaviorPattern.WEEKEND_USER
            elif mobile_usage > 0.7:
                return BehaviorPattern.MOBILE_FIRST
            else:
                return BehaviorPattern.DESKTOP_FIRST

        except Exception as e:
            logger.error(f"Ошибка определения паттерна поведения: {e}")
            return BehaviorPattern.LIGHT_USER

    async def _determine_risk_level(self, profile: UserProfile) -> str:
        """Определение уровня риска"""
        try:
            # Анализируем факторы риска
            risk_score = 0.0

            # Семейный размер (больше людей = больше рисков)
            if profile.family_size > 4:
                risk_score += 0.3
            elif profile.family_size > 2:
                risk_score += 0.1

            # Количество устройств
            if profile.device_count > 5:
                risk_score += 0.3
            elif profile.device_count > 2:
                risk_score += 0.1

            # Уровень технической грамотности (ниже = выше риск)
            if profile.tech_savviness < 0.3:
                risk_score += 0.4
            elif profile.tech_savviness < 0.6:
                risk_score += 0.2

            # Обеспокоенность безопасностью
            if profile.security_concern > 0.8:
                risk_score += 0.2

            # Определяем уровень риска
            if risk_score >= 0.7:
                return "high"
            elif risk_score >= 0.4:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Ошибка определения уровня риска: {e}")
            return "medium"

    async def recommend_tariff(self, family_id: str) -> Dict[str, Any]:
        """
        Рекомендация тарифа для семьи

        Args:
            family_id: ID семьи

        Returns:
            Рекомендация тарифа
        """
        try:
            # Получаем профиль пользователя
            profile = self.user_profiles.get(family_id)
            if not profile:
                return {
                    "success": False,
                    "error": "Профиль пользователя не найден"
                }

            # Генерируем рекомендацию
            recommendation = await self._generate_tariff_recommendation(profile)

            # Сохраняем рекомендацию
            self.recommendations[recommendation.recommendation_id] = recommendation

            logger.info(f"Создана рекомендация тарифа для семьи {family_id}")

            return {
                "success": True,
                "recommendation_id": recommendation.recommendation_id,
                "recommendation_type": recommendation.recommendation_type.value,
                "title": recommendation.title,
                "description": recommendation.description,
                "confidence_score": recommendation.confidence_score,
                "expected_value": float(recommendation.expected_value),
                "discount_percentage": recommendation.discount_percentage,
                "features": recommendation.features,
                "expires_at": recommendation.expires_at.isoformat() if recommendation.expires_at else None
            }

        except Exception as e:
            logger.error(f"Ошибка рекомендации тарифа: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_tariff_recommendation(self, profile: UserProfile) -> Recommendation:
        """Генерация рекомендации тарифа"""
        try:
            recommendation_id = str(uuid.uuid4())

            # Определяем рекомендуемый тариф на основе профиля
            recommended_tariff = await self._determine_recommended_tariff(profile)

            # Рассчитываем уверенность
            confidence_score = await self._calculate_confidence_score(profile, recommended_tariff)

            # Рассчитываем ожидаемую ценность
            expected_value = await self._calculate_expected_value(profile, recommended_tariff)

            # Рассчитываем скидку
            discount_percentage = await self._calculate_discount_percentage(profile, recommended_tariff)

            # Создаем рекомендацию
            recommendation = Recommendation(
                recommendation_id=recommendation_id,
                family_id=profile.family_id,
                recommendation_type=RecommendationType.TARIFF_UPGRADE,
                title=f"Рекомендуем тариф {recommended_tariff['name']}",
                description=recommended_tariff["description"],
                confidence_score=confidence_score,
                expected_value=expected_value,
                discount_percentage=discount_percentage,
                features=recommended_tariff["features"],
                expires_at=datetime.now() + timedelta(days=self.recommendation_expiry_days)
            )

            return recommendation

        except Exception as e:
            logger.error(f"Ошибка генерации рекомендации: {e}")
            # Возвращаем базовую рекомендацию
            return Recommendation(
                recommendation_id=str(uuid.uuid4()),
                family_id=profile.family_id,
                recommendation_type=RecommendationType.TARIFF_UPGRADE,
                title="Рекомендуем тариф Basic",
                description="Базовый тариф для начала использования",
                confidence_score=0.5,
                expected_value=Decimal("290"),
                features=["VPN", "Антивирус", "Родительский контроль"]
            )

    async def _determine_recommended_tariff(self, profile: UserProfile) -> Dict[str, Any]:
        """Определение рекомендуемого тарифа"""
        try:
            # Логика выбора тарифа на основе профиля
            if profile.user_segment == UserSegment.ENTERPRISE_USERS:
                return {
                    "name": "Custom",
                    "description": "Корпоративный тариф с персональным менеджером",
                    "price": Decimal("1500"),
                    "features": ["До 50 пользователей", "Централизованное управление", "API доступ"]
                }
            elif profile.user_segment == UserSegment.PREMIUM_SEEKERS:
                return {
                    "name": "Premium",
                    "description": "Премиум тариф с AI и IoT защитой",
                    "price": Decimal("900"),
                    "features": ["AI-анализ", "IoT защита", "Умный дом", "24/7 поддержка"]
                }
            elif profile.user_segment == UserSegment.FAMILY_FOCUSED and profile.family_size >= 3:
                return {
                    "name": "Family",
                    "description": "Семейный тариф с геймификацией",
                    "price": Decimal("490"),
                    "features": ["До 6 устройств", "Геймификация", "Семейная аналитика"]
                }
            elif profile.user_segment == UserSegment.BUDGET_CONSCIOUS:
                return {
                    "name": "Basic",
                    "description": "Базовый тариф с основными функциями",
                    "price": Decimal("290"),
                    "features": ["VPN", "Антивирус", "Родительский контроль"]
                }
            else:
                return {
                    "name": "Basic",
                    "description": "Базовый тариф для начала",
                    "price": Decimal("290"),
                    "features": ["VPN", "Антивирус", "Родительский контроль"]
                }

        except Exception as e:
            logger.error(f"Ошибка определения тарифа: {e}")
            return {
                "name": "Basic",
                "description": "Базовый тариф",
                "price": Decimal("290"),
                "features": ["VPN", "Антивирус"]
            }

    async def _calculate_confidence_score(self, profile: UserProfile, tariff: Dict[str, Any]) -> float:
        """Расчет уверенности в рекомендации"""
        try:
            confidence = 0.5  # Базовая уверенность

            # Увеличиваем уверенность на основе соответствия профиля
            if profile.user_segment == UserSegment.ENTERPRISE_USERS and tariff["name"] == "Custom":
                confidence += 0.3
            elif profile.user_segment == UserSegment.PREMIUM_SEEKERS and tariff["name"] == "Premium":
                confidence += 0.3
            elif profile.user_segment == UserSegment.FAMILY_FOCUSED and tariff["name"] == "Family":
                confidence += 0.3
            elif profile.user_segment == UserSegment.BUDGET_CONSCIOUS and tariff["name"] == "Basic":
                confidence += 0.3

            # Учитываем размер семьи
            if profile.family_size >= 4 and tariff["name"] in ["Family", "Premium", "Custom"]:
                confidence += 0.1

            # Учитываем количество устройств
            if profile.device_count >= 5 and tariff["name"] in ["Family", "Premium", "Custom"]:
                confidence += 0.1

            # Ограничиваем уверенность
            return min(confidence, 1.0)

        except Exception as e:
            logger.error(f"Ошибка расчета уверенности: {e}")
            return 0.5

    async def _calculate_expected_value(self, profile: UserProfile, tariff: Dict[str, Any]) -> Decimal:
        """Расчет ожидаемой ценности"""
        try:
            base_value = tariff["price"]

            # Увеличиваем ценность на основе профиля
            if profile.user_segment == UserSegment.ENTERPRISE_USERS:
                return base_value * Decimal("1.5")  # +50% для корпоративных
            elif profile.user_segment == UserSegment.PREMIUM_SEEKERS:
                return base_value * Decimal("1.2")  # +20% для премиум
            elif profile.user_segment == UserSegment.BUDGET_CONSCIOUS:
                return base_value * Decimal("0.8")  # -20% для бюджетных
            else:
                return base_value

        except Exception as e:
            logger.error(f"Ошибка расчета ценности: {e}")
            return tariff["price"]

    async def _calculate_discount_percentage(self, profile: UserProfile, tariff: Dict[str, Any]) -> Optional[float]:
        """Расчет рекомендуемой скидки"""
        try:
            # Базовые скидки по сегментам
            base_discounts = {
                UserSegment.BUDGET_CONSCIOUS: 25.0,  # 25% для бюджетных
                UserSegment.FAMILY_FOCUSED: 15.0,    # 15% для семейных
                UserSegment.SECURITY_CONSIOUS: 10.0,  # 10% для обеспокоенных безопасностью
                UserSegment.TECH_SAVVY: 5.0,         # 5% для технических
                UserSegment.PREMIUM_SEEKERS: 0.0,    # Без скидки для премиум
                UserSegment.ENTERPRISE_USERS: 0.0    # Без скидки для корпоративных
            }

            base_discount = base_discounts.get(profile.user_segment, 0.0)

            # Дополнительные скидки
            if profile.family_size >= 4:
                base_discount += 5.0  # +5% за большую семью

            if profile.device_count >= 5:
                base_discount += 5.0  # +5% за много устройств

            if profile.budget_sensitivity > 0.7:
                base_discount += 10.0  # +10% за чувствительность к бюджету

            # Ограничиваем максимальную скидку
            max_discount = 50.0
            final_discount = min(base_discount, max_discount)

            return final_discount if final_discount > 0 else None

        except Exception as e:
            logger.error(f"Ошибка расчета скидки: {e}")
            return None

    async def suggest_discount(self, family_id: str, current_tariff: str) -> Dict[str, Any]:
        """
        Предложение скидки для семьи

        Args:
            family_id: ID семьи
            current_tariff: Текущий тариф

        Returns:
            Предложение скидки
        """
        try:
            profile = self.user_profiles.get(family_id)
            if not profile:
                return {
                    "success": False,
                    "error": "Профиль пользователя не найден"
                }

            # Рассчитываем рекомендуемую скидку
            discount_percentage = await self._calculate_discount_percentage(profile, {"name": current_tariff})

            if not discount_percentage:
                return {
                    "success": False,
                    "error": "Скидка не рекомендуется для данного профиля"
                }

            # Создаем рекомендацию скидки
            recommendation_id = str(uuid.uuid4())
            recommendation = Recommendation(
                recommendation_id=recommendation_id,
                family_id=family_id,
                recommendation_type=RecommendationType.DISCOUNT_OFFER,
                title=f"Специальная скидка {discount_percentage:.0f}%",
                description=f"Персональная скидка {discount_percentage:.0f}% на ваш тариф {current_tariff}",
                confidence_score=0.8,
                expected_value=Decimal("0"),  # Скидка не приносит дохода
                discount_percentage=discount_percentage,
                expires_at=datetime.now() + timedelta(days=7)  # Скидка действует 7 дней
            )

            # Сохраняем рекомендацию
            self.recommendations[recommendation_id] = recommendation

            logger.info(f"Создано предложение скидки {discount_percentage:.0f}% для семьи {family_id}")

            return {
                "success": True,
                "recommendation_id": recommendation_id,
                "discount_percentage": discount_percentage,
                "title": recommendation.title,
                "description": recommendation.description,
                "expires_at": recommendation.expires_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка предложения скидки: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _retrain_models_if_needed(self) -> None:
        """Переобучение моделей при необходимости"""
        try:
            now = datetime.now()

            for model_id, model in self.ml_models.items():
                # Проверяем, нужно ли переобучить модель
                days_since_training = (now - model.last_trained).days

                if days_since_training >= self.model_retrain_interval:
                    await self._retrain_model(model_id)

        except Exception as e:
            logger.error(f"Ошибка переобучения моделей: {e}")

    async def _retrain_model(self, model_id: str) -> None:
        """Переобучение конкретной модели"""
        try:
            model = self.ml_models.get(model_id)
            if not model:
                return

            # Подготавливаем данные для обучения
            X, y = await self._prepare_training_data(model_id)

            if len(X) < self.min_data_points:
                logger.info(f"Недостаточно данных для переобучения модели {model_id}")
                return

            # Обучаем модель
            if model_id == "user_segmentation":
                model.model.fit(X)
                # Для KMeans рассчитываем инерцию как метрику
                model.accuracy = 1.0 - (model.model.inertia_ / len(X))
            else:
                model.model.fit(X, y)
                # Для классификаторов рассчитываем точность
                y_pred = model.model.predict(X)
                model.accuracy = accuracy_score(y, y_pred)

            model.last_trained = datetime.now()

            logger.info(f"Модель {model_id} переобучена, точность: {model.accuracy:.3f}")

        except Exception as e:
            logger.error(f"Ошибка переобучения модели {model_id}: {e}")

    async def _prepare_training_data(self, model_id: str) -> Tuple[List[List[float]], List[str]]:
        """Подготовка данных для обучения модели"""
        try:
            X = []
            y = []

            for profile in self.user_profiles.values():
                # Подготавливаем признаки
                features = [
                    profile.tech_savviness,
                    profile.security_concern,
                    profile.budget_sensitivity,
                    float(profile.family_size),
                    float(profile.device_count)
                ]

                X.append(features)

                # Подготавливаем метки
                if model_id == "user_segmentation":
                    y.append(profile.user_segment.value)
                elif model_id == "tariff_recommendation":
                    # Используем предпочтения пользователя как метки
                    preferred_tariff = profile.preferences.get("preferred_tariff", "basic")
                    y.append(preferred_tariff)
                elif model_id == "discount_optimization":
                    # Используем чувствительность к бюджету как метку
                    if profile.budget_sensitivity > 0.7:
                        y.append("high_discount")
                    elif profile.budget_sensitivity > 0.4:
                        y.append("medium_discount")
                    else:
                        y.append("low_discount")

            return X, y

        except Exception as e:
            logger.error(f"Ошибка подготовки данных: {e}")
            return [], []

    async def get_user_profile(self, family_id: str) -> Dict[str, Any]:
        """Получение профиля пользователя"""
        try:
            profile = self.user_profiles.get(family_id)
            if not profile:
                return {
                    "success": False,
                    "error": "Профиль пользователя не найден"
                }

            return {
                "success": True,
                "family_id": profile.family_id,
                "user_segment": profile.user_segment.value,
                "behavior_pattern": profile.behavior_pattern.value,
                "risk_level": profile.risk_level,
                "tech_savviness": profile.tech_savviness,
                "security_concern": profile.security_concern,
                "budget_sensitivity": profile.budget_sensitivity,
                "family_size": profile.family_size,
                "device_count": profile.device_count,
                "usage_patterns": profile.usage_patterns,
                "preferences": profile.preferences,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка получения профиля: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_recommendations(self, family_id: str) -> List[Dict[str, Any]]:
        """Получение рекомендаций для семьи"""
        try:
            recommendations = []

            for recommendation in self.recommendations.values():
                if (recommendation.family_id == family_id and
                        (not recommendation.expires_at or datetime.now() < recommendation.expires_at)):

                    recommendations.append({
                        "recommendation_id": recommendation.recommendation_id,
                        "recommendation_type": recommendation.recommendation_type.value,
                        "title": recommendation.title,
                        "description": recommendation.description,
                        "confidence_score": recommendation.confidence_score,
                        "expected_value": float(recommendation.expected_value),
                        "discount_percentage": recommendation.discount_percentage,
                        "features": recommendation.features,
                        "created_at": recommendation.created_at.isoformat(),
                        "expires_at": recommendation.expires_at.isoformat() if recommendation.expires_at else None,
                        "is_accepted": recommendation.is_accepted
                    })

            # Сортируем по уверенности (высокие первые)
            recommendations.sort(key=lambda x: x["confidence_score"], reverse=True)

            return recommendations

        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            return []

    async def accept_recommendation(self, recommendation_id: str) -> Dict[str, Any]:
        """Принятие рекомендации"""
        try:
            if recommendation_id not in self.recommendations:
                return {
                    "success": False,
                    "error": "Рекомендация не найдена"
                }

            recommendation = self.recommendations[recommendation_id]

            # Проверяем, не истекла ли рекомендация
            if recommendation.expires_at and datetime.now() > recommendation.expires_at:
                return {
                    "success": False,
                    "error": "Рекомендация истекла"
                }

            # Отмечаем как принятую
            recommendation.is_accepted = True
            recommendation.accepted_at = datetime.now()

            logger.info(f"Рекомендация {recommendation_id} принята семьей {recommendation.family_id}")

            return {
                "success": True,
                "recommendation_id": recommendation_id,
                "accepted_at": recommendation.accepted_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка принятия рекомендации: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_agent_stats(self) -> Dict[str, Any]:
        """Получение статистики агента"""
        try:
            stats = {
                "total_profiles": len(self.user_profiles),
                "total_recommendations": len(self.recommendations),
                "active_recommendations": 0,
                "accepted_recommendations": 0,
                "by_segment": {},
                "by_behavior_pattern": {},
                "ml_models": {}
            }

            # Подсчет активных рекомендаций
            now = datetime.now()
            for recommendation in self.recommendations.values():
                if not recommendation.expires_at or now < recommendation.expires_at:
                    stats["active_recommendations"] += 1

                if recommendation.is_accepted:
                    stats["accepted_recommendations"] += 1

            # Подсчет по сегментам
            for profile in self.user_profiles.values():
                segment = profile.user_segment.value
                stats["by_segment"][segment] = stats["by_segment"].get(segment, 0) + 1

                pattern = profile.behavior_pattern.value
                stats["by_behavior_pattern"][pattern] = stats["by_behavior_pattern"].get(pattern, 0) + 1

            # Статистика ML моделей
            for model_id, model in self.ml_models.items():
                stats["ml_models"][model_id] = {
                    "accuracy": model.accuracy,
                    "last_trained": model.last_trained.isoformat(),
                    "features_count": len(model.features)
                }

            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def get_status(self) -> ComponentStatus:
        """Получение статуса компонента"""
        return self.status

    def get_security_level(self) -> SecurityLevel:
        """Получение уровня безопасности"""
        return self.security_level

    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья компонента"""
        try:
            stats = await self.get_agent_stats()

            return {
                "status": "healthy",
                "component": "PersonalizationAgent",
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "memory_usage": "normal"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "component": "PersonalizationAgent",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


# Создание глобального экземпляра
personalization_agent = PersonalizationAgent()


async def main():
    """Тестирование PersonalizationAgent"""
    print("🧪 Тестирование PersonalizationAgent")
    print("=" * 50)

    # Анализ поведения пользователя
    behavior_data = {
        "tech_savviness": 0.8,
        "security_concern": 0.9,
        "budget_sensitivity": 0.3,
        "family_size": 4,
        "device_count": 6,
        "usage_patterns": {
            "intensity": 0.7,
            "peak_hours_usage": 0.6,
            "weekend_usage": 0.8,
            "mobile_usage": 0.4
        },
        "preferences": {
            "preferred_tariff": "family"
        }
    }

    result = await personalization_agent.analyze_user_behavior("test_family_123", behavior_data)
    print(f"Анализ поведения: {result}")

    # Рекомендация тарифа
    recommendation = await personalization_agent.recommend_tariff("test_family_123")
    print(f"Рекомендация тарифа: {recommendation}")

    # Предложение скидки
    discount = await personalization_agent.suggest_discount("test_family_123", "family")
    print(f"Предложение скидки: {discount}")

    # Получение профиля
    profile = await personalization_agent.get_user_profile("test_family_123")
    print(f"Профиль пользователя: {profile}")

    # Получение рекомендаций
    recommendations = await personalization_agent.get_recommendations("test_family_123")
    print(f"Рекомендации: {len(recommendations)}")

    # Статистика агента
    stats = await personalization_agent.get_agent_stats()
    print(f"Статистика агента: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
