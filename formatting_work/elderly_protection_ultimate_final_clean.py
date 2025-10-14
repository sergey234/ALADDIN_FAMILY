"""
ElderlyProtection - Защита пожилых людей
Специальная защита от социальной инженерии, мошенничества и обмана
"""

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from core.base import SecurityBase

# Неиспользуемые импорты удалены для соответствия PEP8


class ThreatType(Enum):
    """Типы угроз для пожилых"""

    PHONE_SCAM = "phone_scam"  # Телефонное мошенничество
    EMAIL_PHISHING = "email_phishing"  # Фишинг по email
    FAKE_WEBSITE = "fake_website"  # Поддельные сайты
    SOCIAL_ENGINEERING = "social_engineering"  # Социальная инженерия
    FINANCIAL_FRAUD = "financial_fraud"  # Финансовое мошенничество
    TECH_SUPPORT_SCAM = "tech_support_scam"  # Мошенничество техподдержки
    MEDICAL_SCAM = "medical_scam"  # Медицинское мошенничество
    LOTTERY_SCAM = "lottery_scam"  # Лотерейное мошенничество


class RiskLevel(Enum):
    """Уровни риска"""

    LOW = "low"  # Низкий риск
    MEDIUM = "medium"  # Средний риск
    HIGH = "high"  # Высокий риск
    CRITICAL = "critical"  # Критический риск


class ProtectionAction(Enum):
    """Действия защиты"""

    ALLOW = "allow"  # Разрешить
    WARN = "warn"  # Предупредить
    BLOCK = "block"  # Заблокировать
    NOTIFY_FAMILY = "notify_family"  # Уведомить семью
    EMERGENCY_CONTACT = "emergency_contact"  # Экстренный контакт


@dataclass
class ScamPattern:
    """Паттерн мошенничества"""

    pattern_id: str
    threat_type: ThreatType
    keywords: List[str]
    phone_patterns: List[str] = field(default_factory=list)
    email_patterns: List[str] = field(default_factory=list)
    website_patterns: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    description: str = ""


@dataclass
class ElderlyActivity:
    """Активность пожилого человека"""

    activity_id: str
    elderly_id: str
    activity_type: str
    content: str
    source: str  # phone, email, website, app
    timestamp: datetime
    threat_detected: Optional[ThreatType] = None
    risk_level: RiskLevel = RiskLevel.LOW
    action_taken: ProtectionAction = ProtectionAction.ALLOW
    family_notified: bool = False


@dataclass
class FamilyContact:
    """Контакт семьи для уведомлений"""

    contact_id: str
    name: str
    phone: str
    email: str
    relationship: str  # son, daughter, caregiver
    priority: int = 1  # 1 = highest priority


class ElderlyProtection(SecurityBase):
    """
    Защита пожилых людей
    Специальная защита от социальной инженерии, мошенничества и обмана
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ElderlyProtection", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Хранилища данных
        self.scam_patterns: Dict[str, ScamPattern] = {}
        self.elderly_activities: Dict[str, List[ElderlyActivity]] = {}
        self.family_contacts: Dict[str, List[FamilyContact]] = {}
        self.blocked_numbers: Set[str] = set()
        self.blocked_emails: Set[str] = set()
        self.blocked_websites: Set[str] = set()
        self.trusted_contacts: Set[str] = set()

        # Дополнительные атрибуты для улучшенной функциональности
        self.elderly_profiles: Dict[str, Dict[str, Any]] = {}
        self.risk_thresholds: Dict[str, float] = {
            "high_risk_percentage": 30.0,
            "medium_risk_percentage": 15.0,
            "critical_threat_count": 5,
        }
        self.notification_settings: Dict[str, Any] = {
            "email_notifications": True,
            "sms_notifications": False,
            "push_notifications": True,
            "notification_frequency": "immediate",
        }
        self._backup_data: Dict[str, Any] = {}
        self.statistics_cache: Dict[str, Any] = {}
        self.last_backup_time: Optional[datetime] = None
        self.max_activities_per_elderly: int = 1000
        self.auto_cleanup_days: int = 30

        # Инициализация паттернов мошенничества
        self._initialize_scam_patterns()

    def _initialize_scam_patterns(self) -> None:
        """Инициализация паттернов мошенничества"""

        # Телефонное мошенничество
        phone_scam = ScamPattern(
            pattern_id="phone_scam_001",
            threat_type=ThreatType.PHONE_SCAM,
            keywords=[
                "выиграли",
                "приз",
                "лотерея",
                "наследство",
                "деньги",
                "банк",
                "карта",
                "блокировка",
                "срочно",
                "немедленно",
                "техподдержка",
                "вирус",
                "взлом",
                "безопасность",
            ],
            phone_patterns=[
                r"\+7\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}",  # Российские номера
                r"8\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}",
                r"\+1\s?\d{3}\s?\d{3}\s?\d{4}",  # Американские номера
            ],
            risk_level=RiskLevel.HIGH,
            description=(
                "Телефонное мошенничество с призами и банковскими услугами"
            ),
        )

        # Email фишинг
        email_phishing = ScamPattern(
            pattern_id="email_phishing_001",
            threat_type=ThreatType.EMAIL_PHISHING,
            keywords=[
                "срочно",
                "немедленно",
                "блокировка",
                "взлом",
                "безопасность",
                "подтвердите",
                "обновите",
                "восстановите",
                "аккаунт",
                "банк",
                "карта",
                "платеж",
                "штраф",
                "долг",
            ],
            email_patterns=[
                r"noreply@.*\.ru",
                r"support@.*\.com",
                r"security@.*\.org",
                r".*@.*\.tk$",  # Подозрительные домены
                r".*@.*\.ml$",
            ],
            risk_level=RiskLevel.HIGH,
            description="Фишинговые письма с просьбой подтвердить данные",
        )

        # Поддельные сайты
        fake_website = ScamPattern(
            pattern_id="fake_website_001",
            threat_type=ThreatType.FAKE_WEBSITE,
            keywords=[
                "бесплатно",
                "подарок",
                "выигрыш",
                "приз",
                "деньги",
                "лечение",
                "лекарство",
                "здоровье",
                "диагностика",
            ],
            website_patterns=[
                r".*\.tk$",
                r".*\.ml$",
                r".*\.ga$",
                r".*\.cf$",
                r"http://.*",  # Небезопасные соединения
                r".*bank.*\.ru$",  # Поддельные банковские сайты
                r".*gosuslugi.*\.ru$",  # Поддельные госуслуги
            ],
            risk_level=RiskLevel.CRITICAL,
            description="Поддельные сайты для кражи данных",
        )

        # Медицинское мошенничество
        medical_scam = ScamPattern(
            pattern_id="medical_scam_001",
            threat_type=ThreatType.MEDICAL_SCAM,
            keywords=[
                "лечение",
                "лекарство",
                "диагностика",
                "анализ",
                "здоровье",
                "бесплатно",
                "скидка",
                "акция",
                "срочно",
                "немедленно",
                "рак",
                "диабет",
                "давление",
                "сердце",
                "сосуды",
            ],
            risk_level=RiskLevel.HIGH,
            description="Медицинское мошенничество с поддельными лекарствами",
        )

        # Сохраняем паттерны
        self.scam_patterns = {
            phone_scam.pattern_id: phone_scam,
            email_phishing.pattern_id: email_phishing,
            fake_website.pattern_id: fake_website,
            medical_scam.pattern_id: medical_scam,
        }

    def analyze_phone_call(
        self,
        elderly_id: str,
        phone_number: str,
        caller_name: str = "",
        call_content: str = "",
    ) -> Tuple[RiskLevel, ProtectionAction, str]:
        """
        Анализ телефонного звонка

        Args:
            elderly_id: ID пожилого человека
            phone_number: Номер телефона
            caller_name: Имя звонящего
            call_content: Содержимое разговора

        Returns:
            Tuple[RiskLevel, ProtectionAction, str]: (уровень риска, действие,
                причина)
        """
        try:
            # Проверяем заблокированные номера
            if phone_number in self.blocked_numbers:
                return (
                    RiskLevel.CRITICAL,
                    ProtectionAction.BLOCK,
                    "Номер заблокирован",
                )

            # Проверяем доверенные контакты
            if phone_number in self.trusted_contacts:
                return (
                    RiskLevel.LOW,
                    ProtectionAction.ALLOW,
                    "Доверенный контакт",
                )

            # Анализируем содержимое разговора
            content_lower = call_content.lower()
            detected_threats = []

            for pattern in self.scam_patterns.values():
                if pattern.threat_type == ThreatType.PHONE_SCAM:
                    # Проверяем ключевые слова
                    for keyword in pattern.keywords:
                        if keyword in content_lower:
                            detected_threats.append((pattern, keyword))

                    # Проверяем паттерны номеров
                    for phone_pattern in pattern.phone_patterns:
                        if re.search(phone_pattern, phone_number):
                            detected_threats.append(
                                (pattern, "suspicious_number")
                            )

            # Определяем уровень риска
            if detected_threats:
                risk_levels = [
                    threat[0].risk_level for threat in detected_threats
                ]
                max_risk = max(risk_levels, key=lambda x: x.value)
                threat_types = [
                    threat[0].threat_type.value for threat in detected_threats
                ]

                # Создаем активность
                activity = ElderlyActivity(
                    activity_id=f"{elderly_id}_{int(time.time())}",
                    elderly_id=elderly_id,
                    activity_type="phone_call",
                    content=call_content,
                    source="phone",
                    timestamp=datetime.now(),
                    threat_detected=detected_threats[0][0].threat_type,
                    risk_level=max_risk,
                )

                self._add_activity(elderly_id, activity)

                # Определяем действие
                if max_risk == RiskLevel.CRITICAL:
                    action = ProtectionAction.BLOCK
                    reason = f"Критическая угроза: {', '.join(threat_types)}"
                elif max_risk == RiskLevel.HIGH:
                    action = ProtectionAction.NOTIFY_FAMILY
                    reason = f"Высокий риск: {', '.join(threat_types)}"
                else:
                    action = ProtectionAction.WARN
                    reason = (
                        f"Подозрительная активность: {', '.join(threat_types)}"
                    )

                return max_risk, action, reason

            return RiskLevel.LOW, ProtectionAction.ALLOW, "Звонок безопасен"

        except Exception as e:
            self.logger.error(f"Ошибка анализа телефонного звонка: {e}")
            return RiskLevel.MEDIUM, ProtectionAction.WARN, "Ошибка анализа"

    def analyze_email(
        self,
        elderly_id: str,
        sender_email: str,
        subject: str = "",
        content: str = "",
    ) -> Tuple[RiskLevel, ProtectionAction, str]:
        """
        Анализ email сообщения

        Args:
            elderly_id: ID пожилого человека
            sender_email: Email отправителя
            subject: Тема письма
            content: Содержимое письма

        Returns:
            Tuple[RiskLevel, ProtectionAction, str]: (уровень риска, действие,
                причина)
        """
        try:
            # Проверяем заблокированные email
            if sender_email in self.blocked_emails:
                return (
                    RiskLevel.CRITICAL,
                    ProtectionAction.BLOCK,
                    "Email заблокирован",
                )

            # Анализируем содержимое
            full_content = f"{subject} {content}".lower()
            detected_threats = []

            for pattern in self.scam_patterns.values():
                if pattern.threat_type == ThreatType.EMAIL_PHISHING:
                    # Проверяем ключевые слова
                    for keyword in pattern.keywords:
                        if keyword in full_content:
                            detected_threats.append((pattern, keyword))

                    # Проверяем паттерны email
                    for email_pattern in pattern.email_patterns:
                        if re.search(email_pattern, sender_email):
                            detected_threats.append(
                                (pattern, "suspicious_email")
                            )

            # Определяем уровень риска
            if detected_threats:
                risk_levels = [
                    threat[0].risk_level for threat in detected_threats
                ]
                max_risk = max(risk_levels, key=lambda x: x.value)
                threat_types = [
                    threat[0].threat_type.value for threat in detected_threats
                ]

                # Создаем активность
                activity = ElderlyActivity(
                    activity_id=f"{elderly_id}_{int(time.time())}",
                    elderly_id=elderly_id,
                    activity_type="email",
                    content=f"Subject: {subject}\nContent: {content[:200]}...",
                    source="email",
                    timestamp=datetime.now(),
                    threat_detected=detected_threats[0][0].threat_type,
                    risk_level=max_risk,
                )

                self._add_activity(elderly_id, activity)

                # Определяем действие
                if max_risk == RiskLevel.CRITICAL:
                    action = ProtectionAction.BLOCK
                    reason = f"Критическая угроза: {', '.join(threat_types)}"
                elif max_risk == RiskLevel.HIGH:
                    action = ProtectionAction.NOTIFY_FAMILY
                    reason = f"Высокий риск: {', '.join(threat_types)}"
                else:
                    action = ProtectionAction.WARN
                    reason = (
                        f"Подозрительное письмо: {', '.join(threat_types)}"
                    )

                return max_risk, action, reason

            return RiskLevel.LOW, ProtectionAction.ALLOW, "Email безопасен"

        except Exception as e:
            self.logger.error(f"Ошибка анализа email: {e}")
            return RiskLevel.MEDIUM, ProtectionAction.WARN, "Ошибка анализа"

    def analyze_website(
        self, elderly_id: str, website_url: str, page_content: str = ""
    ) -> Tuple[RiskLevel, ProtectionAction, str]:
        """
        Анализ веб-сайта

        Args:
            elderly_id: ID пожилого человека
            website_url: URL сайта
            page_content: Содержимое страницы

        Returns:
            Tuple[RiskLevel, ProtectionAction, str]: (уровень риска, действие,
                причина)
        """
        try:
            # Проверяем заблокированные сайты
            if website_url in self.blocked_websites:
                return (
                    RiskLevel.CRITICAL,
                    ProtectionAction.BLOCK,
                    "Сайт заблокирован",
                )

            # Анализируем URL и содержимое
            content_lower = f"{website_url} {page_content}".lower()
            detected_threats = []

            for pattern in self.scam_patterns.values():
                if pattern.threat_type == ThreatType.FAKE_WEBSITE:
                    # Проверяем ключевые слова
                    for keyword in pattern.keywords:
                        if keyword in content_lower:
                            detected_threats.append((pattern, keyword))

                    # Проверяем паттерны URL
                    for url_pattern in pattern.website_patterns:
                        if re.search(url_pattern, website_url):
                            detected_threats.append(
                                (pattern, "suspicious_url")
                            )

            # Определяем уровень риска
            if detected_threats:
                risk_levels = [
                    threat[0].risk_level for threat in detected_threats
                ]
                max_risk = max(risk_levels, key=lambda x: x.value)
                threat_types = [
                    threat[0].threat_type.value for threat in detected_threats
                ]

                # Создаем активность
                activity = ElderlyActivity(
                    activity_id=f"{elderly_id}_{int(time.time())}",
                    elderly_id=elderly_id,
                    activity_type="website_visit",
                    content=(
                        f"URL: {website_url}\nContent: {page_content[:200]}..."
                    ),
                    source="website",
                    timestamp=datetime.now(),
                    threat_detected=detected_threats[0][0].threat_type,
                    risk_level=max_risk,
                )

                self._add_activity(elderly_id, activity)

                # Определяем действие
                if max_risk == RiskLevel.CRITICAL:
                    action = ProtectionAction.BLOCK
                    reason = f"Критическая угроза: {', '.join(threat_types)}"
                elif max_risk == RiskLevel.HIGH:
                    action = ProtectionAction.NOTIFY_FAMILY
                    reason = f"Высокий риск: {', '.join(threat_types)}"
                else:
                    action = ProtectionAction.WARN
                    reason = f"Подозрительный сайт: {', '.join(threat_types)}"

                return max_risk, action, reason

            return RiskLevel.LOW, ProtectionAction.ALLOW, "Сайт безопасен"

        except Exception as e:
            self.logger.error(f"Ошибка анализа сайта: {e}")
            return RiskLevel.MEDIUM, ProtectionAction.WARN, "Ошибка анализа"

    def block_contact(
        self, contact_info: str, contact_type: str = "phone"
    ) -> bool:
        """
        Блокировка контакта

        Args:
            contact_info: Информация о контакте (номер, email, URL)
            contact_type: Тип контакта (phone, email, website)

        Returns:
            bool: Успешно ли заблокирован контакт
        """
        try:
            if contact_type == "phone":
                self.blocked_numbers.add(contact_info)
            elif contact_type == "email":
                self.blocked_emails.add(contact_info)
            elif contact_type == "website":
                self.blocked_websites.add(contact_info)

            self.logger.info(f"Заблокирован {contact_type}: {contact_info}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка блокировки контакта: {e}")
            return False

    def add_trusted_contact(
        self, contact_info: str, contact_type: str = "phone"
    ) -> bool:
        """
        Добавление доверенного контакта

        Args:
            contact_info: Информация о контакте
            contact_type: Тип контакта

        Returns:
            bool: Успешно ли добавлен контакт
        """
        try:
            self.trusted_contacts.add(contact_info)
            self.logger.info(
                f"Добавлен доверенный {contact_type}: {contact_info}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка добавления доверенного контакта: {e}")
            return False

    def add_family_contact(
        self, elderly_id: str, contact: FamilyContact
    ) -> bool:
        """
        Добавление контакта семьи

        Args:
            elderly_id: ID пожилого человека
            contact: Контакт семьи

        Returns:
            bool: Успешно ли добавлен контакт
        """
        try:
            if elderly_id not in self.family_contacts:
                self.family_contacts[elderly_id] = []

            self.family_contacts[elderly_id].append(contact)
            self.logger.info(
                f"Добавлен контакт семьи для {elderly_id}: {contact.name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Ошибка добавления контакта семьи: {e}")
            return False

    def notify_family(
        self, elderly_id: str, message: str, priority: int = 1
    ) -> bool:
        """
        Уведомление семьи

        Args:
            elderly_id: ID пожилого человека
            message: Сообщение
            priority: Приоритет (1 = высший)

        Returns:
            bool: Успешно ли отправлены уведомления
        """
        try:
            contacts = self.family_contacts.get(elderly_id, [])

            # Сортируем по приоритету
            contacts.sort(key=lambda x: x.priority)

            notified_count = 0
            for contact in contacts:
                if contact.priority <= priority:
                    # В реальной системе здесь будет отправка SMS/email
                    self.logger.info(
                        f"Уведомление {contact.name} ({contact.phone}): "
                        f"{message}"
                    )
                    notified_count += 1

            return notified_count > 0

        except Exception as e:
            self.logger.error(f"Ошибка уведомления семьи: {e}")
            return False

    def get_elderly_activity_report(
        self, elderly_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Получение отчета об активности пожилого человека

        Args:
            elderly_id: ID пожилого человека
            days: Количество дней для отчета

        Returns:
            Dict[str, Any]: Отчет об активности
        """
        try:
            activities = self.elderly_activities.get(elderly_id, [])
            cutoff_date = datetime.now() - timedelta(days=days)

            # Фильтруем активности за указанный период
            recent_activities = [
                activity
                for activity in activities
                if activity.timestamp >= cutoff_date
            ]

            # Статистика по угрозам
            threat_stats: Dict[str, int] = {}
            risk_stats: Dict[str, int] = {}

            for activity in recent_activities:
                if activity.threat_detected:
                    threat_type = activity.threat_detected.value
                    threat_stats[threat_type] = (
                        threat_stats.get(threat_type, 0) + 1
                    )

                risk_level = activity.risk_level.value
                risk_stats[risk_level] = risk_stats.get(risk_level, 0) + 1

            # Статистика по источникам
            source_stats: Dict[str, int] = {}
            for activity in recent_activities:
                source = activity.source
                source_stats[source] = source_stats.get(source, 0) + 1

            return {
                "elderly_id": elderly_id,
                "period_days": days,
                "total_activities": len(recent_activities),
                "threats_detected": sum(
                    1 for a in recent_activities if a.threat_detected
                ),
                "threat_statistics": threat_stats,
                "risk_statistics": risk_stats,
                "source_statistics": source_stats,
                "family_notifications": sum(
                    1 for a in recent_activities if a.family_notified
                ),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения отчета: {e}")
            return {"error": str(e)}

    def _add_activity(
        self, elderly_id: str, activity: ElderlyActivity
    ) -> None:
        """Добавление активности"""
        if elderly_id not in self.elderly_activities:
            self.elderly_activities[elderly_id] = []
        self.elderly_activities[elderly_id].append(activity)

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы защиты пожилых"""
        try:
            total_elderly = len(self.elderly_activities)
            total_activities = sum(
                len(activities)
                for activities in self.elderly_activities.values()
            )
            total_family_contacts = sum(
                len(contacts) for contacts in self.family_contacts.values()
            )

            return {
                "status": "active",
                "total_elderly": total_elderly,
                "total_activities": total_activities,
                "scam_patterns_count": len(self.scam_patterns),
                "blocked_numbers_count": len(self.blocked_numbers),
                "blocked_emails_count": len(self.blocked_emails),
                "blocked_websites_count": len(self.blocked_websites),
                "trusted_contacts_count": len(self.trusted_contacts),
                "family_contacts_count": total_family_contacts,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    def get_elderly_profile(self, elderly_id: str) -> Dict[str, Any]:
        """
        Получение профиля пожилого человека

        Args:
            elderly_id: ID пожилого человека

        Returns:
            Dict[str, Any]: Профиль пожилого человека
        """
        try:
            if elderly_id not in self.elderly_activities:
                return {"error": "Профиль не найден"}

            activities = self.elderly_activities[elderly_id]
            family_contacts = self.family_contacts.get(elderly_id, [])

            # Анализ активности
            total_activities = len(activities)
            high_risk_activities = sum(
                1 for a in activities if a.risk_level == RiskLevel.HIGH
            )
            blocked_activities = sum(
                1
                for a in activities
                if a.action_taken == ProtectionAction.BLOCK
            )

            return {
                "elderly_id": elderly_id,
                "total_activities": total_activities,
                "high_risk_activities": high_risk_activities,
                "blocked_activities": blocked_activities,
                "family_contacts_count": len(family_contacts),
                "last_activity": (
                    activities[-1].timestamp.isoformat()
                    if activities
                    else None
                ),
                "risk_level": (
                    "HIGH"
                    if high_risk_activities > total_activities * 0.3
                    else "LOW"
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения профиля: {e}")
            return {"error": str(e)}

    def update_elderly_profile(
        self, elderly_id: str, profile_data: Dict[str, Any]
    ) -> bool:
        """
        Обновление профиля пожилого человека

        Args:
            elderly_id: ID пожилого человека
            profile_data: Данные профиля для обновления

        Returns:
            bool: Успешность обновления
        """
        try:
            # Здесь можно добавить логику обновления профиля
            self.logger.info(
                f"Обновление профиля {elderly_id}: {profile_data}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления профиля: {e}")
            return False

    def get_threat_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики угроз

        Returns:
            Dict[str, Any]: Статистика угроз
        """
        try:
            threat_counts = {}
            risk_counts = {}

            for activities in self.elderly_activities.values():
                for activity in activities:
                    if activity.threat_detected:
                        threat_type = activity.threat_detected.value
                        threat_counts[threat_type] = (
                            threat_counts.get(threat_type, 0) + 1
                        )

                    risk_level = activity.risk_level.value
                    risk_counts[risk_level] = (
                        risk_counts.get(risk_level, 0) + 1
                    )

            return {
                "threat_types": threat_counts,
                "risk_levels": risk_counts,
                "total_threats": sum(threat_counts.values()),
                "high_risk_percentage": risk_counts.get("high", 0)
                / max(sum(risk_counts.values()), 1)
                * 100,
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {"error": str(e)}

    def export_activity_data(
        self, elderly_id: str, format: str = "json"
    ) -> str:
        """
        Экспорт данных активности

        Args:
            elderly_id: ID пожилого человека
            format: Формат экспорта (json, csv)

        Returns:
            str: Экспортированные данные
        """
        try:
            if elderly_id not in self.elderly_activities:
                return ""

            activities = self.elderly_activities[elderly_id]

            if format == "json":
                import json

                data = []
                for activity in activities:
                    data.append(
                        {
                            "activity_id": activity.activity_id,
                            "activity_type": activity.activity_type,
                            "content": activity.content,
                            "source": activity.source,
                            "timestamp": activity.timestamp.isoformat(),
                            "threat_detected": (
                                activity.threat_detected.value
                                if activity.threat_detected
                                else None
                            ),
                            "risk_level": activity.risk_level.value,
                            "action_taken": activity.action_taken.value,
                            "family_notified": activity.family_notified,
                        }
                    )
                return json.dumps(data, ensure_ascii=False, indent=2)
            else:
                return "Формат не поддерживается"
        except Exception as e:
            self.logger.error(f"Ошибка экспорта: {e}")
            return ""

    def validate_contact(
        self, contact_info: str, contact_type: str = "phone"
    ) -> bool:
        """
        Валидация контактной информации

        Args:
            contact_info: Контактная информация
            contact_type: Тип контакта (phone, email)

        Returns:
            bool: Валидность контакта
        """
        try:
            if contact_type == "phone":
                # Простая валидация телефона
                phone_pattern = r"^[\+]?[0-9\s\-\(\)]{10,15}$"
                return bool(re.match(phone_pattern, contact_info))
            elif contact_type == "email":
                # Простая валидация email
                email_pattern = (
                    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                )
                return bool(re.match(email_pattern, contact_info))
            return False
        except Exception as e:
            self.logger.error(f"Ошибка валидации: {e}")
            return False

    def is_trusted_contact(self, contact_info: str) -> bool:
        """
        Проверка, является ли контакт доверенным

        Args:
            contact_info: Контактная информация

        Returns:
            bool: Является ли контакт доверенным
        """
        return contact_info in self.trusted_contacts

    def is_blocked_contact(
        self, contact_info: str, contact_type: str = "phone"
    ) -> bool:
        """
        Проверка, заблокирован ли контакт

        Args:
            contact_info: Контактная информация
            contact_type: Тип контакта (phone, email, website)

        Returns:
            bool: Заблокирован ли контакт
        """
        try:
            if contact_type == "phone":
                return contact_info in self.blocked_numbers
            elif contact_type == "email":
                return contact_info in self.blocked_emails
            elif contact_type == "website":
                return contact_info in self.blocked_websites
            return False
        except Exception as e:
            self.logger.error(f"Ошибка проверки блокировки: {e}")
            return False

    def get_risk_assessment(self, elderly_id: str) -> Dict[str, Any]:
        """
        Получение оценки риска для пожилого человека

        Args:
            elderly_id: ID пожилого человека

        Returns:
            Dict[str, Any]: Оценка риска
        """
        try:
            if elderly_id not in self.elderly_activities:
                return {"risk_level": "UNKNOWN", "score": 0}

            activities = self.elderly_activities[elderly_id]
            if not activities:
                return {"risk_level": "LOW", "score": 0}

            # Простая оценка риска
            high_risk_count = sum(
                1 for a in activities if a.risk_level == RiskLevel.HIGH
            )
            medium_risk_count = sum(
                1 for a in activities if a.risk_level == RiskLevel.MEDIUM
            )
            total_activities = len(activities)

            risk_score = (high_risk_count * 3 + medium_risk_count * 1) / max(
                total_activities, 1
            )

            if risk_score > 2:
                risk_level = "HIGH"
            elif risk_score > 1:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            return {
                "risk_level": risk_level,
                "score": risk_score,
                "high_risk_activities": high_risk_count,
                "medium_risk_activities": medium_risk_count,
                "total_activities": total_activities,
            }
        except Exception as e:
            self.logger.error(f"Ошибка оценки риска: {e}")
            return {"risk_level": "ERROR", "score": -1}

    def get_protection_recommendations(self, elderly_id: str) -> List[str]:
        """
        Получение рекомендаций по защите

        Args:
            elderly_id: ID пожилого человека

        Returns:
            List[str]: Список рекомендаций
        """
        try:
            recommendations = []
            risk_assessment = self.get_risk_assessment(elderly_id)

            if risk_assessment["risk_level"] == "HIGH":
                recommendations.extend(
                    [
                        "Увеличить мониторинг активности",
                        "Добавить дополнительные контакты семьи",
                        "Настроить автоматические уведомления",
                        "Рассмотреть блокировку подозрительных контактов",
                    ]
                )
            elif risk_assessment["risk_level"] == "MEDIUM":
                recommendations.extend(
                    [
                        "Регулярно проверять активность",
                        "Обновить список доверенных контактов",
                        "Настроить базовые уведомления",
                    ]
                )
            else:
                recommendations.extend(
                    [
                        "Продолжать текущий уровень мониторинга",
                        "Периодически обновлять настройки безопасности",
                    ]
                )

            return recommendations
        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендаций: {e}")
            return ["Ошибка получения рекомендаций"]

    def backup_data(self) -> bool:
        """
        Создание резервной копии данных

        Returns:
            bool: Успешность создания бэкапа
        """
        try:
            self._backup_data = {
                "elderly_activities": dict(self.elderly_activities),
                "family_contacts": dict(self.family_contacts),
                "scam_patterns": dict(self.scam_patterns),
                "blocked_numbers": list(self.blocked_numbers),
                "blocked_emails": list(self.blocked_emails),
                "blocked_websites": list(self.blocked_websites),
                "trusted_contacts": list(self.trusted_contacts),
                "elderly_profiles": dict(self.elderly_profiles),
                "backup_time": datetime.now().isoformat(),
            }
            self.last_backup_time = datetime.now()
            self.logger.info("Резервная копия создана успешно")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка создания бэкапа: {e}")
            return False

    def restore_data(self) -> bool:
        """
        Восстановление данных из резервной копии

        Returns:
            bool: Успешность восстановления
        """
        try:
            if not self._backup_data:
                self.logger.warning("Нет данных для восстановления")
                return False

            self.elderly_activities = self._backup_data.get(
                "elderly_activities", {}
            )
            self.family_contacts = self._backup_data.get("family_contacts", {})
            self.scam_patterns = self._backup_data.get("scam_patterns", {})
            self.blocked_numbers = set(
                self._backup_data.get("blocked_numbers", [])
            )
            self.blocked_emails = set(
                self._backup_data.get("blocked_emails", [])
            )
            self.blocked_websites = set(
                self._backup_data.get("blocked_websites", [])
            )
            self.trusted_contacts = set(
                self._backup_data.get("trusted_contacts", [])
            )
            self.elderly_profiles = self._backup_data.get(
                "elderly_profiles", {}
            )

            self.logger.info("Данные восстановлены успешно")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка восстановления: {e}")
            return False

    def cleanup_old_activities(self) -> int:
        """
        Очистка старых активностей

        Returns:
            int: Количество удаленных активностей
        """
        try:
            cutoff_date = datetime.now() - timedelta(
                days=self.auto_cleanup_days
            )
            removed_count = 0

            for elderly_id, activities in self.elderly_activities.items():
                original_count = len(activities)
                self.elderly_activities[elderly_id] = [
                    activity
                    for activity in activities
                    if activity.timestamp > cutoff_date
                ]
                removed_count += original_count - len(
                    self.elderly_activities[elderly_id]
                )

            self.logger.info(f"Удалено {removed_count} старых активностей")
            return removed_count
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")
            return 0

    def update_risk_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """
        Обновление порогов риска

        Args:
            thresholds: Новые пороги риска

        Returns:
            bool: Успешность обновления
        """
        try:
            self.risk_thresholds.update(thresholds)
            self.logger.info(f"Пороги риска обновлены: {thresholds}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления порогов: {e}")
            return False

    def get_statistics_cached(self) -> Dict[str, Any]:
        """
        Получение кэшированной статистики

        Returns:
            Dict[str, Any]: Кэшированная статистика
        """
        try:
            if not self.statistics_cache:
                self.statistics_cache = self.get_threat_statistics()
            return self.statistics_cache
        except Exception as e:
            self.logger.error(f"Ошибка получения кэшированной статистики: {e}")
            return {"error": str(e)}
