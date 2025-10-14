"""
ElderlyProtection - Защита пожилых людей
Специальная защита от социальной инженерии, мошенничества и обмана
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from core.base import SecurityBase
from core.security_base import SecurityEvent, SecurityRule, IncidentSeverity
from security.family.family_profile_manager import FamilyMember, AgeGroup


class ThreatType(Enum):
    """Типы угроз для пожилых"""
    PHONE_SCAM = "phone_scam"           # Телефонное мошенничество
    EMAIL_PHISHING = "email_phishing"   # Фишинг по email
    FAKE_WEBSITE = "fake_website"       # Поддельные сайты
    SOCIAL_ENGINEERING = "social_engineering"  # Социальная инженерия
    FINANCIAL_FRAUD = "financial_fraud" # Финансовое мошенничество
    TECH_SUPPORT_SCAM = "tech_support_scam"  # Мошенничество техподдержки
    MEDICAL_SCAM = "medical_scam"       # Медицинское мошенничество
    LOTTERY_SCAM = "lottery_scam"       # Лотерейное мошенничество


class RiskLevel(Enum):
    """Уровни риска"""
    LOW = "low"         # Низкий риск
    MEDIUM = "medium"   # Средний риск
    HIGH = "high"       # Высокий риск
    CRITICAL = "critical"  # Критический риск


class ProtectionAction(Enum):
    """Действия защиты"""
    ALLOW = "allow"           # Разрешить
    WARN = "warn"             # Предупредить
    BLOCK = "block"           # Заблокировать
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
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Хранилища данных
        self.scam_patterns: Dict[str, ScamPattern] = {}
        self.elderly_activities: Dict[str, List[ElderlyActivity]] = {}
        self.family_contacts: Dict[str, List[FamilyContact]] = {}
        self.blocked_numbers: Set[str] = set()
        self.blocked_emails: Set[str] = set()
        self.blocked_websites: Set[str] = set()
        self.trusted_contacts: Set[str] = set()
        
        # Инициализация паттернов мошенничества
        self._initialize_scam_patterns()
        
    def _initialize_scam_patterns(self) -> None:
        """Инициализация паттернов мошенничества"""
        
        # Телефонное мошенничество
        phone_scam = ScamPattern(
            pattern_id="phone_scam_001",
            threat_type=ThreatType.PHONE_SCAM,
            keywords=[
                "выиграли", "приз", "лотерея", "наследство", "деньги",
                "банк", "карта", "блокировка", "срочно", "немедленно",
                "техподдержка", "вирус", "взлом", "безопасность"
            ],
            phone_patterns=[
                r"\+7\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}",  # Российские номера
                r"8\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}",
                r"\+1\s?\d{3}\s?\d{3}\s?\d{4}"  # Американские номера
            ],
            risk_level=RiskLevel.HIGH,
            description="Телефонное мошенничество с призами и банковскими услугами"
        )
        
        # Email фишинг
        email_phishing = ScamPattern(
            pattern_id="email_phishing_001",
            threat_type=ThreatType.EMAIL_PHISHING,
            keywords=[
                "срочно", "немедленно", "блокировка", "взлом", "безопасность",
                "подтвердите", "обновите", "восстановите", "аккаунт",
                "банк", "карта", "платеж", "штраф", "долг"
            ],
            email_patterns=[
                r"noreply@.*\.ru",
                r"support@.*\.com",
                r"security@.*\.org",
                r".*@.*\.tk$",  # Подозрительные домены
                r".*@.*\.ml$"
            ],
            risk_level=RiskLevel.HIGH,
            description="Фишинговые письма с просьбой подтвердить данные"
        )
        
        # Поддельные сайты
        fake_website = ScamPattern(
            pattern_id="fake_website_001",
            threat_type=ThreatType.FAKE_WEBSITE,
            keywords=[
                "бесплатно", "подарок", "выигрыш", "приз", "деньги",
                "лечение", "лекарство", "здоровье", "диагностика"
            ],
            website_patterns=[
                r".*\.tk$",
                r".*\.ml$",
                r".*\.ga$",
                r".*\.cf$",
                r"http://.*",  # Небезопасные соединения
                r".*bank.*\.ru$",  # Поддельные банковские сайты
                r".*gosuslugi.*\.ru$"  # Поддельные госуслуги
            ],
            risk_level=RiskLevel.CRITICAL,
            description="Поддельные сайты для кражи данных"
        )
        
        # Медицинское мошенничество
        medical_scam = ScamPattern(
            pattern_id="medical_scam_001",
            threat_type=ThreatType.MEDICAL_SCAM,
            keywords=[
                "лечение", "лекарство", "диагностика", "анализ", "здоровье",
                "бесплатно", "скидка", "акция", "срочно", "немедленно",
                "рак", "диабет", "давление", "сердце", "сосуды"
            ],
            risk_level=RiskLevel.HIGH,
            description="Медицинское мошенничество с поддельными лекарствами"
        )
        
        # Сохраняем паттерны
        self.scam_patterns = {
            phone_scam.pattern_id: phone_scam,
            email_phishing.pattern_id: email_phishing,
            fake_website.pattern_id: fake_website,
            medical_scam.pattern_id: medical_scam
        }
    
    def analyze_phone_call(
        self, 
        elderly_id: str, 
        phone_number: str, 
        caller_name: str = "",
        call_content: str = ""
    ) -> Tuple[RiskLevel, ProtectionAction, str]:
        """
        Анализ телефонного звонка
        
        Args:
            elderly_id: ID пожилого человека
            phone_number: Номер телефона
            caller_name: Имя звонящего
            call_content: Содержимое разговора
            
        Returns:
            Tuple[RiskLevel, ProtectionAction, str]: (уровень риска, действие, причина)
        """
        try:
            # Проверяем заблокированные номера
            if phone_number in self.blocked_numbers:
                return RiskLevel.CRITICAL, ProtectionAction.BLOCK, "Номер заблокирован"
            
            # Проверяем доверенные контакты
            if phone_number in self.trusted_contacts:
                return RiskLevel.LOW, ProtectionAction.ALLOW, "Доверенный контакт"
            
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
                            detected_threats.append((pattern, "suspicious_number"))
            
            # Определяем уровень риска
            if detected_threats:
                risk_levels = [threat[0].risk_level for threat in detected_threats]
                max_risk = max(risk_levels, key=lambda x: x.value)
                threat_types = [threat[0].threat_type.value for threat in detected_threats]
                
                # Создаем активность
                activity = ElderlyActivity(
                    activity_id=f"{elderly_id}_{int(time.time())}",
                    elderly_id=elderly_id,
                    activity_type="phone_call",
                    content=call_content,
                    source="phone",
                    timestamp=datetime.now(),
                    threat_detected=detected_threats[0][0].threat_type,
                    risk_level=max_risk
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
                    reason = f"Подозрительная активность: {', '.join(threat_types)}"
                
                return max_risk, action, reason
            
            return RiskLevel.LOW, ProtectionAction.ALLOW, "Звонок безопасен"
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа телефонного звонка: {e}")
            return RiskLevel.MEDIUM, ProtectionAction.WARN, "Ошибка анализа"
    
    def analyze_email(
        self, 
        elderly_id: str, 
        sender_email: str, 
        subject: str, 
        content: str
    ) -> Tuple[RiskLevel, ProtectionAction, str]:
        """
        Анализ email сообщения
        
        Args:
            elderly_id: ID пожилого человека
            sender_email: Email отправителя
            subject: Тема письма
            content: Содержимое письма
            
        Returns:
            Tuple[RiskLevel, ProtectionAction, str]: (уровень риска, действие, причина)
        """
        try:
            # Проверяем заблокированные email
            if sender_email in self.blocked_emails:
                return RiskLevel.CRITICAL, ProtectionAction.BLOCK, "Email заблокирован"
            
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
                            detected_threats.append((pattern, "suspicious_email"))
            
            # Определяем уровень риска
            if detected_threats:
                risk_levels = [threat[0].risk_level for threat in detected_threats]
                max_risk = max(risk_levels, key=lambda x: x.value)
                threat_types = [threat[0].threat_type.value for threat in detected_threats]
                
                # Создаем активность
                activity = ElderlyActivity(
                    activity_id=f"{elderly_id}_{int(time.time())}",
                    elderly_id=elderly_id,
                    activity_type="email",
                    content=f"Subject: {subject}\nContent: {content[:200]}...",
                    source="email",
                    timestamp=datetime.now(),
                    threat_detected=detected_threats[0][0].threat_type,
                    risk_level=max_risk
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
                    reason = f"Подозрительное письмо: {', '.join(threat_types)}"
                
                return max_risk, action, reason
            
            return RiskLevel.LOW, ProtectionAction.ALLOW, "Email безопасен"
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа email: {e}")
            return RiskLevel.MEDIUM, ProtectionAction.WARN, "Ошибка анализа"
    
    def analyze_website(
        self, 
        elderly_id: str, 
        website_url: str, 
        page_content: str = ""
    ) -> Tuple[RiskLevel, ProtectionAction, str]:
        """
        Анализ веб-сайта
        
        Args:
            elderly_id: ID пожилого человека
            website_url: URL сайта
            page_content: Содержимое страницы
            
        Returns:
            Tuple[RiskLevel, ProtectionAction, str]: (уровень риска, действие, причина)
        """
        try:
            # Проверяем заблокированные сайты
            if website_url in self.blocked_websites:
                return RiskLevel.CRITICAL, ProtectionAction.BLOCK, "Сайт заблокирован"
            
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
                            detected_threats.append((pattern, "suspicious_url"))
            
            # Определяем уровень риска
            if detected_threats:
                risk_levels = [threat[0].risk_level for threat in detected_threats]
                max_risk = max(risk_levels, key=lambda x: x.value)
                threat_types = [threat[0].threat_type.value for threat in detected_threats]
                
                # Создаем активность
                activity = ElderlyActivity(
                    activity_id=f"{elderly_id}_{int(time.time())}",
                    elderly_id=elderly_id,
                    activity_type="website_visit",
                    content=f"URL: {website_url}\nContent: {page_content[:200]}...",
                    source="website",
                    timestamp=datetime.now(),
                    threat_detected=detected_threats[0][0].threat_type,
                    risk_level=max_risk
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
    
    def block_contact(self, contact_info: str, contact_type: str = "phone") -> bool:
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
    
    def add_trusted_contact(self, contact_info: str, contact_type: str = "phone") -> bool:
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
            self.logger.info(f"Добавлен доверенный {contact_type}: {contact_info}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления доверенного контакта: {e}")
            return False
    
    def add_family_contact(
        self, 
        elderly_id: str, 
        contact: FamilyContact
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
            self.logger.info(f"Добавлен контакт семьи для {elderly_id}: {contact.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления контакта семьи: {e}")
            return False
    
    def notify_family(
        self, 
        elderly_id: str, 
        message: str, 
        priority: int = 1
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
                    self.logger.info(f"Уведомление {contact.name} ({contact.phone}): {message}")
                    notified_count += 1
            
            return notified_count > 0
            
        except Exception as e:
            self.logger.error(f"Ошибка уведомления семьи: {e}")
            return False
    
    def get_elderly_activity_report(
        self, 
        elderly_id: str, 
        days: int = 7
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
                activity for activity in activities 
                if activity.timestamp >= cutoff_date
            ]
            
            # Статистика по угрозам
            threat_stats: Dict[str, int] = {}
            risk_stats: Dict[str, int] = {}
            
            for activity in recent_activities:
                if activity.threat_detected:
                    threat_type = activity.threat_detected.value
                    threat_stats[threat_type] = threat_stats.get(threat_type, 0) + 1
                
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
                "threats_detected": sum(1 for a in recent_activities if a.threat_detected),
                "threat_statistics": threat_stats,
                "risk_statistics": risk_stats,
                "source_statistics": source_stats,
                "family_notifications": sum(1 for a in recent_activities if a.family_notified)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения отчета: {e}")
            return {"error": str(e)}
    
    def _add_activity(self, elderly_id: str, activity: ElderlyActivity) -> None:
        """Добавление активности"""
        if elderly_id not in self.elderly_activities:
            self.elderly_activities[elderly_id] = []
        self.elderly_activities[elderly_id].append(activity)
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы защиты пожилых"""
        try:
            total_elderly = len(self.elderly_activities)
            total_activities = sum(len(activities) for activities in self.elderly_activities.values())
            total_family_contacts = sum(len(contacts) for contacts in self.family_contacts.values())
            
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
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
