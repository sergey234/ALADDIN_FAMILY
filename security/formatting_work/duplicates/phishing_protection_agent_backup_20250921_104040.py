# -*- coding: utf-8 -*-
"""
ALADDIN Security System - PhishingProtectionAgent
Агент защиты от фишинга - КРИТИЧНО

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import datetime
import re
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PhishingType(Enum):
    """Типы фишинговых атак"""

    EMAIL = "email"
    SMS = "sms"
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    VOICE = "voice"
    QR_CODE = "qr_code"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Уровень угрозы фишинга"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(Enum):
    """Метод обнаружения фишинга"""

    URL_ANALYSIS = "url_analysis"
    CONTENT_ANALYSIS = "content_analysis"
    DOMAIN_ANALYSIS = "domain_analysis"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    MACHINE_LEARNING = "machine_learning"
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"


@dataclass
class PhishingIndicator:
    """Индикатор фишинговой атаки"""

    indicator_id: str
    name: str
    phishing_type: PhishingType
    threat_level: ThreatLevel
    pattern: str  # Регулярное выражение или паттерн
    description: str
    detection_method: DetectionMethod
    confidence: float  # 0.0 - 1.0
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "name": self.name,
            "phishing_type": self.phishing_type.value,
            "threat_level": self.threat_level.value,
            "pattern": self.pattern,
            "description": self.description,
            "detection_method": self.detection_method.value,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhishingIndicator":
        return cls(
            indicator_id=data["indicator_id"],
            name=data["name"],
            phishing_type=PhishingType(data["phishing_type"]),
            threat_level=ThreatLevel(data["threat_level"]),
            pattern=data["pattern"],
            description=data["description"],
            detection_method=DetectionMethod(data["detection_method"]),
            confidence=data["confidence"],
            created_at=data.get(
                "created_at", datetime.datetime.now().isoformat()
            ),
            is_active=data.get("is_active", True),
        )


@dataclass
class PhishingDetection:
    """Результат обнаружения фишинга"""

    detection_id: str
    source: str  # URL, email, SMS, etc.
    phishing_type: PhishingType
    threat_level: ThreatLevel
    confidence: float  # 0.0 - 1.0
    detection_method: DetectionMethod
    indicators_matched: List[str] = field(default_factory=list)
    description: str = ""
    detected_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    is_blocked: bool = False
    user_action: Optional[str] = None  # "blocked", "reported", "ignored"
    additional_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "source": self.source,
            "phishing_type": self.phishing_type.value,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "detection_method": self.detection_method.value,
            "indicators_matched": self.indicators_matched,
            "description": self.description,
            "detected_at": self.detected_at,
            "is_blocked": self.is_blocked,
            "user_action": self.user_action,
            "additional_info": self.additional_info,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhishingDetection":
        return cls(
            detection_id=data["detection_id"],
            source=data["source"],
            phishing_type=PhishingType(data["phishing_type"]),
            threat_level=ThreatLevel(data["threat_level"]),
            confidence=data["confidence"],
            detection_method=DetectionMethod(data["detection_method"]),
            indicators_matched=data.get("indicators_matched", []),
            description=data.get("description", ""),
            detected_at=data.get(
                "detected_at", datetime.datetime.now().isoformat()
            ),
            is_blocked=data.get("is_blocked", False),
            user_action=data.get("user_action"),
            additional_info=data.get("additional_info", {}),
        )


@dataclass
class PhishingReport:
    """Отчет о фишинговой атаке"""

    report_id: str
    user_id: Optional[str]
    source: str
    phishing_type: PhishingType
    threat_level: ThreatLevel
    description: str
    reported_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )
    status: str = "pending"  # pending, verified, false_positive, resolved
    verification_notes: str = ""
    action_taken: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "user_id": self.user_id,
            "source": self.source,
            "phishing_type": self.phishing_type.value,
            "threat_level": self.threat_level.value,
            "description": self.description,
            "reported_at": self.reported_at,
            "status": self.status,
            "verification_notes": self.verification_notes,
            "action_taken": self.action_taken,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhishingReport":
        return cls(
            report_id=data["report_id"],
            user_id=data.get("user_id"),
            source=data["source"],
            phishing_type=PhishingType(data["phishing_type"]),
            threat_level=ThreatLevel(data["threat_level"]),
            description=data["description"],
            reported_at=data.get(
                "reported_at", datetime.datetime.now().isoformat()
            ),
            status=data.get("status", "pending"),
            verification_notes=data.get("verification_notes", ""),
            action_taken=data.get("action_taken", ""),
        )


class PhishingProtectionAgent:
    """
    Агент защиты от фишинговых атак с использованием множественных методов
    обнаружения.
    """

    def __init__(self, name: str = "PhishingProtectionAgent"):
        self.name = name
        self.indicators: List[PhishingIndicator] = []
        self.detections: List[PhishingDetection] = []
        self.reports: List[PhishingReport] = []
        self.blocked_domains: set = set()
        self.trusted_domains: set = set()
        self.suspicious_keywords: List[str] = []

        # Загружаем базовые индикаторы
        self._load_default_indicators()

    def _load_default_indicators(self):
        """Загружает базовые индикаторы фишинга"""
        default_indicators = [
            PhishingIndicator(
                indicator_id="ind_001",
                name="Подозрительные URL паттерны",
                phishing_type=PhishingType.WEBSITE,
                threat_level=ThreatLevel.HIGH,
                pattern=r"(bit\.ly|tinyurl|goo\.gl|t\.co|is\.gd|v\.gd)",
                description="Короткие URL сервисы часто используются для "
                "маскировки",
                detection_method=DetectionMethod.URL_ANALYSIS,
                confidence=0.8,
            ),
            PhishingIndicator(
                indicator_id="ind_002",
                name="Поддельные банковские домены",
                phishing_type=PhishingType.WEBSITE,
                threat_level=ThreatLevel.CRITICAL,
                pattern=r"(sberbank|vtb|gazprombank|alfabank|tinkoff|"
                r"raiffeisen)",
                description="Поддельные домены банков",
                detection_method=DetectionMethod.DOMAIN_ANALYSIS,
                confidence=0.9,
            ),
            PhishingIndicator(
                indicator_id="ind_003",
                name="Срочные финансовые сообщения",
                phishing_type=PhishingType.EMAIL,
                threat_level=ThreatLevel.HIGH,
                pattern=r"(срочно|немедленно|блокировка|заблокирован|"
                r"подтвердите|проверьте)",
                description="Срочные сообщения с финансовой тематикой",
                detection_method=DetectionMethod.CONTENT_ANALYSIS,
                confidence=0.7,
            ),
            PhishingIndicator(
                indicator_id="ind_004",
                name="Подозрительные вложения",
                phishing_type=PhishingType.EMAIL,
                threat_level=ThreatLevel.HIGH,
                pattern=r"\.(exe|scr|bat|cmd|com|pif|zip|rar)$",
                description="Подозрительные расширения файлов",
                detection_method=DetectionMethod.CONTENT_ANALYSIS,
                confidence=0.8,
            ),
            PhishingIndicator(
                indicator_id="ind_005",
                name="Фишинговые ключевые слова",
                phishing_type=PhishingType.EMAIL,
                threat_level=ThreatLevel.MEDIUM,
                pattern=r"(пароль|логин|аккаунт|карта|счет|деньги|перевод|"
                r"платеж)",
                description="Ключевые слова, связанные с финансовой "
                "информацией",
                detection_method=DetectionMethod.CONTENT_ANALYSIS,
                confidence=0.6,
            ),
        ]

        self.indicators.extend(default_indicators)
        print(
            f"Загружено {len(default_indicators)} базовых индикаторов фишинга"
        )

    def add_indicator(self, indicator: PhishingIndicator):
        """Добавляет новый индикатор фишинга"""
        self.indicators.append(indicator)
        print(f"Добавлен индикатор: {indicator.name}")

    def analyze_url(self, url: str) -> Optional[PhishingDetection]:
        """Анализирует URL на предмет фишинга"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()

            # Проверяем черный список доменов
            if domain in self.blocked_domains:
                return self._create_detection(
                    source=url,
                    phishing_type=PhishingType.WEBSITE,
                    threat_level=ThreatLevel.CRITICAL,
                    confidence=1.0,
                    detection_method=DetectionMethod.BLACKLIST,
                    description="Домен в черном списке",
                )

            # Проверяем белый список доменов
            if domain in self.trusted_domains:
                return None

            # Анализируем по индикаторам
            matched_indicators = []
            max_confidence = 0.0
            max_threat_level = ThreatLevel.LOW

            for indicator in self.indicators:
                if (
                    not indicator.is_active
                    or indicator.phishing_type != PhishingType.WEBSITE
                ):
                    continue

                if re.search(indicator.pattern, url, re.IGNORECASE):
                    matched_indicators.append(indicator.indicator_id)
                    max_confidence = max(max_confidence, indicator.confidence)
                    if indicator.threat_level.value > max_threat_level.value:
                        max_threat_level = indicator.threat_level

            if matched_indicators:
                return self._create_detection(
                    source=url,
                    phishing_type=PhishingType.WEBSITE,
                    threat_level=max_threat_level,
                    confidence=max_confidence,
                    detection_method=DetectionMethod.URL_ANALYSIS,
                    indicators_matched=matched_indicators,
                    description=f"Обнаружено {len(matched_indicators)} "
                    f"индикаторов фишинга",
                )

            # Дополнительные проверки
            detection = self._additional_url_checks(url, domain)
            if detection:
                return detection

        except Exception as e:
            print(f"Ошибка при анализе URL {url}: {e}")

        return None

    def analyze_email(
        self, subject: str, content: str, sender: str = ""
    ) -> Optional[PhishingDetection]:
        """Анализирует email на предмет фишинга"""
        try:
            text_to_analyze = f"{subject} {content} {sender}".lower()
            matched_indicators = []
            max_confidence = 0.0
            max_threat_level = ThreatLevel.LOW

            for indicator in self.indicators:
                if (
                    not indicator.is_active
                    or indicator.phishing_type != PhishingType.EMAIL
                ):
                    continue

                if re.search(
                    indicator.pattern, text_to_analyze, re.IGNORECASE
                ):
                    matched_indicators.append(indicator.indicator_id)
                    max_confidence = max(max_confidence, indicator.confidence)
                    if indicator.threat_level.value > max_threat_level.value:
                        max_threat_level = indicator.threat_level

            if matched_indicators:
                return self._create_detection(
                    source=f"Email from {sender}",
                    phishing_type=PhishingType.EMAIL,
                    threat_level=max_threat_level,
                    confidence=max_confidence,
                    detection_method=DetectionMethod.CONTENT_ANALYSIS,
                    indicators_matched=matched_indicators,
                    description=f"Обнаружено {len(matched_indicators)} "
                    f"индикаторов фишинга в email",
                )

            # Дополнительные проверки email
            detection = self._additional_email_checks(subject, content, sender)
            if detection:
                return detection

        except Exception as e:
            print(f"Ошибка при анализе email: {e}")

        return None

    def analyze_sms(
        self, content: str, sender: str = ""
    ) -> Optional[PhishingDetection]:
        """Анализирует SMS на предмет фишинга"""
        try:
            text_to_analyze = f"{content} {sender}".lower()
            matched_indicators = []
            max_confidence = 0.0
            max_threat_level = ThreatLevel.LOW

            for indicator in self.indicators:
                if (
                    not indicator.is_active
                    or indicator.phishing_type != PhishingType.SMS
                ):
                    continue

                if re.search(
                    indicator.pattern, text_to_analyze, re.IGNORECASE
                ):
                    matched_indicators.append(indicator.indicator_id)
                    max_confidence = max(max_confidence, indicator.confidence)
                    if indicator.threat_level.value > max_threat_level.value:
                        max_threat_level = indicator.threat_level

            if matched_indicators:
                return self._create_detection(
                    source=f"SMS from {sender}",
                    phishing_type=PhishingType.SMS,
                    threat_level=max_threat_level,
                    confidence=max_confidence,
                    detection_method=DetectionMethod.CONTENT_ANALYSIS,
                    indicators_matched=matched_indicators,
                    description=f"Обнаружено {len(matched_indicators)} "
                    f"индикаторов фишинга в SMS",
                )

        except Exception as e:
            print(f"Ошибка при анализе SMS: {e}")

        return None

    def _additional_url_checks(
        self, url: str, domain: str
    ) -> Optional[PhishingDetection]:
        """Дополнительные проверки URL"""
        # Проверка на подозрительные домены
        suspicious_domains = [
            r"[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}",  # IP адреса
            r"xn--",  # Punycode
            r"[а-яё]",  # Кириллица в домене
        ]

        for pattern in suspicious_domains:
            if re.search(pattern, domain):
                return self._create_detection(
                    source=url,
                    phishing_type=PhishingType.WEBSITE,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=0.7,
                    detection_method=DetectionMethod.DOMAIN_ANALYSIS,
                    description="Подозрительный домен",
                )

        return None

    def _additional_email_checks(
        self, subject: str, content: str, sender: str
    ) -> Optional[PhishingDetection]:
        """Дополнительные проверки email"""
        # Проверка на подозрительные отправители
        suspicious_senders = [
            r"noreply@",
            r"no-reply@",
            r"support@",
            r"security@",
            r"admin@",
        ]

        for pattern in suspicious_senders:
            if re.search(pattern, sender.lower()):
                return self._create_detection(
                    source=f"Email from {sender}",
                    phishing_type=PhishingType.EMAIL,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=0.6,
                    detection_method=DetectionMethod.CONTENT_ANALYSIS,
                    description="Подозрительный отправитель",
                )

        return None

    def _create_detection(
        self,
        source: str,
        phishing_type: PhishingType,
        threat_level: ThreatLevel,
        confidence: float,
        detection_method: DetectionMethod,
        indicators_matched: List[str] = None,
        description: str = "",
    ) -> PhishingDetection:
        """Создает объект обнаружения фишинга"""
        return PhishingDetection(
            detection_id=f"phish_{datetime.datetime.now().timestamp()}",
            source=source,
            phishing_type=phishing_type,
            threat_level=threat_level,
            confidence=confidence,
            detection_method=detection_method,
            indicators_matched=indicators_matched or [],
            description=description,
        )

    def block_domain(self, domain: str):
        """Добавляет домен в черный список"""
        self.blocked_domains.add(domain.lower())
        print(f"Домен добавлен в черный список: {domain}")

    def trust_domain(self, domain: str):
        """Добавляет домен в белый список"""
        self.trusted_domains.add(domain.lower())
        print(f"Домен добавлен в белый список: {domain}")

    def report_phishing(
        self,
        user_id: str,
        source: str,
        description: str,
        phishing_type: PhishingType = PhishingType.UNKNOWN,
    ) -> PhishingReport:
        """Создает отчет о фишинге от пользователя"""
        report = PhishingReport(
            report_id=f"report_{datetime.datetime.now().timestamp()}",
            user_id=user_id,
            source=source,
            phishing_type=phishing_type,
            threat_level=ThreatLevel.MEDIUM,
            description=description,
        )

        self.reports.append(report)
        print(f"Создан отчет о фишинге: {report.report_id}")
        return report

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику обнаружений"""
        if not self.detections:
            return {"total_detections": 0}

        stats = {
            "total_detections": len(self.detections),
            "by_type": {},
            "by_threat_level": {},
            "by_method": {},
            "blocked": sum(1 for d in self.detections if d.is_blocked),
            "reports": len(self.reports),
        }

        for detection in self.detections:
            # По типу
            phishing_type = detection.phishing_type.value
            stats["by_type"][phishing_type] = (
                stats["by_type"].get(phishing_type, 0) + 1
            )

            # По уровню угрозы
            threat_level = detection.threat_level.value
            stats["by_threat_level"][threat_level] = (
                stats["by_threat_level"].get(threat_level, 0) + 1
            )

            # По методу обнаружения
            method = detection.detection_method.value
            stats["by_method"][method] = stats["by_method"].get(method, 0) + 1

        return stats

    def get_recent_detections(
        self, hours: int = 24
    ) -> List[PhishingDetection]:
        """Возвращает недавние обнаружения"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        recent_detections = []

        for detection in self.detections:
            detected_time = datetime.datetime.fromisoformat(
                detection.detected_at
            )
            if detected_time >= cutoff_time:
                recent_detections.append(detection)

        return recent_detections

    def simulate_phishing_detection(
        self,
        source: str,
        phishing_type: PhishingType,
        threat_level: ThreatLevel,
        confidence: float = 0.8,
    ):
        """Симулирует обнаружение фишинга для тестирования"""
        detection = PhishingDetection(
            detection_id=f"sim_{datetime.datetime.now().timestamp()}",
            source=source,
            phishing_type=phishing_type,
            threat_level=threat_level,
            confidence=confidence,
            detection_method=DetectionMethod.MACHINE_LEARNING,
            description=f"Симулированное обнаружение "
            f"{phishing_type.value}",
            additional_info={"simulated": True},
        )

        self.detections.append(detection)
        print(
            f"Симулировано обнаружение фишинга: {source} - "
            f"{phishing_type.value}"
        )
        return detection

    def update_indicator(self, indicator_id: str, updates: Dict[str, Any]):
        """Обновляет индикатор фишинга"""
        for indicator in self.indicators:
            if indicator.indicator_id == indicator_id:
                for key, value in updates.items():
                    if hasattr(indicator, key):
                        setattr(indicator, key, value)
                print(f"Обновлен индикатор: {indicator_id}")
                return True
        return False

    def deactivate_indicator(self, indicator_id: str):
        """Деактивирует индикатор фишинга"""
        for indicator in self.indicators:
            if indicator.indicator_id == indicator_id:
                indicator.is_active = False
                print(f"Деактивирован индикатор: {indicator_id}")
                return True
        return False

    def get_status(self) -> str:
        """Получение статуса PhishingProtectionAgent"""
        try:
            if hasattr(self, 'is_running') and self.is_running:
                return "running"
            else:
                return "stopped"
        except Exception:
            return "unknown"

    def start_protection(self) -> bool:
        """Запуск системы защиты от фишинга"""
        try:
            self.is_running = True
            print("Система защиты от фишинга запущена")
            return True
        except Exception as e:
            print(f"Ошибка запуска системы защиты от фишинга: {e}")
            return False

    def stop_protection(self) -> bool:
        """Остановка системы защиты от фишинга"""
        try:
            self.is_running = False
            print("Система защиты от фишинга остановлена")
            return True
        except Exception as e:
            print(f"Ошибка остановки системы защиты от фишинга: {e}")
            return False

    def get_protection_info(self) -> Dict[str, Any]:
        """Получение информации о системе защиты от фишинга"""
        try:
            return {
                "is_running": getattr(self, 'is_running', False),
                "indicators_count": len(self.indicators),
                "active_indicators": len([i for i in self.indicators if i.is_active]),
                "detection_methods": len(DetectionMethod),
                "phishing_types": len(PhishingType),
                "threat_levels": len(ThreatLevel),
                "blocked_domains": len(getattr(self, 'blocked_domains', [])),
                "trusted_domains": len(getattr(self, 'trusted_domains', [])),
                "total_detections": getattr(self, 'total_detections', 0),
            }
        except Exception as e:
            print(f"Ошибка получения информации о системе защиты от фишинга: {e}")
            return {
                "is_running": False,
                "indicators_count": 0,
                "active_indicators": 0,
                "detection_methods": 0,
                "phishing_types": 0,
                "threat_levels": 0,
                "blocked_domains": 0,
                "trusted_domains": 0,
                "total_detections": 0,
                "error": str(e),
            }
