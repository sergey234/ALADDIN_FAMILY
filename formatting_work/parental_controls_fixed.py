# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Parental Controls
Централизованная система родительского контроля
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-02
"""
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.base import SecurityBase
from core.security_base import IncidentSeverity, SecurityEvent
from security.family.child_protection import (
    ChildProtection,
    ContentCategory,
    ThreatLevel,
)
from security.family.elderly_protection import ElderlyProtection
from security.family.family_profile_manager import (
    AgeGroup,
    FamilyProfileManager,
    FamilyRole,
)


class ControlType(Enum):
    """Типы родительского контроля"""

    TIME_LIMIT = "time_limit"  # Ограничение времени
    CONTENT_FILTER = "content_filter"  # Фильтрация контента
    APP_CONTROL = "app_control"  # Контроль приложений
    LOCATION_TRACKING = "location_tracking"  # Отслеживание местоположения
    EMERGENCY_CONTROL = "emergency_control"  # Экстренный контроль
    COMMUNICATION_MONITOR = "communication_monitor"  # Мониторинг общения
    IPV6_PROTECTION = "ipv6_protection"  # IPv6 защита для детей
    KILL_SWITCH = "kill_switch"  # Экстренное отключение


class ControlStatus(Enum):
    """Статус контроля"""

    ACTIVE = "active"  # Активен
    INACTIVE = "inactive"  # Неактивен
    SUSPENDED = "suspended"  # Приостановлен
    EMERGENCY = "emergency"  # Экстренный режим


class NotificationType(Enum):
    """Типы уведомлений"""

    TIME_LIMIT_REACHED = "time_limit_reached"  # Превышено время
    SUSPICIOUS_ACTIVITY = "suspicious_activity"  # Подозрительная активность
    EMERGENCY_ALERT = "emergency_alert"  # Экстренное уведомление
    DAILY_REPORT = "daily_report"  # Ежедневный отчет
    WEEKLY_SUMMARY = "weekly_summary"  # Еженедельная сводка


@dataclass
class ControlRule:
    """Правило родительского контроля"""

    rule_id: str
    child_id: str
    control_type: ControlType
    status: ControlStatus
    settings: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class ParentalNotification:
    """Уведомление для родителей"""

    notification_id: str
    parent_id: str
    child_id: str
    notification_type: NotificationType
    title: str
    message: str
    severity: IncidentSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    is_read: bool = False
    action_required: bool = False


@dataclass
class ChildActivitySummary:
    """Сводка активности ребенка"""

    child_id: str
    date: datetime
    total_screen_time: timedelta
    blocked_attempts: int
    suspicious_activities: int
    emergency_alerts: int
    apps_used: List[str]
    websites_visited: List[str]
    contacts_interacted: List[str]


class ParentalControls(SecurityBase):
    """
    Централизованная система родительского контроля
    Объединяет все семейные функции безопасности
    """

    def __init__(
        self,
        family_profile_manager: FamilyProfileManager,
        child_protection: ChildProtection,
        elderly_protection: ElderlyProtection,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("ParentalControls", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Зависимости
        self.family_profile_manager = family_profile_manager
        self.child_protection = child_protection
        self.elderly_protection = elderly_protection

        # Данные системы
        self.control_rules: Dict[str, ControlRule] = {}
        self.notifications: Dict[str, ParentalNotification] = {}
        self.activity_summaries: Dict[str, ChildActivitySummary] = {}
        self.emergency_contacts: Dict[str, List[str]] = {}
        self.activity_log: List[SecurityEvent] = []

        # Настройки по умолчанию
        self.default_time_limits: Dict[AgeGroup, timedelta] = {
            AgeGroup.TODDLER: timedelta(hours=1),  # 1-3 года: 1 час
            AgeGroup.CHILD: timedelta(hours=2),  # 3-6 лет: 2 часа
            AgeGroup.TEEN: timedelta(hours=3),  # 6-12 лет: 3 часа
            AgeGroup.ADULT: timedelta(hours=4),  # 12-18 лет: 4 часа
        }

        self.default_content_filters: Dict[AgeGroup, List[ContentCategory]] = {
            AgeGroup.TODDLER: [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
            ],
            AgeGroup.CHILD: [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
                ContentCategory.GAMES,
            ],
            AgeGroup.TEEN: [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
                ContentCategory.GAMES,
                ContentCategory.SOCIAL,
            ],
            AgeGroup.ADULT: [
                ContentCategory.EDUCATIONAL,
                ContentCategory.ENTERTAINMENT,
                ContentCategory.GAMES,
                ContentCategory.SOCIAL,
                ContentCategory.NEWS,
            ],
        }

        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Инициализация правил по умолчанию"""
        try:
            # Получаем всех детей из семейных профилей
            families = self.family_profile_manager.families
            for family in families.values():
                for member_id, member in family.members.items():
                    if member.role == FamilyRole.CHILD:
                        self._create_default_rules_for_child(member.id)

            self.logger.info(
                "Инициализированы правила по умолчанию для всех детей"
            )

        except Exception as e:
            self.logger.error(f"Ошибка инициализации правил по умолчанию: {e}")

    def _create_default_rules_for_child(self, child_id: str) -> None:
        """Создание правил по умолчанию для ребенка"""
        try:
            # Получаем информацию о ребенке
            child_info = None
            for family in self.family_profile_manager.families.values():
                for member_id, member in family.members.items():
                    if member.id == child_id:
                        child_info = member
                        break
                if child_info:
                    break

            if not child_info:
                return

            age_group = child_info.age_group

            # Правило ограничения времени
            time_rule = ControlRule(
                rule_id=f"{child_id}_time_limit",
                child_id=child_id,
                control_type=ControlType.TIME_LIMIT,
                status=ControlStatus.ACTIVE,
                settings={
                    "daily_limit": self.default_time_limits[
                        age_group
                    ].total_seconds(),
                    "bedtime": "21:00",
                    "wake_time": "07:00",
                    "weekend_extension": 1.5,  # Выходные: +50% времени
                },
            )
            self.control_rules[time_rule.rule_id] = time_rule

            # Правило фильтрации контента
            content_rule = ControlRule(
                rule_id=f"{child_id}_content_filter",
                child_id=child_id,
                control_type=ControlType.CONTENT_FILTER,
                status=ControlStatus.ACTIVE,
                settings={
                    "allowed_categories": [
                        cat.value
                        for cat in self.default_content_filters[age_group]
                    ],
                    "blocked_keywords": ["насилие", "наркотики", "алкоголь"],
                    "safe_search": True,
                    "youtube_kids_mode": True,
                },
            )
            self.control_rules[content_rule.rule_id] = content_rule

            # Правило контроля приложений
            app_rule = ControlRule(
                rule_id=f"{child_id}_app_control",
                child_id=child_id,
                control_type=ControlType.APP_CONTROL,
                status=ControlStatus.ACTIVE,
                settings={
                    "allowed_apps": ["образовательные", "игры", "творчество"],
                    "blocked_apps": [
                        "социальные сети",
                        "мессенджеры",
                        "браузеры",
                    ],
                    "require_approval": True,
                    "time_limits_per_app": {},
                },
            )
            self.control_rules[app_rule.rule_id] = app_rule

            # Правило отслеживания местоположения
            location_rule = ControlRule(
                rule_id=f"{child_id}_location_tracking",
                child_id=child_id,
                control_type=ControlType.LOCATION_TRACKING,
                status=ControlStatus.ACTIVE,
                settings={
                    "tracking_enabled": True,
                    "safe_zones": ["дом", "школа", "спорт"],
                    "alert_on_leave": True,
                    "location_history_days": 30,
                },
            )
            self.control_rules[location_rule.rule_id] = location_rule

            # Правило экстренного контроля
            emergency_rule = ControlRule(
                rule_id=f"{child_id}_emergency_control",
                child_id=child_id,
                control_type=ControlType.EMERGENCY_CONTROL,
                status=ControlStatus.ACTIVE,
                settings={
                    "sos_button": True,
                    "auto_emergency_contacts": True,
                    "location_sharing": True,
                    "screen_lock_on_emergency": True,
                },
            )
            self.control_rules[emergency_rule.rule_id] = emergency_rule

            # Правило IPv6 защиты для детей
            ipv6_rule = ControlRule(
                rule_id=f"{child_id}_ipv6_protection",
                child_id=child_id,
                control_type=ControlType.IPV6_PROTECTION,
                status=ControlStatus.ACTIVE,
                settings={
                    "block_ipv6": True,
                    "prevent_ipv6_leaks": True,
                    "monitor_ipv6_connections": True,
                    "alert_on_ipv6_detection": True,
                    "auto_block_ipv6": True,
                },
            )
            self.control_rules[ipv6_rule.rule_id] = ipv6_rule

            # Правило Kill Switch для детей
            kill_switch_rule = ControlRule(
                rule_id=f"{child_id}_kill_switch",
                child_id=child_id,
                control_type=ControlType.KILL_SWITCH,
                status=ControlStatus.ACTIVE,
                settings={
                    "auto_kill_on_vpn_disconnect": True,
                    "kill_on_suspicious_activity": True,
                    "kill_on_emergency": True,
                    "notify_parents_on_kill": True,
                    "auto_reconnect_after_kill": False,
                },
            )
            self.control_rules[kill_switch_rule.rule_id] = kill_switch_rule

            self.logger.info(
                f"Созданы правила по умолчанию для ребенка {child_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Ошибка создания правил для ребенка {child_id}: {e}"
            )

    def create_control_rule(
        self,
        child_id: str,
        control_type: ControlType,
        settings: Dict[str, Any],
    ) -> bool:
        """
        Создание нового правила контроля
        Args:
            child_id: ID ребенка
            control_type: Тип контроля
            settings: Настройки правила
        Returns:
            bool: True если правило создано
        """
        try:
            rule_id = f"{child_id}_{control_type.value}_{int(time.time())}"

            rule = ControlRule(
                rule_id=rule_id,
                child_id=child_id,
                control_type=control_type,
                status=ControlStatus.ACTIVE,
                settings=settings,
            )

            self.control_rules[rule_id] = rule

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="parental_control_rule_created",
                severity=IncidentSeverity.LOW,
                description=(
                    f"Создано правило контроля {control_type.value} "
                    f"для ребенка {child_id}"
                ),
                source="ParentalControls",
            )
            self.activity_log.append(event)

            self.logger.info(f"Создано правило контроля {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания правила контроля: {e}")
            return False

    def update_control_rule(
        self, rule_id: str, settings: Dict[str, Any]
    ) -> bool:
        """
        Обновление правила контроля
        Args:
            rule_id: ID правила
            settings: Новые настройки
        Returns:
            bool: True если правило обновлено
        """
        try:
            if rule_id not in self.control_rules:
                self.logger.warning(f"Правило {rule_id} не найдено")
                return False

            rule = self.control_rules[rule_id]
            rule.settings.update(settings)
            rule.updated_at = datetime.now()

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="parental_control_rule_updated",
                severity=IncidentSeverity.LOW,
                description=f"Обновлено правило контроля {rule_id}",
                source="ParentalControls",
            )
            self.activity_log.append(event)

            self.logger.info(f"Обновлено правило контроля {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления правила контроля: {e}")
            return False

    def activate_control_rule(self, rule_id: str) -> bool:
        """
        Активация правила контроля
        Args:
            rule_id: ID правила
        Returns:
            bool: True если правило активировано
        """
        try:
            if rule_id not in self.control_rules:
                return False

            rule = self.control_rules[rule_id]
            rule.status = ControlStatus.ACTIVE
            rule.is_active = True
            rule.updated_at = datetime.now()

            self.logger.info(f"Активировано правило контроля {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка активации правила контроля: {e}")
            return False

    def deactivate_control_rule(self, rule_id: str) -> bool:
        """
        Деактивация правила контроля
        Args:
            rule_id: ID правила
        Returns:
            bool: True если правило деактивировано
        """
        try:
            if rule_id not in self.control_rules:
                return False

            rule = self.control_rules[rule_id]
            rule.status = ControlStatus.INACTIVE
            rule.is_active = False
            rule.updated_at = datetime.now()

            self.logger.info(f"Деактивировано правило контроля {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка деактивации правила контроля: {e}")
            return False

    def get_child_control_rules(self, child_id: str) -> List[ControlRule]:
        """
        Получение всех правил контроля для ребенка
        Args:
            child_id: ID ребенка
        Returns:
            List[ControlRule]: Список правил контроля
        """
        try:
            rules = []
            for rule in self.control_rules.values():
                if rule.child_id == child_id:
                    rules.append(rule)

            return sorted(rules, key=lambda x: x.created_at, reverse=True)

        except Exception as e:
            self.logger.error(
                f"Ошибка получения правил для ребенка {child_id}: {e}"
            )
            return []

    def check_time_limit(self, child_id: str) -> Tuple[bool, str]:
        """
        Проверка ограничения времени для ребенка
        Args:
            child_id: ID ребенка
        Returns:
            Tuple[bool, str]: (превышен ли лимит, сообщение)
        """
        try:
            # Ищем правило ограничения времени
            time_rules = [
                rule
                for rule in self.control_rules.values()
                if rule.child_id == child_id
                and rule.control_type == ControlType.TIME_LIMIT
                and rule.is_active
            ]

            if not time_rules:
                return False, "Правила ограничения времени не настроены"

            rule = time_rules[0]
            daily_limit = rule.settings.get("daily_limit", 0)

            # Получаем активность ребенка за сегодня
            activities_result = (
                self.child_protection.get_child_activity_report(child_id)
            )
            activities: List[Any]
            if isinstance(activities_result, list):
                activities = activities_result
            else:
                activities = []

            total_time = timedelta()
            for activity in activities:
                if (
                    hasattr(activity, "end_time")
                    and activity.end_time
                    and hasattr(activity, "start_time")
                    and activity.start_time
                ):
                    total_time += activity.end_time - activity.start_time

            if total_time.total_seconds() >= daily_limit:
                # Создаем уведомление
                self._create_notification(
                    parent_id=self._get_parent_id(child_id),
                    child_id=child_id,
                    notification_type=NotificationType.TIME_LIMIT_REACHED,
                    title="Превышено время использования",
                    message=(
                        f"Ребенок {child_id} превысил дневной лимит времени"
                    ),
                    severity=IncidentSeverity.MEDIUM,
                    action_required=True,
                )

                return True, f"Превышен дневной лимит времени: {total_time}"

            remaining_time = timedelta(seconds=daily_limit) - total_time
            return False, f"Осталось времени: {remaining_time}"

        except Exception as e:
            self.logger.error(f"Ошибка проверки ограничения времени: {e}")
            return False, f"Ошибка проверки: {e}"

    def check_content_access(
        self, child_id: str, content_url: str, content_type: str
    ) -> Tuple[bool, str]:
        """
        Проверка доступа к контенту
        Args:
            child_id: ID ребенка
            content_url: URL контента
            content_type: Тип контента
        Returns:
            Tuple[bool, str]: (разрешен ли доступ, сообщение)
        """
        try:
            # Используем ChildProtection для проверки контента
            # Получаем возраст ребенка
            child_age = 10  # По умолчанию
            for family in self.family_profile_manager.families.values():
                for member_id, member in family.members.items():
                    if member.id == child_id:
                        child_age = member.age
                        break

            allowed, message, threat_level = (
                self.child_protection.check_content_access(
                    child_id,
                    content_url,
                    ContentCategory.ENTERTAINMENT,
                    child_age,
                )
            )

            if not allowed:
                # Создаем уведомление о блокировке
                self._create_notification(
                    parent_id=self._get_parent_id(child_id),
                    child_id=child_id,
                    notification_type=NotificationType.SUSPICIOUS_ACTIVITY,
                    title="Заблокирован доступ к контенту",
                    message=(
                        f"Ребенок {child_id} пытался получить доступ "
                        f"к заблокированному контенту: {content_url}"
                    ),
                    severity=IncidentSeverity.MEDIUM,
                )

            return allowed, message

        except Exception as e:
            self.logger.error(f"Ошибка проверки доступа к контенту: {e}")
            return False, f"Ошибка проверки: {e}"

    def emergency_lock_child_device(self, child_id: str, reason: str) -> bool:
        """
        Экстренная блокировка устройства ребенка
        Args:
            child_id: ID ребенка
            reason: Причина блокировки
        Returns:
            bool: True если устройство заблокировано
        """
        try:
            # Активируем экстренный режим для всех правил ребенка
            child_rules = self.get_child_control_rules(child_id)
            for rule in child_rules:
                rule.status = ControlStatus.EMERGENCY
                rule.updated_at = datetime.now()

            # Создаем экстренное уведомление
            self._create_notification(
                parent_id=self._get_parent_id(child_id),
                child_id=child_id,
                notification_type=NotificationType.EMERGENCY_ALERT,
                title="ЭКСТРЕННАЯ БЛОКИРОВКА",
                message=(
                    f"Устройство ребенка {child_id} заблокировано. "
                    f"Причина: {reason}"
                ),
                severity=IncidentSeverity.CRITICAL,
                action_required=True,
            )

            # Создаем событие безопасности
            event = SecurityEvent(
                event_type="emergency_device_lock",
                severity=IncidentSeverity.HIGH,
                description=(
                    f"Экстренная блокировка устройства ребенка "
                    f"{child_id}: {reason}"
                ),
                source="ParentalControls",
            )
            self.activity_log.append(event)

            self.logger.critical(
                f"Экстренная блокировка устройства ребенка "
                f"{child_id}: {reason}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка экстренной блокировки: {e}")
            return False

    def get_daily_activity_summary(
        self, child_id: str, date: Optional[datetime] = None
    ) -> Optional[ChildActivitySummary]:
        """
        Получение сводки активности ребенка за день
        Args:
            child_id: ID ребенка
            date: Дата (по умолчанию сегодня)
        Returns:
            Optional[ChildActivitySummary]: Сводка активности
        """
        try:
            if date is None:
                target_date = datetime.now().date()
            else:
                target_date = date.date()

            # Получаем активность ребенка
            activities_result = (
                self.child_protection.get_child_activity_report(child_id)
            )
            activities: List[Any]
            if isinstance(activities_result, list):
                activities = activities_result
            else:
                activities = []

            # Подсчитываем статистику
            total_screen_time = timedelta()
            blocked_attempts = 0
            suspicious_activities = 0
            emergency_alerts = 0
            apps_used = set()
            websites_visited = set()
            contacts_interacted = set()

            for activity in activities:
                if (
                    hasattr(activity, "end_time")
                    and activity.end_time
                    and hasattr(activity, "start_time")
                    and activity.start_time
                ):
                    total_screen_time += (
                        activity.end_time - activity.start_time
                    )

                if (
                    hasattr(activity, "threat_detected")
                    and activity.threat_detected
                ):
                    if activity.threat_detected == ThreatLevel.HIGH:
                        emergency_alerts += 1
                    else:
                        suspicious_activities += 1

                if hasattr(activity, "blocked") and activity.blocked:
                    blocked_attempts += 1

                # Собираем информацию о приложениях и сайтах
                if hasattr(activity, "app_name") and activity.app_name:
                    apps_used.add(activity.app_name)

                if hasattr(activity, "website_url") and activity.website_url:
                    websites_visited.add(activity.website_url)

                if hasattr(activity, "contact_info") and activity.contact_info:
                    contacts_interacted.add(activity.contact_info)

            summary = ChildActivitySummary(
                child_id=child_id,
                date=datetime.combine(target_date, datetime.min.time()),
                total_screen_time=total_screen_time,
                blocked_attempts=blocked_attempts,
                suspicious_activities=suspicious_activities,
                emergency_alerts=emergency_alerts,
                apps_used=list(apps_used),
                websites_visited=list(websites_visited),
                contacts_interacted=list(contacts_interacted),
            )

            # Сохраняем сводку
            summary_key = f"{child_id}_{target_date.strftime('%Y%m%d')}"
            self.activity_summaries[summary_key] = summary

            return summary

        except Exception as e:
            self.logger.error(f"Ошибка получения сводки активности: {e}")
            return None

    def get_parent_notifications(
        self, parent_id: str, unread_only: bool = False
    ) -> List[ParentalNotification]:
        """
        Получение уведомлений для родителя
        Args:
            parent_id: ID родителя
            unread_only: Только непрочитанные
        Returns:
            List[ParentalNotification]: Список уведомлений
        """
        try:
            notifications = []
            for notification in self.notifications.values():
                if notification.parent_id == parent_id:
                    if not unread_only or not notification.is_read:
                        notifications.append(notification)

            return sorted(
                notifications, key=lambda x: x.timestamp, reverse=True
            )

        except Exception as e:
            self.logger.error(f"Ошибка получения уведомлений: {e}")
            return []

    def mark_notification_read(self, notification_id: str) -> bool:
        """
        Отметка уведомления как прочитанного
        Args:
            notification_id: ID уведомления
        Returns:
            bool: True если уведомление отмечено
        """
        try:
            if notification_id in self.notifications:
                self.notifications[notification_id].is_read = True
                return True
            return False

        except Exception as e:
            self.logger.error(f"Ошибка отметки уведомления: {e}")
            return False

    def _create_notification(
        self,
        parent_id: str,
        child_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        severity: IncidentSeverity,
        action_required: bool = False,
    ) -> None:
        """Создание уведомления для родителя"""
        try:
            notification_id = f"{parent_id}_{child_id}_{int(time.time())}"

            notification = ParentalNotification(
                notification_id=notification_id,
                parent_id=parent_id,
                child_id=child_id,
                notification_type=notification_type,
                title=title,
                message=message,
                severity=severity,
                action_required=action_required,
            )

            self.notifications[notification_id] = notification

        except Exception as e:
            self.logger.error(f"Ошибка создания уведомления: {e}")

    def _get_parent_id(self, child_id: str) -> str:
        """Получение ID родителя для ребенка"""
        try:
            # Получаем семейную информацию
            families = self.family_profile_manager.families
            for family in families.values():
                for member_id, member in family.members.items():
                    if member.id == child_id:
                        # Ищем родителя в той же семье
                        for parent_id, parent in family.members.items():
                            if parent.role == FamilyRole.PARENT:
                                return parent.id

            return "unknown_parent"

        except Exception as e:
            self.logger.error(f"Ошибка получения ID родителя: {e}")
            return "unknown_parent"

    def check_ipv6_protection(self, child_id: str) -> Tuple[bool, str]:
        """
        Проверка IPv6 защиты для ребенка
        Args:
            child_id: ID ребенка
        Returns:
            Tuple[bool, str]: (защищен, сообщение)
        """
        try:
            # Ищем правило IPv6 защиты
            ipv6_rule = None
            for rule in self.control_rules.values():
                if (
                    rule.child_id == child_id
                    and rule.control_type == ControlType.IPV6_PROTECTION
                    and rule.is_active
                ):
                    ipv6_rule = rule
                    break

            if not ipv6_rule:
                return False, "IPv6 защита не настроена для ребенка"

            # Проверяем настройки защиты
            settings = ipv6_rule.settings
            if not settings.get("block_ipv6", False):
                return False, "IPv6 блокировка отключена"

            # В реальной реализации здесь будет проверка IPv6 соединений
            # Для демонстрации возвращаем успешный результат
            return True, "IPv6 защита активна для ребенка"

        except Exception as e:
            self.logger.error(f"Ошибка проверки IPv6 защиты: {e}")
            return False, f"Ошибка проверки IPv6 защиты: {e}"

    def activate_kill_switch(
        self, child_id: str, reason: str = "Родительский контроль"
    ) -> bool:
        """
        Активация Kill Switch для ребенка
        Args:
            child_id: ID ребенка
            reason: Причина активации
        Returns:
            bool: True если Kill Switch активирован
        """
        try:
            # Ищем правило Kill Switch
            kill_switch_rule = None
            for rule in self.control_rules.values():
                if (
                    rule.child_id == child_id
                    and rule.control_type == ControlType.KILL_SWITCH
                    and rule.is_active
                ):
                    kill_switch_rule = rule
                    break

            if not kill_switch_rule:
                self.logger.warning(
                    f"Kill Switch не настроен для ребенка {child_id}"
                )
                return False

            # Получаем настройки
            settings = kill_switch_rule.settings

            # Активируем Kill Switch
            if settings.get("auto_kill_on_vpn_disconnect", False):
                # В реальной реализации здесь будет отключение интернета
                self.logger.info(
                    f"Kill Switch активирован для ребенка "
                    f"{child_id}: {reason}"
                )

                # Уведомляем родителей
                if settings.get("notify_parents_on_kill", False):
                    parent_id = self._get_parent_id(child_id)
                    self._create_notification(
                        parent_id=parent_id,
                        child_id=child_id,
                        notification_type=NotificationType.EMERGENCY_ALERT,
                        title="Kill Switch активирован",
                        message=(
                            f"Kill Switch активирован для {child_id}. "
                            f"Причина: {reason}"
                        ),
                        severity=IncidentSeverity.HIGH,
                        action_required=True,
                    )

                return True

            return False

        except Exception as e:
            self.logger.error(f"Ошибка активации Kill Switch: {e}")
            return False

    def deactivate_kill_switch(self, child_id: str) -> bool:
        """
        Деактивация Kill Switch для ребенка
        Args:
            child_id: ID ребенка
        Returns:
            bool: True если Kill Switch деактивирован
        """
        try:
            # В реальной реализации здесь будет восстановление интернета
            self.logger.info(
                f"Kill Switch деактивирован для ребенка "
                f"{child_id}"
            )

            # Уведомляем родителей
            parent_id = self._get_parent_id(child_id)
            self._create_notification(
                parent_id=parent_id,
                child_id=child_id,
                notification_type=NotificationType.DAILY_REPORT,
                title="Kill Switch деактивирован",
                message=(
                    f"Kill Switch деактивирован для {child_id}. "
                    f"Интернет восстановлен."
                ),
                severity=IncidentSeverity.LOW,
                action_required=False,
            )

            return True

        except Exception as e:
            self.logger.error(f"Ошибка деактивации Kill Switch: {e}")
            return False

    def get_modern_protection_status(self, child_id: str) -> Dict[str, Any]:
        """
        Получение статуса современных функций защиты для ребенка
        Args:
            child_id: ID ребенка
        Returns:
            Dict[str, Any]: Статус защиты
        """
        try:
            status = {
                "child_id": child_id,
                "ipv6_protection": {
                    "enabled": False,
                    "status": "unknown",
                    "message": "",
                },
                "kill_switch": {
                    "enabled": False,
                    "status": "unknown",
                    "message": "",
                },
                "modern_features_active": 0,
                "total_modern_features": 2,
            }

            # Проверяем IPv6 защиту
            ipv6_protected, ipv6_message = self.check_ipv6_protection(child_id)
            status["ipv6_protection"]["enabled"] = ipv6_protected
            status["ipv6_protection"]["status"] = (
                "protected" if ipv6_protected else "unprotected"
            )
            status["ipv6_protection"]["message"] = ipv6_message

            # Проверяем Kill Switch
            kill_switch_rule = None
            for rule in self.control_rules.values():
                if (
                    rule.child_id == child_id
                    and rule.control_type == ControlType.KILL_SWITCH
                    and rule.is_active
                ):
                    kill_switch_rule = rule
                    break

            if kill_switch_rule:
                status["kill_switch"]["enabled"] = True
                status["kill_switch"]["status"] = "ready"
                status["kill_switch"][
                    "message"
                ] = "Kill Switch готов к активации"
            else:
                status["kill_switch"]["enabled"] = False
                status["kill_switch"]["status"] = "not_configured"
                status["kill_switch"]["message"] = "Kill Switch не настроен"

            # Подсчитываем активные современные функции
            if status["ipv6_protection"]["enabled"]:
                status["modern_features_active"] += 1
            if status["kill_switch"]["enabled"]:
                status["modern_features_active"] += 1

            return status

        except Exception as e:
            self.logger.error(
                f"Ошибка получения статуса современных функций: {e}"
            )
            return {
                "child_id": child_id,
                "error": str(e),
                "modern_features_active": 0,
                "total_modern_features": 2,
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса системы родительского контроля
        Returns:
            Dict[str, Any]: Статус системы
        """
        try:
            # Получаем базовый статус
            base_status = super().get_status()

            # Добавляем специфичную информацию
            status = {
                **base_status,
                "total_control_rules": len(self.control_rules),
                "active_rules": len(
                    [r for r in self.control_rules.values() if r.is_active]
                ),
                "total_notifications": len(self.notifications),
                "unread_notifications": len(
                    [n for n in self.notifications.values() if not n.is_read]
                ),
                "activity_summaries": len(self.activity_summaries),
                "emergency_contacts": len(self.emergency_contacts),
                "control_types_active": {
                    control_type.value: len(
                        [
                            r
                            for r in self.control_rules.values()
                            if r.control_type == control_type and r.is_active
                        ]
                    )
                    for control_type in ControlType
                },
                "modern_features": {
                    "ipv6_protection_rules": len(
                        [
                            r
                            for r in self.control_rules.values()
                            if r.control_type == ControlType.IPV6_PROTECTION
                            and r.is_active
                        ]
                    ),
                    "kill_switch_rules": len(
                        [
                            r
                            for r in self.control_rules.values()
                            if r.control_type == ControlType.KILL_SWITCH
                            and r.is_active
                        ]
                    ),
                    "total_modern_features": 2,
                    "active_modern_features": len(
                        [
                            r
                            for r in self.control_rules.values()
                            if r.control_type
                            in [
                                ControlType.IPV6_PROTECTION,
                                ControlType.KILL_SWITCH,
                            ]
                            and r.is_active
                        ]
                    ),
                },
            }

            return status

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
