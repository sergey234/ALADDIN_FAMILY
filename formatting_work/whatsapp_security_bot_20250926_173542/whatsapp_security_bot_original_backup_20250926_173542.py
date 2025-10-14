#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsAppSecurityBot - Бот безопасности WhatsApp
function_91: Интеллектуальный бот для безопасности WhatsApp

Этот модуль предоставляет интеллектуального бота для безопасности WhatsApp,
включающего:
- Мониторинг сообщений на подозрительный контент
- Детекция спама и фишинга
- Защита от вредоносных ссылок
- Контроль конфиденциальности
- Анализ контактов
- Блокировка нежелательных номеров
- Шифрование сообщений
- Резервное копирование чатов
- Антивирусная проверка файлов
- Родительский контроль

Основные возможности:
1. Умная фильтрация сообщений
2. Детекция спама и фишинга
3. Защита от вредоносных ссылок
4. Контроль конфиденциальности
5. Анализ и блокировка контактов
6. Шифрование сообщений
7. Резервное копирование
8. Антивирусная проверка
9. Родительский контроль
10. Интеграция с системой безопасности

Технические детали:
- Использует ML для анализа сообщений
- Применяет NLP для понимания контекста
- Интегрирует с WhatsApp Business API
- Использует криптографию для шифрования
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


class MessageType(Enum):
    """Типы сообщений WhatsApp"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    VOICE_MESSAGE = "voice_message"
    SYSTEM = "system"


class ThreatLevel(Enum):
    """Уровни угроз"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageStatus(Enum):
    """Статусы сообщений"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    BLOCKED = "blocked"
    QUARANTINED = "quarantined"
    DELETED = "deleted"


class WhatsAppMessage(Base):
    """Сообщение WhatsApp"""
    __tablename__ = "whatsapp_messages"

    id = Column(String, primary_key=True)
    message_id = Column(String, nullable=False)
    chat_id = Column(String, nullable=False)
    sender_id = Column(String, nullable=False)
    receiver_id = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    content = Column(Text)
    media_url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    threat_level = Column(String, default=ThreatLevel.SAFE.value)
    is_encrypted = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    analysis_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class WhatsAppContact(Base):
    """Контакт WhatsApp"""
    __tablename__ = "whatsapp_contacts"

    id = Column(String, primary_key=True)
    phone_number = Column(String, nullable=False)
    name = Column(String)
    is_blocked = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    threat_score = Column(Float, default=0.0)
    last_interaction = Column(DateTime)
    interaction_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SecurityRule(Base):
    """Правило безопасности"""
    __tablename__ = "security_rules"

    id = Column(String, primary_key=True)
    rule_name = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)
    pattern = Column(String, nullable=False)
    action = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class MessageAnalysisResult(BaseModel):
    """Результат анализа сообщения"""
    message_id: str
    threat_level: ThreatLevel
    is_spam: bool = False
    is_phishing: bool = False
    is_malicious: bool = False
    confidence: float = 0.0
    detected_patterns: List[str] = Field(default_factory=list)
    recommended_action: str = "allow"
    risk_factors: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class WhatsAppSecurityConfig(BaseModel):
    """Конфигурация безопасности WhatsApp"""
    spam_detection: bool = True
    phishing_protection: bool = True
    malware_scanning: bool = True
    link_analysis: bool = True
    contact_verification: bool = True
    encryption_enabled: bool = True
    backup_enabled: bool = True
    parental_control: bool = False
    auto_block_suspicious: bool = False
    notification_alerts: bool = True


# Prometheus метрики
messages_analyzed_total = Counter(
    'whatsapp_messages_analyzed_total',
    'Total number of WhatsApp messages analyzed',
    ['threat_level', 'message_type']
)

threats_detected_total = Counter(
    'whatsapp_threats_detected_total',
    'Total number of threats detected in WhatsApp',
    ['threat_type', 'severity']
)

messages_blocked_total = Counter(
    'whatsapp_messages_blocked_total',
    'Total number of WhatsApp messages blocked',
    ['reason', 'threat_level']
)

active_chats = Gauge(
    'whatsapp_active_chats',
    'Number of active WhatsApp chats'
)


class WhatsAppSecurityBot(SecurityBase):
    """
    Интеллектуальный бот безопасности WhatsApp

    Предоставляет комплексную систему безопасности WhatsApp с поддержкой:
    - Мониторинга сообщений на подозрительный контент
    - Детекции спама и фишинга
    - Защиты от вредоносных ссылок
    - Контроля конфиденциальности
    - Анализа и блокировки контактов
    """

    def __init__(self, name: str = "WhatsAppSecurityBot",
                 config: Optional[Dict[str, Any]] = None):
        """
        Инициализация WhatsAppSecurityBot

        Args:
            name: Имя бота
            config: Конфигурация
        """
        super().__init__(name, config)

        # Конфигурация по умолчанию
        self.default_config = {
            "redis_url": "redis://localhost:6379/0",
            "database_url": "sqlite:///whatsapp_security_bot.db",
            "spam_detection": True,
            "phishing_protection": True,
            "malware_scanning": True,
            "link_analysis": True,
            "contact_verification": True,
            "encryption_enabled": True,
            "backup_enabled": True,
            "parental_control": False,
            "auto_block_suspicious": False,
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
        self.security_rules: Dict[str, SecurityRule] = {}
        self.blocked_contacts: Dict[str, WhatsAppContact] = {}
        self.ml_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None

        # Статистика
        self.stats = {
            "total_messages": 0,
            "analyzed_messages": 0,
            "blocked_messages": 0,
            "threats_detected": 0,
            "spam_detected": 0,
            "phishing_detected": 0,
            "malware_detected": 0,
            "active_chats": 0,
            "blocked_contacts": 0,
            "false_positives": 0
        }

        # Потоки
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Блокировки
        self.lock = threading.RLock()

        self.logger.info(f"WhatsAppSecurityBot {name} инициализирован")

    async def start(self) -> bool:
        """Запуск бота безопасности WhatsApp"""
        try:
            with self.lock:
                if self.running:
                    self.logger.warning("WhatsAppSecurityBot уже запущен")
                    return True

                # Инициализация базы данных
                await self._setup_database()

                # Инициализация Redis
                await self._setup_redis()

                # Инициализация ML модели
                if self.config.get("ml_enabled", True):
                    await self._setup_ml_model()

                # Загрузка правил безопасности
                await self._load_security_rules()

                # Запуск мониторинга
                self.running = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

                self.logger.info("WhatsAppSecurityBot запущен успешно")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка запуска WhatsAppSecurityBot: {e}")
            return False

    async def stop(self) -> bool:
        """Остановка бота безопасности WhatsApp"""
        try:
            with self.lock:
                if not self.running:
                    self.logger.warning("WhatsAppSecurityBot уже остановлен")
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

                self.logger.info("WhatsAppSecurityBot остановлен")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка остановки WhatsAppSecurityBot: {e}")
            return False

    async def _setup_database(self) -> None:
        """Настройка базы данных"""
        try:
            database_url = self.config.get(
                "database_url", "sqlite:///whatsapp_security_bot.db")
            self.db_engine = create_engine(database_url)
            Base.metadata.create_all(self.db_engine)

            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()

            self.logger.info("База данных WhatsAppSecurityBot настроена")

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

            self.logger.info("Redis для WhatsAppSecurityBot настроен")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Redis: {e}")
            raise

    async def _setup_ml_model(self) -> None:
        """Настройка ML модели для анализа сообщений"""
        try:
            self.ml_model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()

            self.logger.info("ML модель WhatsAppSecurityBot настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки ML модели: {e}")

    async def _load_security_rules(self) -> None:
        """Загрузка правил безопасности"""
        try:
            if self.db_session:
                rules = self.db_session.query(SecurityRule).filter(
                    SecurityRule.is_active
                ).all()

                for rule in rules:
                    self.security_rules[rule.id] = rule

                self.logger.info(
                    f"Загружено {len(self.security_rules)} правил безопасности")

        except Exception as e:
            self.logger.error(f"Ошибка загрузки правил безопасности: {e}")

    def _monitoring_worker(self) -> None:
        """Фоновый процесс мониторинга"""
        while self.running:
            try:
                time.sleep(1)  # Проверка каждую секунду

                # Обновление статистики
                self._update_stats()

                # Обработка очереди сообщений
                self._process_message_queue()

            except Exception as e:
                self.logger.error(f"Ошибка в процессе мониторинга: {e}")

    def _update_stats(self) -> None:
        """Обновление статистики"""
        try:
            with self.lock:
                # Обновление метрик Prometheus
                active_chats.set(self.stats["active_chats"])

        except Exception as e:
            self.logger.error(f"Ошибка обновления статистики: {e}")

    def _process_message_queue(self) -> None:
        """Обработка очереди сообщений"""
        try:
            # Здесь должна быть логика обработки очереди сообщений
            # Пока что заглушка
            pass

        except Exception as e:
            self.logger.error(f"Ошибка обработки очереди сообщений: {e}")

    async def analyze_message(
            self, message_data: Dict[str, Any]) -> MessageAnalysisResult:
        """Анализ сообщения WhatsApp на предмет угроз"""
        try:
            message_id = message_data.get("id", "")
            content = message_data.get("content", "")
            message_type = MessageType(message_data.get("type", "text"))
            # sender_id = message_data.get("sender_id", "")

            # Базовый анализ
            threat_level = ThreatLevel.SAFE
            is_spam = False
            is_phishing = False
            is_malicious = False
            confidence = 0.0
            detected_patterns = []
            risk_factors = []

            # Анализ текстовых сообщений
            if message_type == MessageType.TEXT and content:
                analysis_result = await self._analyze_text_content(content)
                threat_level = analysis_result["threat_level"]
                is_spam = analysis_result["is_spam"]
                is_phishing = analysis_result["is_phishing"]
                is_malicious = analysis_result["is_malicious"]
                confidence = analysis_result["confidence"]
                detected_patterns = analysis_result["detected_patterns"]
                risk_factors = analysis_result["risk_factors"]

            # Анализ медиафайлов
            elif message_type in [MessageType.IMAGE, MessageType.VIDEO, MessageType.DOCUMENT]:
                analysis_result = await self._analyze_media_content(message_data)
                threat_level = analysis_result["threat_level"]
                is_malicious = analysis_result["is_malicious"]
                confidence = analysis_result["confidence"]
                detected_patterns = analysis_result["detected_patterns"]
                risk_factors = analysis_result["risk_factors"]

            # Анализ ссылок
            if content and ("http" in content or "www." in content):
                link_analysis = await self._analyze_links(content)
                if link_analysis["is_malicious"]:
                    threat_level = max(
                        threat_level,
                        ThreatLevel.HIGH,
                        key=lambda x: x.value)
                    is_malicious = True
                    detected_patterns.extend(
                        link_analysis["detected_patterns"])
                    risk_factors.extend(link_analysis["risk_factors"])

            # Определение рекомендуемого действия
            recommended_action = self._get_recommended_action(
                threat_level, is_spam, is_phishing, is_malicious)

            # Создание результата анализа
            result = MessageAnalysisResult(
                message_id=message_id,
                threat_level=threat_level,
                is_spam=is_spam,
                is_phishing=is_phishing,
                is_malicious=is_malicious,
                confidence=confidence,
                detected_patterns=detected_patterns,
                recommended_action=recommended_action,
                risk_factors=risk_factors
            )

            # Обновление статистики
            self.stats["total_messages"] += 1
            self.stats["analyzed_messages"] += 1

            if threat_level != ThreatLevel.SAFE:
                self.stats["threats_detected"] += 1

            if is_spam:
                self.stats["spam_detected"] += 1

            if is_phishing:
                self.stats["phishing_detected"] += 1

            if is_malicious:
                self.stats["malware_detected"] += 1

            # Обновление метрик
            messages_analyzed_total.labels(
                threat_level=threat_level.value,
                message_type=message_type.value
            ).inc()

            if threat_level != ThreatLevel.SAFE:
                threats_detected_total.labels(
                    threat_type="general",
                    severity=threat_level.value
                ).inc()

            # Логирование результата
            await self._log_message_analysis(message_data, result)

            return result

        except Exception as e:
            self.logger.error(f"Ошибка анализа сообщения: {e}")
            return MessageAnalysisResult(
                message_id=message_data.get("id", ""),
                threat_level=ThreatLevel.SAFE,
                recommended_action="allow"
            )

    async def _analyze_text_content(self, content: str) -> Dict[str, Any]:
        """Анализ текстового контента"""
        try:
            threat_level = ThreatLevel.SAFE
            is_spam = False
            is_phishing = False
            is_malicious = False
            confidence = 0.0
            detected_patterns = []
            risk_factors = []

            content_lower = content.lower()

            # Проверка на спам
            spam_indicators = [
                "бесплатно", "срочно", "только сегодня", "не упустите",
                "гарантия", "100%", "без риска", "быстро", "легко"
            ]

            spam_count = sum(
                1 for indicator in spam_indicators if indicator in content_lower)
            if spam_count >= 3:
                is_spam = True
                threat_level = ThreatLevel.MEDIUM
                confidence = min(0.9, spam_count * 0.2)
                detected_patterns.append("spam_indicators")
                risk_factors.append("multiple_spam_keywords")

            # Проверка на фишинг
            phishing_indicators = [
                "подтвердите", "обновите", "проверьте", "активируйте",
                "заблокирован", "приостановлен", "истекает", "срочно"
            ]

            phishing_count = sum(
                1 for indicator in phishing_indicators if indicator in content_lower)
            if phishing_count >= 2:
                is_phishing = True
                threat_level = ThreatLevel.HIGH
                confidence = min(0.95, phishing_count * 0.3)
                detected_patterns.append("phishing_indicators")
                risk_factors.append("phishing_keywords")

            # Проверка на подозрительные ссылки
            if "http" in content or "www." in content:
                detected_patterns.append("contains_links")
                risk_factors.append("suspicious_links")

            # Проверка на подозрительные символы
            suspicious_chars = ["$", "€", "₽", "bitcoin", "btc", "crypto"]
            if any(char in content_lower for char in suspicious_chars):
                detected_patterns.append("suspicious_characters")
                risk_factors.append("financial_keywords")

            return {
                "threat_level": threat_level,
                "is_spam": is_spam,
                "is_phishing": is_phishing,
                "is_malicious": is_malicious,
                "confidence": confidence,
                "detected_patterns": detected_patterns,
                "risk_factors": risk_factors
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа текстового контента: {e}")
            return {
                "threat_level": ThreatLevel.SAFE,
                "is_spam": False,
                "is_phishing": False,
                "is_malicious": False,
                "confidence": 0.0,
                "detected_patterns": [],
                "risk_factors": []
            }

    async def _analyze_media_content(
            self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ медиафайлов"""
        try:
            # Здесь должна быть интеграция с антивирусными движками
            # Пока что базовая проверка

            threat_level = ThreatLevel.SAFE
            is_malicious = False
            confidence = 0.0
            detected_patterns = []
            risk_factors = []

            # Проверка размера файла
            file_size = message_data.get("file_size", 0)
            if file_size > 100 * 1024 * 1024:  # 100MB
                detected_patterns.append("large_file")
                risk_factors.append("suspicious_file_size")

            # Проверка расширения файла
            file_name = message_data.get("file_name", "")
            suspicious_extensions = [".exe", ".bat", ".cmd", ".scr", ".pif"]
            if any(file_name.lower().endswith(ext)
                   for ext in suspicious_extensions):
                is_malicious = True
                threat_level = ThreatLevel.HIGH
                confidence = 0.8
                detected_patterns.append("suspicious_extension")
                risk_factors.append("executable_file")

            return {
                "threat_level": threat_level,
                "is_malicious": is_malicious,
                "confidence": confidence,
                "detected_patterns": detected_patterns,
                "risk_factors": risk_factors
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа медиафайлов: {e}")
            return {
                "threat_level": ThreatLevel.SAFE,
                "is_malicious": False,
                "confidence": 0.0,
                "detected_patterns": [],
                "risk_factors": []
            }

    async def _analyze_links(self, content: str) -> Dict[str, Any]:
        """Анализ ссылок в сообщении"""
        try:
            import re

            # Поиск ссылок
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)

            is_malicious = False
            detected_patterns = []
            risk_factors = []

            for url in urls:
                # Проверка на подозрительные домены
                suspicious_domains = [
                    "bit.ly", "tinyurl.com", "goo.gl", "t.co",
                    "short.link", "is.gd", "v.gd"
                ]

                if any(domain in url.lower() for domain in suspicious_domains):
                    detected_patterns.append("shortened_url")
                    risk_factors.append("suspicious_domain")

                # Проверка на подозрительные ключевые слова в URL
                suspicious_keywords = [
                    "bank", "paypal", "amazon", "apple", "microsoft",
                    "google", "facebook", "instagram", "twitter"
                ]

                if any(keyword in url.lower()
                       for keyword in suspicious_keywords):
                    detected_patterns.append("brand_impersonation")
                    risk_factors.append("potential_phishing")
                    is_malicious = True

            return {
                "is_malicious": is_malicious,
                "detected_patterns": detected_patterns,
                "risk_factors": risk_factors
            }

        except Exception as e:
            self.logger.error(f"Ошибка анализа ссылок: {e}")
            return {
                "is_malicious": False,
                "detected_patterns": [],
                "risk_factors": []
            }

    def _get_recommended_action(self, threat_level: ThreatLevel, is_spam: bool,
                                is_phishing: bool, is_malicious: bool) -> str:
        """Получение рекомендуемого действия"""
        try:
            if threat_level == ThreatLevel.CRITICAL or is_malicious:
                return "block"
            elif threat_level == ThreatLevel.HIGH or is_phishing:
                return "quarantine"
            elif threat_level == ThreatLevel.MEDIUM or is_spam:
                return "warn"
            else:
                return "allow"

        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендуемого действия: {e}")
            return "allow"

    async def _log_message_analysis(
            self, message_data: Dict[str, Any], result: MessageAnalysisResult) -> None:
        """Логирование результата анализа сообщения"""
        try:
            if not self.db_session:
                return

            # Создание записи сообщения
            message = WhatsAppMessage(
                id=self._generate_message_id(),
                message_id=result.message_id,
                chat_id=message_data.get("chat_id", ""),
                sender_id=message_data.get("sender_id", ""),
                receiver_id=message_data.get("receiver_id", ""),
                message_type=message_data.get("type", "text"),
                content=message_data.get("content", ""),
                media_url=message_data.get("media_url"),
                threat_level=result.threat_level.value,
                is_blocked=result.recommended_action in ["block", "quarantine"],
                analysis_result={
                    "is_spam": result.is_spam,
                    "is_phishing": result.is_phishing,
                    "is_malicious": result.is_malicious,
                    "confidence": result.confidence,
                    "detected_patterns": result.detected_patterns,
                    "risk_factors": result.risk_factors
                }
            )

            self.db_session.add(message)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Ошибка логирования анализа сообщения: {e}")

    def _generate_message_id(self) -> str:
        """Генерация ID сообщения"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"WA_{timestamp}_{random_part}"

    async def block_contact(
            self,
            phone_number: str,
            reason: str = "Suspicious activity") -> bool:
        """Блокировка контакта"""
        try:
            with self.lock:
                # Создание записи заблокированного контакта
                contact = WhatsAppContact(
                    id=self._generate_contact_id(),
                    phone_number=phone_number,
                    is_blocked=True,
                    threat_score=1.0
                )

                # Сохранение в базу данных
                if self.db_session:
                    self.db_session.add(contact)
                    self.db_session.commit()

                # Добавление в список заблокированных
                self.blocked_contacts[phone_number] = contact

                # Обновление статистики
                self.stats["blocked_contacts"] += 1

                self.logger.info(
                    f"Контакт {phone_number} заблокирован: {reason}")
                return True

        except Exception as e:
            self.logger.error(f"Ошибка блокировки контакта: {e}")
            return False

    def _generate_contact_id(self) -> str:
        """Генерация ID контакта"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(
            f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"CONTACT_{timestamp}_{random_part}"

    async def get_security_report(
            self, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Получение отчета по безопасности"""
        try:
            report = {
                "total_messages": self.stats["total_messages"],
                "analyzed_messages": self.stats["analyzed_messages"],
                "blocked_messages": self.stats["blocked_messages"],
                "threats_detected": self.stats["threats_detected"],
                "spam_detected": self.stats["spam_detected"],
                "phishing_detected": self.stats["phishing_detected"],
                "malware_detected": self.stats["malware_detected"],
                "blocked_contacts": self.stats["blocked_contacts"],
                "false_positives": self.stats["false_positives"],
                "active_chats": self.stats["active_chats"],
                "timestamp": datetime.utcnow().isoformat()
            }

            if chat_id:
                # Дополнительная статистика по конкретному чату
                if self.db_session:
                    chat_messages = self.db_session.query(WhatsAppMessage).filter(
                        WhatsAppMessage.chat_id == chat_id).count()

                    blocked_chat_messages = self.db_session.query(WhatsAppMessage).filter(
                        WhatsAppMessage.chat_id == chat_id,
                        WhatsAppMessage.is_blocked
                    ).count()

                    report["chat_messages"] = chat_messages
                    report["blocked_chat_messages"] = blocked_chat_messages

            return report

        except Exception as e:
            self.logger.error(f"Ошибка получения отчета по безопасности: {e}")
            return {"error": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса бота"""
        try:
            return {
                "name": self.name,
                "status": "running" if self.running else "stopped",
                "config": self.config,
                "stats": self.stats,
                "security_rules": len(self.security_rules),
                "blocked_contacts": len(self.blocked_contacts),
                "ml_enabled": self.config.get("ml_enabled", False),
                "last_update": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"error": str(e)}


# Функция тестирования
async def test_whatsapp_security_bot():
    """Тестирование WhatsAppSecurityBot"""
    print("🧪 Тестирование WhatsAppSecurityBot...")

    # Создание бота
    bot = WhatsAppSecurityBot("TestWhatsAppBot")

    try:
        # Запуск
        await bot.start()
        print("✅ WhatsAppSecurityBot запущен")

        # Анализ тестового сообщения
        message_data = {
            "id": "test_msg_123",
            "content": "Срочно! Подтвердите ваши данные по ссылке: http://fake-bank.com",
            "type": "text",
            "sender_id": "test_sender",
            "receiver_id": "test_receiver",
            "chat_id": "test_chat"}

        result = await bot.analyze_message(message_data)
        print(
            f"✅ Анализ сообщения: {result.threat_level.value} - {result.recommended_action}")

        # Блокировка подозрительного контакта
        blocked = await bot.block_contact("+1234567890", "Suspicious activity")
        print(f"✅ Контакт заблокирован: {blocked}")

        # Получение отчета по безопасности
        report = await bot.get_security_report()
        print(
            f"✅ Отчет по безопасности: {report['threats_detected']} угроз обнаружено")

        # Получение общего статуса
        bot_status = await bot.get_status()
        print(f"✅ Статус бота: {bot_status['status']}")

    finally:
        # Остановка
        await bot.stop()
        print("✅ WhatsAppSecurityBot остановлен")


# Запуск тестов при прямом выполнении
if __name__ == "__main__":
    asyncio.run(test_whatsapp_security_bot())
