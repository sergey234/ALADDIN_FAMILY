#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABTestingManager - Менеджер A/B тестирования ALADDIN
Версия 1.0 - Полная система A/B тестирования с аналитикой конверсии

Интегрируется с:
- SubscriptionManager (тестирование тарифов)
- QRPaymentManager (тестирование способов оплаты)
- PersonalizationAgent (тестирование рекомендаций)
- FamilyNotificationManager (тестирование уведомлений)

Автор: ALADDIN Security System
Версия: 1.0.0
Дата: 2025-01-27
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import random
from scipy import stats
import numpy as np

from security.core.security_base import ComponentStatus, SecurityBase, SecurityLevel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Статусы A/B тестов"""
    DRAFT = "draft"             # Черновик
    ACTIVE = "active"           # Активный
    PAUSED = "paused"           # Приостановлен
    COMPLETED = "completed"     # Завершен
    CANCELLED = "cancelled"     # Отменен


class TestType(Enum):
    """Типы A/B тестов"""
    TARIFF_PRICING = "tariff_pricing"           # Тестирование цен тарифов
    TRIAL_PERIOD = "trial_period"               # Тестирование тестовых периодов
    PAYMENT_METHODS = "payment_methods"         # Тестирование способов оплаты
    UI_DESIGN = "ui_design"                     # Тестирование дизайна интерфейса
    NOTIFICATION_TEXT = "notification_text"     # Тестирование текстов уведомлений
    RECOMMENDATION_ALGORITHM = "recommendation_algorithm"  # Тестирование алгоритмов рекомендаций
    DISCOUNT_OFFERS = "discount_offers"         # Тестирование предложений скидок
    ONBOARDING_FLOW = "onboarding_flow"         # Тестирование процесса онбординга


class ConversionEvent(Enum):
    """События конверсии"""
    TRIAL_START = "trial_start"                 # Начало тестового периода
    TRIAL_CONVERSION = "trial_conversion"       # Конверсия из тестового периода
    SUBSCRIPTION_PURCHASE = "subscription_purchase"  # Покупка подписки
    TARIFF_UPGRADE = "tariff_upgrade"           # Обновление тарифа
    REFERRAL_SIGNUP = "referral_signup"         # Регистрация по реферальной ссылке
    FEATURE_USAGE = "feature_usage"             # Использование функции
    RETENTION_DAY_7 = "retention_day_7"         # Удержание на 7 день
    RETENTION_DAY_30 = "retention_day_30"       # Удержание на 30 день


class StatisticalSignificance(Enum):
    """Уровни статистической значимости"""
    NOT_SIGNIFICANT = "not_significant"         # Не значимо
    MARGINAL = "marginal"                       # Маргинально значимо (90%)
    SIGNIFICANT = "significant"                 # Значимо (95%)
    HIGHLY_SIGNIFICANT = "highly_significant"   # Высоко значимо (99%)


@dataclass
class TestVariant:
    """Вариант A/B теста"""
    variant_id: str
    name: str
    description: str
    traffic_percentage: float  # 0.0 - 1.0
    configuration: Dict[str, Any] = field(default_factory=dict)
    is_control: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ABTest:
    """A/B тест"""
    test_id: str
    name: str
    description: str
    test_type: TestType
    status: TestStatus
    variants: List[TestVariant] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    success_metrics: List[ConversionEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    min_sample_size: int = 1000
    max_duration_days: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestParticipant:
    """Участник A/B теста"""
    participant_id: str
    family_id: str
    test_id: str
    variant_id: str
    assigned_at: datetime = field(default_factory=datetime.now)
    conversion_events: List[ConversionEvent] = field(default_factory=list)
    conversion_timestamps: List[datetime] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResults:
    """Результаты A/B теста"""
    test_id: str
    variant_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    statistical_significance: StatisticalSignificance = StatisticalSignificance.NOT_SIGNIFICANT
    p_value: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    winner_variant: Optional[str] = None
    lift_percentage: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.now)


class ABTestingManager(SecurityBase):
    """
    Менеджер A/B тестирования ALADDIN

    Функции:
    - Создание и управление A/B тестами
    - Назначение пользователей к вариантам
    - Отслеживание конверсий
    - Статистический анализ результатов
    - Автоматическое завершение тестов
    """

    def __init__(self):
        """Инициализация менеджера A/B тестирования"""
        super().__init__()

        # Хранилища данных
        self.tests: Dict[str, ABTest] = {}
        self.participants: Dict[str, TestParticipant] = {}
        self.conversion_events: Dict[str, List[Tuple[str, ConversionEvent, datetime]]] = {}
        self.test_results: Dict[str, TestResults] = {}

        # Конфигурация
        self.default_traffic_split = 0.5  # 50/50 по умолчанию
        self.min_conversion_rate = 0.01   # Минимальный уровень конверсии 1%
        self.max_test_duration = 30       # Максимальная длительность теста в днях

        # Статус компонента
        self.status = ComponentStatus.ACTIVE
        self.security_level = SecurityLevel.HIGH

        logger.info("ABTestingManager инициализирован")

    async def create_test(self, name: str, description: str, test_type: TestType,
                          variants: List[Dict[str, Any]],
                          success_metrics: List[ConversionEvent],
                          target_audience: Optional[Dict[str, Any]] = None,
                          min_sample_size: int = 1000,
                          max_duration_days: int = 30) -> Dict[str, Any]:
        """
        Создание нового A/B теста

        Args:
            name: Название теста
            description: Описание теста
            test_type: Тип теста
            variants: Список вариантов теста
            success_metrics: Метрики успеха
            target_audience: Целевая аудитория
            min_sample_size: Минимальный размер выборки
            max_duration_days: Максимальная длительность в днях

        Returns:
            Информация о созданном тесте
        """
        try:
            # Создаем ID теста
            test_id = str(uuid.uuid4())

            # Валидируем варианты
            if len(variants) < 2:
                return {
                    "success": False,
                    "error": "Необходимо минимум 2 варианта для A/B теста"
                }

            # Проверяем, что сумма трафика = 100%
            total_traffic = sum(v.get("traffic_percentage", 0) for v in variants)
            if abs(total_traffic - 1.0) > 0.01:
                return {
                    "success": False,
                    "error": "Сумма трафика всех вариантов должна равняться 100%"
                }

            # Создаем варианты
            test_variants = []
            for i, variant_data in enumerate(variants):
                variant = TestVariant(
                    variant_id=str(uuid.uuid4()),
                    name=variant_data.get("name", f"Variant {i+1}"),
                    description=variant_data.get("description", ""),
                    traffic_percentage=variant_data.get("traffic_percentage", 1.0 / len(variants)),
                    configuration=variant_data.get("configuration", {}),
                    is_control=(i == 0)  # Первый вариант - контрольный
                )
                test_variants.append(variant)

            # Создаем тест
            test = ABTest(
                test_id=test_id,
                name=name,
                description=description,
                test_type=test_type,
                status=TestStatus.DRAFT,
                variants=test_variants,
                target_audience=target_audience or {},
                success_metrics=success_metrics,
                min_sample_size=min_sample_size,
                max_duration_days=max_duration_days
            )

            # Сохраняем тест
            self.tests[test_id] = test

            logger.info(f"Создан A/B тест {test_id}: {name}")

            return {
                "success": True,
                "test_id": test_id,
                "name": name,
                "test_type": test_type.value,
                "variants_count": len(test_variants),
                "status": TestStatus.DRAFT.value
            }

        except Exception as e:
            logger.error(f"Ошибка создания A/B теста: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start_test(self, test_id: str) -> Dict[str, Any]:
        """
        Запуск A/B теста

        Args:
            test_id: ID теста

        Returns:
            Результат запуска теста
        """
        try:
            if test_id not in self.tests:
                return {
                    "success": False,
                    "error": "A/B тест не найден"
                }

            test = self.tests[test_id]

            if test.status != TestStatus.DRAFT:
                return {
                    "success": False,
                    "error": f"Тест уже запущен или завершен (статус: {test.status.value})"
                }

            # Проверяем валидность теста
            if len(test.variants) < 2:
                return {
                    "success": False,
                    "error": "Недостаточно вариантов для запуска теста"
                }

            # Запускаем тест
            test.status = TestStatus.ACTIVE
            test.started_at = datetime.now()

            logger.info(f"A/B тест {test_id} запущен")

            return {
                "success": True,
                "test_id": test_id,
                "status": TestStatus.ACTIVE.value,
                "started_at": test.started_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка запуска A/B теста: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def assign_user_to_variant(self, family_id: str, test_id: str) -> Dict[str, Any]:
        """
        Назначение пользователя к варианту теста

        Args:
            family_id: ID семьи
            test_id: ID теста

        Returns:
            Назначенный вариант
        """
        try:
            if test_id not in self.tests:
                return {
                    "success": False,
                    "error": "A/B тест не найден"
                }

            test = self.tests[test_id]

            if test.status != TestStatus.ACTIVE:
                return {
                    "success": False,
                    "error": f"Тест не активен (статус: {test.status.value})"
                }

            # Проверяем, не участвует ли пользователь уже в тесте
            existing_participant = None
            for participant in self.participants.values():
                if (participant.family_id == family_id and
                        participant.test_id == test_id):
                    existing_participant = participant
                    break

            if existing_participant:
                return {
                    "success": True,
                    "test_id": test_id,
                    "variant_id": existing_participant.variant_id,
                    "variant_name": self._get_variant_name(test, existing_participant.variant_id),
                    "is_existing": True
                }

            # Проверяем целевую аудиторию
            if not await self._is_user_in_target_audience(family_id, test.target_audience):
                return {
                    "success": False,
                    "error": "Пользователь не входит в целевую аудиторию теста"
                }

            # Назначаем вариант на основе трафика
            variant = await self._assign_variant_by_traffic(test)

            # Создаем участника теста
            participant_id = str(uuid.uuid4())
            participant = TestParticipant(
                participant_id=participant_id,
                family_id=family_id,
                test_id=test_id,
                variant_id=variant.variant_id,
                assigned_at=datetime.now()
            )

            # Сохраняем участника
            self.participants[participant_id] = participant

            logger.info(f"Пользователь {family_id} назначен к варианту {variant.variant_id} в тесте {test_id}")

            return {
                "success": True,
                "test_id": test_id,
                "variant_id": variant.variant_id,
                "variant_name": variant.name,
                "is_control": variant.is_control,
                "configuration": variant.configuration,
                "is_existing": False
            }

        except Exception as e:
            logger.error(f"Ошибка назначения пользователя к варианту: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _assign_variant_by_traffic(self, test: ABTest) -> TestVariant:
        """Назначение варианта на основе трафика"""
        try:
            # Генерируем случайное число от 0 до 1
            random_value = random.random()

            # Накапливаем трафик для каждого варианта
            cumulative_traffic = 0.0
            for variant in test.variants:
                cumulative_traffic += variant.traffic_percentage
                if random_value <= cumulative_traffic:
                    return variant

            # Если что-то пошло не так, возвращаем первый вариант
            return test.variants[0]

        except Exception as e:
            logger.error(f"Ошибка назначения варианта: {e}")
            return test.variants[0]

    async def _is_user_in_target_audience(self, family_id: str, target_audience: Dict[str, Any]) -> bool:
        """Проверка, входит ли пользователь в целевую аудиторию"""
        try:
            # Если целевая аудитория не задана, все пользователи подходят
            if not target_audience:
                return True

            # Здесь должна быть логика проверки целевой аудитории
            # Пока что возвращаем True для всех пользователей
            return True

        except Exception as e:
            logger.error(f"Ошибка проверки целевой аудитории: {e}")
            return True

    def _get_variant_name(self, test: ABTest, variant_id: str) -> str:
        """Получение названия варианта по ID"""
        for variant in test.variants:
            if variant.variant_id == variant_id:
                return variant.name
        return "Unknown"

    async def track_conversion(self, family_id: str, test_id: str,
                               conversion_event: ConversionEvent) -> Dict[str, Any]:
        """
        Отслеживание конверсии

        Args:
            family_id: ID семьи
            test_id: ID теста
            conversion_event: Событие конверсии

        Returns:
            Результат отслеживания
        """
        try:
            # Находим участника теста
            participant = None
            for p in self.participants.values():
                if p.family_id == family_id and p.test_id == test_id:
                    participant = p
                    break

            if not participant:
                return {
                    "success": False,
                    "error": "Пользователь не участвует в данном тесте"
                }

            # Добавляем событие конверсии
            participant.conversion_events.append(conversion_event)
            participant.conversion_timestamps.append(datetime.now())

            # Сохраняем событие в общем хранилище
            if test_id not in self.conversion_events:
                self.conversion_events[test_id] = []

            self.conversion_events[test_id].append((family_id, conversion_event, datetime.now()))

            logger.info(
                f"Зафиксирована конверсия {conversion_event.value} для пользователя {family_id} в тесте {test_id}")

            return {
                "success": True,
                "family_id": family_id,
                "test_id": test_id,
                "conversion_event": conversion_event.value,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка отслеживания конверсии: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """
        Получение результатов A/B теста

        Args:
            test_id: ID теста

        Returns:
            Результаты теста
        """
        try:
            if test_id not in self.tests:
                return {
                    "success": False,
                    "error": "A/B тест не найден"
                }

            test = self.tests[test_id]

            # Собираем данные по вариантам
            variant_data = {}
            for variant in test.variants:
                participants = [p for p in self.participants.values()
                                if p.test_id == test_id and p.variant_id == variant.variant_id]

                # Подсчитываем метрики
                total_participants = len(participants)
                conversions = {}

                for metric in test.success_metrics:
                    conversions[metric.value] = sum(1 for p in participants
                                                    if metric in p.conversion_events)

                # Рассчитываем конверсию
                conversion_rates = {}
                for metric, count in conversions.items():
                    if total_participants > 0:
                        conversion_rates[metric] = count / total_participants
                    else:
                        conversion_rates[metric] = 0.0

                variant_data[variant.variant_id] = {
                    "variant_name": variant.name,
                    "is_control": variant.is_control,
                    "total_participants": total_participants,
                    "conversions": conversions,
                    "conversion_rates": conversion_rates
                }

            # Проводим статистический анализ
            statistical_analysis = await self._perform_statistical_analysis(test_id, variant_data)

            # Определяем победителя
            winner = await self._determine_winner(test_id, variant_data, statistical_analysis)

            # Создаем результаты
            results = TestResults(
                test_id=test_id,
                variant_results=variant_data,
                statistical_significance=statistical_analysis["significance"],
                p_value=statistical_analysis["p_value"],
                confidence_interval=statistical_analysis["confidence_interval"],
                winner_variant=winner,
                lift_percentage=statistical_analysis.get("lift_percentage", 0.0)
            )

            # Сохраняем результаты
            self.test_results[test_id] = results

            return {
                "success": True,
                "test_id": test_id,
                "test_name": test.name,
                "test_status": test.status.value,
                "variant_results": variant_data,
                "statistical_analysis": statistical_analysis,
                "winner": winner,
                "calculated_at": results.calculated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка получения результатов теста: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _perform_statistical_analysis(self, test_id: str, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Проведение статистического анализа"""
        try:
            # Получаем данные для анализа
            variants = list(variant_data.keys())
            if len(variants) < 2:
                return {
                    "significance": StatisticalSignificance.NOT_SIGNIFICANT,
                    "p_value": 1.0,
                    "confidence_interval": (0.0, 0.0)
                }

            # Берем первый вариант как контрольный
            control_variant = variants[0]
            treatment_variant = variants[1]

            control_data = variant_data[control_variant]
            treatment_data = variant_data[treatment_variant]

            # Получаем конверсии для основного метрика
            # Используем первое событие конверсии как основное
            test = self.tests[test_id]
            if not test.success_metrics:
                return {
                    "significance": StatisticalSignificance.NOT_SIGNIFICANT,
                    "p_value": 1.0,
                    "confidence_interval": (0.0, 0.0)
                }

            main_metric = test.success_metrics[0].value
            control_conversions = control_data["conversions"].get(main_metric, 0)
            treatment_conversions = treatment_data["conversions"].get(main_metric, 0)
            control_participants = control_data["total_participants"]
            treatment_participants = treatment_data["total_participants"]

            if control_participants == 0 or treatment_participants == 0:
                return {
                    "significance": StatisticalSignificance.NOT_SIGNIFICANT,
                    "p_value": 1.0,
                    "confidence_interval": (0.0, 0.0)
                }

            # Рассчитываем конверсии
            control_rate = control_conversions / control_participants
            treatment_rate = treatment_conversions / treatment_participants

            # Проводим z-тест для пропорций
            p1, n1 = control_conversions, control_participants
            p2, n2 = treatment_conversions, treatment_participants

            # Объединенная пропорция
            p_pooled = (p1 + p2) / (n1 + n2)

            # Стандартная ошибка
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1 / n1 + 1 / n2))

            # Z-статистика
            if se > 0:
                z_score = (treatment_rate - control_rate) / se
            else:
                z_score = 0

            # P-значение (двусторонний тест)
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

            # Определяем значимость
            if p_value < 0.01:
                significance = StatisticalSignificance.HIGHLY_SIGNIFICANT
            elif p_value < 0.05:
                significance = StatisticalSignificance.SIGNIFICANT
            elif p_value < 0.10:
                significance = StatisticalSignificance.MARGINAL
            else:
                significance = StatisticalSignificance.NOT_SIGNIFICANT

            # Доверительный интервал для разности пропорций
            diff = treatment_rate - control_rate
            margin_error = 1.96 * se  # 95% доверительный интервал
            ci_lower = diff - margin_error
            ci_upper = diff + margin_error

            # Процент улучшения
            if control_rate > 0:
                lift_percentage = ((treatment_rate - control_rate) / control_rate) * 100
            else:
                lift_percentage = 0.0

            return {
                "significance": significance,
                "p_value": p_value,
                "confidence_interval": (ci_lower, ci_upper),
                "z_score": z_score,
                "control_rate": control_rate,
                "treatment_rate": treatment_rate,
                "lift_percentage": lift_percentage
            }

        except Exception as e:
            logger.error(f"Ошибка статистического анализа: {e}")
            return {
                "significance": StatisticalSignificance.NOT_SIGNIFICANT,
                "p_value": 1.0,
                "confidence_interval": (0.0, 0.0)
            }

    async def _determine_winner(self, test_id: str, variant_data: Dict[str, Any],
                                statistical_analysis: Dict[str, Any]) -> Optional[str]:
        """Определение победителя теста"""
        try:
            # Если нет статистической значимости, победителя нет
            if statistical_analysis["significance"] == StatisticalSignificance.NOT_SIGNIFICANT:
                return None

            # Находим вариант с лучшей конверсией
            best_variant = None
            best_rate = 0.0

            for variant_id, data in variant_data.items():
                # Используем первое событие конверсии как основное
                test = self.tests[test_id]
                if test.success_metrics:
                    main_metric = test.success_metrics[0].value
                    rate = data["conversion_rates"].get(main_metric, 0.0)

                    if rate > best_rate:
                        best_rate = rate
                        best_variant = variant_id

            return best_variant

        except Exception as e:
            logger.error(f"Ошибка определения победителя: {e}")
            return None

    async def complete_test(self, test_id: str) -> Dict[str, Any]:
        """
        Завершение A/B теста

        Args:
            test_id: ID теста

        Returns:
            Результат завершения теста
        """
        try:
            if test_id not in self.tests:
                return {
                    "success": False,
                    "error": "A/B тест не найден"
                }

            test = self.tests[test_id]

            if test.status != TestStatus.ACTIVE:
                return {
                    "success": False,
                    "error": f"Тест не активен (статус: {test.status.value})"
                }

            # Получаем результаты
            results = await self.get_test_results(test_id)

            # Завершаем тест
            test.status = TestStatus.COMPLETED
            test.ended_at = datetime.now()

            logger.info(f"A/B тест {test_id} завершен")

            return {
                "success": True,
                "test_id": test_id,
                "status": TestStatus.COMPLETED.value,
                "ended_at": test.ended_at.isoformat(),
                "results": results
            }

        except Exception as e:
            logger.error(f"Ошибка завершения теста: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_active_tests(self) -> List[Dict[str, Any]]:
        """Получение списка активных тестов"""
        try:
            active_tests = []

            for test in self.tests.values():
                if test.status == TestStatus.ACTIVE:
                    # Подсчитываем участников
                    participants_count = sum(1 for p in self.participants.values()
                                             if p.test_id == test.test_id)

                    active_tests.append({
                        "test_id": test.test_id,
                        "name": test.name,
                        "test_type": test.test_type.value,
                        "variants_count": len(test.variants),
                        "participants_count": participants_count,
                        "started_at": test.started_at.isoformat() if test.started_at else None,
                        "duration_days": (datetime.now() - test.started_at).days if test.started_at else 0
                    })

            return active_tests

        except Exception as e:
            logger.error(f"Ошибка получения активных тестов: {e}")
            return []

    async def get_test_participants(self, test_id: str) -> List[Dict[str, Any]]:
        """Получение участников теста"""
        try:
            participants = []

            for participant in self.participants.values():
                if participant.test_id == test_id:
                    participants.append({
                        "participant_id": participant.participant_id,
                        "family_id": participant.family_id,
                        "variant_id": participant.variant_id,
                        "assigned_at": participant.assigned_at.isoformat(),
                        "conversion_events": [e.value for e in participant.conversion_events],
                        "conversion_count": len(participant.conversion_events)
                    })

            return participants

        except Exception as e:
            logger.error(f"Ошибка получения участников теста: {e}")
            return []

    async def get_manager_stats(self) -> Dict[str, Any]:
        """Получение статистики менеджера"""
        try:
            stats = {
                "total_tests": len(self.tests),
                "active_tests": 0,
                "completed_tests": 0,
                "total_participants": len(self.participants),
                "total_conversions": 0,
                "by_test_type": {},
                "by_status": {}
            }

            # Подсчет по статусам
            for test in self.tests.values():
                if test.status == TestStatus.ACTIVE:
                    stats["active_tests"] += 1
                elif test.status == TestStatus.COMPLETED:
                    stats["completed_tests"] += 1

                # Подсчет по типам
                test_type = test.test_type.value
                stats["by_test_type"][test_type] = stats["by_test_type"].get(test_type, 0) + 1

                # Подсчет по статусам
                status = test.status.value
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Подсчет конверсий
            for participant in self.participants.values():
                stats["total_conversions"] += len(participant.conversion_events)

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
            stats = await self.get_manager_stats()

            return {
                "status": "healthy",
                "component": "ABTestingManager",
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "memory_usage": "normal"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "component": "ABTestingManager",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }


# Создание глобального экземпляра
ab_testing_manager = ABTestingManager()


async def main():
    """Тестирование ABTestingManager"""
    print("🧪 Тестирование ABTestingManager")
    print("=" * 50)

    # Создание A/B теста
    test_result = await ab_testing_manager.create_test(
        name="Тест цен тарифов",
        description="Тестирование влияния цены на конверсию",
        test_type=TestType.TARIFF_PRICING,
        variants=[
            {
                "name": "Контроль (290₽)",
                "description": "Текущая цена",
                "traffic_percentage": 0.5,
                "configuration": {"price": 290}
            },
            {
                "name": "Тест (250₽)",
                "description": "Сниженная цена",
                "traffic_percentage": 0.5,
                "configuration": {"price": 250}
            }
        ],
        success_metrics=[ConversionEvent.SUBSCRIPTION_PURCHASE],
        min_sample_size=100,
        max_duration_days=7
    )
    print(f"Создание теста: {test_result}")

    if test_result["success"]:
        test_id = test_result["test_id"]

        # Запуск теста
        start_result = await ab_testing_manager.start_test(test_id)
        print(f"Запуск теста: {start_result}")

        # Назначение пользователей
        for i in range(10):
            family_id = f"test_family_{i}"
            assign_result = await ab_testing_manager.assign_user_to_variant(family_id, test_id)
            print(f"Назначение {family_id}: {assign_result}")

            # Симуляция конверсий
            if random.random() < 0.3:  # 30% конверсия
                conversion_result = await ab_testing_manager.track_conversion(
                    family_id, test_id, ConversionEvent.SUBSCRIPTION_PURCHASE
                )
                print(f"Конверсия {family_id}: {conversion_result}")

        # Получение результатов
        results = await ab_testing_manager.get_test_results(test_id)
        print(f"Результаты теста: {results}")

        # Завершение теста
        complete_result = await ab_testing_manager.complete_test(test_id)
        print(f"Завершение теста: {complete_result}")

        # Статистика
        stats = await ab_testing_manager.get_manager_stats()
        print(f"Статистика: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
