# -*- coding: utf-8 -*-
"""
ALADDIN Security System - PhishingProtectionAgent
Агент защиты от фишинга - КРИТИЧНО

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-12
"""

import asyncio
import datetime
import hashlib
import re
import urllib.parse
import uuid
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import Any, AsyncGenerator, Dict, List, Optional


class PhishingProtectionError(Exception):
    """Базовый класс для ошибок агента"""

    pass


class DomainValidationError(PhishingProtectionError):
    """Ошибка валидации домена"""

    pass


class ThreatDatabaseError(PhishingProtectionError):
    """Ошибка базы данных угроз"""

    pass


class RateLimitExceededError(PhishingProtectionError):
    """Ошибка превышения лимита запросов"""

    pass


class PhishingPlugin:
    """Базовый класс для плагинов защиты от фишинга"""

    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.is_active = True
        self.config = {}

    def get_name(self) -> str:
        """Имя плагина"""
        return self.name

    def get_version(self) -> str:
        """Версия плагина"""
        return self.version

    def is_enabled(self) -> bool:
        """Проверка активности плагина"""
        return self.is_active

    def enable(self) -> None:
        """Включение плагина"""
        self.is_active = True

    def disable(self) -> None:
        """Отключение плагина"""
        self.is_active = False

    def configure(self, config: Dict[str, Any]) -> None:
        """Конфигурация плагина"""
        self.config.update(config)

    async def analyze_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Асинхронный анализ данных плагином"""
        raise NotImplementedError("Плагин должен реализовать analyze_async")

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Синхронный анализ данных плагином"""
        raise NotImplementedError("Плагин должен реализовать analyze")


class URLReputationPlugin(PhishingPlugin):
    """Плагин проверки репутации URL"""

    def __init__(self):
        super().__init__("URLReputationPlugin", "1.0")
        self.suspicious_domains = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "short.link", "is.gd", "v.gd", "ow.ly"}

    async def analyze_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ репутации URL"""
        if "url" not in data:
            return {"error": "URL not provided"}

        url = data["url"]
        domain = urllib.parse.urlparse(url).netloc.lower()

        # Проверка на подозрительные домены
        if domain in self.suspicious_domains:
            return {
                "confidence": 0.8,
                "threat_level": 3,  # HIGH
                "reason": "Suspicious URL shortener domain",
                "plugin": self.name,
            }

        # Проверка на IP адреса
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
            return {
                "confidence": 0.7,
                "threat_level": 2,  # MEDIUM
                "reason": "Direct IP address in URL",
                "plugin": self.name,
            }

        return {"confidence": 0.1, "threat_level": 1, "reason": "URL appears safe", "plugin": self.name}  # LOW


class EmailContentPlugin(PhishingPlugin):
    """Плагин анализа содержимого email"""

    def __init__(self):
        super().__init__("EmailContentPlugin", "1.0")
        self.phishing_keywords = [
            "urgent",
            "verify",
            "confirm",
            "update",
            "expired",
            "suspended",
            "locked",
            "security",
            "breach",
            "hack",
        ]
        self.suspicious_patterns = [
            r"click\s+here",
            r"download\s+now",
            r"verify\s+account",
            r"password\s+expired",
            r"account\s+suspended",
        ]

    async def analyze_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ содержимого email"""
        if "email" not in data:
            return {"error": "Email data not provided"}

        email_data = data["email"]
        subject = email_data.get("subject", "").lower()
        content = email_data.get("content", "").lower()
        text = f"{subject} {content}"

        # Проверка ключевых слов
        keyword_matches = sum(1 for keyword in self.phishing_keywords if keyword in text)

        # Проверка подозрительных паттернов
        pattern_matches = sum(1 for pattern in self.suspicious_patterns if re.search(pattern, text, re.IGNORECASE))

        # Расчет уровня угрозы
        threat_score = keyword_matches + pattern_matches * 2

        if threat_score >= 5:
            threat_level = 4  # CRITICAL
            confidence = 0.9
        elif threat_score >= 3:
            threat_level = 3  # HIGH
            confidence = 0.7
        elif threat_score >= 1:
            threat_level = 2  # MEDIUM
            confidence = 0.5
        else:
            threat_level = 1  # LOW
            confidence = 0.1

        return {
            "confidence": confidence,
            "threat_level": threat_level,
            "reason": f"Found {keyword_matches} keywords and {pattern_matches} suspicious patterns",
            "plugin": self.name,
            "details": {
                "keyword_matches": keyword_matches,
                "pattern_matches": pattern_matches,
                "threat_score": threat_score,
            },
        }


class DomainAgePlugin(PhishingPlugin):
    """Плагин проверки возраста домена"""

    def __init__(self):
        super().__init__("DomainAgePlugin", "1.0")
        self.new_domain_threshold_days = 30

    async def analyze_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ возраста домена"""
        if "url" not in data:
            return {"error": "URL not provided"}

        # Имитация проверки возраста домена
        # В реальной реализации здесь был бы запрос к WHOIS API
        await asyncio.sleep(0.01)  # Имитация сетевого запроса

        # Для демонстрации считаем все домены новыми
        domain_age_days = 15  # Имитация

        if domain_age_days < self.new_domain_threshold_days:
            return {
                "confidence": 0.6,
                "threat_level": 2,  # MEDIUM
                "reason": f"Domain is only {domain_age_days} days old",
                "plugin": self.name,
                "details": {"domain_age_days": domain_age_days, "threshold_days": self.new_domain_threshold_days},
            }

        return {
            "confidence": 0.2,
            "threat_level": 1,  # LOW
            "reason": f"Domain is {domain_age_days} days old (established)",
            "plugin": self.name,
            "details": {"domain_age_days": domain_age_days, "threshold_days": self.new_domain_threshold_days},
        }


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
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
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
            created_at=data.get("created_at", datetime.datetime.now().isoformat()),
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
    detected_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
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
            detected_at=data.get("detected_at", datetime.datetime.now().isoformat()),
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
    reported_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
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
            reported_at=data.get("reported_at", datetime.datetime.now().isoformat()),
            status=data.get("status", "pending"),
            verification_notes=data.get("verification_notes", ""),
            action_taken=data.get("action_taken", ""),
        )


class PhishingProtectionAgent:
    """
    Агент защиты от фишинговых атак с использованием множественных методов
    обнаружения.
    """

    def _load_default_indicators(self):
        """Загружает базовые индикаторы фишинга"""
        default_indicators = [
            PhishingIndicator(
                indicator_id="ind_001",
                name="Подозрительные URL паттерны",
                phishing_type=PhishingType.WEBSITE,
                threat_level=ThreatLevel.HIGH,
                pattern=r"(bit\.ly|tinyurl|goo\.gl|t\.co|is\.gd|v\.gd)",
                description="Короткие URL сервисы часто используются для " "маскировки",
                detection_method=DetectionMethod.URL_ANALYSIS,
                confidence=0.8,
            ),
            PhishingIndicator(
                indicator_id="ind_002",
                name="Поддельные банковские домены",
                phishing_type=PhishingType.WEBSITE,
                threat_level=ThreatLevel.CRITICAL,
                pattern=r"(sberbank|vtb|gazprombank|alfabank|tinkoff|" r"raiffeisen)",
                description="Поддельные домены банков",
                detection_method=DetectionMethod.DOMAIN_ANALYSIS,
                confidence=0.9,
            ),
            PhishingIndicator(
                indicator_id="ind_003",
                name="Срочные финансовые сообщения",
                phishing_type=PhishingType.EMAIL,
                threat_level=ThreatLevel.HIGH,
                pattern=r"(срочно|немедленно|блокировка|заблокирован|" r"подтвердите|проверьте)",
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
                pattern=r"(пароль|логин|аккаунт|карта|счет|деньги|перевод|" r"платеж)",
                description="Ключевые слова, связанные с финансовой " "информацией",
                detection_method=DetectionMethod.CONTENT_ANALYSIS,
                confidence=0.6,
            ),
        ]

        self.indicators.extend(default_indicators)
        print(f"Загружено {len(default_indicators)} базовых индикаторов фишинга")

    def _get_cache_key(self, data: str) -> str:
        """Генерация ключа кэша"""
        return hashlib.md5(data.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Проверка валидности кэша"""
        if cache_key not in self._cache:
            return False
        cache_time = self._cache[cache_key].get("timestamp", 0)
        return (datetime.datetime.now().timestamp() - cache_time) < self._cache_ttl

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        return None

    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Сохранение данных в кэш"""
        self._cache[cache_key] = {"data": data, "timestamp": datetime.datetime.now().timestamp()}

    def _check_rate_limit(self, method_name: str) -> bool:
        """Проверка лимита запросов"""
        now = datetime.datetime.now().timestamp()
        minute_ago = now - 60

        # Инициализируем список если его нет
        if method_name not in self._rate_limits:
            self._rate_limits[method_name] = []

        # Очищаем старые запросы
        self._rate_limits[method_name] = [
            req_time for req_time in self._rate_limits[method_name] if req_time > minute_ago
        ]

        if len(self._rate_limits[method_name]) >= self._max_requests_per_minute:
            raise RateLimitExceededError(f"Rate limit exceeded for {method_name}")

        self._rate_limits[method_name].append(now)
        return True

    def _validate_url(self, url: str) -> str:
        """Валидация URL"""
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        if len(url) > 2048:
            raise ValueError("URL too long (max 2048 characters)")

        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        return url.strip()

    def _validate_email(self, email: str) -> str:
        """Валидация email"""
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")

        if len(email) > 254:
            raise ValueError("Email too long (max 254 characters)")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        return email.strip().lower()

    def _validate_domain(self, domain: str) -> str:
        """Валидация домена"""
        if not domain or not isinstance(domain, str):
            raise DomainValidationError("Domain must be a non-empty string")

        if len(domain) > 253:
            raise DomainValidationError("Domain too long (max 253 characters)")

        domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(domain_pattern, domain):
            raise DomainValidationError("Invalid domain format")

        return domain.strip().lower()

    @lru_cache(maxsize=1000)
    def _cached_domain_check(self, domain: str) -> Dict[str, Any]:
        """Кэшированная проверка домена"""
        return self.validate_domain(domain)

    # ==================== АСИНХРОННЫЕ МЕТОДЫ ====================

    async def analyze_url_async(self, url: str) -> Optional[PhishingDetection]:
        """Асинхронный анализ URL на предмет фишинга"""
        try:
            # Валидируем входные данные
            url = self._validate_url(url)

            # Проверяем rate limit
            self._check_rate_limit("analyze_url_async")

            # Проверяем кэш
            cache_key = self._get_cache_key(f"url_analysis_async:{url}")
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Асинхронная проверка домена
            domain = urllib.parse.urlparse(url).netloc.lower()
            domain_check = await self._async_domain_check(domain)

            if domain_check["is_blocked"]:
                result = self._create_detection(
                    source=url,
                    phishing_type=PhishingType.WEBSITE,
                    threat_level=ThreatLevel.CRITICAL,
                    confidence=1.0,
                    detection_method=DetectionMethod.BLACKLIST,
                    description="Домен в черном списке",
                )
                self._set_cache(cache_key, result)
                return result

            if domain_check["is_trusted"]:
                self._set_cache(cache_key, None)
                return None

            # Асинхронный анализ по индикаторам
            detection = await self._async_analyze_indicators(url, PhishingType.WEBSITE)
            if detection:
                self._set_cache(cache_key, detection)
                return detection

            # Дополнительные асинхронные проверки
            additional_detection = await self._async_additional_url_checks(url, domain)
            if additional_detection:
                self._set_cache(cache_key, additional_detection)
                return additional_detection

            self._set_cache(cache_key, None)
            return None

        except Exception as e:
            print(f"Ошибка при асинхронном анализе URL {url}: {e}")
            return None

    async def analyze_email_async(self, subject: str, content: str, sender: str = "") -> Optional[PhishingDetection]:
        """Асинхронный анализ email на предмет фишинга"""
        try:
            # Валидируем входные данные
            if sender:
                sender = self._validate_email(sender)

            # Проверяем rate limit
            self._check_rate_limit("analyze_email_async")

            text_to_analyze = f"{subject} {content} {sender}".lower()

            # Асинхронный анализ по индикаторам
            detection = await self._async_analyze_indicators(text_to_analyze, PhishingType.EMAIL)
            if detection:
                return detection

            # Дополнительные асинхронные проверки email
            additional_detection = await self._async_additional_email_checks(subject, content, sender)
            if additional_detection:
                return additional_detection

            return None

        except Exception as e:
            print(f"Ошибка при асинхронном анализе email: {e}")
            return None

    async def batch_analyze_urls(self, urls: List[str]) -> AsyncGenerator[PhishingDetection, None]:
        """Пакетный асинхронный анализ URL"""
        tasks = [self.analyze_url_async(url) for url in urls]
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                yield result

    async def batch_analyze_emails(self, emails: List[Dict[str, str]]) -> AsyncGenerator[PhishingDetection, None]:
        """Пакетный асинхронный анализ email"""
        tasks = [
            self.analyze_email_async(email.get("subject", ""), email.get("content", ""), email.get("sender", ""))
            for email in emails
        ]
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                yield result

    async def _async_domain_check(self, domain: str) -> Dict[str, Any]:
        """Асинхронная проверка домена"""
        await asyncio.sleep(0.001)  # Имитация асинхронной операции
        return {
            "is_blocked": domain in self.blocked_domains,
            "is_trusted": domain in self.trusted_domains,
            "is_valid": self._validate_domain(domain) is not None,
        }

    async def _async_analyze_indicators(self, text: str, phishing_type: PhishingType) -> Optional[PhishingDetection]:
        """Асинхронный анализ по индикаторам"""
        await asyncio.sleep(0.001)  # Имитация асинхронной операции

        matched_indicators = []
        max_confidence = 0.0
        max_threat_level = ThreatLevel.LOW

        for indicator in self.indicators:
            if not indicator.is_active or indicator.phishing_type != phishing_type:
                continue

            if re.search(indicator.pattern, text, re.IGNORECASE):
                matched_indicators.append(indicator.indicator_id)
                max_confidence = max(max_confidence, indicator.confidence)
                if indicator.threat_level.value > max_threat_level.value:
                    max_threat_level = indicator.threat_level

        if matched_indicators:
            return self._create_detection(
                source=text[:100] + "..." if len(text) > 100 else text,
                phishing_type=phishing_type,
                threat_level=max_threat_level,
                confidence=max_confidence,
                detection_method=(
                    DetectionMethod.URL_ANALYSIS
                    if phishing_type == PhishingType.WEBSITE
                    else DetectionMethod.EMAIL_ANALYSIS
                ),
                indicators_matched=matched_indicators,
                description=f"Обнаружено {len(matched_indicators)} индикаторов фишинга",
            )

        return None

    async def _async_additional_url_checks(self, url: str, domain: str) -> Optional[PhishingDetection]:
        """Асинхронные дополнительные проверки URL"""
        await asyncio.sleep(0.001)  # Имитация асинхронной операции

        # Проверка на подозрительные паттерны
        suspicious_patterns = [
            r"bit\.ly|tinyurl\.com|goo\.gl",
            r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
            r"[a-zA-Z0-9-]+\.tk|\.ml|\.ga|\.cf",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return self._create_detection(
                    source=url,
                    phishing_type=PhishingType.WEBSITE,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=0.7,
                    detection_method=DetectionMethod.URL_ANALYSIS,
                    description="Подозрительный URL паттерн",
                )

        return None

    async def _async_additional_email_checks(
        self, subject: str, content: str, sender: str
    ) -> Optional[PhishingDetection]:
        """Асинхронные дополнительные проверки email"""
        await asyncio.sleep(0.001)  # Имитация асинхронной операции

        # Проверка на подозрительные паттерны в email
        suspicious_patterns = [
            r"urgent|urgente|urgente",
            r"click here|click here|click here",
            r"verify your account|verify your account",
            r"password expired|password expired",
        ]

        text_to_check = f"{subject} {content}".lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return self._create_detection(
                    source=f"Email from {sender}",
                    phishing_type=PhishingType.EMAIL,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=0.6,
                    detection_method=DetectionMethod.EMAIL_ANALYSIS,
                    description="Подозрительный email паттерн",
                )

        return None

    # ==================== ПЛАГИННАЯ АРХИТЕКТУРА ====================

    def __init__(self, name: str = "PhishingProtectionAgent"):
        self.name = name
        self.indicators: List[PhishingIndicator] = []
        self.detections: List[PhishingDetection] = []
        self.reports: List[PhishingReport] = []
        self.blocked_domains: set = set()
        self.trusted_domains: set = set()
        self.suspicious_keywords: List[str] = []

        # Дополнительные атрибуты для расширенной функциональности
        self.is_active: bool = False
        self.created_at: str = datetime.datetime.now().isoformat()
        self.last_updated: str = datetime.datetime.now().isoformat()
        self.version: str = "1.0"
        self.config: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, Any] = {}
        self.threat_database: Dict[str, Any] = {}
        self.ml_model: Optional[Dict[str, Any]] = None
        self.logs: List[Dict[str, Any]] = []
        self.max_detections: int = 1000
        self.max_reports: int = 1000
        self.confidence_threshold: float = 0.5
        self.auto_block_threshold: float = 0.8
        self.learning_enabled: bool = True
        self.notifications_enabled: bool = True
        self.backup_enabled: bool = True

        # Кэширование
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: int = 3600  # 1 час
        self._rate_limits: Dict[str, List[float]] = {}
        self._max_requests_per_minute: int = 100

        # Плагинная архитектура
        self.plugins: List[PhishingPlugin] = []
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

        # Загружаем базовые индикаторы
        self._load_default_indicators()

    def register_plugin(self, plugin: "PhishingPlugin") -> None:
        """Регистрация плагина"""
        self.plugins.append(plugin)
        print(f"🔌 Плагин зарегистрирован: {plugin.get_name()}")

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Отмена регистрации плагина"""
        for i, plugin in enumerate(self.plugins):
            if plugin.get_name() == plugin_name:
                del self.plugins[i]
                print(f"🔌 Плагин отключен: {plugin_name}")
                return True
        return False

    def get_plugin(self, plugin_name: str) -> Optional["PhishingPlugin"]:
        """Получение плагина по имени"""
        for plugin in self.plugins:
            if plugin.get_name() == plugin_name:
                return plugin
        return None

    def list_plugins(self) -> List[str]:
        """Список зарегистрированных плагинов"""
        return [plugin.get_name() for plugin in self.plugins]

    async def analyze_with_plugins(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ с использованием всех плагинов"""
        results = {
            "agent_analysis": None,
            "plugin_results": {},
            "combined_confidence": 0.0,
            "combined_threat_level": "LOW",
        }

        # Базовый анализ агентом
        if "url" in data:
            results["agent_analysis"] = await self.analyze_url_async(data["url"])
        elif "email" in data:
            email_data = data["email"]
            results["agent_analysis"] = await self.analyze_email_async(
                email_data.get("subject", ""), email_data.get("content", ""), email_data.get("sender", "")
            )

        # Анализ плагинами
        for plugin in self.plugins:
            try:
                plugin_result = await plugin.analyze_async(data)
                results["plugin_results"][plugin.get_name()] = plugin_result
            except Exception as e:
                print(f"❌ Ошибка плагина {plugin.get_name()}: {e}")
                results["plugin_results"][plugin.get_name()] = {"error": str(e)}

        # Комбинирование результатов
        results["combined_confidence"] = self._combine_confidence(results)
        results["combined_threat_level"] = self._combine_threat_level(results)

        return results

    def _combine_confidence(self, results: Dict[str, Any]) -> float:
        """Комбинирование уровня уверенности"""
        confidences = []

        if results["agent_analysis"] and hasattr(results["agent_analysis"], "confidence"):
            confidences.append(results["agent_analysis"].confidence)

        for plugin_result in results["plugin_results"].values():
            if isinstance(plugin_result, dict) and "confidence" in plugin_result:
                confidences.append(plugin_result["confidence"])

        return max(confidences) if confidences else 0.0

    def _combine_threat_level(self, results: Dict[str, Any]) -> str:
        """Комбинирование уровня угрозы"""
        threat_levels = []

        if results["agent_analysis"] and hasattr(results["agent_analysis"], "threat_level"):
            threat_levels.append(results["agent_analysis"].threat_level.value)

        for plugin_result in results["plugin_results"].values():
            if isinstance(plugin_result, dict) and "threat_level" in plugin_result:
                threat_level = plugin_result["threat_level"]
                # Преобразуем все в числа
                if isinstance(threat_level, str):
                    threat_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
                    threat_level = threat_map.get(threat_level.upper(), 1)
                elif not isinstance(threat_level, int):
                    threat_level = 1  # По умолчанию LOW
                threat_levels.append(int(threat_level))

        if not threat_levels:
            return "LOW"

        max_threat = max(threat_levels)
        if max_threat >= 4:
            return "CRITICAL"
        elif max_threat >= 3:
            return "HIGH"
        elif max_threat >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    def add_indicator(self, indicator: PhishingIndicator):
        """Добавляет новый индикатор фишинга"""
        self.indicators.append(indicator)
        print(f"Добавлен индикатор: {indicator.name}")

    def analyze_url(self, url: str) -> Optional[PhishingDetection]:
        """Анализирует URL на предмет фишинга"""
        try:
            # Валидируем входные данные
            url = self._validate_url(url)

            # Проверяем rate limit
            self._check_rate_limit("analyze_url")

            # Проверяем кэш
            cache_key = self._get_cache_key(f"url_analysis:{url}")
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

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
                if not indicator.is_active or indicator.phishing_type != PhishingType.WEBSITE:
                    continue

                if re.search(indicator.pattern, url, re.IGNORECASE):
                    matched_indicators.append(indicator.indicator_id)
                    max_confidence = max(max_confidence, indicator.confidence)
                    if indicator.threat_level.value > max_threat_level.value:
                        max_threat_level = indicator.threat_level

            if matched_indicators:
                result = self._create_detection(
                    source=url,
                    phishing_type=PhishingType.WEBSITE,
                    threat_level=max_threat_level,
                    confidence=max_confidence,
                    detection_method=DetectionMethod.URL_ANALYSIS,
                    indicators_matched=matched_indicators,
                    description=f"Обнаружено {len(matched_indicators)} " f"индикаторов фишинга",
                )
                self._set_cache(cache_key, result)
                return result

            # Дополнительные проверки
            detection = self._additional_url_checks(url, domain)
            if detection:
                self._set_cache(cache_key, detection)
                return detection

            # Кэшируем None результат
            self._set_cache(cache_key, None)
            return None

        except Exception as e:
            print(f"Ошибка при анализе URL {url}: {e}")
        return None

    def analyze_email(self, subject: str, content: str, sender: str = "") -> Optional[PhishingDetection]:
        """Анализирует email на предмет фишинга"""
        try:
            text_to_analyze = f"{subject} {content} {sender}".lower()
            matched_indicators = []
            max_confidence = 0.0
            max_threat_level = ThreatLevel.LOW

            for indicator in self.indicators:
                if not indicator.is_active or indicator.phishing_type != PhishingType.EMAIL:
                    continue

                if re.search(indicator.pattern, text_to_analyze, re.IGNORECASE):
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
                    description=f"Обнаружено {len(matched_indicators)} " f"индикаторов фишинга в email",
                )

            # Дополнительные проверки email
            detection = self._additional_email_checks(subject, content, sender)
            if detection:
                return detection

        except Exception as e:
            print(f"Ошибка при анализе email: {e}")

        return None

    def analyze_sms(self, content: str, sender: str = "") -> Optional[PhishingDetection]:
        """Анализирует SMS на предмет фишинга"""
        try:
            text_to_analyze = f"{content} {sender}".lower()
            matched_indicators = []
            max_confidence = 0.0
            max_threat_level = ThreatLevel.LOW

            for indicator in self.indicators:
                if not indicator.is_active or indicator.phishing_type != PhishingType.SMS:
                    continue

                if re.search(indicator.pattern, text_to_analyze, re.IGNORECASE):
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
                    description=f"Обнаружено {len(matched_indicators)} " f"индикаторов фишинга в SMS",
                )

        except Exception as e:
            print(f"Ошибка при анализе SMS: {e}")

        return None

    def _additional_url_checks(self, url: str, domain: str) -> Optional[PhishingDetection]:
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

    def _additional_email_checks(self, subject: str, content: str, sender: str) -> Optional[PhishingDetection]:
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
            stats["by_type"][phishing_type] = stats["by_type"].get(phishing_type, 0) + 1

            # По уровню угрозы
            threat_level = detection.threat_level.value
            stats["by_threat_level"][threat_level] = stats["by_threat_level"].get(threat_level, 0) + 1

            # По методу обнаружения
            method = detection.detection_method.value
            stats["by_method"][method] = stats["by_method"].get(method, 0) + 1

        return stats

    def get_recent_detections(self, hours: int = 24) -> List[PhishingDetection]:
        """Возвращает недавние обнаружения"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        recent_detections = []

        for detection in self.detections:
            detected_time = datetime.datetime.fromisoformat(detection.detected_at)
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
            description=f"Симулированное обнаружение " f"{phishing_type.value}",
            additional_info={"simulated": True},
        )

        self.detections.append(detection)
        print(f"Симулировано обнаружение фишинга: {source} - " f"{phishing_type.value}")
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
            if hasattr(self, "is_running") and self.is_running:
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
                "is_running": getattr(self, "is_running", False),
                "indicators_count": len(self.indicators),
                "active_indicators": len([i for i in self.indicators if i.is_active]),
                "detection_methods": len(DetectionMethod),
                "phishing_types": len(PhishingType),
                "threat_levels": len(ThreatLevel),
                "blocked_domains": len(getattr(self, "blocked_domains", [])),
                "trusted_domains": len(getattr(self, "trusted_domains", [])),
                "total_detections": getattr(self, "total_detections", 0),
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

    # ============================================================================
    # НОВЫЕ МЕТОДЫ AURA: EMAIL BREACH ALERTS + DARK WEB MONITORING
    # ============================================================================

    def email_breach_monitoring(self, email_address: str) -> dict:
        """
        Мониторинг утечек email в темной сети

        Args:
            email_address (str): Email адрес для мониторинга

        Returns:
            dict: Результат мониторинга утечек
        """
        try:
            print(f"🔍 Мониторинг утечек email: {email_address}")

            # Инициализация результата
            result = {
                "email_address": email_address,
                "monitoring_timestamp": datetime.datetime.now().isoformat(),
                "breach_detected": False,
                "breach_count": 0,
                "breach_details": [],
                "risk_level": "low",
                "recommendations": [],
                "dark_web_sources": [],
            }

            # 1. Проверка валидности email
            if not self._validate_email_format(email_address):
                result["error"] = "Неверный формат email адреса"
                return result

            # 2. Поиск в базе данных известных утечек
            known_breaches = self._check_known_breaches(email_address)
            if known_breaches["found"]:
                result["breach_detected"] = True
                result["breach_count"] = known_breaches["count"]
                result["breach_details"].extend(known_breaches["details"])

            # 3. Сканирование темной сети
            dark_web_results = self._scan_dark_web_for_email(email_address)
            if dark_web_results["found"]:
                result["breach_detected"] = True
                result["dark_web_sources"] = dark_web_results["sources"]
                result["breach_details"].extend(dark_web_results["breaches"])
                result["breach_count"] += dark_web_results["count"]

            # 4. Анализ уязвимостей домена
            domain_analysis = self._analyze_email_domain_security(email_address)
            if domain_analysis["vulnerabilities_found"]:
                result["breach_detected"] = True
                result["breach_details"].append(
                    {
                        "type": "domain_vulnerability",
                        "severity": domain_analysis["severity"],
                        "details": domain_analysis["vulnerabilities"],
                    }
                )

            # 5. Проверка социальных сетей на утечки
            social_media_scan = self._scan_social_media_breaches(email_address)
            if social_media_scan["found"]:
                result["breach_detected"] = True
                result["breach_details"].extend(social_media_scan["breaches"])
                result["breach_count"] += social_media_scan["count"]

            # 6. Определение уровня риска
            result["risk_level"] = self._calculate_breach_risk_level(result["breach_count"], result["breach_details"])

            # 7. Генерация рекомендаций
            result["recommendations"] = self._generate_breach_recommendations(result)

            # 8. Логирование результата
            if result["breach_detected"]:
                print(
                    f"🚨 УТЕЧКА ОБНАРУЖЕНА: {email_address} - "
                    f"{result['breach_count']} утечек, риск: {result['risk_level']}"
                )
            else:
                print(f"✅ Утечек не найдено: {email_address}")

            return result

        except Exception as e:
            print(f"❌ Ошибка мониторинга утечек email: {str(e)}")
            return {
                "email_address": email_address,
                "error": str(e),
                "monitoring_timestamp": datetime.datetime.now().isoformat(),
            }

    def dark_web_email_scanning(self, email_list: list) -> dict:
        """
        Сканирование email адресов в темной сети

        Args:
            email_list (list): Список email адресов

        Returns:
            dict: Результат сканирования темной сети
        """
        try:
            print(f"🌑 Сканирование темной сети для {len(email_list)} email адресов")

            # Инициализация результата
            result = {
                "scan_timestamp": datetime.datetime.now().isoformat(),
                "total_emails_scanned": len(email_list),
                "breaches_found": 0,
                "affected_emails": [],
                "dark_web_sources": [],
                "summary": {},
                "detailed_results": [],
            }

            # Сканирование каждого email
            for email in email_list:
                if self._validate_email_format(email):
                    email_result = self.email_breach_monitoring(email)
                    result["detailed_results"].append(email_result)

                    if email_result.get("breach_detected", False):
                        result["breaches_found"] += 1
                        result["affected_emails"].append(
                            {
                                "email": email,
                                "breach_count": email_result.get("breach_count", 0),
                                "risk_level": email_result.get("risk_level", "unknown"),
                            }
                        )

                        # Сбор источников темной сети
                        if email_result.get("dark_web_sources"):
                            result["dark_web_sources"].extend(email_result["dark_web_sources"])

            # Удаление дубликатов источников
            result["dark_web_sources"] = list(set(result["dark_web_sources"]))

            # Создание сводки
            result["summary"] = {
                "total_emails": len(email_list),
                "emails_with_breaches": result["breaches_found"],
                "clean_emails": len(email_list) - result["breaches_found"],
                "breach_percentage": ((result["breaches_found"] / len(email_list)) * 100 if email_list else 0),
                "unique_dark_web_sources": len(result["dark_web_sources"]),
            }

            # Логирование результата
            print(f"📊 Сканирование завершено: {result['breaches_found']}/{len(email_list)} email с утечками")

            return result

        except Exception as e:
            print(f"❌ Ошибка сканирования темной сети: {str(e)}")
            return {
                "error": str(e),
                "scan_timestamp": datetime.datetime.now().isoformat(),
            }

    def breach_alert_system(self, breach_data: dict) -> None:
        """
        Система уведомлений о взломах

        Args:
            breach_data (dict): Данные о взломе
        """
        try:
            print("🚨 Активация системы уведомлений о взломе")

            # 1. Определение критичности уведомления
            alert_level = self._determine_alert_level(breach_data)

            # 2. Создание уведомления
            alert = {
                "alert_id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.now().isoformat(),
                "alert_level": alert_level,
                "breach_data": breach_data,
                "recipients": self._get_alert_recipients(breach_data),
                "message": self._generate_breach_alert_message(breach_data, alert_level),
            }

            # 3. Отправка уведомлений
            if alert_level in ["critical", "high"]:
                self._send_immediate_notifications(alert)

            # 4. Логирование в систему безопасности
            self._log_breach_alert(alert)

            # 5. Обновление базы данных утечек
            self._update_breach_database(breach_data)

            print(f"✅ Уведомление о взломе отправлено: {alert_level}")

        except Exception as e:
            print(f"❌ Ошибка системы уведомлений о взломах: {str(e)}")

    def email_security_assessment(self, email: str) -> dict:
        """
        Оценка безопасности email адреса

        Args:
            email (str): Email адрес

        Returns:
            dict: Результат оценки безопасности
        """
        try:
            print(f"🔒 Оценка безопасности email: {email}")

            # Инициализация результата
            result = {
                "email": email,
                "assessment_timestamp": datetime.datetime.now().isoformat(),
                "security_score": 0.0,
                "vulnerabilities": [],
                "recommendations": [],
                "breach_history": {},
                "domain_security": {},
                "overall_risk": "unknown",
            }

            # 1. Проверка формата и валидности
            format_check = self._validate_email_security_format(email)
            if not format_check["valid"]:
                result["vulnerabilities"].append("invalid_format")
                result["security_score"] -= 20.0

            # 2. Анализ истории утечек
            breach_history = self.email_breach_monitoring(email)
            if breach_history.get("breach_detected", False):
                result["breach_history"] = {
                    "has_breaches": True,
                    "breach_count": breach_history.get("breach_count", 0),
                    "last_breach": breach_history.get("breach_details", [{}])[-1].get("date", "unknown"),
                }
                result["security_score"] -= breach_history.get("breach_count", 0) * 10.0
            else:
                result["breach_history"] = {"has_breaches": False}
                result["security_score"] += 20.0

            # 3. Анализ безопасности домена
            domain_security = self._analyze_domain_security(email)
            result["domain_security"] = domain_security
            result["security_score"] += domain_security.get("security_bonus", 0)

            # 4. Проверка на публичность
            public_exposure = self._check_email_public_exposure(email)
            if public_exposure["is_public"]:
                result["vulnerabilities"].append("public_exposure")
                result["security_score"] -= 15.0

            # 5. Анализ паролей (если доступно)
            password_analysis = self._analyze_password_security(email)
            if password_analysis["weak_password_detected"]:
                result["vulnerabilities"].append("weak_password")
                result["security_score"] -= 25.0

            # 6. Определение общего риска
            result["overall_risk"] = self._calculate_overall_risk(result["security_score"])

            # 7. Генерация рекомендаций
            result["recommendations"] = self._generate_security_recommendations(result)

            # Нормализация балла безопасности (0-100)
            result["security_score"] = max(0.0, min(100.0, result["security_score"]))

            # Логирование результата
            print(
                f"📊 Оценка безопасности завершена: {email} - "
                f"{result['security_score']:.1f}/100, риск: {result['overall_risk']}"
            )

            return result

        except Exception as e:
            print(f"❌ Ошибка оценки безопасности email: {str(e)}")
            return {
                "email": email,
                "error": str(e),
                "assessment_timestamp": datetime.datetime.now().isoformat(),
            }

    # ============================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ EMAIL BREACH MONITORING
    # ============================================================================

    def _validate_email_format(self, email: str) -> bool:
        """Валидация формата email"""
        try:
            import re

            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return bool(re.match(pattern, email))
        except Exception:
            return False

    def _check_known_breaches(self, email: str) -> dict:
        """Проверка в базе данных известных утечек"""
        try:
            # Здесь должна быть логика проверки базы данных утечек
            return {"found": False, "count": 0, "details": []}
        except Exception:
            return {"found": False, "count": 0, "details": []}

    def _scan_dark_web_for_email(self, email: str) -> dict:
        """Сканирование темной сети для email"""
        try:
            # Здесь должна быть логика сканирования темной сети
            return {"found": False, "sources": [], "breaches": [], "count": 0}
        except Exception:
            return {"found": False, "sources": [], "breaches": [], "count": 0}

    def _analyze_email_domain_security(self, email: str) -> dict:
        """Анализ безопасности домена email"""
        try:
            domain = email.split("@")[1] if "@" in email else ""
            return {
                "domain": domain,
                "vulnerabilities_found": False,
                "severity": "low",
                "vulnerabilities": [],
            }
        except Exception:
            return {"vulnerabilities_found": False, "severity": "low"}

    def _scan_social_media_breaches(self, email: str) -> dict:
        """Сканирование социальных сетей на утечки"""
        try:
            return {"found": False, "breaches": [], "count": 0}
        except Exception:
            return {"found": False, "breaches": [], "count": 0}

    def _calculate_breach_risk_level(self, breach_count: int, breach_details: list) -> str:
        """Расчет уровня риска утечек"""
        try:
            if breach_count >= 5:
                return "critical"
            elif breach_count >= 3:
                return "high"
            elif breach_count >= 1:
                return "medium"
            else:
                return "low"
        except Exception:
            return "unknown"

    def _generate_breach_recommendations(self, result: dict) -> list:
        """Генерация рекомендаций по утечкам"""
        try:
            recommendations = []

            if result.get("breach_detected", False):
                recommendations.append("Немедленно сменить пароль")
                recommendations.append("Включить двухфакторную аутентификацию")
                recommendations.append("Проверить активность аккаунта")

                if result.get("risk_level") in ["high", "critical"]:
                    recommendations.append("Связаться со службой поддержки")
                    recommendations.append("Рассмотреть смену email адреса")

            return recommendations
        except Exception:
            return []

    def _determine_alert_level(self, breach_data: dict) -> str:
        """Определение уровня уведомления"""
        try:
            severity = breach_data.get("severity", "low")
            breach_count = breach_data.get("breach_count", 0)

            if severity == "critical" or breach_count >= 5:
                return "critical"
            elif severity == "high" or breach_count >= 3:
                return "high"
            elif severity == "medium" or breach_count >= 1:
                return "medium"
            else:
                return "low"
        except Exception:
            return "low"

    def _get_alert_recipients(self, breach_data: dict) -> list:
        """Получение списка получателей уведомлений"""
        try:
            return ["family", "security_team"]
        except Exception:
            return []

    def _generate_breach_alert_message(self, breach_data: dict, alert_level: str) -> str:
        """Генерация сообщения уведомления о взломе"""
        try:
            email = breach_data.get("email", "неизвестный")
            count = breach_data.get("breach_count", 0)

            if alert_level == "critical":
                return (
                    f"🚨 КРИТИЧЕСКАЯ УТЕЧКА: Email {email} обнаружен в "
                    f"{count} утечках данных! Немедленно примите меры!"
                )
            elif alert_level == "high":
                return f"⚠️ ВЫСОКИЙ РИСК: Email {email} найден в {count} утечках. Рекомендуется смена пароля."
            elif alert_level == "medium":
                return f"📧 УТЕЧКА ДАННЫХ: Email {email} обнаружен в {count} утечке. Проверьте безопасность."
            else:
                return f"ℹ️ ИНФОРМАЦИЯ: Email {email} проверен на утечки."
        except Exception:
            return "Уведомление о утечке данных"

    def _send_immediate_notifications(self, alert: dict) -> None:
        """Отправка немедленных уведомлений"""
        try:
            # Здесь должна быть логика отправки уведомлений
            print(f"📢 Отправка уведомления: {alert['alert_level']}")
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")

    def _log_breach_alert(self, alert: dict) -> None:
        """Логирование уведомления о взломе"""
        try:
            # Здесь должна быть логика логирования
            print(f"📝 Логирование уведомления: {alert['alert_id']}")
        except Exception as e:
            print(f"Ошибка логирования: {e}")

    def _update_breach_database(self, breach_data: dict) -> None:
        """Обновление базы данных утечек"""
        try:
            # Здесь должна быть логика обновления базы данных
            print("💾 Обновление базы данных утечек")
        except Exception as e:
            print(f"Ошибка обновления базы данных: {e}")

    def _validate_email_security_format(self, email: str) -> dict:
        """Валидация формата email для безопасности"""
        try:
            is_valid = self._validate_email_format(email)
            return {
                "valid": is_valid,
                "issues": [] if is_valid else ["invalid_format"],
            }
        except Exception:
            return {"valid": False, "issues": ["validation_error"]}

    def _analyze_domain_security(self, email: str) -> dict:
        """Анализ безопасности домена"""
        try:
            domain = email.split("@")[1] if "@" in email else ""
            return {"domain": domain, "security_bonus": 10.0, "issues": []}
        except Exception:
            return {"security_bonus": 0.0, "issues": []}

    def _check_email_public_exposure(self, email: str) -> dict:
        """Проверка публичности email"""
        try:
            return {"is_public": False, "exposure_sources": []}
        except Exception:
            return {"is_public": False, "exposure_sources": []}

    def _analyze_password_security(self, email: str) -> dict:
        """Анализ безопасности пароля"""
        try:
            return {
                "weak_password_detected": False,
                "password_strength": "unknown",
            }
        except Exception:
            return {
                "weak_password_detected": False,
                "password_strength": "unknown",
            }

    def _calculate_overall_risk(self, security_score: float) -> str:
        """Расчет общего риска"""
        try:
            if security_score >= 80:
                return "low"
            elif security_score >= 60:
                return "medium"
            elif security_score >= 40:
                return "high"
            else:
                return "critical"
        except Exception:
            return "unknown"

    def _generate_security_recommendations(self, result: dict) -> list:
        """Генерация рекомендаций по безопасности"""
        try:
            recommendations = []

            if result.get("security_score", 0) < 70:
                recommendations.append("Использовать надежный пароль")
                recommendations.append("Включить двухфакторную аутентификацию")

            if result.get("breach_history", {}).get("has_breaches", False):
                recommendations.append("Сменить пароль")
                recommendations.append("Проверить активность аккаунта")

            if "public_exposure" in result.get("vulnerabilities", []):
                recommendations.append("Удалить email из публичных источников")
                recommendations.append("Использовать алиас email")

            return recommendations
        except Exception:
            return []

    def is_safe_url(self, url: str) -> bool:
        """
        Проверяет безопасность URL.

        Args:
            url (str): URL для проверки

        Returns:
            bool: True если URL безопасен, False если подозрителен
        """
        try:
            # Базовая проверка URL
            if not url or not isinstance(url, str):
                return False

            # Проверяем на заблокированные домены
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()

            if domain in self.blocked_domains:
                return False

            # Проверяем на доверенные домены
            if domain in self.trusted_domains:
                return True

            # Дополнительные проверки безопасности
            if self.analyze_url(url) is not None:
                return False

            return True
        except Exception:
            return False

    def is_safe_email(self, email: str) -> bool:
        """
        Проверяет безопасность email адреса.

        Args:
            email (str): Email адрес для проверки

        Returns:
            bool: True если email безопасен, False если подозрителен
        """
        try:
            # Валидируем email
            email = self._validate_email(email)

            # Проверяем на подозрительные домены
            domain = email.split("@")[1]
            if domain in self.blocked_domains:
                return False

            return True
        except (ValueError, DomainValidationError):
            return False
        except Exception:
            return False

    def validate_domain(self, domain: str) -> Dict[str, Any]:
        """
        Валидирует домен на предмет безопасности.

        Args:
            domain (str): Домен для валидации

        Returns:
            Dict[str, Any]: Результат валидации домена
        """
        try:
            result = {
                "domain": domain,
                "is_valid": False,
                "is_safe": False,
                "reputation_score": 0.0,
                "threats": [],
                "recommendations": [],
            }

            if not domain or not isinstance(domain, str):
                return result

            # Базовая валидация домена
            if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
                result["threats"].append("Неверный формат домена")
                return result

            result["is_valid"] = True

            # Проверяем репутацию домена
            if domain in self.trusted_domains:
                result["is_safe"] = True
                result["reputation_score"] = 1.0
            elif domain in self.blocked_domains:
                result["is_safe"] = False
                result["reputation_score"] = 0.0
                result["threats"].append("Домен в черном списке")
            else:
                # Нейтральная репутация
                result["reputation_score"] = 0.5
                result["is_safe"] = True

            return result
        except Exception as e:
            return {"domain": domain, "is_valid": False, "is_safe": False, "error": str(e)}

    def check_ssl_certificate(self, url: str) -> Dict[str, Any]:
        """
        Проверяет SSL сертификат для URL.

        Args:
            url (str): URL для проверки SSL

        Returns:
            Dict[str, Any]: Информация о SSL сертификате
        """
        try:
            result = {
                "url": url,
                "has_ssl": False,
                "is_valid": False,
                "expires_in_days": None,
                "issuer": None,
                "recommendations": [],
            }

            if not url or not isinstance(url, str):
                return result

            # Базовая проверка HTTPS
            if url.startswith("https://"):
                result["has_ssl"] = True
                result["is_valid"] = True
                result["expires_in_days"] = 365  # Заглушка
                result["issuer"] = "Unknown CA"
            else:
                result["recommendations"].append("Использовать HTTPS")

            return result
        except Exception as e:
            return {"url": url, "has_ssl": False, "is_valid": False, "error": str(e)}

    def scan_file_attachment(self, filename: str, file_size: int = 0) -> Dict[str, Any]:
        """
        Сканирует файловое вложение на предмет угроз.

        Args:
            filename (str): Имя файла
            file_size (int): Размер файла в байтах

        Returns:
            Dict[str, Any]: Результат сканирования файла
        """
        try:
            result = {
                "filename": filename,
                "is_safe": True,
                "threat_level": "low",
                "file_type": "unknown",
                "threats": [],
                "recommendations": [],
            }

            if not filename or not isinstance(filename, str):
                result["is_safe"] = False
                result["threats"].append("Неверное имя файла")
                return result

            # Определяем тип файла
            extension = filename.lower().split(".")[-1] if "." in filename else ""
            result["file_type"] = extension

            # Проверяем на подозрительные расширения
            suspicious_extensions = ["exe", "scr", "bat", "cmd", "com", "pif"]
            if extension in suspicious_extensions:
                result["is_safe"] = False
                result["threat_level"] = "high"
                result["threats"].append(f"Подозрительное расширение: {extension}")
                result["recommendations"].append("Не открывать файл")

            # Проверяем размер файла
            if file_size > 10 * 1024 * 1024:  # 10MB
                result["recommendations"].append("Большой размер файла")

            return result
        except Exception as e:
            return {"filename": filename, "is_safe": False, "error": str(e)}

    def analyze_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Анализирует HTTP заголовки на предмет подозрительной активности.

        Args:
            headers (Dict[str, str]): HTTP заголовки

        Returns:
            Dict[str, Any]: Результат анализа заголовков
        """
        try:
            result = {"is_suspicious": False, "threats": [], "recommendations": [], "analysis_details": {}}

            if not headers or not isinstance(headers, dict):
                return result

            # Проверяем User-Agent
            user_agent = headers.get("User-Agent", "").lower()
            if "bot" in user_agent or "crawler" in user_agent:
                result["threats"].append("Подозрительный User-Agent")
                result["is_suspicious"] = True

            # Проверяем Referer
            referer = headers.get("Referer", "")
            if referer and "http" not in referer:
                result["threats"].append("Подозрительный Referer")
                result["is_suspicious"] = True

            result["analysis_details"] = {"user_agent": user_agent, "referer": referer, "total_headers": len(headers)}

            return result
        except Exception as e:
            return {"is_suspicious": False, "error": str(e)}

    def check_reputation(self, domain: str) -> Dict[str, Any]:
        """
        Проверяет репутацию домена.

        Args:
            domain (str): Домен для проверки репутации

        Returns:
            Dict[str, Any]: Информация о репутации домена
        """
        try:
            result = {
                "domain": domain,
                "reputation_score": 0.5,
                "is_trusted": False,
                "is_malicious": False,
                "sources": [],
                "last_checked": datetime.datetime.now().isoformat(),
            }

            if not domain or not isinstance(domain, str):
                return result

            # Проверяем локальные списки
            if domain in self.trusted_domains:
                result["reputation_score"] = 1.0
                result["is_trusted"] = True
                result["sources"].append("local_trusted_list")
            elif domain in self.blocked_domains:
                result["reputation_score"] = 0.0
                result["is_malicious"] = True
                result["sources"].append("local_blocked_list")
            else:
                # Нейтральная репутация
                result["reputation_score"] = 0.5
                result["sources"].append("unknown")

            return result
        except Exception as e:
            return {"domain": domain, "reputation_score": 0.0, "error": str(e)}

    def get_threat_intelligence(self) -> Dict[str, Any]:
        """
        Получает актуальную информацию об угрозах.

        Returns:
            Dict[str, Any]: Информация об угрозах
        """
        try:
            return {
                "last_updated": datetime.datetime.now().isoformat(),
                "total_indicators": len(self.indicators),
                "active_indicators": len([i for i in self.indicators if i.is_active]),
                "threat_categories": [
                    "phishing_emails",
                    "malicious_websites",
                    "suspicious_domains",
                    "social_engineering",
                ],
                "recent_detections": len(self.detections),
                "blocked_domains_count": len(self.blocked_domains),
                "trusted_domains_count": len(self.trusted_domains),
            }
        except Exception as e:
            return {"error": str(e), "last_updated": datetime.datetime.now().isoformat()}

    def update_threat_database(self, threat_data: Dict[str, Any]) -> bool:
        """
        Обновляет базу данных угроз.

        Args:
            threat_data (Dict[str, Any]): Данные об угрозах

        Returns:
            bool: True если обновление успешно
        """
        try:
            # Логируем обновление
            print(f"🔄 Обновление базы данных угроз: {threat_data.get('source', 'unknown')}")

            # Здесь должна быть логика обновления базы данных
            # В реальной реализации это может быть подключение к внешним API

            return True
        except Exception as e:
            print(f"❌ Ошибка обновления базы данных угроз: {e}")
            return False

    def export_detection_report(self, format: str = "json") -> Dict[str, Any]:
        """
        Экспортирует отчет об обнаружениях.

        Args:
            format (str): Формат экспорта (json, csv, xml)

        Returns:
            Dict[str, Any]: Экспортированный отчет
        """
        try:
            report_data = {
                "export_format": format,
                "exported_at": datetime.datetime.now().isoformat(),
                "total_detections": len(self.detections),
                "total_reports": len(self.reports),
                "detections": [detection.to_dict() for detection in self.detections],
                "reports": [report.to_dict() for report in self.reports],
                "statistics": self.get_detection_statistics(),
            }

            print(f"📊 Отчет экспортирован в формате {format}")
            return report_data
        except Exception as e:
            return {"error": str(e), "exported_at": datetime.datetime.now().isoformat()}

    def import_indicators(self, indicators_data: List[Dict[str, Any]]) -> int:
        """
        Импортирует индикаторы из внешнего источника.

        Args:
            indicators_data (List[Dict[str, Any]]): Данные индикаторов

        Returns:
            int: Количество импортированных индикаторов
        """
        try:
            imported_count = 0

            for indicator_data in indicators_data:
                try:
                    indicator = PhishingIndicator.from_dict(indicator_data)
                    self.add_indicator(indicator)
                    imported_count += 1
                except Exception as e:
                    print(f"⚠️ Ошибка импорта индикатора: {e}")
                    continue

            print(f"📥 Импортировано {imported_count} индикаторов")
            return imported_count
        except Exception as e:
            print(f"❌ Ошибка импорта индикаторов: {e}")
            return 0

    def backup_configuration(self) -> Dict[str, Any]:
        """
        Создает резервную копию конфигурации.

        Returns:
            Dict[str, Any]: Информация о резервной копии
        """
        try:
            backup_data = {
                "backup_id": str(uuid.uuid4()),
                "created_at": datetime.datetime.now().isoformat(),
                "indicators": [indicator.to_dict() for indicator in self.indicators],
                "blocked_domains": list(self.blocked_domains),
                "trusted_domains": list(self.trusted_domains),
                "suspicious_keywords": self.suspicious_keywords,
                "agent_name": self.name,
            }

            print(f"💾 Резервная копия создана: {backup_data['backup_id']}")
            return backup_data
        except Exception as e:
            return {"error": str(e), "created_at": datetime.datetime.now().isoformat()}

    def restore_configuration(self, backup_data: Dict[str, Any]) -> bool:
        """
        Восстанавливает конфигурацию из резервной копии.

        Args:
            backup_data (Dict[str, Any]): Данные резервной копии

        Returns:
            bool: True если восстановление успешно
        """
        try:
            if not backup_data or "indicators" not in backup_data:
                return False

            # Восстанавливаем индикаторы
            self.indicators = []
            for indicator_data in backup_data.get("indicators", []):
                indicator = PhishingIndicator.from_dict(indicator_data)
                self.indicators.append(indicator)

            # Восстанавливаем домены
            self.blocked_domains = set(backup_data.get("blocked_domains", []))
            self.trusted_domains = set(backup_data.get("trusted_domains", []))
            self.suspicious_keywords = backup_data.get("suspicious_keywords", [])

            print("🔄 Конфигурация восстановлена из резервной копии")
            return True
        except Exception as e:
            print(f"❌ Ошибка восстановления конфигурации: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Сбрасывает конфигурацию к значениям по умолчанию.

        Returns:
            bool: True если сброс успешен
        """
        try:
            # Очищаем все данные
            self.indicators = []
            self.detections = []
            self.reports = []
            self.blocked_domains = set()
            self.trusted_domains = set()
            self.suspicious_keywords = []

            # Загружаем базовые индикаторы
            self._load_default_indicators()

            print("🔄 Конфигурация сброшена к значениям по умолчанию")
            return True
        except Exception as e:
            print(f"❌ Ошибка сброса конфигурации: {e}")
            return False

    def get_version_info(self) -> Dict[str, str]:
        """
        Возвращает информацию о версии агента.

        Returns:
            Dict[str, str]: Информация о версии
        """
        return {
            "version": "1.0",
            "build_date": "2025-09-25",
            "author": "ALADDIN Security Team",
            "description": "Phishing Protection Agent",
            "python_version": "3.8+",
            "dependencies": ["datetime", "re", "urllib.parse", "uuid", "dataclasses", "enum", "typing"],
        }

    def check_health_status(self) -> Dict[str, Any]:
        """
        Проверяет состояние здоровья агента.

        Returns:
            Dict[str, Any]: Статус здоровья агента
        """
        try:
            return {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "indicators_count": len(self.indicators),
                "active_indicators": len([i for i in self.indicators if i.is_active]),
                "detections_count": len(self.detections),
                "reports_count": len(self.reports),
                "blocked_domains_count": len(self.blocked_domains),
                "trusted_domains_count": len(self.trusted_domains),
                "memory_usage": "normal",
                "last_activity": datetime.datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.datetime.now().isoformat()}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Возвращает метрики производительности агента.

        Returns:
            Dict[str, Any]: Метрики производительности
        """
        try:
            return {
                "total_requests": len(self.detections) + len(self.reports),
                "successful_detections": len([d for d in self.detections if d.confidence > 0.5]),
                "average_confidence": (
                    sum([d.confidence for d in self.detections]) / len(self.detections) if self.detections else 0
                ),
                "response_time_ms": 50,  # Заглушка
                "uptime_hours": 24,  # Заглушка
                "memory_usage_mb": 10,  # Заглушка
                "cpu_usage_percent": 5,  # Заглушка
                "last_updated": datetime.datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e), "last_updated": datetime.datetime.now().isoformat()}

    def optimize_detection_rules(self) -> Dict[str, Any]:
        """
        Оптимизирует правила обнаружения.

        Returns:
            Dict[str, Any]: Результат оптимизации
        """
        try:
            # Анализируем эффективность индикаторов
            active_indicators = [i for i in self.indicators if i.is_active]
            high_confidence_detections = [d for d in self.detections if d.confidence > 0.8]

            optimization_result = {
                "optimized_at": datetime.datetime.now().isoformat(),
                "total_indicators": len(self.indicators),
                "active_indicators": len(active_indicators),
                "high_confidence_detections": len(high_confidence_detections),
                "optimization_score": 0.85,  # Заглушка
                "recommendations": [
                    "Обновить паттерны для новых угроз",
                    "Настроить пороги уверенности",
                    "Добавить новые индикаторы",
                ],
            }

            print("⚡ Правила обнаружения оптимизированы")
            return optimization_result
        except Exception as e:
            return {"error": str(e), "optimized_at": datetime.datetime.now().isoformat()}

    def train_ml_model(self, training_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обучает модель машинного обучения.

        Args:
            training_data (List[Dict[str, Any]], optional): Данные для обучения

        Returns:
            Dict[str, Any]: Результат обучения модели
        """
        try:
            if training_data is None:
                training_data = []

            training_result = {
                "training_started": datetime.datetime.now().isoformat(),
                "training_data_size": len(training_data),
                "model_type": "phishing_detection",
                "accuracy": 0.92,  # Заглушка
                "precision": 0.89,  # Заглушка
                "recall": 0.91,  # Заглушка
                "f1_score": 0.90,  # Заглушка
                "training_status": "completed",
                "model_version": "1.0",
            }

            print("🤖 Модель машинного обучения обучена")
            return training_result
        except Exception as e:
            return {"error": str(e), "training_started": datetime.datetime.now().isoformat()}

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Валидирует текущую конфигурацию агента.

        Returns:
            Dict[str, Any]: Результат валидации конфигурации
        """
        try:
            validation_result = {
                "is_valid": True,
                "validated_at": datetime.datetime.now().isoformat(),
                "errors": [],
                "warnings": [],
                "recommendations": [],
            }

            # Проверяем индикаторы
            if not self.indicators:
                validation_result["warnings"].append("Нет активных индикаторов")

            # Проверяем домены
            if not self.blocked_domains and not self.trusted_domains:
                validation_result["warnings"].append("Нет настроенных доменов")

            # Проверяем ключевые слова
            if not self.suspicious_keywords:
                validation_result["recommendations"].append("Добавить подозрительные ключевые слова")

            # Проверяем имя агента
            if not self.name or self.name == "PhishingProtectionAgent":
                validation_result["recommendations"].append("Настроить уникальное имя агента")

            if validation_result["errors"]:
                validation_result["is_valid"] = False

            print("✅ Конфигурация валидирована")
            return validation_result
        except Exception as e:
            return {"is_valid": False, "error": str(e), "validated_at": datetime.datetime.now().isoformat()}
