# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Risk Assessment
Оценка рисков безопасности для семей
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase
from core.security_base import IncidentSeverity, SecurityEvent


class RiskCategory(Enum):
    """Категории рисков"""

    AUTHENTICATION = "authentication"  # Аутентификация
    AUTHORIZATION = "authorization"  # Авторизация
    DATA_PROTECTION = "data_protection"  # Защита данных
    NETWORK_SECURITY = "network_security"  # Сетевая безопасность
    DEVICE_SECURITY = "device_security"  # Безопасность устройств
    USER_BEHAVIOR = "user_behavior"  # Поведение пользователей
    THIRD_PARTY = "third_party"  # Третьи стороны
    PHYSICAL_SECURITY = "physical_security"  # Физическая безопасность
    COMPLIANCE = "compliance"  # Соответствие требованиям
    BUSINESS_CONTINUITY = "business_continuity"  # Непрерывность бизнеса


class RiskLevel(Enum):
    """Уровни риска"""

    CRITICAL = "critical"  # Критический
    HIGH = "high"  # Высокий
    MEDIUM = "medium"  # Средний
    LOW = "low"  # Низкий
    MINIMAL = "minimal"  # Минимальный


class RiskStatus(Enum):
    """Статусы риска"""

    IDENTIFIED = "identified"  # Выявлен
    ASSESSED = "assessed"  # Оценен
    MITIGATED = "mitigated"  # Смягчен
    ACCEPTED = "accepted"  # Принят
    TRANSFERRED = "transferred"  # Передан
    MONITORED = "monitored"  # Мониторится


class ThreatSource(Enum):
    """Источники угроз"""

    INTERNAL = "internal"  # Внутренние
    EXTERNAL = "external"  # Внешние
    NATURAL = "natural"  # Природные
    TECHNICAL = "technical"  # Технические
    HUMAN = "human"  # Человеческие
    ORGANIZATIONAL = "organizational"  # Организационные


@dataclass
class RiskFactor:
    """Фактор риска"""

    factor_id: str
    name: str
    description: str
    category: RiskCategory
    weight: float  # Вес фактора (0.0 - 1.0)
    impact_score: float  # Оценка воздействия (0.0 - 1.0)
    likelihood_score: float  # Оценка вероятности (0.0 - 1.0)
    risk_score: float = 0.0  # Общий балл риска
    mitigation_controls: List[str] = field(default_factory=list)
    last_assessed: datetime = field(default_factory=datetime.now)


@dataclass
class RiskAssessment:
    """Оценка риска"""

    assessment_id: str
    risk_id: str
    risk_name: str
    category: RiskCategory
    level: RiskLevel
    status: RiskStatus
    risk_score: float
    impact_score: float
    likelihood_score: float
    description: str
    threat_sources: List[ThreatSource]
    affected_assets: List[str]
    mitigation_measures: List[str]
    residual_risk: float
    assessment_date: datetime = field(default_factory=datetime.now)
    assessor: str = "system"
    next_review_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskProfile:
    """Профиль риска пользователя/семьи"""

    profile_id: str
    user_id: str
    risk_factors: Dict[str, RiskFactor]
    overall_risk_score: float
    risk_level: RiskLevel
    last_assessment: datetime = field(default_factory=datetime.now)
    assessment_history: List[RiskAssessment] = field(default_factory=list)
    mitigation_recommendations: List[str] = field(default_factory=list)


class RiskAssessmentService(SecurityBase):
    """
    Оценка рисков безопасности для семей
    Комплексная система анализа и управления рисками
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация сервиса оценки рисков.

        Args:
            config: Конфигурация сервиса (опционально)
        """
        super().__init__("RiskAssessment", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.risk_factors: Dict[str, RiskFactor] = {}
        self.risk_assessments: List[RiskAssessment] = []
        self.risk_profiles: Dict[str, RiskProfile] = {}
        self.risk_controls: Dict[str, Dict[str, Any]] = {}
        self.activity_log: List[SecurityEvent] = []

        # Настройки оценки рисков
        self.risk_thresholds = {
            RiskLevel.CRITICAL: 0.9,
            RiskLevel.HIGH: 0.7,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.LOW: 0.3,
            RiskLevel.MINIMAL: 0.1,
        }

        self.assessment_weights = {
            RiskCategory.AUTHENTICATION: 0.15,
            RiskCategory.AUTHORIZATION: 0.12,
            RiskCategory.DATA_PROTECTION: 0.20,
            RiskCategory.NETWORK_SECURITY: 0.15,
            RiskCategory.DEVICE_SECURITY: 0.10,
            RiskCategory.USER_BEHAVIOR: 0.10,
            RiskCategory.THIRD_PARTY: 0.08,
            RiskCategory.PHYSICAL_SECURITY: 0.05,
            RiskCategory.COMPLIANCE: 0.03,
            RiskCategory.BUSINESS_CONTINUITY: 0.02,
        }

        self._initialize_default_risk_factors()
        self._initialize_risk_controls()

    def __str__(self) -> str:
        """
        Строковое представление сервиса.

        Returns:
            Строковое описание сервиса
        """
        return f"RiskAssessmentService(risk_factors={len(self.risk_factors)}, controls={len(self.risk_controls)})"

    def __repr__(self) -> str:
        """
        Представление сервиса для отладки.

        Returns:
            Детальное представление сервиса
        """
        return f"RiskAssessmentService(risk_factors={len(self.risk_factors)}, controls={len(self.risk_controls)}, logger={self.logger.name})"

    def __len__(self) -> int:
        """
        Количество факторов риска в сервисе.

        Returns:
            Количество факторов риска
        """
        return len(self.risk_factors)

    def __bool__(self) -> bool:
        """
        Проверка инициализации сервиса.

        Returns:
            True если сервис инициализирован
        """
        return bool(self.risk_factors and self.risk_controls)

    def __eq__(self, other) -> bool:
        """
        Сравнение сервисов на равенство.

        Args:
            other: Другой объект для сравнения

        Returns:
            True если сервисы равны
        """
        if not isinstance(other, RiskAssessmentService):
            return False
        return len(self.risk_factors) == len(other.risk_factors) and len(
            self.risk_controls
        ) == len(other.risk_controls)

    def __lt__(self, other) -> bool:
        """
        Сравнение сервисов по количеству факторов риска.

        Args:
            other: Другой сервис для сравнения

        Returns:
            True если у текущего сервиса меньше факторов риска
        """
        if not isinstance(other, RiskAssessmentService):
            return NotImplemented
        return len(self.risk_factors) < len(other.risk_factors)

    def __le__(self, other) -> bool:
        """
        Сравнение сервисов по количеству факторов риска (меньше или равно).

        Args:
            other: Другой сервис для сравнения

        Returns:
            True если у текущего сервиса меньше или равно факторов риска
        """
        if not isinstance(other, RiskAssessmentService):
            return NotImplemented
        return len(self.risk_factors) <= len(other.risk_factors)

    def __gt__(self, other) -> bool:
        """
        Сравнение сервисов по количеству факторов риска (больше).

        Args:
            other: Другой сервис для сравнения

        Returns:
            True если у текущего сервиса больше факторов риска
        """
        if not isinstance(other, RiskAssessmentService):
            return NotImplemented
        return len(self.risk_factors) > len(other.risk_factors)

    def __ge__(self, other) -> bool:
        """
        Сравнение сервисов по количеству факторов риска (больше или равно).

        Args:
            other: Другой сервис для сравнения

        Returns:
            True если у текущего сервиса больше или равно факторов риска
        """
        if not isinstance(other, RiskAssessmentService):
            return NotImplemented
        return len(self.risk_factors) >= len(other.risk_factors)

    def __iter__(self):
        """
        Итерация по факторам риска.

        Yields:
            Факторы риска
        """
        return iter(self.risk_factors.values())

    def __enter__(self):
        """
        Вход в контекстный менеджер.

        Returns:
            Сам сервис
        """
        self.logger.info("Вход в контекстный менеджер RiskAssessmentService")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из контекстного менеджера.

        Args:
            exc_type: Тип исключения
            exc_val: Значение исключения
            exc_tb: Трассировка исключения
        """
        if exc_type:
            self.logger.error(
                f"Ошибка в контекстном менеджере: {exc_type.__name__}: {exc_val}"
            )
        else:
            self.logger.info(
                "Выход из контекстного менеджера RiskAssessmentService"
            )
        return False

    def _initialize_default_risk_factors(self) -> None:
        """Инициализация факторов риска по умолчанию"""
        try:
            default_factors: List[Dict[str, Any]] = [
                {
                    "factor_id": "weak_passwords",
                    "name": "Слабые пароли",
                    "description": (
                        "Использование простых или повторяющихся паролей"
                    ),
                    "category": RiskCategory.AUTHENTICATION,
                    "weight": 0.8,
                    "impact_score": 0.7,
                    "likelihood_score": 0.6,
                },
                {
                    "factor_id": "no_mfa",
                    "name": "Отсутствие MFA",
                    "description": (
                        "Неиспользование многофакторной аутентификации"
                    ),
                    "category": RiskCategory.AUTHENTICATION,
                    "weight": 0.9,
                    "impact_score": 0.8,
                    "likelihood_score": 0.5,
                },
                {
                    "factor_id": "unsecured_wifi",
                    "name": "Незащищенный Wi-Fi",
                    "description": "Подключение к незащищенным сетям Wi-Fi",
                    "category": RiskCategory.NETWORK_SECURITY,
                    "weight": 0.7,
                    "impact_score": 0.6,
                    "likelihood_score": 0.7,
                },
                {
                    "factor_id": "outdated_software",
                    "name": "Устаревшее ПО",
                    "description": (
                        "Использование устаревшего программного обеспечения"
                    ),
                    "category": RiskCategory.DEVICE_SECURITY,
                    "weight": 0.6,
                    "impact_score": 0.7,
                    "likelihood_score": 0.8,
                },
                {
                    "factor_id": "suspicious_behavior",
                    "name": "Подозрительное поведение",
                    "description": (
                        "Аномальные паттерны поведения пользователей"
                    ),
                    "category": RiskCategory.USER_BEHAVIOR,
                    "weight": 0.5,
                    "impact_score": 0.5,
                    "likelihood_score": 0.4,
                },
                {
                    "factor_id": "data_exposure",
                    "name": "Утечка данных",
                    "description": "Потенциальная утечка персональных данных",
                    "category": RiskCategory.DATA_PROTECTION,
                    "weight": 0.9,
                    "impact_score": 0.9,
                    "likelihood_score": 0.3,
                },
                {
                    "factor_id": "third_party_access",
                    "name": "Доступ третьих лиц",
                    "description": (
                        "Неавторизованный доступ третьих лиц к данным"
                    ),
                    "category": RiskCategory.THIRD_PARTY,
                    "weight": 0.7,
                    "impact_score": 0.8,
                    "likelihood_score": 0.4,
                },
                {
                    "factor_id": "physical_access",
                    "name": "Физический доступ",
                    "description": (
                        "Незащищенный физический доступ к устройствам"
                    ),
                    "category": RiskCategory.PHYSICAL_SECURITY,
                    "weight": 0.4,
                    "impact_score": 0.6,
                    "likelihood_score": 0.3,
                },
            ]

            for factor_data in default_factors:
                factor = RiskFactor(
                    factor_id=str(factor_data["factor_id"]),
                    name=str(factor_data["name"]),
                    description=str(factor_data["description"]),
                    category=RiskCategory(factor_data["category"]),
                    weight=float(factor_data["weight"]),
                    impact_score=float(factor_data["impact_score"]),
                    likelihood_score=float(factor_data["likelihood_score"]),
                )
                factor.risk_score = self._calculate_risk_score(factor)
                self.risk_factors[factor.factor_id] = factor

            self.logger.info(
                f"Инициализировано {len(self.risk_factors)} факторов риска"
            )

        except Exception as e:
            self.logger.error(f"Ошибка инициализации факторов риска: {e}")

    def _initialize_risk_controls(self) -> None:
        """Инициализация средств контроля рисков"""
        try:
            self.risk_controls = {
                "authentication": {
                    "strong_passwords": {
                        "name": "Сильные пароли",
                        "description": "Использование сложных паролей",
                        "effectiveness": 0.8,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                    "mfa": {
                        "name": "Многофакторная аутентификация",
                        "description": "Включение MFA для всех аккаунтов",
                        "effectiveness": 0.9,
                        "cost": "medium",
                        "implementation": "1-2 weeks",
                    },
                    "password_manager": {
                        "name": "Менеджер паролей",
                        "description": "Использование менеджера паролей",
                        "effectiveness": 0.7,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                },
                "network_security": {
                    "vpn": {
                        "name": "VPN",
                        "description": "Использование VPN для публичных сетей",
                        "effectiveness": 0.8,
                        "cost": "medium",
                        "implementation": "1 week",
                    },
                    "firewall": {
                        "name": "Файрвол",
                        "description": "Настройка файрвола",
                        "effectiveness": 0.7,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                    "secure_wifi": {
                        "name": "Защищенный Wi-Fi",
                        "description": "Использование только защищенных сетей",
                        "effectiveness": 0.6,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                },
                "device_security": {
                    "updates": {
                        "name": "Обновления ПО",
                        "description": (
                            "Регулярное обновление программного обеспечения"
                        ),
                        "effectiveness": 0.8,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                    "antivirus": {
                        "name": "Антивирус",
                        "description": "Установка и обновление антивируса",
                        "effectiveness": 0.7,
                        "cost": "medium",
                        "implementation": "1 week",
                    },
                    "encryption": {
                        "name": "Шифрование",
                        "description": "Шифрование данных на устройствах",
                        "effectiveness": 0.9,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                },
                "data_protection": {
                    "backup": {
                        "name": "Резервное копирование",
                        "description": (
                            "Регулярное резервное копирование данных"
                        ),
                        "effectiveness": 0.8,
                        "cost": "low",
                        "implementation": "1 week",
                    },
                    "data_classification": {
                        "name": "Классификация данных",
                        "description": "Классификация и маркировка данных",
                        "effectiveness": 0.6,
                        "cost": "medium",
                        "implementation": "2-4 weeks",
                    },
                    "access_control": {
                        "name": "Контроль доступа",
                        "description": "Ограничение доступа к данным",
                        "effectiveness": 0.7,
                        "cost": "low",
                        "implementation": "immediate",
                    },
                },
            }

            self.logger.info("Инициализированы средства контроля рисков")

        except Exception as e:
            self.logger.error(f"Ошибка инициализации средств контроля: {e}")

    def _calculate_risk_score(self, factor: RiskFactor) -> float:
        """Вычисление балла риска"""
        try:
            # Формула: Risk = Impact × Likelihood × Weight
            risk_score = (
                factor.impact_score * factor.likelihood_score * factor.weight
            )
            return min(1.0, risk_score)

        except Exception as e:
            self.logger.error(f"Ошибка вычисления балла риска: {e}")
            return 0.0

    def assess_user_risk(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> RiskProfile:
        """
        Оценка рисков пользователя
        Args:
            user_id: ID пользователя
            user_data: Данные пользователя для анализа
        Returns:
            RiskProfile: Профиль риска пользователя
        """
        try:
            # Создаем профиль риска
            profile = RiskProfile(
                profile_id=f"risk_profile_{user_id}",
                user_id=user_id,
                risk_factors={},
                overall_risk_score=0.0,
                risk_level=RiskLevel.MINIMAL,
            )

            # Анализируем факторы риска
            for factor_id, factor in self.risk_factors.items():
                # Проверяем, применим ли фактор к пользователю
                if self._is_factor_applicable(factor, user_data):
                    # Обновляем оценки на основе данных пользователя
                    updated_factor = self._update_factor_scores(
                        factor, user_data
                    )
                    profile.risk_factors[factor_id] = updated_factor

            # Вычисляем общий балл риска
            profile.overall_risk_score = self._calculate_overall_risk_score(
                profile.risk_factors
            )
            profile.risk_level = self._determine_risk_level(
                profile.overall_risk_score
            )

            # Генерируем рекомендации по снижению рисков
            profile.mitigation_recommendations = (
                self._generate_mitigation_recommendations(profile)
            )

            # Создаем оценку риска
            assessment = RiskAssessment(
                assessment_id=f"assessment_{user_id}_{int(time.time())}",
                risk_id=f"user_risk_{user_id}",
                risk_name=f"Риски пользователя {user_id}",
                category=RiskCategory.USER_BEHAVIOR,
                level=profile.risk_level,
                status=RiskStatus.ASSESSED,
                risk_score=profile.overall_risk_score,
                impact_score=self._calculate_average_impact(
                    profile.risk_factors
                ),
                likelihood_score=self._calculate_average_likelihood(
                    profile.risk_factors
                ),
                description=(
                    f"Комплексная оценка рисков для пользователя {user_id}"
                ),
                threat_sources=[ThreatSource.INTERNAL, ThreatSource.EXTERNAL],
                affected_assets=self._identify_affected_assets(user_data),
                mitigation_measures=profile.mitigation_recommendations,
                residual_risk=profile.overall_risk_score
                * 0.3,  # Предполагаем 70% снижение после мер
            )

            profile.assessment_history.append(assessment)
            self.risk_assessments.append(assessment)

            # Сохраняем профиль
            self.risk_profiles[user_id] = profile

            # Создаем событие безопасности
            if profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                severity = (
                    IncidentSeverity.HIGH
                    if profile.risk_level == RiskLevel.CRITICAL
                    else IncidentSeverity.MEDIUM
                )
                security_event = SecurityEvent(
                    event_type="risk_assessment",
                    severity=severity,
                    description=(
                        f"Выявлен {profile.risk_level.value} уровень риска "
                        f"для пользователя {user_id}"
                    ),
                    source="RiskAssessment",
                )
                self.activity_log.append(security_event)

            self.logger.info(
                f"Оценка рисков завершена для пользователя {user_id}: "
                f"{profile.risk_level.value}"
            )
            return profile

        except Exception as e:
            self.logger.error(f"Ошибка оценки рисков пользователя: {e}")
            return RiskProfile(
                profile_id=f"error_profile_{user_id}",
                user_id=user_id,
                risk_factors={},
                overall_risk_score=1.0,
                risk_level=RiskLevel.CRITICAL,
            )

    def _is_factor_applicable(
        self, factor: RiskFactor, user_data: Dict[str, Any]
    ) -> bool:
        """Проверка применимости фактора риска к пользователю"""
        try:
            # Простая логика проверки применимости
            if factor.category == RiskCategory.AUTHENTICATION:
                return (
                    "password_strength" in user_data
                    or "mfa_enabled" in user_data
                )
            elif factor.category == RiskCategory.NETWORK_SECURITY:
                return (
                    "wifi_usage" in user_data
                    or "network_connections" in user_data
                )
            elif factor.category == RiskCategory.DEVICE_SECURITY:
                return (
                    "device_info" in user_data
                    or "software_updates" in user_data
                )
            elif factor.category == RiskCategory.USER_BEHAVIOR:
                return (
                    "behavior_patterns" in user_data
                    or "activity_log" in user_data
                )
            elif factor.category == RiskCategory.DATA_PROTECTION:
                return (
                    "data_access" in user_data or "file_sharing" in user_data
                )
            else:
                return True  # По умолчанию применим

        except Exception as e:
            self.logger.error(f"Ошибка проверки применимости фактора: {e}")
            return False

    def _update_factor_scores(
        self, factor: RiskFactor, user_data: Dict[str, Any]
    ) -> RiskFactor:
        """Обновление оценок фактора на основе данных пользователя"""
        try:
            updated_factor = RiskFactor(
                factor_id=factor.factor_id,
                name=factor.name,
                description=factor.description,
                category=factor.category,
                weight=factor.weight,
                impact_score=factor.impact_score,
                likelihood_score=factor.likelihood_score,
            )

            # Обновляем оценки на основе данных пользователя
            if factor.category == RiskCategory.AUTHENTICATION:
                if "password_strength" in user_data:
                    strength = user_data["password_strength"]
                    if strength < 0.3:  # Слабый пароль
                        updated_factor.likelihood_score = min(
                            1.0, factor.likelihood_score + 0.3
                        )
                    elif strength > 0.8:  # Сильный пароль
                        updated_factor.likelihood_score = max(
                            0.1, factor.likelihood_score - 0.2
                        )

                if "mfa_enabled" in user_data and not user_data["mfa_enabled"]:
                    updated_factor.likelihood_score = min(
                        1.0, factor.likelihood_score + 0.4
                    )

            elif factor.category == RiskCategory.NETWORK_SECURITY:
                if "wifi_usage" in user_data:
                    unsecured_ratio = user_data["wifi_usage"].get(
                        "unsecured_ratio", 0
                    )
                    updated_factor.likelihood_score = min(
                        1.0, factor.likelihood_score + unsecured_ratio * 0.5
                    )

            elif factor.category == RiskCategory.DEVICE_SECURITY:
                if "software_updates" in user_data:
                    outdated_ratio = user_data["software_updates"].get(
                        "outdated_ratio", 0
                    )
                    updated_factor.likelihood_score = min(
                        1.0, factor.likelihood_score + outdated_ratio * 0.4
                    )

            elif factor.category == RiskCategory.USER_BEHAVIOR:
                if "behavior_patterns" in user_data:
                    anomalies = user_data["behavior_patterns"].get(
                        "anomalies_count", 0
                    )
                    if anomalies > 5:
                        updated_factor.likelihood_score = min(
                            1.0, factor.likelihood_score + 0.3
                        )

            # Пересчитываем балл риска
            updated_factor.risk_score = self._calculate_risk_score(
                updated_factor
            )
            updated_factor.last_assessed = datetime.now()

            return updated_factor

        except Exception as e:
            self.logger.error(f"Ошибка обновления оценок фактора: {e}")
            return factor

    def _calculate_overall_risk_score(
        self, risk_factors: Dict[str, RiskFactor]
    ) -> float:
        """Вычисление общего балла риска"""
        try:
            if not risk_factors:
                return 0.0

            # Взвешенная сумма рисков по категориям
            category_scores: Dict[RiskCategory, float] = {}

            for factor in risk_factors.values():
                category = factor.category
                if category not in category_scores:
                    category_scores[category] = 0.0
                category_scores[category] += factor.risk_score

            # Применяем веса категорий
            weighted_score = 0.0
            total_weight = 0.0

            for category, score in category_scores.items():
                weight = self.assessment_weights.get(category, 0.1)
                weighted_score += score * weight
                total_weight += weight

            return weighted_score / total_weight if total_weight > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Ошибка вычисления общего балла риска: {e}")
            return 0.0

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Определение уровня риска"""
        try:
            for level, threshold in self.risk_thresholds.items():
                if risk_score >= threshold:
                    return level
            return RiskLevel.MINIMAL

        except Exception as e:
            self.logger.error(f"Ошибка определения уровня риска: {e}")
            return RiskLevel.MEDIUM

    def _generate_mitigation_recommendations(
        self, profile: RiskProfile
    ) -> List[str]:
        """Генерация рекомендаций по снижению рисков"""
        try:
            recommendations = []

            # Анализируем факторы риска и генерируем рекомендации
            for factor_id, factor in profile.risk_factors.items():
                if factor.risk_score > 0.5:  # Высокий риск
                    if factor.category == RiskCategory.AUTHENTICATION:
                        if "weak_passwords" in factor_id:
                            recommendations.append(
                                "Используйте сложные пароли с комбинацией "
                                "букв, цифр и символов"
                            )
                        if "no_mfa" in factor_id:
                            recommendations.append(
                                "Включите многофакторную аутентификацию "
                                "для всех аккаунтов"
                            )

                    elif factor.category == RiskCategory.NETWORK_SECURITY:
                        if "unsecured_wifi" in factor_id:
                            recommendations.append(
                                "Используйте VPN при подключении к публичным "
                                "Wi-Fi сетям"
                            )

                    elif factor.category == RiskCategory.DEVICE_SECURITY:
                        if "outdated_software" in factor_id:
                            recommendations.append(
                                "Регулярно обновляйте программное обеспечение "
                                "и операционную систему"
                            )

                    elif factor.category == RiskCategory.DATA_PROTECTION:
                        if "data_exposure" in factor_id:
                            recommendations.append(
                                "Ограничьте доступ к персональным данным "
                                "и используйте шифрование"
                            )

            # Добавляем общие рекомендации
            if profile.overall_risk_score > 0.7:
                recommendations.extend(
                    [
                        "Проведите комплексный аудит безопасности",
                        "Обучите всех членов семьи основам кибербезопасности",
                        "Настройте мониторинг безопасности",
                    ]
                )

            return list(set(recommendations))  # Убираем дубликаты

        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендаций: {e}")
            return ["Проведите консультацию со специалистом по безопасности"]

    def _calculate_average_impact(
        self, risk_factors: Dict[str, RiskFactor]
    ) -> float:
        """Вычисление среднего воздействия"""
        try:
            if not risk_factors:
                return 0.0

            total_impact = sum(
                factor.impact_score for factor in risk_factors.values()
            )
            return total_impact / len(risk_factors)

        except Exception as e:
            self.logger.error(f"Ошибка вычисления среднего воздействия: {e}")
            return 0.0

    def _calculate_average_likelihood(
        self, risk_factors: Dict[str, RiskFactor]
    ) -> float:
        """Вычисление средней вероятности"""
        try:
            if not risk_factors:
                return 0.0

            total_likelihood = sum(
                factor.likelihood_score for factor in risk_factors.values()
            )
            return total_likelihood / len(risk_factors)

        except Exception as e:
            self.logger.error(f"Ошибка вычисления средней вероятности: {e}")
            return 0.0

    def _identify_affected_assets(
        self, user_data: Dict[str, Any]
    ) -> List[str]:
        """Идентификация затронутых активов"""
        try:
            assets = []

            if "devices" in user_data:
                assets.extend(user_data["devices"])

            if "accounts" in user_data:
                assets.extend(
                    [f"account_{acc}" for acc in user_data["accounts"]]
                )

            if "data_types" in user_data:
                assets.extend([f"data_{dt}" for dt in user_data["data_types"]])

            return assets if assets else ["user_data", "devices", "accounts"]

        except Exception as e:
            self.logger.error(f"Ошибка идентификации активов: {e}")
            return ["unknown_assets"]

    def get_risk_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Получение сводки рисков пользователя
        Args:
            user_id: ID пользователя
        Returns:
            Dict[str, Any]: Сводка рисков
        """
        try:
            if user_id not in self.risk_profiles:
                return {
                    "user_id": user_id,
                    "message": "Профиль риска не найден",
                }

            profile = self.risk_profiles[user_id]

            # Группируем риски по категориям
            risks_by_category: Dict[str, List[Dict[str, Any]]] = {}
            for factor_id, factor in profile.risk_factors.items():
                category = factor.category.value
                if category not in risks_by_category:
                    risks_by_category[category] = []

                risks_by_category[category].append(
                    {
                        "factor_id": factor_id,
                        "name": factor.name,
                        "risk_score": factor.risk_score,
                        "impact_score": factor.impact_score,
                        "likelihood_score": factor.likelihood_score,
                    }
                )

            # Сортируем риски по баллу
            for category in risks_by_category:
                risks_by_category[category].sort(
                    key=lambda x: x["risk_score"], reverse=True
                )

            return {
                "user_id": user_id,
                "overall_risk_score": profile.overall_risk_score,
                "risk_level": profile.risk_level.value,
                "risks_by_category": risks_by_category,
                "mitigation_recommendations": (
                    profile.mitigation_recommendations
                ),
                "last_assessment": profile.last_assessment.isoformat(),
                "total_factors": len(profile.risk_factors),
                "high_risk_factors": len(
                    [
                        f
                        for f in profile.risk_factors.values()
                        if f.risk_score > 0.7
                    ]
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения сводки рисков: {e}")
            return {"user_id": user_id, "error": str(e)}

    def get_risk_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Получение трендов рисков
        Args:
            days: Количество дней для анализа
        Returns:
            Dict[str, Any]: Тренды рисков
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            recent_assessments = [
                a
                for a in self.risk_assessments
                if a.assessment_date >= start_date
            ]

            if not recent_assessments:
                return {
                    "period_days": days,
                    "message": "Нет данных за указанный период",
                }

            # Анализируем тренды
            risk_levels = [a.level.value for a in recent_assessments]
            risk_scores = [a.risk_score for a in recent_assessments]

            # Статистики
            level_counts: Dict[str, int] = {}
            for level in risk_levels:
                level_counts[level] = level_counts.get(level, 0) + 1

            avg_risk_score = (
                statistics.mean(risk_scores) if risk_scores else 0.0
            )
            max_risk_score = max(risk_scores) if risk_scores else 0.0
            min_risk_score = min(risk_scores) if risk_scores else 0.0

            # Тренд (упрощенный)
            if len(risk_scores) >= 2:
                trend = (
                    "increasing"
                    if risk_scores[-1] > risk_scores[0]
                    else "decreasing"
                )
            else:
                trend = "stable"

            return {
                "period_days": days,
                "total_assessments": len(recent_assessments),
                "average_risk_score": avg_risk_score,
                "max_risk_score": max_risk_score,
                "min_risk_score": min_risk_score,
                "risk_level_distribution": level_counts,
                "trend": trend,
                "high_risk_periods": len([s for s in risk_scores if s > 0.7]),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения трендов рисков: {e}")
            return {"error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса Risk Assessment
        Returns:
            Dict[str, Any]: Статус сервиса
        """
        try:
            # Получаем базовый статус
            base_status = super().get_status()

            # Добавляем специфичную информацию
            status = {
                **base_status,
                "total_risk_factors": len(self.risk_factors),
                "total_assessments": len(self.risk_assessments),
                "total_profiles": len(self.risk_profiles),
                "risk_factors_by_category": {
                    category.value: len(
                        [
                            f
                            for f in self.risk_factors.values()
                            if f.category == category
                        ]
                    )
                    for category in RiskCategory
                },
                "assessments_by_level": {
                    level.value: len(
                        [a for a in self.risk_assessments if a.level == level]
                    )
                    for level in RiskLevel
                },
                "high_risk_profiles": len(
                    [
                        p
                        for p in self.risk_profiles.values()
                        if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                    ]
                ),
                "avg_risk_score": (
                    statistics.mean(
                        [
                            p.overall_risk_score
                            for p in self.risk_profiles.values()
                        ]
                    )
                    if self.risk_profiles
                    else 0.0
                ),
                "risk_controls_available": len(self.risk_controls),
                "assessment_weights": {
                    k.value: v for k, v in self.assessment_weights.items()
                },
            }

            return status

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
