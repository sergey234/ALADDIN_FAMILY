# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Child Protection
Система защиты детей для семей
Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-10
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase
from core.security_base import IncidentSeverity, SecurityEvent

# Импорт психологической поддержки
try:
    from security.ai_agents.psychological_support_agent import (
        PsychologicalSupportAgent,
        EmotionalState,
        AgeGroup,
        SupportType
    )
    PSYCHOLOGICAL_SUPPORT_AVAILABLE = True
except ImportError:
    PSYCHOLOGICAL_SUPPORT_AVAILABLE = False


class ProtectionLevel(Enum):
    """Уровни защиты детей"""

    BASIC = "basic"  # Базовая защита
    MODERATE = "moderate"  # Умеренная защита
    STRICT = "strict"  # Строгая защита
    MAXIMUM = "maximum"  # Максимальная защита


class ContentCategory(Enum):
    """Категории контента"""

    EDUCATIONAL = "educational"  # Образовательный
    ENTERTAINMENT = "entertainment"  # Развлекательный
    SOCIAL = "social"  # Социальные сети
    GAMING = "gaming"  # Игры
    SHOPPING = "shopping"  # Покупки
    NEWS = "news"  # Новости
    ADULT = "adult"  # Взрослый контент
    VIOLENCE = "violence"  # Насилие
    INAPPROPRIATE = "inappropriate"  # Неподходящий


class ThreatLevel(Enum):
    """Уровни угроз для детей"""

    SAFE = "safe"  # Безопасно
    LOW = "low"  # Низкий риск
    MEDIUM = "medium"  # Средний риск
    HIGH = "high"  # Высокий риск
    DANGEROUS = "dangerous"  # Опасно


@dataclass
class ChildProfile:
    """Профиль ребенка"""

    child_id: str
    name: str
    age: int
    protection_level: ProtectionLevel
    allowed_categories: List[ContentCategory]
    blocked_categories: List[ContentCategory]
    time_limits: Dict[str, int]  # Лимиты времени по категориям
    parent_controls: Dict[str, Any]
    last_activity: datetime
    total_screen_time: int = 0  # Общее время экрана в минутах
    violations: List[str] = field(default_factory=list)


@dataclass
class ContentFilter:
    """Фильтр контента"""

    filter_id: str
    name: str
    category: ContentCategory
    keywords: List[str]
    domains: List[str]
    enabled: bool = True
    severity: int = 1  # 1-5, где 5 - самый строгий


@dataclass
class ActivityLog:
    """Лог активности ребенка"""

    log_id: str
    child_id: str
    activity_type: str
    content_category: ContentCategory
    timestamp: datetime
    duration: int  # В минутах
    details: Dict[str, Any]
    flagged: bool = False


class ChildProtection(SecurityBase):
    """
    Система защиты детей для семей
    Комплексная защита детей в цифровой среде
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ChildProtection", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.child_profiles: Dict[str, ChildProfile] = {}
        self.content_filters: Dict[str, ContentFilter] = {}
        self.activity_logs: List[ActivityLog] = []
        self.blocked_domains: List[str] = []
        self.allowed_domains: List[str] = []

        # Конфигурация
        self.max_screen_time = 120  # Максимальное время экрана (минуты)
        self.violation_threshold = 3  # Порог нарушений
        self.alert_parents = True  # Уведомлять родителей

        # Психологическая поддержка
        if PSYCHOLOGICAL_SUPPORT_AVAILABLE:
            self.psychological_support = PsychologicalSupportAgent()
        else:
            self.psychological_support = None

        # Инициализация
        self._initialize_default_filters()
        self._initialize_default_profiles()

    def _initialize_default_filters(self) -> None:
        """Инициализация фильтров по умолчанию"""
        default_filters = [
            {
                "filter_id": "adult_content",
                "name": "Взрослый контент",
                "category": ContentCategory.ADULT,
                "keywords": ["adult", "xxx", "porn", "sex"],
                "domains": ["adult-site.com", "xxx.com"],
            },
            {
                "filter_id": "violence",
                "name": "Насилие",
                "category": ContentCategory.VIOLENCE,
                "keywords": ["violence", "blood", "kill", "fight"],
                "domains": ["violent-games.com"],
            },
            {
                "filter_id": "gambling",
                "name": "Азартные игры",
                "category": ContentCategory.INAPPROPRIATE,
                "keywords": ["casino", "gambling", "bet", "poker"],
                "domains": ["casino.com", "betting.com"],
            },
        ]

        for filter_data in default_filters:
            self._create_content_filter(filter_data)

    def _initialize_default_profiles(self) -> None:
        """Инициализация профилей по умолчанию"""
        default_children = [
            {
                "child_id": "child_1",
                "name": "Анна",
                "age": 12,
                "protection_level": ProtectionLevel.MODERATE,
                "allowed_categories": [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                    ContentCategory.GAMING,
                ],
                "blocked_categories": [
                    ContentCategory.ADULT,
                    ContentCategory.VIOLENCE,
                    ContentCategory.INAPPROPRIATE,
                ],
                "time_limits": {
                    "gaming": 60,
                    "entertainment": 90,
                    "social": 30,
                },
            },
            {
                "child_id": "child_2",
                "name": "Максим",
                "age": 8,
                "protection_level": ProtectionLevel.STRICT,
                "allowed_categories": [
                    ContentCategory.EDUCATIONAL,
                    ContentCategory.ENTERTAINMENT,
                ],
                "blocked_categories": [
                    ContentCategory.ADULT,
                    ContentCategory.VIOLENCE,
                    ContentCategory.INAPPROPRIATE,
                    ContentCategory.SOCIAL,
                    ContentCategory.GAMING,
                ],
                "time_limits": {"entertainment": 60, "educational": 120},
            },
        ]

        for child_data in default_children:
            self._create_child_profile(child_data)

    def _create_content_filter(self, filter_data: Dict[str, Any]) -> None:
        """Создание фильтра контента"""
        content_filter = ContentFilter(
            filter_id=filter_data["filter_id"],
            name=filter_data["name"],
            category=filter_data["category"],
            keywords=filter_data["keywords"],
            domains=filter_data["domains"],
        )
        self.content_filters[filter_data["filter_id"]] = content_filter

    def _create_child_profile(self, child_data: Dict[str, Any]) -> None:
        """Создание профиля ребенка"""
        profile = ChildProfile(
            child_id=child_data["child_id"],
            name=child_data["name"],
            age=child_data["age"],
            protection_level=child_data["protection_level"],
            allowed_categories=child_data["allowed_categories"],
            blocked_categories=child_data["blocked_categories"],
            time_limits=child_data["time_limits"],
            parent_controls={},
            last_activity=datetime.now(),
        )
        self.child_profiles[child_data["child_id"]] = profile

    def add_child_profile(
        self,
        child_id: str,
        name: str,
        age: int,
        protection_level: ProtectionLevel,
    ) -> bool:
        """Добавление профиля ребенка"""
        if child_id in self.child_profiles:
            return False

        # Определяем категории на основе возраста
        if age < 6:
            allowed = [ContentCategory.EDUCATIONAL]
            blocked = [
                ContentCategory.ADULT,
                ContentCategory.VIOLENCE,
                ContentCategory.INAPPROPRIATE,
                ContentCategory.SOCIAL,
                ContentCategory.GAMING,
            ]
            time_limits = {"educational": 60}
        elif age < 12:
            allowed = [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
            ]
            blocked = [
                ContentCategory.ADULT,
                ContentCategory.VIOLENCE,
                ContentCategory.INAPPROPRIATE,
                ContentCategory.SOCIAL,
            ]
            time_limits = {"educational": 120, "entertainment": 90}
        elif age < 16:
            allowed = [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
                ContentCategory.GAMING,
                ContentCategory.SOCIAL,
            ]
            blocked = [
                ContentCategory.ADULT,
                ContentCategory.VIOLENCE,
                ContentCategory.INAPPROPRIATE,
            ]
            time_limits = {"gaming": 90, "entertainment": 120, "social": 60}
        else:
            allowed = [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
                ContentCategory.GAMING,
                ContentCategory.SOCIAL,
                ContentCategory.NEWS,
            ]
            blocked = [ContentCategory.ADULT]
            time_limits = {"gaming": 120, "entertainment": 180, "social": 120}

        profile = ChildProfile(
            child_id=child_id,
            name=name,
            age=age,
            protection_level=protection_level,
            allowed_categories=allowed,
            blocked_categories=blocked,
            time_limits=time_limits,
            parent_controls={},
            last_activity=datetime.now(),
        )

        self.child_profiles[child_id] = profile
        return True

    def check_content_access(
        self, child_id: str, url: str, content_category: ContentCategory
    ) -> Dict[str, Any]:
        """Проверка доступа к контенту"""
        if child_id not in self.child_profiles:
            return {
                "allowed": False,
                "reason": "Профиль ребенка не найден",
                "action": "block",
            }

        profile = self.child_profiles[child_id]

        # Проверка категории контента
        if content_category in profile.blocked_categories:
            self._log_violation(
                child_id,
                f"Попытка доступа к заблокированной категории: "
                f"{content_category.value}",
            )
            return {
                "allowed": False,
                "reason": f"Категория {content_category.value} заблокирована",
                "action": "block",
            }

        # Проверка домена
        for filter_id, content_filter in self.content_filters.items():
            if not content_filter.enabled:
                continue

            if content_category == content_filter.category:
                for domain in content_filter.domains:
                    if domain in url:
                        self._log_violation(
                            child_id,
                            f"Попытка доступа к заблокированному домену: "
                            f"{domain}",
                        )
                        return {
                            "allowed": False,
                            "reason": f"Домен {domain} заблокирован",
                            "action": "block",
                        }

        # Проверка времени экрана
        if not self._check_screen_time_limits(child_id, content_category):
            return {
                "allowed": False,
                "reason": "Превышен лимит времени экрана",
                "action": "block",
            }

        # Логирование разрешенного доступа
        self._log_activity(child_id, "content_access", content_category, url)

        return {
            "allowed": True,
            "reason": "Доступ разрешен",
            "action": "allow",
        }

    def _check_screen_time_limits(
        self, child_id: str, content_category: ContentCategory
    ) -> bool:
        """Проверка лимитов времени экрана"""
        profile = self.child_profiles[child_id]

        # Получаем время, потраченное на эту категорию сегодня
        category_time = self._get_category_time_today(
            child_id, content_category
        )

        # Проверяем лимит для категории
        if content_category.value in profile.time_limits:
            limit = profile.time_limits[content_category.value]
            if category_time >= limit:
                return False

        # Проверяем общий лимит времени экрана
        total_time = self._get_total_screen_time_today(child_id)
        if total_time >= self.max_screen_time:
            return False

        return True

    def _get_category_time_today(
        self, child_id: str, content_category: ContentCategory
    ) -> int:
        """Получение времени, потраченного на категорию сегодня"""
        today = datetime.now().date()
        total_time = 0

        for log in self.activity_logs:
            if (
                log.child_id == child_id
                and log.content_category == content_category
                and log.timestamp.date() == today
            ):
                total_time += log.duration

        return total_time

    def _get_total_screen_time_today(self, child_id: str) -> int:
        """Получение общего времени экрана сегодня"""
        today = datetime.now().date()
        total_time = 0

        for log in self.activity_logs:
            if log.child_id == child_id and log.timestamp.date() == today:
                total_time += log.duration

        return total_time

    def _log_violation(self, child_id: str, violation: str) -> None:
        """Логирование нарушения"""
        if child_id in self.child_profiles:
            self.child_profiles[child_id].violations.append(violation)

        # Создаем событие безопасности
        SecurityEvent(
            event_type="child_protection_violation",
            severity=IncidentSeverity.MEDIUM,
            description=f"Нарушение защиты ребенка {child_id}: {violation}",
            source="ChildProtection",
            timestamp=datetime.now(),
        )

        self.logger.warning(
            f"Нарушение защиты ребенка {child_id}: {violation}"
        )

        # Уведомляем родителей
        if self.alert_parents:
            self._notify_parents(child_id, violation)

    def _log_activity(
        self,
        child_id: str,
        activity_type: str,
        content_category: ContentCategory,
        details: str,
    ) -> None:
        """Логирование активности"""
        log = ActivityLog(
            log_id=f"log_{int(time.time())}",
            child_id=child_id,
            activity_type=activity_type,
            content_category=content_category,
            timestamp=datetime.now(),
            duration=1,  # Минимальная длительность
            details={"url": details},
        )

        self.activity_logs.append(log)

        # Обновляем профиль ребенка
        if child_id in self.child_profiles:
            self.child_profiles[child_id].last_activity = datetime.now()
            self.child_profiles[child_id].total_screen_time += 1

    def _notify_parents(self, child_id: str, violation: str) -> None:
        """Уведомление родителей о нарушении"""
        # Здесь должна быть логика уведомления родителей
        # Например, отправка email, push-уведомления и т.д.
        self.logger.info(
            f"Уведомление родителям о нарушении {child_id}: {violation}"
        )

    def get_child_report(self, child_id: str) -> Dict[str, Any]:
        """Получение отчета о ребенке"""
        if child_id not in self.child_profiles:
            return {"error": "Профиль ребенка не найден"}

        profile = self.child_profiles[child_id]
        today = datetime.now().date()

        # Статистика за сегодня
        today_activities = [
            log
            for log in self.activity_logs
            if log.child_id == child_id and log.timestamp.date() == today
        ]

        category_stats = {}
        for log in today_activities:
            category = log.content_category.value
            if category not in category_stats:
                category_stats[category] = {"time": 0, "visits": 0}
            category_stats[category]["time"] += log.duration
            category_stats[category]["visits"] += 1

        return {
            "child_id": child_id,
            "name": profile.name,
            "age": profile.age,
            "protection_level": profile.protection_level.value,
            "total_screen_time_today": self._get_total_screen_time_today(
                child_id
            ),
            "category_statistics": category_stats,
            "violations_today": len(
                [v for v in profile.violations if "сегодня" in v.lower()]
            ),
            "last_activity": profile.last_activity.isoformat(),
            "recommendations": self._generate_recommendations(profile),
        }

    def _generate_recommendations(self, profile: ChildProfile) -> List[str]:
        """Генерация рекомендаций для родителей"""
        recommendations = []

        # Рекомендации по времени экрана
        total_time = self._get_total_screen_time_today(profile.child_id)
        if total_time > self.max_screen_time * 0.8:
            recommendations.append(
                f"Время экрана ({total_time} мин) близко к лимиту. "
                "Рекомендуется ограничить активность."
            )

        # Рекомендации по нарушениям
        if len(profile.violations) > self.violation_threshold:
            recommendations.append(
                f"Много нарушений ({len(profile.violations)}). "
                "Рекомендуется усилить контроль."
            )

        # Рекомендации по возрасту
        if (
            profile.age < 12
            and ContentCategory.SOCIAL in profile.allowed_categories
        ):
            recommendations.append(
                "Социальные сети не рекомендуются для детей младше 12 лет."
            )

        return recommendations

    def update_protection_level(
        self, child_id: str, new_level: ProtectionLevel
    ) -> bool:
        """Обновление уровня защиты"""
        if child_id not in self.child_profiles:
            return False

        profile = self.child_profiles[child_id]
        profile.protection_level = new_level

        # Обновляем категории в зависимости от уровня защиты
        if new_level == ProtectionLevel.MAXIMUM:
            profile.allowed_categories = [ContentCategory.EDUCATIONAL]
            profile.blocked_categories = [
                ContentCategory.ADULT,
                ContentCategory.VIOLENCE,
                ContentCategory.INAPPROPRIATE,
                ContentCategory.SOCIAL,
                ContentCategory.GAMING,
                ContentCategory.ENTERTAINMENT,
            ]
        elif new_level == ProtectionLevel.STRICT:
            profile.allowed_categories = [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
            ]
            profile.blocked_categories = [
                ContentCategory.ADULT,
                ContentCategory.VIOLENCE,
                ContentCategory.INAPPROPRIATE,
                ContentCategory.SOCIAL,
                ContentCategory.GAMING,
            ]

        return True

    def add_content_filter(
        self,
        filter_id: str,
        name: str,
        category: ContentCategory,
        keywords: List[str],
        domains: List[str],
    ) -> bool:
        """Добавление фильтра контента"""
        if filter_id in self.content_filters:
            return False

        content_filter = ContentFilter(
            filter_id=filter_id,
            name=name,
            category=category,
            keywords=keywords,
            domains=domains,
        )

        self.content_filters[filter_id] = content_filter
        return True

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        total_children = len(self.child_profiles)
        total_filters = len(self.content_filters)
        total_logs = len(self.activity_logs)

        # Статистика нарушений
        total_violations = sum(
            len(profile.violations) for profile in self.child_profiles.values()
        )

        return {
            "status": "active",
            "total_children": total_children,
            "total_filters": total_filters,
            "total_activity_logs": total_logs,
            "total_violations": total_violations,
            "max_screen_time": self.max_screen_time,
            "violation_threshold": self.violation_threshold,
            "last_updated": datetime.now().isoformat(),
        }

    def reset_daily_limits(self) -> None:
        """Сброс дневных лимитов"""
        for profile in self.child_profiles.values():
            profile.violations = []
            profile.total_screen_time = 0

        # Очищаем старые логи (старше 30 дней)
        cutoff_date = datetime.now() - timedelta(days=30)
        self.activity_logs = [
            log for log in self.activity_logs if log.timestamp > cutoff_date
        ]

    def get_family_dashboard(self) -> Dict[str, Any]:
        """Получение данных для семейного дашборда"""
        children_data = []
        for child_id, profile in self.child_profiles.items():
            report = self.get_child_report(child_id)
            children_data.append(report)

        return {
            "children": children_data,
            "system_status": self.get_status(),
            "recommendations": self._get_family_recommendations(),
        }

    def _get_family_recommendations(self) -> List[str]:
        """Получение рекомендаций для семьи"""
        recommendations = []

        # Общие рекомендации
        if len(self.child_profiles) > 1:
            recommendations.append(
                "Установите одинаковые правила для всех детей в семье."
            )

        # Рекомендации по времени
        total_screen_time = sum(
            self._get_total_screen_time_today(child_id)
            for child_id in self.child_profiles.keys()
        )

        if total_screen_time > self.max_screen_time * len(self.child_profiles):
            recommendations.append(
                "Общее время экрана семьи превышает рекомендуемые нормы."
            )

        return recommendations

    # Психологическая поддержка
    def analyze_child_emotional_state(
        self,
        child_id: str,
        text_input: str,
        behavior_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Анализ эмоционального состояния ребенка"""
        if not self.psychological_support:
            return {"error": "Психологическая поддержка недоступна"}

        try:
            # Создаем профиль ребенка если его нет
            if child_id not in self.child_profiles:
                return {"error": "Профиль ребенка не найден"}

            profile = self.child_profiles[child_id]

            # Определяем возрастную группу
            if profile.age <= 6:
                age_group = AgeGroup.CHILD_3_6
            elif profile.age <= 12:
                age_group = AgeGroup.CHILD_7_12
            else:
                age_group = AgeGroup.TEEN_13_17

            # Создаем профиль в системе психологической поддержки
            if not self.psychological_support.user_profiles.get(child_id):
                self.psychological_support.create_user_profile(
                    child_id, profile.name, profile.age, age_group
                )

            # Анализируем эмоциональное состояние
            analysis = self.psychological_support.analyze_emotional_state(
                child_id, text_input, behavior_data
            )

            # Если высокий уровень риска, уведомляем родителей
            if analysis.get("risk_level") in ["high", "critical"]:
                self._notify_parents_psychological_concern(child_id, analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Ошибка анализа эмоционального состояния: {e}")
            return {"error": str(e)}

    def provide_psychological_support(
        self, child_id: str, support_type: str = "emotional"
    ) -> Dict[str, Any]:
        """Предоставление психологической поддержки ребенку"""
        if not self.psychological_support:
            return {"error": "Психологическая поддержка недоступна"}

        try:
            if child_id not in self.child_profiles:
                return {"error": "Профиль ребенка не найден"}

            profile = self.child_profiles[child_id]

            # Определяем возрастную группу
            if profile.age <= 6:
                age_group = AgeGroup.CHILD_3_6
            elif profile.age <= 12:
                age_group = AgeGroup.CHILD_7_12
            else:
                age_group = AgeGroup.TEEN_13_17

            # Определяем тип поддержки
            support_type_enum = SupportType.EMOTIONAL
            if support_type == "behavioral":
                support_type_enum = SupportType.BEHAVIORAL
            elif support_type == "educational":
                support_type_enum = SupportType.EDUCATIONAL
            elif support_type == "social":
                support_type_enum = SupportType.SOCIAL

            # Предоставляем поддержку
            result = self.psychological_support.provide_emotional_support(
                child_id, age_group, EmotionalState.CALM, support_type_enum
            )

            # Логируем поддержку
            self._log_activity(
                child_id, "psychological_support", ContentCategory.EDUCATIONAL,
                f"Психологическая поддержка: {support_type}"
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Ошибка предоставления психологической поддержки: {e}"
            )
            return {"error": str(e)}

    def get_psychological_profile(self, child_id: str) -> Dict[str, Any]:
        """Получение психологического профиля ребенка"""
        if not self.psychological_support:
            return {"error": "Психологическая поддержка недоступна"}

        try:
            return self.psychological_support.get_user_psychological_profile(
                child_id
            )
        except Exception as e:
            self.logger.error(
                f"Ошибка получения психологического профиля: {e}"
            )
            return {"error": str(e)}

    def emergency_psychological_support(
        self, child_id: str, crisis_type: str
    ) -> Dict[str, Any]:
        """Экстренная психологическая поддержка"""
        if not self.psychological_support:
            return {"error": "Психологическая поддержка недоступна"}

        try:
            # Активируем экстренную поддержку
            result = self.psychological_support.emergency_support(
                child_id, crisis_type
            )

            # Немедленно уведомляем родителей
            self._notify_parents_emergency(child_id, crisis_type)

            return result

        except Exception as e:
            self.logger.error(
                f"Ошибка экстренной психологической поддержки: {e}"
            )
            return {"error": str(e)}

    def _notify_parents_psychological_concern(
        self, child_id: str, analysis: Dict[str, Any]
    ) -> None:
        """Уведомление родителей о психологических проблемах"""
        if not self.alert_parents:
            return

        concern_level = analysis.get("risk_level", "low")
        dominant_emotion = analysis.get("dominant_emotion", "unknown")

        message = (
            f"Психологическая тревога для {child_id}: "
            f"{dominant_emotion} (уровень: {concern_level})"
        )

        self.logger.warning(message)

        # Здесь можно добавить отправку уведомлений родителям
        # Например, через email, SMS, push-уведомления

    def _notify_parents_emergency(
        self, child_id: str, crisis_type: str
    ) -> None:
        """Уведомление родителей об экстренной ситуации"""
        if not self.alert_parents:
            return

        message = (
            f"ЭКСТРЕННАЯ СИТУАЦИЯ для {child_id}: {crisis_type}"
        )

        self.logger.critical(message)

        # Здесь можно добавить немедленную отправку уведомлений
        # Например, через все доступные каналы связи
