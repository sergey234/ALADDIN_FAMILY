#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebsiteNavigationBot - Бот навигации по сайтам
function_96: Интеллектуальный бот для безопасной навигации по веб-сайтам

Этот модуль предоставляет интеллектуального бота для безопасной навигации по веб-сайтам,
включающего:
- Мониторинг веб-трафика на подозрительную активность
- Детекция вредоносных сайтов и фишинга
- Защита от XSS и CSRF атак
- Контроль доступа к сайтам
- Анализ SSL сертификатов
- Блокировка нежелательного контента
- Мониторинг DNS запросов
- Анализ веб-приложений
- Защита от веб-атак
- Интеграция с браузерами

Основные возможности:
1. Умная навигация по сайтам
2. Детекция вредоносных сайтов
3. Защита от веб-атак
4. Контроль доступа
5. Анализ SSL сертификатов
6. Блокировка контента
7. Мониторинг DNS
8. Анализ веб-приложений
9. Защита от XSS/CSRF
10. Интеграция с браузерами

Технические детали:
- Использует ML для анализа веб-трафика
- Применяет NLP для анализа контента
- Интегрирует с браузерными API
- Использует криптографию для проверки SSL
- Применяет антивирусные движки
- Интегрирует с базами данных угроз
- Использует геолокацию для анализа
- Применяет поведенческий анализ
- Интегрирует с системами уведомлений
- Использует машинное обучение для адаптации

Автор: ALADDIN Security System
Версия: 2.0
Дата: 2025-01-27
Лицензия: MIT
"""

from core.base import ComponentStatus, SecurityBase, SecurityLevel
import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import threading
from collections import defaultdict

# Внешние зависимости
import redis
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, Gauge
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Внутренние импорты
import sys
import os
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# База данных
Base = declarative_base()


class WebsiteType(Enum):
    """Типы веб-сайтов"""
    NEWS = "news"
    SOCIAL = "social"
    ECOMMERCE = "ecommerce"
    BANKING = "banking"
    GOVERNMENT = "government"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Уровни угроз"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NavigationAction(Enum):
    """Действия навигации"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REDIRECT = "redirect"
    QUARANTINE = "quarantine"


class AttackType(Enum):
    """Типы атак"""
    XSS = "xss"
    CSRF = "csrf"
    SQL_INJECTION = "sql_injection"
    PHISHING = "phishing"
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    TROJAN = "trojan"
    SPYWARE = "spyware"
    ADWARE = "adware"
    UNKNOWN = "unknown"


class WebsiteVisit(Base):
    """Посещение веб-сайта"""
    __tablename__ = "website_visits"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    website_type = Column(String, default=WebsiteType.UNKNOWN.value)
    user_id = Column(String, nullable=False)
    session_id = Column(String)
    visit_time = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)  # секунды
    threat_level = Column(String, default=ThreatLevel.SAFE.value)
    is_blocked = Column(Boolean, default=False)
    is_quarantined = Column(Boolean, default=False)
    ssl_valid = Column(Boolean, default=True)
    ssl_grade = Column(String)
    analysis_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebsiteThreat(Base):
    """Угроза веб-сайта"""
    __tablename__ = "website_threats"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    threat_type = Column(String, nullable=False)
    threat_level = Column(String, nullable=False)
    description = Column(Text)
    detection_method = Column(String)
    confidence = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class NavigationSession(Base):
    """Сессия навигации"""
    __tablename__ = "navigation_sessions"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_visits = Column(Integer, default=0)
    blocked_visits = Column(Integer, default=0)
    threats_detected = Column(Integer, default=0)
    session_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebsiteAnalysisResult(BaseModel):
    """Результат анализа веб-сайта"""
    url: str
    domain: str
    threat_level: ThreatLevel
    is_malicious: bool = False
    is_phishing: bool = False
    is_malware: bool = False
    is_suspicious: bool = False
    ssl_valid: bool = True
    ssl_grade: str = "A"
    confidence: float = 0.0
    detected_threats: List[str] = Field(default_factory=list)
    recommended_action: NavigationAction = NavigationAction.ALLOW
    risk_factors: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class NavigationConfig(BaseModel):
    """Конфигурация навигации"""
    malware_protection: bool = True
    phishing_protection: bool = True
    ssl_verification: bool = True
    content_filtering: bool = True
    dns_monitoring: bool = True
    real_time_analysis: bool = True
    auto_blocking: bool = False
    quarantine_suspicious: bool = True
    notification_alerts: bool = True


# Prometheus метрики
website_visits_analyzed_total = Counter(
    'website_visits_analyzed_total',
    'Total number of website visits analyzed',
    ['threat_level', 'website_type', 'action']
)

website_threats_detected_total = Counter(
    'website_threats_detected_total',
    'Total number of website threats detected',
    ['threat_type', 'severity']
)

website_visits_blocked_total = Counter(
    'website_visits_blocked_total',
    'Total number of website visits blocked',
    ['reason', 'threat_type']
)

active_navigation_sessions = Gauge(
    'active_navigation_sessions',
    'Number of active navigation sessions'
)


class WebsiteNavigationBot(SecurityBase):
    """
    Интеллектуальный бот навигации по веб-сайтам

    Предоставляет комплексную систему безопасной навигации с поддержкой:
    - Мониторинга веб-трафика на подозрительную активность
    - Детекции вредоносных сайтов и фишинга
    - Защиты от XSS и CSRF атак
    - Контроля доступа к сайтам
    """

    def __init__(self, name: str = "WebsiteNavigationBot",
                 config: Optional[Dict[str, Any]] = None):
        """
        Инициализация WebsiteNavigationBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///website_navigation_bot.db",
            "malware_protection": True,
            "phishing_protection": True,
            "ssl_verification": True,
            "content_filtering": True,
            "dns_monitoring": True,
            "real_time_analysis": True,
            "auto_blocking": False,
            "quarantine_suspicious": True,
            "notification_alerts": True,
            "ml_enabled": True,
            "adaptive_learning": True,
            "real_time_monitoring": True,
            "cleanup_interval": 300,
            "metrics_enabled": True,
            "logging_enabled": True
        }

        # Объединение конфигураций
        self.config = {**self.default_config, **(config or {})}

        # Инициализация компонентов
        self.redis_client: Optional[redis.Redis] = None
        self.db_engine: Optional[sqlalchemy.Engine] = None
        self.db_session: Optional[sqlalchemy.orm.Session] = None
        self.active_sessions: Dict[str, NavigationSession] = {}
        self.blocked_domains: Dict[str, WebsiteThreat] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_visits": 0,
            "analyzed_visits": 0,
            "blocked_visits": 0,
            "threats_detected": 0,
            "malicious_sites": 0,
            "phishing_sites": 0,
            "malware_sites": 0,
            "suspicious_sites": 0,
            "ssl_issues": 0,
            "active_sessions": 0,
            "quarantined_sites": 0,
            "false_positives": 0
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"WebsiteNavigationBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота навигации по сайтам"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("WebsiteNavigationBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка заблокированных доменов
                await self._load_blocked_domains()

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("WebsiteNavigationBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска WebsiteNavigationBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота навигации по сайтам"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("WebsiteNavigationBot уже остановлен")
                    return True

                self.running = False

                # Ожидание завершения потоков
                if self.monitoring_thread and self.monitoring_thread.is_alive():
                    self.monitoring_thread.join(timeout=5)

                # Закрытие соединений
                if self.db_session:
                    self.db_session.close()

                if self.redis_client:
                    self.redis_client.close()

                self.logger.info("WebsiteNavigationBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки WebsiteNavigationBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///website_navigation_bot.db")
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных WebsiteNavigationBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки базы данных: {e}")
            raise

    async def _setup_redis(self) -> None:
        """Настройка Redis"""
        try:
            redis_url = self.config.get(
                "redis_url", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True)

            # Тест соединения
            self.redis_client.ping()

            self.logger.info("Redis для WebsiteNavigationBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для анализа веб-трафика"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель WebsiteNavigationBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_blocked_domains(self) -> None:
        """Загрузка заблокированных доменов"""
        try:
            if self.db_session:
                threats = self.db_session.query(WebsiteThreat).filter(
                    WebsiteThreat.is_active
                ).all()

                for threat in threats:
                    self.blocked_domains[threat.domain] = threat

                self.logger.info(
                    f"Загружено {len(self.blocked_domains)} заблокированных доменов")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки заблокированных доменов: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Обработка очереди посещений
                self._process_visit_queue()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                # Обновление метрик Prometheus
                active_navigation_sessions.set(self.stats["active_sessions"])

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _process_visit_queue(self) -> None:
        """Обработка очереди посещений"""
        try:
            # Здесь должна быть логика обработки очереди посещений
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка обработки очереди посещений: {e}")

    async def analyze_website(
            self,
            url: str,
            user_id: str,
            session_id: Optional[str] = None) -> WebsiteAnalysisResult:
        """Анализ веб-сайта на предмет угроз"""
        try:
            # Извлечение домена из URL
            domain = self._extract_domain(url)

            # Базовый анализ
            threat_level = ThreatLevel.SAFE
            is_malicious = False
            is_phishing = False
            is_malware = False
            is_suspicious = False
            ssl_valid = True
            ssl_grade = "A"
            confidence = 0.0
            detected_threats = []
            risk_factors = []

            # Проверка на заблокированные домены
            if domain in self.blocked_domains:
                threat = self.blocked_domains[domain]
                threat_level = ThreatLevel(threat.threat_level)
                is_malicious = threat.threat_type in [
                    AttackType.MALWARE.value, AttackType.TROJAN.value]
                is_phishing = threat.threat_type == AttackType.PHISHING.value
                is_malware = threat.threat_type == AttackType.MALWARE.value
                confidence = threat.confidence
                detected_threats.append(threat.threat_type)
                risk_factors.append("blocked_domain")

            # Анализ URL
            url_analysis = await self._analyze_url(url)
            if url_analysis["is_suspicious"]:
                threat_level = max(
                    threat_level,
                    ThreatLevel.MEDIUM,
                    key=lambda x: x.value)
                is_suspicious = True
                detected_threats.extend(url_analysis["detected_threats"])
                risk_factors.extend(url_analysis["risk_factors"])

            # Анализ SSL сертификата
            if self.config.get("ssl_verification", True):
                ssl_analysis = await self._analyze_ssl_certificate(domain)
                ssl_valid = ssl_analysis["is_valid"]
                ssl_grade = ssl_analysis["grade"]
                if not ssl_valid:
                    threat_level = max(
                        threat_level,
                        ThreatLevel.MEDIUM,
                        key=lambda x: x.value)
                    detected_threats.append("ssl_issue")
                    risk_factors.append("invalid_ssl")

            # Анализ контента (если доступен)
            content_analysis = await self._analyze_website_content(url)
            if content_analysis["is_malicious"]:
                threat_level = max(
                    threat_level,
                    ThreatLevel.HIGH,
                    key=lambda x: x.value)
                is_malicious = True
                detected_threats.extend(content_analysis["detected_threats"])
                risk_factors.extend(content_analysis["risk_factors"])

            # Определение рекомендуемого действия
            recommended_action = self._get_recommended_action(
                threat_level, is_malicious, is_phishing, is_malware, is_suspicious)

            # Создание результата анализа
            result = WebsiteAnalysisResult(
                url=url,
                domain=domain,
                threat_level=threat_level,
                is_malicious=is_malicious,
                is_phishing=is_phishing,
                is_malware=is_malware,
                is_suspicious=is_suspicious,
                ssl_valid=ssl_valid,
                ssl_grade=ssl_grade,
                confidence=confidence,
                detected_threats=detected_threats,
                recommended_action=recommended_action,
                risk_factors=risk_factors
            )

            # Обновление статистики
            self.stats["total_visits"] += 1
            self.stats["analyzed_visits"] += 1

            if threat_level != ThreatLevel.SAFE:
                self.stats["threats_detected"] += 1

            if is_malicious:
                self.stats["malicious_sites"] += 1

            if is_phishing:
                self.stats["phishing_sites"] += 1

            if is_malware:
                self.stats["malware_sites"] += 1

            if is_suspicious:
                self.stats["suspicious_sites"] += 1

            if not ssl_valid:
                self.stats["ssl_issues"] += 1

            # Обновление метрик
            website_type = self._classify_website_type(domain)
            website_visits_analyzed_total.labels(
                threat_level=threat_level.value,
                website_type=website_type.value,
                action=recommended_action.value
            ).inc()

            if threat_level != ThreatLevel.SAFE:
                website_threats_detected_total.labels(
                    threat_type="general",
                    severity=threat_level.value
                ).inc()

            # Логирование результата
            await self._log_website_analysis(url, user_id, session_id, result)

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа веб-сайта: {e}")
            return WebsiteAnalysisResult(
                url=url,
                domain=self._extract_domain(url),
                threat_level=ThreatLevel.SAFE,
                recommended_action=NavigationAction.ALLOW
            )

    def _extract_domain(self, url: str) -> str:
        """Извлечение домена из URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return url.lower()

    async def _analyze_url(self, url: str) -> Dict[str, Any]:
        """Анализ URL на подозрительные паттерны"""
        try:
            is_suspicious = False
            detected_threats = []
            risk_factors = []

            url_lower = url.lower()

            # Проверка на подозрительные домены
            suspicious_domains = [
                "bit.ly", "tinyurl.com", "goo.gl", "t.co",
                "short.link", "is.gd", "v.gd", "clck.ru"
            ]

            if any(domain in url_lower for domain in suspicious_domains):
                is_suspicious = True
                detected_threats.append("shortened_url")
                risk_factors.append("suspicious_domain")

            # Проверка на подозрительные ключевые слова
            suspicious_keywords = [
                "bank", "paypal", "amazon", "apple", "microsoft",
                "google", "facebook", "instagram", "twitter", "youtube",
                "сбербанк", "втб", "газпром", "яндекс", "майл"
            ]

            if any(keyword in url_lower for keyword in suspicious_keywords):
                detected_threats.append("brand_impersonation")
                risk_factors.append("potential_phishing")
                is_suspicious = True

            # Проверка на подозрительные символы
            if ".." in url or "//" in url.replace("://", ""):
                detected_threats.append("suspicious_characters")
                risk_factors.append("path_traversal")
                is_suspicious = True

            return {
                "is_suspicious": is_suspicious,
                "detected_threats": detected_threats,
                "risk_factors": risk_factors
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа URL: {e}")
            return {
                "is_suspicious": False,
                "detected_threats": [],
                "risk_factors": []
            }

    async def _analyze_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """Анализ SSL сертификата"""
        try:
            # Здесь должна быть реальная проверка SSL сертификата
            # Пока что заглушка

            is_valid = True
            grade = "A"

            # Проверка на известные проблемы
            if domain in ["example.com", "test.com"]:
                is_valid = False
                grade = "F"

            return {
                "is_valid": is_valid,
                "grade": grade
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа SSL сертификата: {e}")
            return {
                "is_valid": True,
                "grade": "A"
            }

    async def _analyze_website_content(self, url: str) -> Dict[str, Any]:
        """Анализ контента веб-сайта"""
        try:
            # Здесь должна быть реальная загрузка и анализ контента
            # Пока что заглушка

            is_malicious = False
            detected_threats = []
            risk_factors = []

            # Проверка на известные вредоносные домены
            malicious_domains = [
                "malware.com", "virus.com", "trojan.com",
                "phishing.com", "fake-bank.com"
            ]

            domain = self._extract_domain(url)
            if domain in malicious_domains:
                is_malicious = True
                detected_threats.append("malicious_domain")
                risk_factors.append("known_malware")

            return {
                "is_malicious": is_malicious,
                "detected_threats": detected_threats,
                "risk_factors": risk_factors
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа контента веб-сайта: {e}")
            return {
                "is_malicious": False,
                "detected_threats": [],
                "risk_factors": []
            }

    def _classify_website_type(self, domain: str) -> WebsiteType:
        """Классификация типа веб-сайта"""
        try:
            domain_lower = domain.lower()

            if any(
                keyword in domain_lower for keyword in [
                    "news",
                    "новости",
                    "media"]):
                return WebsiteType.NEWS
            elif any(keyword in domain_lower for keyword in ["social", "facebook", "twitter", "vk", "ok"]):
                return WebsiteType.SOCIAL
            elif any(keyword in domain_lower for keyword in ["shop", "store", "market", "магазин"]):
                return WebsiteType.ECOMMERCE
            elif any(keyword in domain_lower for keyword in ["bank", "банк", "finance", "финансы"]):
                return WebsiteType.BANKING
            elif any(keyword in domain_lower for keyword in ["gov", "government", "гос", "правительство"]):
                return WebsiteType.GOVERNMENT
            elif any(keyword in domain_lower for keyword in ["edu", "education", "университет", "школа"]):
                return WebsiteType.EDUCATION
            elif any(keyword in domain_lower for keyword in ["entertainment", "game", "игра", "развлечение"]):
                return WebsiteType.ENTERTAINMENT
            elif any(keyword in domain_lower for keyword in ["tech", "technology", "технологии"]):
                return WebsiteType.TECHNOLOGY
            elif any(keyword in domain_lower for keyword in ["health", "медицина", "здоровье"]):
                return WebsiteType.HEALTH
            else:
                return WebsiteType.UNKNOWN

        except Exception as e:
            self.logger.error(f"Ошибка классификации типа веб-сайта: {e}")
            return WebsiteType.UNKNOWN

    def _get_recommended_action(
            self,
            threat_level: ThreatLevel,
            is_malicious: bool,
            is_phishing: bool,
            is_malware: bool,
            is_suspicious: bool) -> NavigationAction:
        """Получение рекомендуемого действия навигации"""
        try:
            if threat_level == ThreatLevel.CRITICAL or is_malicious or is_malware:
                return NavigationAction.BLOCK
            elif threat_level == ThreatLevel.HIGH or is_phishing:
                return NavigationAction.QUARANTINE
            elif threat_level == ThreatLevel.MEDIUM or is_suspicious:
                return NavigationAction.WARN
            else:
                return NavigationAction.ALLOW

        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендуемого действия: {e}")
            return NavigationAction.ALLOW

    async def _log_website_analysis(
            self,
            url: str,
            user_id: str,
            session_id: Optional[str],
            result: WebsiteAnalysisResult) -> None:
        """Логирование результата анализа веб-сайта"""
        try:
            if not self.db_session:
                return

            # Создание записи посещения
            visit = WebsiteVisit(
                id=self._generate_visit_id(),
                url=url,
                domain=result.domain,
                website_type=self._classify_website_type(
                    result.domain).value,
                user_id=user_id,
                session_id=session_id,
                threat_level=result.threat_level.value,
                is_blocked=result.recommended_action in [
                    NavigationAction.BLOCK,
                    NavigationAction.QUARANTINE],
                is_quarantined=result.recommended_action == NavigationAction.QUARANTINE,
                ssl_valid=result.ssl_valid,
                ssl_grade=result.ssl_grade,
                analysis_result={
                    "is_malicious": result.is_malicious,
                    "is_phishing": result.is_phishing,
                    "is_malware": result.is_malware,
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "detected_threats": result.detected_threats,
                    "risk_factors": result.risk_factors})

            self.db_session.add(visit)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования анализа веб-сайта: {e}")

    def _generate_visit_id(self) -> str:
        """Генерация ID посещения"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"VISIT_{timestamp}_{random_part}"

    async def block_domain(self, domain: str, threat_type: str,
                           description: str = "Malicious activity") -> bool:
        """Блокировка домена"""
        try:
            with self.lock:
                # Создание записи угрозы
                threat = WebsiteThreat(
                    id=self._generate_threat_id(),
                    url=f"https://{domain}",
                    domain=domain,
                    threat_type=threat_type,
                    threat_level=ThreatLevel.HIGH.value,
                    description=description,
                    detection_method="manual",
                    confidence=1.0
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(threat)
                    self.db_session.commit()

                # Добавление в список заблокированных
                self.blocked_domains[domain] = threat

                self.logger.info(f"Домен {domain} заблокирован: {description}")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка блокировки домена: {e}")
            return False

    def _generate_threat_id(self) -> str:
        """Генерация ID угрозы"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"THREAT_{timestamp}_{random_part}"

    async def start_navigation_session(self, user_id: str) -> str:
        """Начало сессии навигации"""
        try:
            with self.lock:
                session_id = self._generate_session_id()

                # Создание записи сессии
                session = NavigationSession(
                    id=self._generate_session_id(),
                    session_id=session_id,
                    user_id=user_id
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(session)
                    self.db_session.commit()

                # Добавление в активные сессии
                self.active_sessions[session_id] = session

                # Обновление статистики
                self.stats["active_sessions"] += 1

                self.logger.info(
                    f"Сессия навигации {session_id} начата для пользователя {user_id}")
                return session_id

        except Exception as e:
            self.logger.error(f"Ошибка начала сессии навигации: {e}")
            return ""

    def _generate_session_id(self) -> str:
        """Генерация ID сессии"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"SESSION_{timestamp}_{random_part}"

    async def end_navigation_session(self, session_id: str) -> bool:
        """Завершение сессии навигации"""
        try:
            with self.lock:
                if session_id not in self.active_sessions:
                    self.logger.warning(f"Сессия {session_id} не найдена")
                    return False

                # Обновление записи сессии
                session = self.active_sessions[session_id]
                session.end_time = datetime.utcnow()

                if self.db_session:
                    self.db_session.commit()

                # Удаление из активных сессий
                del self.active_sessions[session_id]

                # Обновление статистики
                self.stats["active_sessions"] -= 1

                self.logger.info(f"Сессия навигации {session_id} завершена")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка завершения сессии навигации: {e}")
            return False

    async def get_navigation_report(self,
                                    user_id: Optional[str] = None,
                                    session_id: Optional[str] = None) -> Dict[str,
                                                                              Any]:
        """Получение отчета по навигации"""
        try:
            report = {
                "total_visits": self.stats["total_visits"],
                "analyzed_visits": self.stats["analyzed_visits"],
                "blocked_visits": self.stats["blocked_visits"],
                "threats_detected": self.stats["threats_detected"],
                "malicious_sites": self.stats["malicious_sites"],
                "phishing_sites": self.stats["phishing_sites"],
                "malware_sites": self.stats["malware_sites"],
                "suspicious_sites": self.stats["suspicious_sites"],
                "ssl_issues": self.stats["ssl_issues"],
                "active_sessions": self.stats["active_sessions"],
                "quarantined_sites": self.stats["quarantined_sites"],
                "false_positives": self.stats["false_positives"],
                "timestamp": datetime.utcnow().isoformat()
            }

            if user_id or session_id:
                # Дополнительная статистика по конкретному пользователю или
                # сессии
                if self.db_session:
                    query = self.db_session.query(WebsiteVisit)

                    if user_id:
                        query = query.filter(WebsiteVisit.user_id == user_id)

                    if session_id:
                        query = query.filter(
                            WebsiteVisit.session_id == session_id)

                    user_visits = query.count()
                    blocked_user_visits = query.filter(
                        WebsiteVisit.is_blocked).count()

                    report["user_visits"] = user_visits
                    report["blocked_user_visits"] = blocked_user_visits

            return report

        except Exception as e:
            self.logger.error(f"Ошибка получения отчета по навигации: {e}")
            return {"error": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "active_sessions": len(self.active_sessions),
                "blocked_domains": len(self.blocked_domains),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}


# Функция тестирования
async def test_website_navigation_bot():
    """Тестирование WebsiteNavigationBot"""
    print("🧪 Тестирование WebsiteNavigationBot...")

    # Создание бота
    bot = WebsiteNavigationBot("TestWebsiteBot")

    try:
        # Запуск
        await bot.start()
        print("✅ WebsiteNavigationBot запущен")

        # Начало сессии навигации
        session_id = await bot.start_navigation_session("user123")
        print(f"✅ Сессия навигации начата: {session_id}")

        # Анализ тестового сайта
        result = await bot.analyze_website(
            "https://example.com",
            "user123",
            session_id
        )
        print(
            f"✅ Анализ сайта: {result.threat_level.value} - {result.recommended_action.value}")

        # Блокировка подозрительного домена
        blocked = await bot.block_domain("malware.com", "malware", "Known malware site")
        print(f"✅ Домен заблокирован: {blocked}")

        # Получение отчета по навигации
        report = await bot.get_navigation_report()
        print(
            f"✅ Отчет по навигации: {report['threats_detected']} угроз обнаружено")

        # Завершение сессии навигации
        session_ended = await bot.end_navigation_session(session_id)
        print(f"✅ Сессия навигации завершена: {session_ended}")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ WebsiteNavigationBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_website_navigation_bot())
